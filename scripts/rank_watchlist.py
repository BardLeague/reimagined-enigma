#!/usr/bin/env python3
"""Rank the watchlist from all analysis/*/pass2_valuation.json files.

Usage:
    py scripts/rank_watchlist.py

Filters out names with data_reliability_score < 6 or
risks.value_trap == "High", sorts the rest by margin_of_safety_percent
descending (tiebreak: overall_score descending), and writes:

    analysis/ranking.md    - human-readable table + filtered-out section
    analysis/ranking.json  - same data for downstream use

Both files are written UTF-8 without BOM.
"""

import glob
import json
import os
import sys
from datetime import datetime, timezone

ANALYSIS_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "analysis")

MIN_RELIABILITY = 6


def load_pass2_files():
    rows, broken = [], []
    pattern = os.path.join(ANALYSIS_DIR, "*", "pass2_valuation.json")
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, "r", encoding="utf-8") as f:
                rows.append((path, json.load(f)))
        except (OSError, json.JSONDecodeError) as e:
            broken.append((path, str(e)))
    return rows, broken


def fmt_num(v, suffix="", decimals=1):
    if v is None or not isinstance(v, (int, float)) or isinstance(v, bool):
        return "n/a"
    return ("%%.%df%%s" % decimals) % (v, suffix)


def build_row(data):
    returns = data.get("returns") or {}
    five = returns.get("five_year") or {}
    dcf = data.get("dcf") or {}
    risks = data.get("risks") or {}
    return {
        "ticker": data.get("ticker", "?"),
        "current_price": data.get("current_price"),
        "expected_intrinsic_value": dcf.get("expected_intrinsic_value"),
        "margin_of_safety_percent": data.get("margin_of_safety_percent"),
        "five_year_expected_return": five.get("expected"),
        "overall_score": data.get("overall_score"),
        "verdict": data.get("verdict", "?"),
        "data_reliability_score": data.get("data_reliability_score"),
        "value_trap": risks.get("value_trap"),
    }


def exclusion_reasons(row):
    reasons = []
    score = row["data_reliability_score"]
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        reasons.append("data_reliability_score missing or non-numeric")
    elif score < MIN_RELIABILITY:
        reasons.append("data_reliability_score %s < %d"
                       % (score, MIN_RELIABILITY))
    if row["value_trap"] == "High":
        reasons.append('risks.value_trap == "High"')
    return reasons


def sort_key(row):
    mos = row["margin_of_safety_percent"]
    score = row["overall_score"]
    mos = mos if isinstance(mos, (int, float)) else float("-inf")
    score = score if isinstance(score, (int, float)) else float("-inf")
    return (-mos, -score)


def main():
    rows, broken = load_pass2_files()
    if not rows and not broken:
        print("No analysis/*/pass2_valuation.json files found - nothing "
              "to rank.")
        return 1

    ranked, excluded = [], []
    for _, data in rows:
        row = build_row(data)
        reasons = exclusion_reasons(row)
        if reasons:
            row["excluded_reasons"] = reasons
            excluded.append(row)
        else:
            ranked.append(row)

    ranked.sort(key=sort_key)

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Watchlist Ranking",
        "",
        "Generated: %s" % generated,
        "",
        "Sorted by margin of safety (desc), tiebreak overall score (desc). "
        "Discount rate is pinned at 10% for every name, so the comparison "
        "is apples-to-apples.",
        "",
        "| # | Ticker | Price | Expected IV | Margin of Safety | "
        "5yr Exp. Return | Overall Score | Verdict | Reliability |",
        "|---|--------|-------|-------------|------------------|"
        "-----------------|---------------|---------|-------------|",
    ]
    for i, row in enumerate(ranked, 1):
        lines.append(
            "| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                i,
                row["ticker"],
                fmt_num(row["current_price"], decimals=2),
                fmt_num(row["expected_intrinsic_value"], decimals=2),
                fmt_num(row["margin_of_safety_percent"], "%"),
                fmt_num(row["five_year_expected_return"], "%"),
                fmt_num(row["overall_score"], decimals=0),
                row["verdict"],
                fmt_num(row["data_reliability_score"], "/10", decimals=0),
            ))
    if not ranked:
        lines.append("| - | (none passed the filters) | | | | | | | |")

    lines += ["", "## Filtered out", ""]
    if excluded or broken:
        for row in excluded:
            lines.append("- **%s**: %s" % (row["ticker"],
                                           "; ".join(row["excluded_reasons"])))
        for path, err in broken:
            lines.append("- **%s**: unreadable pass2 file (%s)"
                         % (os.path.basename(os.path.dirname(path)), err))
    else:
        lines.append("(none)")
    lines.append("")

    md_path = os.path.join(ANALYSIS_DIR, "ranking.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    json_path = os.path.join(ANALYSIS_DIR, "ranking.json")
    payload = {
        "generated": generated,
        "filters": {
            "min_data_reliability_score": MIN_RELIABILITY,
            "exclude_value_trap": "High",
        },
        "ranked": ranked,
        "excluded": excluded,
        "unreadable": [{"path": p, "error": e} for p, e in broken],
    }
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\n".join(lines))
    print("\nWrote %s and %s" % (md_path, json_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
