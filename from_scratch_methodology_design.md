# From-scratch forecasting design (blank methodology starting point)

This is a clean starting methodology for the 3 flow metrics that drive Closing GBV:

- `Coll_Principal`
- `Coll_Interest`
- `InterestRevenue`

Generated output file:

- `Rate_Methodology_from_scratch_flow_metrics.csv`

Generator script:

- `tools/generate_from_scratch_flow_methodology.py`

## Universe used
I built rules for every segment×cohort that exists in the Oct-25 backtest universe (`14_Backtest_Comparison`, metric `OpeningGBV`), which gives 95 combinations.

Rows generated:

- 95 combinations × 3 metrics × 3 MOB regimes = 855 rows.

## Regime logic used

### A) Default cohorts (most cohorts)
For each metric and cohort:

1. MOB `1-12`: `StaticCohortAvg(3)`
2. MOB `13-36`: `StaticCohortAvg(6)`
3. MOB `37-999`: `StaticCohortAvg(12)`

Reasoning:
- Short lookback in early life keeps recency.
- Medium lookback in mid life reduces noise.
- Long lookback in mature tail stabilizes drift.
- `StaticCohortAvg` only uses actual historical curve points (no recursive forecast compounding).

### B) Very recent cohorts (`202508`, `202509`)
For each metric and cohort:

1. MOB `1-6`: `DonorCohort(202507)` (same-segment donor)
2. MOB `7-24`: `StaticCohortAvg(3)`
3. MOB `25-999`: `StaticCohortAvg(6)`

Reasoning:
- Newest cohorts have limited own history at cutoff, so a short bridge donor avoids unstable sparse averaging.
- Then transition to cohort’s own actual-only behaviour.

## Why this is a good blank-file baseline
- Fully cohort-specific (no broad `ALL` cohorts).
- Same-segment donor policy respected.
- Systematic regime windows, not month patches.
- Uses one consistent approach family (`StaticCohortAvg`) where possible, improving interpretability.

## How to regenerate

```bash
python tools/generate_from_scratch_flow_methodology.py \
  --xlsx 'BB Forecast V5.2.xlsx' \
  --month 2025-10 \
  --out Rate_Methodology_from_scratch_flow_metrics.csv
```
