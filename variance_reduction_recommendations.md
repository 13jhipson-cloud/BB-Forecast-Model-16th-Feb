# Variance Reduction Recommendations (Principal Collections)

## Context reviewed
- Objective is to reduce forecast vs actual variance (ex-contra basis) via **regime-based methodology rules only** (no single-month patches).  
- Current methodology guidance already favors: early MOB donor continuity, mid MOB stabilizers, and late MOB tail caps (CohortAvg/SegMedian).  
- Backtest focus window is Oct-25 to Jan-26.

## What the latest output shows (BB Forecast V5.2.xlsx)
Using sheet `14_Backtest_Comparison` and metric `Coll_Principal` only, the segment-level variance (Forecast - Actual) for Oct-25 to Jan-26 is:

| Month | NON PRIME | NRP-S | NRP-M | NRP-L | PRIME |
|---|---:|---:|---:|---:|---:|
| 2025-10 | -142,471 | -74,364 | -70,639 | 15,378 | -72,591 |
| 2025-11 | -749,657 | -284,368 | -249,255 | 25,538 | -119,222 |
| 2025-12 | -564,015 | -165,454 | -120,671 | -42,346 | -85,575 |
| 2026-01 | -872,105 | -304,837 | -52,879 | -4,521 | -67,845 |

Interpretation: variance is broadly negative in key segments, consistent with **systematic over-collection** in forecast principal collections.

Top cohort drivers (aggregate variance across Oct-25 to Jan-26):

1. NRP-M 202101: -480,671  
2. NON PRIME 202509: -375,514  
3. PRIME 202101: -353,500  
4. NON PRIME 202507: -320,908  
5. NON PRIME 202503: -251,054  
6. NRP-M 202301: -233,211  
7. NON PRIME 202508: -224,307  
8. NRP-S 202101: -221,812

## Suggested minimum set of regime-based methodology changes

1. **NON PRIME recent vintages (202503, 202504, 202505, 202506, 202507, 202508, 202509), Coll_Principal, MOB 0-12:** shift to a milder donor family anchored to 202503/202504 behavior (or ScaledDonor where feasible) to reduce early-ramp over-collection while preserving shape continuity.
2. **NON PRIME ALL, Coll_Principal, MOB 13-24:** replace any trend-like or aggressive donor logic with `CohortAvg(12)` to damp persistent mid-life negative bias.
3. **NRP-M stressed cohorts (202101, 202301), Coll_Principal, MOB 13-36:** use `CohortAvg(12)` (or SegMedian fallback) to suppress systematic over-collection while keeping regime consistency.
4. **PRIME 202101 (and similar old-vintage cluster), Coll_Principal, MOB 13-36:** shift to donor from a closer-performing PRIME cohort or `CohortAvg(12)` to remove sustained negative variance.
5. **NRP-S 202101 / 202301 cluster, Coll_Principal, MOB 13-36 plus 37+:** mid-window stabilize with `CohortAvg(12)` and set tail cap via `SegMedian` or `CohortAvg(12)` for MOB 37+ to prevent long-run drift.

## Practical validation loop (after edits)
1. Re-run with cutoff `2025-10` and `--ex-contra`.
2. Re-check monthly totals for Coll_Principal variance (Oct-25 to Jan-26), targeting reduction in absolute variance with no month-specific overrides.
3. Inspect cohort curves for continuity at regime boundaries (0/12/13/24/37).
4. Reject rules that improve one month but worsen Nov-Jan aggregate.
5. Freeze principal set, then move to provisions decomposition (CR effect vs ex-contra GBV effect).
