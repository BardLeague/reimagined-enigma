#!/usr/bin/env python3
"""Live market data layer (yfinance).

Usage:
    py scripts/market_data.py NVDA MU ...      # prints JSON list of snapshots

get_snapshot(ticker) returns:
    {
      "ticker": str,
      "last_price": float,
      "change_5d_pct": float,
      "volume": float,
      "market_cap": int | None,
      "pe_ratio": float | None,
      "beta": float | None
    }

Fields that cannot be determined are None; a ticker whose price history is
entirely unavailable raises MarketDataError. Network note: this module needs
outbound access to Yahoo Finance. In environments where that host is blocked
by egress policy, pre-fetch snapshots elsewhere and feed them to
run_watchlist.py via --snapshots-file.
"""

import json
import sys


class MarketDataError(Exception):
    """Raised when no usable market data could be fetched for a ticker."""


def _to_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None  # reject NaN


def _to_int(v):
    f = _to_float(v)
    return int(f) if f is not None else None


def get_snapshot(ticker):
    """Fetch a point-in-time market snapshot for one ticker via yfinance."""
    import yfinance as yf

    t = yf.Ticker(ticker)

    try:
        hist = t.history(period="6d", interval="1d", auto_adjust=True)
    except Exception as e:
        raise MarketDataError("%s: price history fetch failed: %s"
                              % (ticker, e)) from e
    if hist is None or len(hist) == 0:
        raise MarketDataError("%s: no price history returned" % ticker)

    closes = [c for c in hist["Close"].tolist() if _to_float(c) is not None]
    if not closes:
        raise MarketDataError("%s: no usable closing prices" % ticker)

    last_price = float(closes[-1])
    change_5d_pct = None
    if len(closes) >= 2 and closes[0]:
        change_5d_pct = (last_price / float(closes[0]) - 1.0) * 100.0

    volumes = [v for v in hist["Volume"].tolist() if _to_float(v) is not None]
    volume = float(volumes[-1]) if volumes else None

    market_cap = pe_ratio = beta = None
    try:
        fi = t.fast_info
        market_cap = _to_int(getattr(fi, "market_cap", None))
    except Exception:
        pass
    try:
        info = t.info or {}
        if market_cap is None:
            market_cap = _to_int(info.get("marketCap"))
        pe_ratio = _to_float(info.get("trailingPE"))
        beta = _to_float(info.get("beta"))
        if volume is None:
            volume = _to_float(info.get("averageVolume"))
    except Exception:
        pass  # profile endpoints are best-effort; price data is mandatory

    return {
        "ticker": ticker,
        "last_price": last_price,
        "change_5d_pct": change_5d_pct,
        "volume": volume,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "beta": beta,
    }


def get_leaps_chain(ticker, min_dte_days=365):
    """Fetch long-dated call options for one ticker via yfinance.

    Returns {"ticker", "as_of", "last_price", "expirations": [
        {"expiration", "dte_days", "calls": [
            {"strike", "bid", "ask", "last", "open_interest", "volume",
             "implied_volatility", "in_the_money"}]}]}.
    Only expirations at least min_dte_days out are included. Raises
    MarketDataError when the chain is unavailable (same network caveat as
    get_snapshot: pre-fetch elsewhere and use leaps_scan.py --chains-file
    when Yahoo Finance is blocked).
    """
    import datetime

    import yfinance as yf

    t = yf.Ticker(ticker)
    try:
        expirations = list(t.options or ())
    except Exception as e:
        raise MarketDataError("%s: option expirations fetch failed: %s"
                              % (ticker, e)) from e
    if not expirations:
        raise MarketDataError("%s: no option expirations returned" % ticker)

    today = datetime.date.today()
    out_exps = []
    for exp in expirations:
        try:
            exp_date = datetime.date.fromisoformat(exp)
        except ValueError:
            continue
        dte = (exp_date - today).days
        if dte < min_dte_days:
            continue
        try:
            chain = t.option_chain(exp)
        except Exception as e:
            raise MarketDataError("%s: option chain fetch failed for %s: %s"
                                  % (ticker, exp, e)) from e
        calls = []
        for row in chain.calls.itertuples():
            calls.append({
                "strike": _to_float(getattr(row, "strike", None)),
                "bid": _to_float(getattr(row, "bid", None)),
                "ask": _to_float(getattr(row, "ask", None)),
                "last": _to_float(getattr(row, "lastPrice", None)),
                "open_interest": _to_int(getattr(row, "openInterest", None)),
                "volume": _to_int(getattr(row, "volume", None)),
                "implied_volatility": _to_float(
                    getattr(row, "impliedVolatility", None)),
                "in_the_money": bool(getattr(row, "inTheMoney", False)),
            })
        out_exps.append({"expiration": exp, "dte_days": dte, "calls": calls})

    snapshot = get_snapshot(ticker)
    return {
        "ticker": ticker,
        "as_of": today.isoformat(),
        "last_price": snapshot["last_price"],
        "expirations": out_exps,
    }


def main(argv):
    args = argv[1:]
    fetch_options = "--options" in args
    args = [a for a in args if a != "--options"]
    if not args:
        print("Usage: market_data.py [--options] TICKER [TICKER ...]")
        return 1
    out, failed = [], []
    for ticker in args:
        try:
            if fetch_options:
                out.append(get_leaps_chain(ticker))
            else:
                out.append(get_snapshot(ticker))
        except MarketDataError as e:
            failed.append(str(e))
    print(json.dumps(out, indent=2))
    for msg in failed:
        print("ERROR: %s" % msg, file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
