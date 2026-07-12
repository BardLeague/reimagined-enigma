# Equity Analysis Orchestrator (v3 — sequential, cost-gated)

Three-stage pipeline: a **deterministic** market-data pass filters the
watchlist, a **selective** Claude research pass runs only on tickers that
clear the signal filter, and the existing valuation/memo/ranking workflow
follows. The analytical framework lives in
`framework/equity_analysis_framework_v2.md` (Pass 2 valuation and Pass 3 memo
content are still authoritative there).

## Layout

```
framework/equity_analysis_framework_v2.md   # valuation/memo framework (source of truth)
config/watchlist.json                       # array of ticker strings
config/thresholds.json                      # cost gates: warning_units, hard_stop_units
scripts/market_data.py                      # yfinance layer: get_snapshot(ticker), get_leaps_chain(ticker)
scripts/run_watchlist.py                    # deterministic orchestrator (pass1 + filter + cost gate)
scripts/validate_json.py                    # validation: pass1 | claude_pass1 | pass2
scripts/rank_watchlist.py                   # final ranking (unchanged)
scripts/leaps_scan.py                       # deterministic LEAPS call scan over ranked buy-rated names
analysis/{TICKER}/pass1_data.json           # deterministic market snapshot + signal score
analysis/{TICKER}/claude_pass1.json         # Claude research pass (only if signal_score >= 2)
analysis/{TICKER}/pass2_valuation.json      # valuation (framework Pass 2)
analysis/{TICKER}/pass3_memo.md             # committee memo (framework Pass 3)
analysis/run_plan.json                      # run_watchlist.py output: queue + cost
analysis/ranking.md / ranking.json          # rank_watchlist.py output
analysis/leaps_scan.json / leaps_scan.md    # leaps_scan.py output + narrative report
runlog.md                                   # append-only run log
```

Python is `py` on Windows, `python3` elsewhere — same arguments.

## Hard constraints (non-negotiable)

- **Sequential execution only.** One ticker at a time, one pass at a time.
- **Never spawn subagents or parallel agents** — no Agent-tool calls, no
  recursive agent chains. All Claude work happens inline in the main session.
- **Never run Claude analysis on all tickers indiscriminately** — only
  tickers where `should_send_to_claude` returned true (signal_score >= 2).
- **Cost gates are mandatory**: 1 unit per deterministic pass, 5 units per
  Claude-analyzed ticker. `run_watchlist.py` enforces them (exit 2 = needs
  confirmation, exit 3 = refused). Never bypass a hard stop.
- No web access outside `scripts/market_data.py` and the explicit Claude
  research pass.
- All file writes UTF-8 without BOM; analysis JSON is raw JSON (straight
  quotes, no trailing commas, no fences).
- Validation gates: the next stage of a ticker starts only after
  `scripts/validate_json.py` printed PASS for the current stage's file.
- Never invent financial figures. Pass 2 may only use numbers present in
  `pass1_data.json` and `claude_pass1.json` (whose figures must carry
  sources); Pass 3 only numbers from the pass1/claude_pass1/pass2 files.

## Commands (user-triggered workflows)

### "run the watchlist" (optionally "force" / "dry-run")

1. Before the first full run in a session, show the ticker list from
   `config/watchlist.json` and ask the user to confirm it.
2. Run the deterministic stage (strictly sequential inside the script):
   `python3 scripts/run_watchlist.py` (add `--force` to ignore the 7-day
   freshness skip; add `--dry-run` for evaluation only).
   - Exit 2: projected cost exceeds the warning threshold. Show the user the
     printed projection, ask for confirmation, and re-run with `--confirm`
     only if they approve.
   - Exit 3: hard stop exceeded. Report and stop — do not work around it.
   The script writes `pass1_data.json` per ticker, appends runlog rows, and
   writes `analysis/run_plan.json` with the `claude_queue`.
3. For each ticker in `claude_queue`, **one at a time, in order**:
   a. **Claude research pass** (inline): using web search scoped to this
      ticker, produce `analysis/{TICKER}/claude_pass1.json`:
      `{"ticker", "thesis", "catalysts": [], "risk_factors": [],
      "sentiment": "bullish|neutral|bearish"}`.
      Optionally add `"key_financials"`: sourced figures (revenue, FCF, net
      debt, shares, guidance — each with source + date) so Pass 2 has ground
      truth to value from. Never state a figure without its source.
      Validate: `python3 scripts/validate_json.py analysis/{TICKER}/claude_pass1.json claude_pass1`
   b. **Pass 2 valuation** (inline, per framework Pass 2 text): numbers only
      from `pass1_data.json` + `claude_pass1.json`. If `key_financials` is
      too thin for a responsible DCF, degrade honestly (nulls + explanation,
      lower `confidence_level`) rather than inventing inputs. Write
      `pass2_valuation.json`, validate with `... pass2`.
   c. **Pass 3 memo** (inline, per framework Pass 3 text): write
      `pass3_memo.md` from the JSON files only.
   d. Log each stage in `runlog.md` (append-only). Up to two self-correction
      attempts per validation; then mark the ticker FAILED and move on.
4. Tickers with `signal_score < 2` are already logged as
   `SKIPPED_LOW_SIGNAL` by the script — no Claude work for them, ever.
5. When the queue is exhausted, run `python3 scripts/rank_watchlist.py` and
   show the ranking table.

### "run {TICKER}"

`python3 scripts/run_watchlist.py {TICKER}` then steps 3–5 above for that
ticker only. Same gates, same logging.

### "run watchlist --dry-run"

`python3 scripts/run_watchlist.py --dry-run` — shows which tickers would
trigger Claude analysis and the projected cost. Executes no analysis, writes
no files. Report the table to the user and stop.

### "scan leaps" (optionally "--budget N")

`python3 scripts/leaps_scan.py` — deterministic scan of long-dated calls
(≥ 365 DTE, premium ≤ budget, OI/spread/delta filters) on tickers whose
ranking verdict is strong_buy/buy. Uses `get_leaps_chain` from
`scripts/market_data.py` (same Yahoo egress caveat: pre-fetch with
`py scripts/market_data.py --options T1 T2 ... > chains.json` and pass
`--chains-file chains.json` where Yahoo is blocked). Writes
`analysis/leaps_scan.json`; narrative goes in `analysis/leaps_scan.md`.
Costs 1 unit per scanned ticker (deterministic pass); no Claude analysis
is triggered by this command.

### "rerank"

`python3 scripts/rank_watchlist.py` against existing outputs. No re-analysis.

## Notes

- Remote/CI sessions: Yahoo Finance may be blocked by egress policy. In that
  case pre-fetch snapshots on a machine with access
  (`py scripts/market_data.py NVDA MU ... > snapshots.json`) and pass
  `--snapshots-file snapshots.json` to `run_watchlist.py`. Do not attempt to
  route around a blocked host.
- Freshness: a ticker whose `pass2_valuation.json` is < 7 days old is
  skipped (`SKIPPED_FRESH`) unless the user said "force".
- The old three-subagent architecture is retired; its Pass 2/Pass 3 content
  remains authoritative in the framework file and is executed inline.
