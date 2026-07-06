# Equity Analysis Orchestrator

Claude Code orchestration for a three-pass equity analysis framework
(research → valuation → committee memo) across a watchlist of tickers.

- **Framework:** `framework/equity_analysis_framework_v2.md` — the analytical
  source of truth.
- **Subagents:** `.claude/agents/` — `research-analyst` (Pass 1),
  `valuation-analyst` (Pass 2), `memo-writer` (Pass 3), each embedding its
  framework pass verbatim.
- **Scripts:** `scripts/validate_json.py` (validation gate between passes),
  `scripts/rank_watchlist.py` (cross-watchlist ranking).
- **Orchestration:** see `CLAUDE.md` for the "run the watchlist",
  "run {TICKER}", and "rerank" workflows.

Edit `config/watchlist.json` to set your tickers, open Claude Code at the
repo root, and say "run the watchlist".
