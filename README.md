# Equity Analysis Orchestrator

Cost-efficient, sequential equity analysis pipeline: a deterministic
yfinance market-data pass filters the watchlist, only high-signal tickers
get Claude research, then valuation and committee memos follow the framework.

- **Framework:** `framework/equity_analysis_framework_v2.md` — analytical
  source of truth for valuation (Pass 2) and memo (Pass 3) content.
- **Market data:** `scripts/market_data.py` — `get_snapshot(ticker)` via
  yfinance.
- **Orchestrator:** `scripts/run_watchlist.py` — sequential deterministic
  pass, signal-score filter (`should_send_to_claude`), cost projection with
  warning/hard-stop gates, `--dry-run`, `--force`, `--snapshots-file`.
- **Validation:** `scripts/validate_json.py` (`pass1`, `claude_pass1`,
  `pass2`); **Ranking:** `scripts/rank_watchlist.py`.
- **Orchestration contract:** see `CLAUDE.md` — sequential only, no
  subagents, no indiscriminate Claude usage.

Edit `config/watchlist.json`, open Claude Code at the repo root, and say
"run the watchlist" (or "run watchlist --dry-run" to preview cost).
