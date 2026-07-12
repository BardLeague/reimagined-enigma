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
as arithmetic bounds.*
