#!/usr/bin/env python3
"""Deterministic LEAPS call scan over the ranked watchlist.

Usage:
    py scripts/leaps_scan.py [options] [TICKER ...]

Options:
    --budget N          max premium per contract in dollars (default 3500)
    --min-dte N         minimum days to expiration (default 365)
    --verdicts LIST     comma-separated ranking verdicts to include when no
                        tickers are given (default strong_buy,buy)
    --min-oi N          minimum open interest (default 25)
    --max-spread-pct N  max bid/ask spread as % of mid (default 15)
    --delta-band LO,HI  approximate-delta band to keep (default 0.45,0.90);
                        contracts with no implied vol are kept but flagged
    --rate R            risk-free rate for the delta approximation
                        (default 0.04)
    --chains-file FILE  pre-fetched chains JSON (output of
                        `market_data.py --options T1 T2 ...`) for
                        environments where Yahoo Finance is blocked
    --out FILE          output path (default analysis/leaps_scan.json)

Reads analysis/ranking.json for verdicts and expected intrinsic values; the
scan itself introduces no new fundamental figures. The Black-Scholes delta
is an approximation computed from the quoted implied volatility and is
labeled as such in the output.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RANKING = os.path.join(ROOT, "analysis", "ranking.json")


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_call_delta(spot, strike, dte_days, iv, rate):
    """Approximate Black-Scholes call delta; None when inputs unusable."""
    if not spot or not strike or not iv or iv <= 0 or dte_days <= 0:
        return None
    t = dte_days / 365.0
    try:
        d1 = ((math.log(spot / strike) + (rate + 0.5 * iv * iv) * t)
              / (iv * math.sqrt(t)))
    except (ValueError, ZeroDivisionError):
        return None
    return norm_cdf(d1)


def mid_price(call):
    bid, ask = call.get("bid"), call.get("ask")
    if bid and ask and bid > 0 and ask >= bid:
        return (bid + ask) / 2.0
    last = call.get("last")
    return last if last and last > 0 else None


def scan_ticker(chain, rank_row, opts):
    ticker = chain["ticker"]
    spot = chain.get("last_price")
    expected_iv_ps = rank_row.get("expected_intrinsic_value")
    candidates = []
    for exp in chain.get("expirations", ()):
        if exp["dte_days"] < opts["min_dte"]:
            continue
        for call in exp.get("calls", ()):
            strike = call.get("strike")
            mid = mid_price(call)
            if not strike or not mid:
                continue
            cost = mid * 100.0
            if cost > opts["budget"]:
                continue
            oi = call.get("open_interest") or 0
            if oi < opts["min_oi"]:
                continue
            bid, ask = call.get("bid"), call.get("ask")
            spread_pct = None
            if bid and ask and bid > 0:
                spread_pct = (ask - bid) / mid * 100.0
                if spread_pct > opts["max_spread_pct"]:
                    continue
            delta = bs_call_delta(spot, strike, exp["dte_days"],
                                  call.get("implied_volatility"),
                                  opts["rate"])
            if delta is not None and not (
                    opts["delta_lo"] <= delta <= opts["delta_hi"]):
                continue
            breakeven = strike + mid
            payoff_at_expected_iv = None
            payoff_ratio = None
            if expected_iv_ps:
                payoff_at_expected_iv = max(expected_iv_ps - strike, 0) * 100
                payoff_ratio = payoff_at_expected_iv / cost if cost else None
            candidates.append({
                "ticker": ticker,
                "expiration": exp["expiration"],
                "dte_days": exp["dte_days"],
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid": round(mid, 2),
                "cost_per_contract": round(cost, 2),
                "open_interest": oi,
                "spread_pct": round(spread_pct, 1)
                              if spread_pct is not None else None,
                "implied_volatility": call.get("implied_volatility"),
                "approx_delta": round(delta, 3) if delta is not None
                                else None,
                "breakeven": round(breakeven, 2),
                "breakeven_vs_spot_pct": round(
                    (breakeven / spot - 1.0) * 100.0, 1) if spot else None,
                "spot": spot,
                "ranking_verdict": rank_row.get("verdict"),
                "expected_intrinsic_value": expected_iv_ps,
                "payoff_if_converges_to_iv": payoff_at_expected_iv,
                "payoff_ratio": round(payoff_ratio, 2)
                                if payoff_ratio is not None else None,
            })
    return candidates


def parse_args(argv):
    opts = {"budget": 3500.0, "min_dte": 365, "min_oi": 25,
            "max_spread_pct": 15.0, "delta_lo": 0.45, "delta_hi": 0.90,
            "rate": 0.04, "chains_file": None,
            "verdicts": ("strong_buy", "buy"),
            "out": os.path.join(ROOT, "analysis", "leaps_scan.json")}
    tickers = []
    it = iter(argv[1:])
    for a in it:
        if a == "--budget":
            opts["budget"] = float(next(it))
        elif a == "--min-dte":
            opts["min_dte"] = int(next(it))
        elif a == "--min-oi":
            opts["min_oi"] = int(next(it))
        elif a == "--max-spread-pct":
            opts["max_spread_pct"] = float(next(it))
        elif a == "--delta-band":
            lo, hi = next(it).split(",")
            opts["delta_lo"], opts["delta_hi"] = float(lo), float(hi)
        elif a == "--rate":
            opts["rate"] = float(next(it))
        elif a == "--chains-file":
            opts["chains_file"] = next(it)
        elif a == "--verdicts":
            opts["verdicts"] = tuple(next(it).split(","))
        elif a == "--out":
            opts["out"] = next(it)
        elif a.startswith("--"):
            print("unknown option: %s" % a, file=sys.stderr)
            return None, None
        else:
            tickers.append(a.upper())
    return opts, tickers


def main(argv):
    opts, tickers = parse_args(argv)
    if opts is None:
        return 1

    with open(RANKING, "r", encoding="utf-8") as f:
        ranking = json.load(f)
    rank_by_ticker = {r["ticker"]: r for r in ranking.get("ranked", ())}

    if not tickers:
        tickers = [r["ticker"] for r in ranking.get("ranked", ())
                   if r.get("verdict") in opts["verdicts"]]
    if not tickers:
        print("No tickers matched verdicts %s" % (opts["verdicts"],))
        return 1

    chains = {}
    if opts["chains_file"]:
        with open(opts["chains_file"], "r", encoding="utf-8") as f:
            for chain in json.load(f):
                chains[chain["ticker"]] = chain
    else:
        sys.path.insert(0, HERE)
        from market_data import MarketDataError, get_leaps_chain
        for ticker in tickers:  # strictly sequential
            try:
                chains[ticker] = get_leaps_chain(ticker, opts["min_dte"])
            except MarketDataError as e:
                print("ERROR: %s" % e, file=sys.stderr)

    all_candidates, missing = [], []
    for ticker in tickers:
        chain = chains.get(ticker)
        if not chain:
            missing.append(ticker)
            continue
        all_candidates.extend(
            scan_ticker(chain, rank_by_ticker.get(ticker, {}), opts))

    all_candidates.sort(
        key=lambda c: (c["payoff_ratio"] is None,
                       -(c["payoff_ratio"] or 0.0)))

    result = {
        "generated": __import__("datetime").datetime.utcnow()
                     .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "criteria": {
            "budget_per_contract": opts["budget"],
            "min_dte_days": opts["min_dte"],
            "min_open_interest": opts["min_oi"],
            "max_spread_pct": opts["max_spread_pct"],
            "approx_delta_band": [opts["delta_lo"], opts["delta_hi"]],
            "risk_free_rate_for_delta": opts["rate"],
            "verdicts": list(opts["verdicts"]),
        },
        "note": ("approx_delta is a Black-Scholes approximation from quoted "
                 "implied volatility; payoff_if_converges_to_iv assumes the "
                 "underlying reaches the pipeline's expected intrinsic value "
                 "by expiration and is a scenario, not a forecast."),
        "tickers_scanned": [t for t in tickers if t in chains],
        "tickers_missing_chain": missing,
        "candidates": all_candidates,
    }
    with open(opts["out"], "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print("Wrote %s (%d candidates, %d tickers, %d missing chains)"
          % (opts["out"], len(all_candidates), len(result["tickers_scanned"]),
             len(missing)))

    for c in all_candidates[:20]:
        print("%-5s %s (%dd) K=%-8.2f mid=%-8.2f cost=%-8.0f delta~%-5s "
              "BE=%+.1f%% OI=%-6d payoff_ratio=%s"
              % (c["ticker"], c["expiration"], c["dte_days"], c["strike"],
                 c["mid"], c["cost_per_contract"],
                 c["approx_delta"] if c["approx_delta"] is not None else "?",
                 c["breakeven_vs_spot_pct"], c["open_interest"],
                 c["payoff_ratio"]))
    return 0 if not missing else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
