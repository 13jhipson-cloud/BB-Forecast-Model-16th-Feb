# Approach options to close cohort-level principal variance (without Manual locks)

You are right: if actuals are known for Oct/Nov, the ideal calibration target is known. But if you want to avoid `Manual` month locks, use an approach that can still be systematic and less fragile.

## Why existing approaches can miss
- `ScaledCohortAvg` scales a rolling average that can include forecasted prior months, so the level can drift and overshoot/undershoot one month even when total ratio looked right.
- Broad `ALL` rules mix cohort behaviors; fixing one cohort can worsen another.

## New approach added: `StaticCohortAvg`
- This new approach computes the cohort average using **historical actual curve points only**.
- It excludes forecast-generated rows (`__is_forecast=True`) in rolling lookup.
- So it avoids recursive compounding from previously forecasted values.

### When to use
- Best for cohorts where level is biased but shape is broadly right.
- Especially useful for mature cohorts where trend approaches are too aggressive.

## Suggested first batch (top 5 cohorts)
Use `Rate_Methodology_patch_top5_static_cohortavg.csv` and apply these cohort-specific lines first:
- NON PRIME 202507 (MOB 1-12, StaticCohortAvg(2))
- NON PRIME 202509 (MOB 1-12, StaticCohortAvg(2))
- NRP-M 202101 (MOB 37+, StaticCohortAvg(3))
- PRIME 202101 (MOB 37+, StaticCohortAvg(3))
- NRP-M 202301 (MOB 13-36, StaticCohortAvg(3))

## Workflow to ensure we are actually closing variance
1. Apply only 1 cohort override at a time (largest variance first).
2. Run backtest, check Oct and Nov for that cohort.
3. Keep only if both months improve or net abs variance improves materially.
4. Move to next cohort.

This keeps changes auditable and prevents broad regressions.
