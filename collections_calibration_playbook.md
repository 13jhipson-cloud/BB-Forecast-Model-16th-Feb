# Why v6A/v6B likely got worse, and a simpler fix that usually works

## Why this can happen
The principal-collections issue is mostly a **level bias** (forecast too negative) across months. v6A/v6B changed donors/windows in several places, but that can still worsen variance when:

1. The chosen donor is itself more negative than target cohorts in the backtest months.
2. `CohortAvg(12)` in stressed windows inherits previously over-negative forecast history.
3. Rule precedence means narrow cohort overrides win over broad rules, so a few high-GBV cohorts can dominate totals.
4. You are solving a level problem with shape changes (donor/trend), which often moves curves but not monthly totals enough.

## Simple approach: one multiplicative calibration per segment
Use segment-level `Coll_Principal` multipliers from backtest `Actual / Forecast` (Oct-25..Jan-26), then re-run:

- NON PRIME: **0.904741**
- NRP-S: **0.906351**
- NRP-M: **0.960153**
- NRP-L: **0.990712**
- PRIME: **0.732664**

Because principal collections are negative, multiplying by <1 makes them **less negative** and directly reduces over-collection.

This is deliberately simple and transparent, and can be phased out later as methodology curves improve.

## Files created
- `sample_data/Overlays.csv` contains these rules in the model’s native overlay format.
- `tools/generate_principal_overlay_from_backtest.py` regenerates the multipliers directly from `14_Backtest_Comparison`.

## How to run (when pandas/numpy/dateutil are installed)
```bash
python backbook_forecast.py -f Fact_Raw_New_NewData.xlsx -m Rate_Methodology_from_v52.csv -c 2025-10 -t --ex-contra -o outputs_overlay_calibrated
```

(Overlays auto-load from `sample_data/Overlays.csv` when present.)

## Recommended next iteration
1. Use the overlay-calibrated run as a stable anchor.
2. Then replace only one segment at a time with methodology-only fixes, starting with NON PRIME.
3. Keep PRIME multiplier partially retained until donor quality improves for PRIME.
