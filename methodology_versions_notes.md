# Rate Methodology test versions (prepared)

I prepared two candidate methodology files from the v5.2 workbook baseline and aligned to your latest constraints:

- **Same-segment donors only**.
- Keep principal-collection focus first.
- Avoid one-off monthly patches.

## Files
- `Rate_Methodology_from_v52.csv` (baseline extracted from `BB Forecast V5.2.xlsx`)
- `Rate_Methodology_v6A.csv` (conservative targeted overrides)
- `Rate_Methodology_v6B.csv` (stronger de-bias version)

## Key differences

### v6A (conservative)
- NON PRIME cohorts `202507/202508/202509`: `Coll_Principal`, MOB `1-12` → `DonorCohort(202503)`.
- NRP-M cohorts `202101/202301`: `Coll_Principal`, MOB `13-36` → `CohortAvg(12)`.
- PRIME cohort `202101`: `Coll_Principal`, MOB `13-36` → `CohortAvg(12)`.
- NRP-S cohorts `202101/202301`: `Coll_Principal`, MOB `13-36` → `CohortAvg(12)` and MOB `37+` → `SegMedian`.

### v6B (stronger)
- NON PRIME cohorts `202503..202509`: `Coll_Principal`, MOB `1-12` → `DonorCohort(202503)`.
- NON PRIME cohorts `202503..202509`: `Coll_Principal`, MOB `13-24` → `CohortAvg(12)`.
- NRP-M cohorts `202101/202301`: `Coll_Principal`, MOB `13-36` → `CohortAvg(12)`, MOB `37+` → `SegMedian`.
- PRIME `ALL`: `Coll_Principal`, MOB `13-36` → `CohortAvg(12)` (replaces trend behaviour for this window).
- NRP-S cohorts `202101/202301`: `Coll_Principal`, MOB `13-36` → `CohortAvg(12)`, MOB `37+` → `SegMedian`.

## Run commands (when pandas/numpy/dateutil are available)

```bash
python backbook_forecast.py -f Fact_Raw_New_NewData.xlsx -m Rate_Methodology_v6A.csv -c 2025-10 -t --ex-contra -o outputs_v6A
python backbook_forecast.py -f Fact_Raw_New_NewData.xlsx -m Rate_Methodology_v6B.csv -c 2025-10 -t --ex-contra -o outputs_v6B
```

Then compare `14_Backtest_Comparison` for `Coll_Principal` by month/segment/cohort (Oct-25..Jan-26) and pick the version with lower absolute variance and better curve continuity.

## Environment limitation encountered
This container currently cannot install required python dependencies (`pandas`, `numpy`, `python-dateutil`) due network/proxy 403 restrictions, so I could not execute the forecast engine inside this environment.
