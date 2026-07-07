#!/usr/bin/env python3
"""Validate JSON outputs of the equity analysis pipeline.

Usage:
    py scripts/validate_json.py analysis/{TICKER}/pass1_data.json pass1
    py scripts/validate_json.py analysis/{TICKER}/claude_pass1.json claude_pass1
    py scripts/validate_json.py analysis/{TICKER}/pass2_valuation.json pass2

Exit code 0 on pass; exit code 1 with a printed list of specific errors on
fail, so the generating process can self-correct.

pass1 is the deterministic market-data pass (scripts/run_watchlist.py);
claude_pass1 is the selective Claude research pass; pass2 required fields
are derived from the schema in framework/equity_analysis_framework_v2.md.
"""

import json
import re
import sys

# ---------------------------------------------------------------------------
# Schema definitions (from the framework doc)
# ---------------------------------------------------------------------------

# Deterministic pass1: market snapshot fields. Required numeric fields must
# be numbers; nullable fields may be null when the provider had no value.
PASS1_SNAPSHOT_REQUIRED = ("last_price", "change_5d_pct", "volume")
PASS1_SNAPSHOT_NULLABLE = ("market_cap", "pe_ratio", "beta")

SENTIMENT_ENUM = ("bullish", "neutral", "bearish")
CLAUDE_PASS1_LISTS = ("catalysts", "risk_factors")

VERDICT_ENUM = ("strong_buy", "buy", "hold", "avoid", "short_candidate")
RISK_KEYS = ("value_trap", "bankruptcy", "competitive", "regulatory",
             "technological")
RISK_ENUM = ("Low", "Medium", "High")
SCENARIO_KEYS = ("bear", "base", "bull")

PASS2_TOP_STRINGS = (
    "ticker", "company", "analysis_date", "data_as_of_date",
    "business_type", "moat_rating", "moat_source", "management_grade",
    "capital_allocation_grade", "balance_sheet_grade",
    "sensitivity_key_driver", "primary_model_risk",
    "expectations_gap_verdict", "expectations_gap_key_variable",
    "position_size_recommendation", "verdict", "confidence_level",
)

PASS2_TOP_NUMBERS = (
    "roic", "roe", "roa", "current_price", "margin_of_safety_percent",
    "probability_of_success", "probability_of_permanent_loss",
    "overall_score",
)

PASS2_TOP_LISTS = ("top_5_bull_arguments", "top_5_bear_arguments",
                   "thesis_breakers")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def diagnose_raw(raw):
    """Return hints about common non-strict-JSON artifacts in raw text."""
    hints = []
    if raw.startswith("﻿"):
        hints.append("File starts with a UTF-8 BOM. Rewrite as UTF-8 "
                     "without BOM (PowerShell's default encoding adds one).")
    if re.search(r"^\s*```", raw, re.MULTILINE):
        hints.append("File contains markdown code fences (```); the file "
                     "must be raw JSON only.")
    curly = [c for c in "‘’“”" if c in raw]
    if curly:
        hints.append("File contains curly/smart quotes (%s); use straight "
                     "ASCII quotes only." % ", ".join(repr(c) for c in curly))
    if re.search(r",\s*[}\]]", raw):
        hints.append("Possible trailing comma before a closing brace or "
                     "bracket.")
    if re.search(r"^\s*//", raw, re.MULTILINE) or "/*" in raw:
        hints.append("Possible comments in file; JSON does not allow "
                     "comments.")
    return hints


def check_string(errors, data, key, path=""):
    full = "%s%s" % (path, key)
    if key not in data:
        errors.append("missing required field '%s'" % full)
    elif not isinstance(data[key], str):
        errors.append("%s: expected string, got %s"
                      % (full, type(data[key]).__name__))


def check_number(errors, data, key, path="", allow_null=False):
    full = "%s%s" % (path, key)
    if key not in data:
        errors.append("missing required field '%s'" % full)
        return None
    v = data[key]
    if v is None and allow_null:
        return None
    if not is_number(v):
        errors.append("%s: expected number, got %r" % (full, v))
        return None
    return v


# ---------------------------------------------------------------------------
# Pass 1
# ---------------------------------------------------------------------------

def validate_pass1(data):
    errors = []

    check_string(errors, data, "ticker")

    md = data.get("market_data")
    if not isinstance(md, dict):
        errors.append("missing or non-object section 'market_data'")
    else:
        for key in PASS1_SNAPSHOT_REQUIRED:
            check_number(errors, md, key, "market_data.")
        for key in PASS1_SNAPSHOT_NULLABLE:
            check_number(errors, md, key, "market_data.", allow_null=True)

    score = check_number(errors, data, "signal_score")
    if score is not None and (not isinstance(score, int) or score < 0):
        errors.append("signal_score: %r must be a non-negative integer"
                      % score)

    rel = check_number(errors, data, "data_reliability_score")
    if rel is not None and not (1 <= rel <= 10):
        errors.append("data_reliability_score: %r outside range 1-10" % rel)

    return errors


# ---------------------------------------------------------------------------
# Claude research pass
# ---------------------------------------------------------------------------

def validate_claude_pass1(data):
    errors = []

    for key in ("ticker", "thesis"):
        check_string(errors, data, key)

    for key in CLAUDE_PASS1_LISTS:
        if key not in data:
            errors.append("missing required field '%s'" % key)
        elif not isinstance(data[key], list):
            errors.append("%s: expected list, got %s"
                          % (key, type(data[key]).__name__))
        elif not all(isinstance(x, str) for x in data[key]):
            errors.append("%s: all entries must be strings" % key)

    if data.get("sentiment") not in SENTIMENT_ENUM:
        errors.append("sentiment: %r not in %s"
                      % (data.get("sentiment"), list(SENTIMENT_ENUM)))

    return errors


# ---------------------------------------------------------------------------
# Pass 2
# ---------------------------------------------------------------------------

def validate_pass2(data):
    errors = []

    for key in PASS2_TOP_STRINGS:
        check_string(errors, data, key)
    for key in PASS2_TOP_NUMBERS:
        check_number(errors, data, key, allow_null=(key in ("roic", "roe",
                                                            "roa")))
    for key in PASS2_TOP_LISTS:
        if key not in data:
            errors.append("missing required field '%s'" % key)
        elif not isinstance(data[key], list):
            errors.append("%s: expected list, got %s"
                          % (key, type(data[key]).__name__))

    score = check_number(errors, data, "data_reliability_score")
    if score is not None and not (1 <= score <= 10):
        errors.append("data_reliability_score: %r outside range 1-10" % score)

    overall = data.get("overall_score")
    if is_number(overall) and not (0 <= overall <= 100):
        errors.append("overall_score: %r outside range 0-100" % overall)

    if isinstance(data.get("verdict"), str) and \
            data["verdict"] not in VERDICT_ENUM:
        errors.append("verdict: %r not in %s"
                      % (data["verdict"], list(VERDICT_ENUM)))

    # --- dcf block ---
    dcf = data.get("dcf")
    if not isinstance(dcf, dict):
        errors.append("missing or non-object section 'dcf'")
    else:
        rate = dcf.get("discount_rate")
        if rate != 0.10:
            errors.append("dcf.discount_rate: must be exactly 0.10 "
                          "(comparability constraint), got %r" % rate)
        prob_sum = 0
        prob_ok = True
        for s in SCENARIO_KEYS:
            scen = dcf.get(s)
            if not isinstance(scen, dict):
                errors.append("dcf.%s: missing or non-object scenario" % s)
                prob_ok = False
                continue
            for key in ("probability", "intrinsic_value",
                        "terminal_multiple"):
                v = check_number(errors, scen, key, "dcf.%s." % s)
                if key == "probability":
                    if v is None:
                        prob_ok = False
                    else:
                        prob_sum += v
        if prob_ok and abs(prob_sum - 100) > 1e-6:
            errors.append("dcf: scenario probabilities sum to %s, must sum "
                          "to 100" % prob_sum)
        check_number(errors, dcf, "expected_intrinsic_value", "dcf.")

    # --- returns block ---
    returns = data.get("returns")
    if not isinstance(returns, dict):
        errors.append("missing or non-object section 'returns'")
    else:
        for horizon in ("three_year", "five_year"):
            block = returns.get(horizon)
            if not isinstance(block, dict):
                errors.append("returns.%s: missing or non-object" % horizon)
                continue
            for key in ("bear", "base", "bull", "expected"):
                check_number(errors, block, key, "returns.%s." % horizon)

    # --- risks block ---
    risks = data.get("risks")
    if not isinstance(risks, dict):
        errors.append("missing or non-object section 'risks'")
    else:
        for key in RISK_KEYS:
            if key not in risks:
                errors.append("risks: missing required rating '%s'" % key)
            elif risks[key] not in RISK_ENUM:
                errors.append("risks.%s: %r not in %s"
                              % (key, risks[key], list(RISK_ENUM)))

    return errors


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

VALIDATORS = {"pass1": validate_pass1, "claude_pass1": validate_claude_pass1,
              "pass2": validate_pass2}


def main(argv):
    if len(argv) != 3 or argv[2] not in VALIDATORS:
        print("Usage: validate_json.py <file.json> "
              "<pass1|claude_pass1|pass2>")
        return 1

    path, which = argv[1], argv[2]

    try:
        with open(path, "rb") as f:
            raw_bytes = f.read()
    except OSError as e:
        print("FAIL: cannot read %s: %s" % (path, e))
        return 1

    raw = raw_bytes.decode("utf-8", errors="replace")

    try:
        # Strict parse of the exact file bytes; a BOM makes this fail,
        # which is intended (files must be UTF-8 without BOM).
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("FAIL: %s is not strict JSON" % path)
        print("  - JSON parse error: %s" % e)
        for hint in diagnose_raw(raw):
            print("  - hint: %s" % hint)
        return 1

    if not isinstance(data, dict):
        print("FAIL: %s: top-level value must be a JSON object" % path)
        return 1

    errors = VALIDATORS[which](data)

    if errors:
        print("FAIL: %s failed %s validation with %d error(s):"
              % (path, which, len(errors)))
        for err in errors:
            print("  - %s" % err)
        return 1

    print("PASS: %s is valid %s output" % (path, which))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
