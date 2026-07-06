#!/usr/bin/env python3
"""Validate pass1/pass2 JSON outputs of the equity analysis framework.

Usage:
    py scripts/validate_json.py analysis/{TICKER}/pass1_data.json pass1
    py scripts/validate_json.py analysis/{TICKER}/pass2_valuation.json pass2

Exit code 0 on pass; exit code 1 with a printed list of specific errors on
fail, so the generating agent can self-correct.

Required-field lists are derived from the schemas in
framework/equity_analysis_framework_v2.md.
"""

import json
import re
import sys

# ---------------------------------------------------------------------------
# Schema definitions (from the framework doc)
# ---------------------------------------------------------------------------

# Every metric object uses the shape:
# {value, source, source_date, basis: "reported"|"estimated",
#  confidence: "high"|"medium"|"low"}
METRIC_KEYS = ("value", "source", "source_date", "basis", "confidence")
BASIS_ENUM = ("reported", "estimated")
CONFIDENCE_ENUM = ("high", "medium", "low")

PASS1_METRIC_GROUPS = {
    "market_data": (
        "current_price", "market_cap", "enterprise_value", "diluted_shares",
    ),
    "financials_ttm": (
        "revenue", "gross_margin", "operating_margin", "eps_diluted",
        "fcf", "fcf_margin", "roic", "roe", "roa", "net_debt",
        "interest_coverage",
    ),
    "capital_allocation_3yr": (
        "buybacks", "dividends", "capex", "sbc_pct_revenue",
    ),
}

PASS1_FORWARD_METRICS = (
    "consensus_revenue_fy1", "consensus_revenue_fy2",
    "consensus_eps_fy1", "consensus_eps_fy2",
)

PASS1_TOP_STRINGS = ("ticker", "company", "analysis_date", "data_as_of_date")

FLAG_KEYS = ("missing", "stale", "conflicting", "unverifiable")

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


def check_metric(errors, obj, path, allow_null_value=True):
    """Validate one metric object against the shared shape."""
    if not isinstance(obj, dict):
        errors.append("%s: expected a metric object %s, got %s"
                      % (path, dict(zip(METRIC_KEYS, ("...",) * 5)),
                         type(obj).__name__))
        return
    for key in METRIC_KEYS:
        if key not in obj:
            errors.append("%s: missing required key '%s'" % (path, key))
    v = obj.get("value")
    if v is not None and not is_number(v):
        errors.append("%s.value: expected number or null, got %r" % (path, v))
    if v is None and not allow_null_value:
        errors.append("%s.value: null not allowed here" % path)
    for key in ("source", "source_date"):
        if key in obj and not isinstance(obj[key], (str, type(None))):
            errors.append("%s.%s: expected string, got %r"
                          % (path, key, obj[key]))
    if "basis" in obj and obj["basis"] not in BASIS_ENUM:
        errors.append("%s.basis: %r not in %s" % (path, obj.get("basis"),
                                                  list(BASIS_ENUM)))
    if "confidence" in obj and obj["confidence"] not in CONFIDENCE_ENUM:
        errors.append("%s.confidence: %r not in %s"
                      % (path, obj.get("confidence"), list(CONFIDENCE_ENUM)))


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

    for key in PASS1_TOP_STRINGS:
        check_string(errors, data, key)

    for group, metrics in PASS1_METRIC_GROUPS.items():
        section = data.get(group)
        if not isinstance(section, dict):
            errors.append("missing or non-object section '%s'" % group)
            continue
        for m in metrics:
            if m not in section:
                errors.append("%s: missing required metric '%s'" % (group, m))
            else:
                check_metric(errors, section[m], "%s.%s" % (group, m))

    forward = data.get("forward")
    if not isinstance(forward, dict):
        errors.append("missing or non-object section 'forward'")
    else:
        for m in PASS1_FORWARD_METRICS:
            if m not in forward:
                errors.append("forward: missing required metric '%s'" % m)
            else:
                check_metric(errors, forward[m], "forward.%s" % m)
        for key in ("guidance_verbatim", "guidance_date"):
            check_string(errors, forward, key, "forward.")

    flags = data.get("flags")
    if not isinstance(flags, dict):
        errors.append("missing or non-object section 'flags'")
    else:
        for key in FLAG_KEYS:
            if key not in flags:
                errors.append("flags: missing required list '%s'" % key)
            elif not isinstance(flags[key], list):
                errors.append("flags.%s: expected list, got %s"
                              % (key, type(flags[key]).__name__))

    score = check_number(errors, data, "data_reliability_score")
    if score is not None and not (1 <= score <= 10):
        errors.append("data_reliability_score: %r outside range 1-10" % score)

    check_string(errors, data, "reliability_notes")

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

VALIDATORS = {"pass1": validate_pass1, "pass2": validate_pass2}


def main(argv):
    if len(argv) != 3 or argv[2] not in VALIDATORS:
        print("Usage: validate_json.py <file.json> <pass1|pass2>")
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
