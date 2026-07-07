#!/usr/bin/env python3
"""Deterministic, sequential watchlist orchestrator with cost gating.

Usage:
    py scripts/run_watchlist.py [TICKER ...] [--dry-run] [--force]
                                [--confirm] [--snapshots-file FILE]

Flow per ticker (strictly sequential — no parallelism, no subagents):
  A. Pull a live market snapshot (scripts/market_data.py).
  B. Compute the deterministic signal score and write
     analysis/{TICKER}/pass1_data.json (skipped in --dry-run).
  C. signal_score < 2  ->  Claude analysis is skipped and logged.
  D/E. Qualifying tickers are queued in analysis/run_plan.json for the
     Claude research pass (claude_pass1.json), executed later by the
     orchestrating session, one ticker at a time.
  F. Valuation (pass2) and memo (pass3) then follow the existing workflow.

Cost model: 1 unit per deterministic pass, +5 units per ticker that
qualifies for Claude analysis. Projected cost above the warning threshold
requires --confirm; above the hard stop threshold the run is refused.

--dry-run evaluates snapshots, scores, and projected cost but writes no
files and appends nothing to runlog.md.

--snapshots-file provides pre-fetched snapshots (JSON list or dict keyed by
ticker) for environments where Yahoo Finance is unreachable, and for tests.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from market_data import get_snapshot, MarketDataError  # noqa: E402

WATCHLIST_PATH = os.path.join(ROOT, "config", "watchlist.json")
THRESHOLDS_PATH = os.path.join(ROOT, "config", "thresholds.json")
ANALYSIS_DIR = os.path.join(ROOT, "analysis")
RUNLOG_PATH = os.path.join(ROOT, "runlog.md")
RUN_PLAN_PATH = os.path.join(ANALYSIS_DIR, "run_plan.json")

DETERMINISTIC_UNITS = 1
CLAUDE_UNITS = 5
FRESH_DAYS = 7
FIXED_RELIABILITY = 8  # deterministic pass: single machine-read source

DEFAULT_THRESHOLDS = {"warning_units": 40, "hard_stop_units": 100}


def signal_score(snap):
    """Deterministic signal score from a market snapshot."""
    score = 0
    if snap.get("change_5d_pct") is not None and snap["change_5d_pct"] > 5:
        score += 2
    if snap.get("volume") is not None and snap["volume"] > 1_000_000:
        score += 1
    if snap.get("market_cap") is not None and \
            snap["market_cap"] > 10_000_000_000:
        score += 1
    if snap.get("beta") is not None and snap["beta"] > 1.2:
        score += 1
    return score


def should_send_to_claude(pass1_data):
    """Only tickers with signal_score >= 2 proceed to Claude analysis."""
    return pass1_data.get("signal_score", 0) >= 2


def load_thresholds():
    try:
        with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULT_THRESHOLDS, **data}
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_THRESHOLDS)


def load_watchlist():
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def is_fresh(ticker, now):
    path = os.path.join(ANALYSIS_DIR, ticker, "pass2_valuation.json")
    if not os.path.exists(path):
        return False
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    return (now - mtime) < timedelta(days=FRESH_DAYS)


def append_runlog(rows):
    with open(RUNLOG_PATH, "a", encoding="utf-8", newline="\n") as f:
        for ticker, pass_name, ts, status, reliability, note in rows:
            f.write("| %s | %s | %s | %s | %s | %s |\n"
                    % (ticker, pass_name, ts, status, reliability, note))


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def load_snapshots_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {s["ticker"]: s for s in data}
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="*",
                    help="override config/watchlist.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="ignore the %d-day freshness skip" % FRESH_DAYS)
    ap.add_argument("--confirm", action="store_true",
                    help="proceed past the warning threshold")
    ap.add_argument("--snapshots-file",
                    help="pre-fetched snapshots JSON (list or dict)")
    args = ap.parse_args()

    thresholds = load_thresholds()
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    tickers = args.tickers or load_watchlist()
    pre_fetched = (load_snapshots_file(args.snapshots_file)
                   if args.snapshots_file else {})

    plan, log_rows = [], []
    for ticker in tickers:  # strictly sequential
        if not args.force and is_fresh(ticker, now):
            plan.append({"ticker": ticker, "status": "skipped_fresh"})
            log_rows.append((ticker, "pass1", ts, "SKIPPED_FRESH", "-",
                             "pass2 output < %d days old" % FRESH_DAYS))
            continue
        if ticker in pre_fetched:
            snap = pre_fetched[ticker]
        else:
            try:
                snap = get_snapshot(ticker)
            except MarketDataError as e:
                plan.append({"ticker": ticker, "status": "no_data",
                             "error": str(e)})
                log_rows.append((ticker, "pass1", ts, "FAILED", "-",
                                 "market data unavailable: %s" % e))
                continue
        score = signal_score(snap)
        pass1_data = {
            "ticker": ticker,
            "as_of": ts,
            "market_data": snap,
            "signal_score": score,
            "data_reliability_score": FIXED_RELIABILITY,
        }
        claude = should_send_to_claude(pass1_data)
        plan.append({"ticker": ticker,
                     "status": "claude_queued" if claude
                     else "skipped_low_signal",
                     "signal_score": score,
                     "pass1_data": pass1_data})
        if claude:
            log_rows.append((ticker, "pass1", ts, "VALIDATED",
                             FIXED_RELIABILITY,
                             "signal_score=%d; queued for claude" % score))
        else:
            log_rows.append((ticker, "pass1", ts, "SKIPPED_LOW_SIGNAL",
                             FIXED_RELIABILITY,
                             "signal_score=%d < 2; claude skipped" % score))

    processed = [p for p in plan if "signal_score" in p]
    queued = [p for p in processed if p["status"] == "claude_queued"]
    det_units = len(processed) * DETERMINISTIC_UNITS
    claude_units = len(queued) * CLAUDE_UNITS
    total_units = det_units + claude_units

    print("Projected cost:")
    print("  Deterministic pass units: %d" % det_units)
    print("  Claude analysis units:    %d" % claude_units)
    print("  Total estimated units:    %d" % total_units)
    print("  (warning threshold %d, hard stop %d)"
          % (thresholds["warning_units"], thresholds["hard_stop_units"]))
    print()
    print("| Ticker | Status | Signal | 5d % | Volume | Mkt cap | Beta |")
    print("|--------|--------|--------|------|--------|---------|------|")
    for p in plan:
        md = p.get("pass1_data", {}).get("market_data", {})

        def n(key, fmt="%.2f"):
            v = md.get(key)
            return (fmt % v) if isinstance(v, (int, float)) else "n/a"

        print("| %s | %s | %s | %s | %s | %s | %s |" % (
            p["ticker"], p["status"],
            p.get("signal_score", "-"),
            n("change_5d_pct"), n("volume", "%.0f"),
            n("market_cap", "%.0f"), n("beta")))
    print()

    if args.dry_run:
        print("DRY RUN: no files written, no analysis executed.")
        print("Tickers that would trigger Claude analysis: %s"
              % (", ".join(p["ticker"] for p in queued) or "(none)"))
        return 0

    if total_units > thresholds["hard_stop_units"]:
        print("REFUSED: projected %d units exceeds hard stop threshold %d."
              % (total_units, thresholds["hard_stop_units"]))
        print("Reduce the ticker list and re-run.")
        return 3

    if total_units > thresholds["warning_units"] and not args.confirm:
        print("CONFIRMATION REQUIRED: projected %d units exceeds warning "
              "threshold %d." % (total_units, thresholds["warning_units"]))
        print("Re-run with --confirm to proceed. No files were written.")
        return 2

    for p in processed:
        write_json(os.path.join(ANALYSIS_DIR, p["ticker"],
                                "pass1_data.json"), p["pass1_data"])
    append_runlog(log_rows)
    write_json(RUN_PLAN_PATH, {
        "generated": ts,
        "cost": {"deterministic_units": det_units,
                 "claude_units": claude_units, "total_units": total_units},
        "claude_queue": [p["ticker"] for p in queued],
        "tickers": [{k: v for k, v in p.items() if k != "pass1_data"}
                    for p in plan],
    })

    print("Wrote pass1_data.json for %d ticker(s); %d queued for Claude "
          "analysis (see analysis/run_plan.json)."
          % (len(processed), len(queued)))
    print("Next: run the Claude research pass sequentially for: %s"
          % (", ".join(p["ticker"] for p in queued) or "(none)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
