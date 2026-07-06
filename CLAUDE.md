# Equity Analysis Orchestrator

This project runs a three-pass equity analysis framework across a watchlist of
tickers. The framework lives in `framework/equity_analysis_framework_v2.md` and
is the single source of truth for analysis content; the three subagents in
`.claude/agents/` each embed their pass verbatim.

## Layout

```
framework/equity_analysis_framework_v2.md   # the framework (source of truth)
config/watchlist.json                       # array of ticker strings
analysis/{TICKER}/pass1_data.json           # Pass 1 output (research-analyst)
analysis/{TICKER}/pass2_valuation.json      # Pass 2 output (valuation-analyst)
analysis/{TICKER}/pass3_memo.md             # Pass 3 output (memo-writer)
analysis/ranking.md / ranking.json          # rank_watchlist.py output
scripts/validate_json.py                    # schema validation between passes
scripts/rank_watchlist.py                   # final ranking
runlog.md                                   # append-only run log
```

Python is invoked as `py` (Windows launcher). If `py` is not on PATH (e.g. a
Linux session), substitute `python3` — same arguments.

## Commands (user-triggered workflows)

### "run the watchlist"

1. Read `config/watchlist.json`. **Before the first full run in a session,
   show the ticker list and ask the user to confirm it** — then proceed.
2. Freshness check: skip any ticker whose `analysis/{TICKER}/pass2_valuation.json`
   already exists and is less than 7 days old, unless the user said "force".
   Log skips as `SKIPPED_FRESH` in `runlog.md`.
3. Launch a `research-analyst` subagent for every remaining ticker **in
   parallel** (one Agent call per ticker, all in one batch). Each prompt names
   exactly one ticker.
4. As each Pass 1 validates, launch that ticker's `valuation-analyst`, then its
   `memo-writer`, **sequentially per ticker**. Different tickers may proceed
   independently — never let one ticker block the batch.
5. Stop rule: if Pass 1 reports `data_reliability_score <= 3`, do NOT run
   Pass 2/3 for that ticker. Log `SKIPPED_LOW_RELIABILITY` with the note
   "insufficient data quality".
6. Failure policy: each pass validates itself and gets up to two
   self-correction attempts. If a pass still fails validation after that, mark
   the ticker `FAILED` in `runlog.md` with the validator error, and continue
   with the remaining tickers.
7. When all tickers are done, run `py scripts/rank_watchlist.py` and show the
   user the ranking table it prints.
8. Log every pass transition in `runlog.md` (see format at the top of that
   file). Append only — never rewrite existing rows.

### "run {TICKER}"

Run the single ticker end-to-end with the same rules as above (freshness check,
stop rule, failure policy, runlog entries), then re-run
`py scripts/rank_watchlist.py` so the ranking reflects the new output.

### "rerank"

Just run `py scripts/rank_watchlist.py` against existing outputs and show the
table. No re-analysis.

## Hard rules

- Subagent prompts already contain the framework pass text verbatim — task
  prompts to them only need the ticker and any run-specific notes (e.g.
  "force"). Do not restate or paraphrase the framework in task prompts.
- Never let any agent invent financial figures. Pass 2 may only use numbers
  from `pass1_data.json`; Pass 3 only from the two JSON files. These
  ground-truth constraints are load-bearing.
- All file writes are UTF-8 **without BOM** (PowerShell's default encoding
  will bite otherwise; the validator intentionally fails on a BOM).
- Analysis JSON files are raw JSON: straight ASCII quotes, no trailing commas,
  no comments, no markdown fences.
- Validation gates are mandatory: a ticker's Pass N+1 starts only after
  `scripts/validate_json.py` printed PASS for Pass N.
