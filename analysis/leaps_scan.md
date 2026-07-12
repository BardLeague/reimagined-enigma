# LEAPS Opportunity Scan — Watchlist + Extended Corpus

**Generated:** 2026-07-12 · **Corpus:** 30 analyzed names (ranking of 2026-07-12 00:19 UTC)
**Mandate:** long calls, ≥ 12 months DTE at purchase, ≤ $3,500 premium per contract, intended holding period 1–9 months (sell well before expiration).

## Data caveat (read first)

Live option chains could not be fetched in this session: Yahoo Finance and public
chain providers are blocked by the environment's egress policy, per project policy we
do not route around blocked hosts. **No option premium, IV, or delta below is a live
quote.** Everything here is derived from the pipeline's own validated outputs
(`ranking.json`, per-ticker pass2 valuations, pass1 snapshots of 2026-07-09) plus
arithmetic bounds. To complete the scan with real quotes, on a machine with Yahoo
access run:

```
python3 scripts/market_data.py --options ADBE NVDA CRM > chains.json
python3 scripts/leaps_scan.py --chains-file chains.json
```

`leaps_scan.py` applies the full filter set (budget ≤ $3,500, DTE ≥ 365, OI ≥ 25,
spread ≤ 15%, approx delta 0.45–0.90) and ranks by payoff-if-price-converges-to-
expected-intrinsic-value.

## Underlying selection (from the validated pipeline)

Of 30 names analyzed, only three carry buy-side verdicts. LEAPS concentrate equity
risk with leverage and expiry risk, so anything the pipeline rates hold/avoid is
excluded from long-call consideration by construction.

| Ticker | Price (07-09) | Expected IV | Margin of safety | Verdict | LEAPS suitability |
|--------|--------------|-------------|------------------|---------|-------------------|
| ADBE | $221.54 | $333.20 | **+33.5%** | strong_buy | **Primary candidate** |
| NVDA | $192.53 | $225.50 | +14.6% | buy | Marginal (thin convexity) |
| CRM | $165.84 | $194.00 | +14.5% | buy | Marginal (thin convexity) |
| CEG | $244.03 | $238.30 | −2.4% | hold | Watch only — near fair value, no edge to lever |

Everything else in the corpus (including the two newly completed names, MNST at
−27.6% MoS and ELF at −39.2% MoS, both **avoid**) fails the first gate: never buy
calls on a stock the framework says is above intrinsic value.

## Budget arithmetic ($3,500 = $35.00/share of premium)

A call's premium is never less than its intrinsic value, so the budget puts a hard
floor on how deep in-the-money you can buy — before adding any time value:

| Ticker | Spot | Deepest ITM strike affordable on intrinsic alone (S − $35) | Practical implication |
|--------|------|------------------------------------------------------------|----------------------|
| ADBE | $221.54 | ≥ $186.54 (0.84× spot) | With ~1.5yr of time value on top, the affordable region realistically starts near/above the money — confirm on the live chain |
| NVDA | $192.53 | ≥ $157.53 (0.82× spot) | Same: affordable strikes cluster around ATM and above |
| CRM | $165.84 | ≥ $130.84 (0.79× spot) | Lowest spot of the three — most room for an ITM strike within budget |

## Convergence scenario per contract (pipeline expected IV reached by expiration)

Payoff = (expected IV − strike) × 100, **if** the stock converges to the pipeline's
probability-weighted intrinsic value. This is the pipeline's own scenario, not a
forecast; a contract qualifies only if its live premium is ≤ $3,500.

**ADBE (expected IV $333.20):**

| Strike | Moneyness | Payoff if converged | Payoff ÷ max budget |
|--------|-----------|--------------------:|--------------------:|
| $220 | ATM | $11,320 | ≥ 3.2× |
| $240 | +8% OTM | $9,320 | ≥ 2.7× |
| $260 | +17% OTM | $7,320 | ≥ 2.1× |
| $280 | +26% OTM | $5,320 | ≥ 1.5× |

**NVDA (expected IV $225.50):**

| Strike | Moneyness | Payoff if converged | Payoff ÷ max budget |
|--------|-----------|--------------------:|--------------------:|
| $190 | ATM | $3,550 | ≥ 1.0× |
| $200 | +4% OTM | $2,550 | ≥ 0.7× |
| $210 | +9% OTM | $1,550 | ≥ 0.4× |

**CRM (expected IV $194.00):**

| Strike | Moneyness | Payoff if converged | Payoff ÷ max budget |
|--------|-----------|--------------------:|--------------------:|
| $165 | ATM | $2,900 | ≥ 0.8× |
| $170 | +3% OTM | $2,400 | ≥ 0.7× |
| $180 | +9% OTM | $1,400 | ≥ 0.4× |

Reading: at full convergence ADBE clears the cost hurdle at every affordable strike
with room to spare; NVDA and CRM barely return the premium even in the convergence
scenario, because their 14–15% margins of safety are thin once filtered through an
option's time-value drag. **The LEAPS case in this corpus is effectively an ADBE
case.**

## Fit to the stated holding plan (buy ≥ 1yr DTE, hold 1–9 months)

- A 1–9 month hold monetizes *partial* convergence plus delta, not the full
  convergence table above — favor **higher-delta (0.55–0.75), nearer-the-money
  strikes** over cheap far-OTM lottery strikes, and prioritize tight spreads
  (the exit is a sale, not an exercise).
- Catalysts inside the holding window (from validated research files):
  - **ADBE Q3 FY2026 earnings (~Sept 2026)** — guidance $6.67–6.72B; a third
    consecutive beat-and-raise directly attacks the AI-disruption discount. This is
    the single best-aligned catalyst in the corpus for a 1–9 month LEAPS hold.
  - ADBE Firefly/AI-ARR disclosures and ~10%/yr share-retirement buyback at a 13%
    FCF yield (continuous support).
  - ADBE CEO transition resolution (timing uncertain; cuts both ways).
- Key risk to the trade (from ADBE pass2): the AI-disruption narrative worsening —
  the stock is cheap *because* of it, and a 1–9 month window may be too short for
  the narrative to crack even if fundamentals hold. Thesis breakers are listed in
  `analysis/ADBE/pass3_memo.md`.

## Live-market anchors (sourced) and model estimates

Chain tables remain unfetchable from this environment (providers return 403 via the
egress proxy), but scoped research recovered these dated anchors:

- **ADBE**: spot **$223.64** with near-term (Jul 17, 2026) implied volatility
  **43.0%** and IV rank 54% — optionsamurai.com data surfaced 2026-07-10.
- **NVDA**: 30-day IV **38.1%**, IV rank 30% (52-wk IV range 31.1%–54.2%) —
  projectoption.com, as of 2026-05-26 (stale ~6 weeks; treat as approximate).
- **CRM**: no reliable IV figure could be sourced (the one datum found was a
  single-expiration outlier); no model estimate is offered for CRM.
- Sentiment color, July 2026: Michael Burry disclosed adding to a long Adobe
  position (Yahoo Finance/Benzinga coverage of his long-dated call purchases), and
  The Motley Fool's options service lists **long ADBE January 2028 $330 calls** as a
  recommendation — external confirmation that Jan-2028 ADBE LEAPS are a trafficked
  expression of this thesis.

**Black-Scholes estimates (NOT quotes)** — computed from the sourced spot/IV above,
r = 4%, ~558 DTE (Jan 21, 2028); long-dated IV typically sits below an elevated
near-term IV, so the two columns bracket the plausible premium:

**ADBE (spot $223.64):**

| Strike | Est. premium @ 35% IV | Est. premium @ 43% IV | Est. delta | Fits $3,500? |
|--------|----------------------:|----------------------:|-----------:|--------------|
| $230 | ~$4,140 | ~$4,990 | 0.62–0.63 | No |
| $250 | ~$3,380 | ~$4,250 | 0.54–0.57 | Borderline |
| $260 | ~$3,050 | ~$3,930 | 0.50–0.54 | Borderline |
| $280 | ~$2,470 | ~$3,350 | 0.44–0.48 | **Yes** |
| $330 | ~$1,460 | ~$2,260 | 0.29–0.36 | Yes (below delta band) |

**NVDA (spot $192.53, snapshot 2026-07-09):**

| Strike | Est. premium @ 33% IV | Est. premium @ 38% IV | Est. delta | Payoff if → $225.50 |
|--------|----------------------:|----------------------:|-----------:|--------------------:|
| $200 | ~$3,300 | ~$3,760 | 0.60–0.61 | $2,550 |
| $210 | ~$2,910 | ~$3,380 | 0.56–0.57 | $1,550 |
| $220 | ~$2,560 | ~$3,030 | 0.51–0.53 | $1,050 |

NVDA reading: every strike that fits the budget pays back **less than its estimated
cost** even if the stock fully converges to the pipeline's expected intrinsic value —
the 14.6% margin of safety cannot carry a LEAPS premium. The buy verdict is an
equity verdict, not an options verdict.

ADBE reading: the budget/delta/convexity intersection sits at **K ≈ $260–$280,
Jan-2028**: estimated cost $2,500–$3,900 (confirm ≤ $3,500 on the live chain),
delta ~0.44–0.54, and payoff-if-converged of $5,320–$7,320 (≈ 1.5–2.9× the budget
cap). The published $330-strike recommendation fits the budget easily but sits
below the 0.45 delta floor — it is a higher-variance expression of the same thesis.

## Recommended next action

1. Pre-fetch chains where Yahoo is reachable (`market_data.py --options ADBE NVDA CRM`).
2. Run `leaps_scan.py --chains-file chains.json` — it will produce the ranked,
   liquidity-filtered contract list under `analysis/leaps_scan.json`.
3. Expected outcome given the arithmetic above: ADBE Jan-2028 (or later) calls in
   roughly the $230–$280 strike region are where budget, delta band, and convexity
   most plausibly intersect — validate premium ≤ $3,500, OI ≥ 25, spread ≤ 15%
   before any purchase.

*Not investment advice; this is the pipeline's framework applied to the user's
LEAPS mandate. All figures trace to validated pipeline files except where labeled
as arithmetic bounds or Black-Scholes estimates from the sourced anchors above.*

## Sources (live-market anchors section)

- ADBE spot/IV: optionsamurai.com ADBE option chain (data of 2026-07-10)
- NVDA IV30/rank: projectoption.com NVDA implied volatility (as of 2026-05-26)
- Burry Adobe position: finance.yahoo.com "Michael Burry Buys Long-Dated Microsoft
  Calls, Adds To JD And Adobe" / benzinga.com Burry LEAP coverage (July 2026)
- ADBE Jan-2028 $330 call recommendation: The Motley Fool options disclosure line
  (surfaced July 2026)
