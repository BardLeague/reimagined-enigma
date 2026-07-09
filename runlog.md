# Run Log

Append-only. One line per pass attempt. Never edit or delete prior entries.

Format: `| ticker | pass | timestamp (UTC ISO 8601) | status | reliability score | notes |`

Status values: `STARTED`, `VALIDATED`, `RETRY`, `FAILED`, `SKIPPED_FRESH`, `SKIPPED_LOW_RELIABILITY`, `SKIPPED_LOW_SIGNAL`.

| Ticker | Pass | Timestamp | Status | Reliability | Notes |
|--------|------|-----------|--------|-------------|-------|
| NVDA | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| MU | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| AVGO | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| ASML | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| AMAT | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| LRCX | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| KLAC | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| PLTR | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| SOUN | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| AAOI | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| RKLB | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| ASTS | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| COHR | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| LITE | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| PENG | pass1 | 2026-07-06T18:13:46Z | STARTED | - | full watchlist run |
| NVDA | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| MU | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| AVGO | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| ASML | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| AMAT | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| LRCX | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| KLAC | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| PLTR | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| SOUN | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| AAOI | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| RKLB | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| ASTS | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| COHR | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| LITE | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| PENG | pass1 | 2026-07-07T17:01:31Z | FAILED | - | 2026-07-06 parallel run terminated by session limit; no outputs persisted |
| PLTR | pass1 | 2026-07-07T17:32:12Z | VALIDATED | 8 | signal_score=5; queued for claude |
| RKLB | pass1 | 2026-07-07T17:32:12Z | VALIDATED | 8 | signal_score=5; queued for claude |
| ASTS | pass1 | 2026-07-07T17:32:12Z | VALIDATED | 8 | signal_score=5; queued for claude |
| PLTR | claude_pass1 | 2026-07-07T17:33:07Z | VALIDATED | 8 | research pass complete |
| PLTR | pass2 | 2026-07-07T17:34:07Z | VALIDATED | 8 | expected IV 117.7 vs price 133.36; hold |
| PLTR | pass3 | 2026-07-07T17:34:33Z | VALIDATED | 8 | memo written; verdict hold |
| RKLB | claude_pass1 | 2026-07-07T17:36:18Z | VALIDATED | 8 | research pass complete |
| RKLB | pass2 | 2026-07-07T17:36:18Z | VALIDATED | 8 | expected IV 18.3 vs price 87.38; avoid |
| RKLB | pass3 | 2026-07-07T17:36:18Z | VALIDATED | 8 | memo written; verdict avoid |
| ASTS | claude_pass1 | 2026-07-07T17:38:08Z | VALIDATED | 8 | research pass complete |
| ASTS | pass2 | 2026-07-07T17:38:08Z | VALIDATED | 8 | expected IV 42.0 vs price 85.13; avoid |
| ASTS | pass3 | 2026-07-07T17:38:08Z | VALIDATED | 8 | memo written; verdict avoid |
| COHR | pass1 | 2026-07-07T17:43:04Z | VALIDATED | 8 | signal_score=3; queued for claude |
| LITE | pass1 | 2026-07-07T17:43:04Z | VALIDATED | 8 | signal_score=3; queued for claude |
| AAOI | pass1 | 2026-07-07T17:43:04Z | VALIDATED | 8 | signal_score=2; queued for claude |
| COHR | claude_pass1 | 2026-07-07T17:45:06Z | VALIDATED | 8 | research pass complete |
| COHR | pass2 | 2026-07-07T17:45:06Z | VALIDATED | 8 | expected IV 189.0 vs price 327.59; avoid |
| COHR | pass3 | 2026-07-07T17:45:06Z | VALIDATED | 8 | memo written; verdict avoid |
| LITE | claude_pass1 | 2026-07-07T17:46:59Z | VALIDATED | 8 | research pass complete |
| LITE | pass2 | 2026-07-07T17:46:59Z | VALIDATED | 8 | expected IV 427.5 vs price 728.32; avoid |
| LITE | pass3 | 2026-07-07T17:46:59Z | VALIDATED | 8 | memo written; verdict avoid |
| AAOI | claude_pass1 | 2026-07-07T17:48:50Z | VALIDATED | 8 | research pass complete |
| AAOI | pass2 | 2026-07-07T17:48:50Z | VALIDATED | 8 | expected IV 30.1 vs price 121.26; avoid |
| AAOI | pass3 | 2026-07-07T17:48:50Z | VALIDATED | 8 | memo written; verdict avoid |
| NVDA | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| MU | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| AVGO | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| ASML | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| AMAT | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| LRCX | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| KLAC | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=3; queued for claude |
| SOUN | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=2; queued for claude |
| PENG | pass1 | 2026-07-07T17:49:03Z | VALIDATED | 8 | signal_score=2; queued for claude |
| NVDA | claude_pass1 | 2026-07-07T17:51:01Z | VALIDATED | 8 | research pass complete |
| NVDA | pass2 | 2026-07-07T17:51:01Z | VALIDATED | 8 | expected IV 225.5 vs price 192.53; buy |
| NVDA | pass3 | 2026-07-07T17:51:01Z | VALIDATED | 8 | memo written; verdict buy |
| MU | claude_pass1 | 2026-07-08T22:18:23Z | VALIDATED | 8 | research pass complete; pass2/pass3 pending |
| MU | pass2 | 2026-07-08T22:19:38Z | VALIDATED | 8 | expected IV 494.5 vs price 912.77; avoid (value_trap High) |
| MU | pass3 | 2026-07-08T22:19:38Z | VALIDATED | 8 | memo written; verdict avoid |
| AVGO | claude_pass1 | 2026-07-08T22:21:24Z | VALIDATED | 8 | research pass complete |
| AVGO | pass2 | 2026-07-08T22:21:24Z | VALIDATED | 8 | expected IV 334.8 vs price 373.90; hold |
| AVGO | pass3 | 2026-07-08T22:21:24Z | VALIDATED | 8 | memo written; verdict hold |
| ASML | claude_pass1 | 2026-07-08T22:23:13Z | VALIDATED | 8 | research pass complete |
| ASML | pass2 | 2026-07-08T22:23:13Z | VALIDATED | 8 | expected IV 1172.5 vs price 1855.35; avoid |
| ASML | pass3 | 2026-07-08T22:23:13Z | VALIDATED | 8 | memo written; verdict avoid |
| AMAT | claude_pass1 | 2026-07-08T22:25:01Z | VALIDATED | 8 | research pass complete |
| AMAT | pass2 | 2026-07-08T22:25:01Z | VALIDATED | 8 | expected IV 252.3 vs price 622.59; avoid |
| AMAT | pass3 | 2026-07-08T22:25:01Z | VALIDATED | 8 | memo written; verdict avoid |
| LRCX | claude_pass1 | 2026-07-08T22:26:47Z | VALIDATED | 8 | research pass complete |
| LRCX | pass2 | 2026-07-08T22:26:47Z | VALIDATED | 8 | expected IV 139.8 vs price 349.64; avoid |
| LRCX | pass3 | 2026-07-08T22:26:47Z | VALIDATED | 8 | memo written; verdict avoid |
| KLAC | claude_pass1 | 2026-07-08T22:28:47Z | VALIDATED | 7 | research pass complete; quote data inconsistent |
| KLAC | pass2 | 2026-07-08T22:28:47Z | VALIDATED | 7 | expected IV 90.3 vs price 235.55; avoid |
| KLAC | pass3 | 2026-07-08T22:28:47Z | VALIDATED | 7 | memo written; verdict avoid |
| SOUN | claude_pass1 | 2026-07-08T22:30:33Z | VALIDATED | 8 | research pass complete |
| SOUN | pass2 | 2026-07-08T22:30:33Z | VALIDATED | 8 | expected IV 3.45 vs price 6.96; avoid |
| SOUN | pass3 | 2026-07-08T22:30:33Z | VALIDATED | 8 | memo written; verdict avoid |
| PENG | claude_pass1 | 2026-07-08T22:32:17Z | VALIDATED | 8 | research pass complete |
| PENG | pass2 | 2026-07-08T22:32:17Z | VALIDATED | 8 | expected IV 55.2 vs price 67.71; hold |
| PENG | pass3 | 2026-07-08T22:32:17Z | VALIDATED | 8 | memo written; verdict hold |
| AMZN | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=5; queued for claude |
| MSFT | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=2; queued for claude |
| USAR | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=2; queued for claude |
| TSM | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=3; queued for claude |
| MRVL | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=3; queued for claude |
| PEP | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=2; queued for claude |
| GS | pass1 | 2026-07-09T05:10:56Z | VALIDATED | 8 | signal_score=3; queued for claude |
| AMZN | claude_pass1 | 2026-07-09T05:12:40Z | VALIDATED | 8 | research pass complete |
| AMZN | pass2 | 2026-07-09T05:12:40Z | VALIDATED | 8 | expected IV 213.0 vs price 250.56; hold |
| AMZN | pass3 | 2026-07-09T05:12:40Z | VALIDATED | 8 | memo written; verdict hold |
| MSFT | claude_pass1 | 2026-07-09T05:14:35Z | VALIDATED | 8 | research pass complete |
| MSFT | pass2 | 2026-07-09T05:14:35Z | VALIDATED | 8 | expected IV 325.3 vs price 388.84; hold |
| MSFT | pass3 | 2026-07-09T05:14:35Z | VALIDATED | 8 | memo written; verdict hold |
| USAR | claude_pass1 | 2026-07-09T05:16:23Z | VALIDATED | 8 | research pass complete |
| USAR | pass2 | 2026-07-09T05:16:23Z | VALIDATED | 8 | expected IV 9.6 vs price 18.59; avoid |
| USAR | pass3 | 2026-07-09T05:16:23Z | VALIDATED | 8 | memo written; verdict avoid |
| TSM | claude_pass1 | 2026-07-09T05:18:18Z | VALIDATED | 8 | research pass complete |
| TSM | pass2 | 2026-07-09T05:18:18Z | VALIDATED | 8 | expected IV 263.3 vs price 436.59; avoid |
| TSM | pass3 | 2026-07-09T05:18:18Z | VALIDATED | 8 | memo written; verdict avoid |
