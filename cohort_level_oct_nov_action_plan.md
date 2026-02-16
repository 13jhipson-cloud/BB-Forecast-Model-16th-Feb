# Cohort-by-cohort action plan (starting with biggest Oct-25 + Nov-25 variances)

Objective: isolate the **largest segment × cohort** principal-collections variances from the original `BB Forecast V5.2.xlsx`, then add **cohort-specific rules** in `Rate_Methodology.csv` so each fix is isolated (instead of broad ALL-cohort approach changes).

## 1) Largest drivers first (Coll_Principal, Oct+Nov combined)

Ranking below is sorted by absolute variance from `14_Backtest_Comparison` (Forecast - Actual). Negative means forecast is too negative (over-collection).

| Rank | Segment | Cohort | Forecast | Actual | Variance | Actual/Forecast |
|---:|---|---:|---:|---:|---:|---:|
| 1 | NON PRIME | 202507 | -1,450,531.67 | -1,211,163.56 | -239,368.11 | 0.8350 |
| 2 | NON PRIME | 202509 | -1,180,602.55 | -948,492.13 | -232,110.42 | 0.8034 |
| 3 | NRP-M | 202101 | -627,771.00 | -399,033.87 | -228,737.13 | 0.6356 |
| 4 | PRIME | 202101 | -672,659.09 | -467,537.60 | -205,121.49 | 0.6951 |
| 5 | NRP-M | 202301 | -943,971.70 | -778,479.95 | -165,491.75 | 0.8247 |
| 6 | NON PRIME | 202506 | -1,155,015.57 | -1,024,455.93 | -130,559.64 | 0.8870 |
| 7 | NON PRIME | 202508 | -1,079,612.99 | -953,136.62 | -126,476.37 | 0.8829 |
| 8 | NRP-S | 202101 | -417,038.82 | -291,056.34 | -125,982.48 | 0.6979 |
| 9 | NRP-M | 202508 | -381,425.24 | -271,545.55 | -109,879.69 | 0.7119 |
| 10 | NON PRIME | 202503 | -803,944.70 | -714,462.87 | -89,481.83 | 0.8887 |

## 2) Why cohort-specific lines should work better here

Current baseline principal rules are mostly broad `ALL` cohort blocks by segment (e.g., NON PRIME `ALL` donor/CohortAvg windows, NRP-M `ALL`, PRIME `ALL`, etc.), so one broad change can improve one cohort but worsen another. Cohort-specific lines have higher specificity and isolate the fix to one cohort only.

## 3) Exact rule lines to add (copy/paste)

Add these rows to `Rate_Methodology.csv` (or your active methodology file). Keep metric = `Coll_Principal`.

> Suggested approach: `ScaledCohortAvg` using `Param1=12` and `Param2=Actual/Forecast ratio` from Oct+Nov.
> 
> Rationale: this gives a direct cohort-level level correction while preserving each cohort’s own curve shape.

```csv
Segment,Cohort,Metric,MOB_Start,MOB_End,Approach,Param1,Param2,Explanation
NON PRIME,202507,Coll_Principal,1,12,ScaledCohortAvg,12,0.8350,Oct-Nov cohort calibration (reduce over-collection)
NON PRIME,202509,Coll_Principal,1,12,ScaledCohortAvg,12,0.8034,Oct-Nov cohort calibration (reduce over-collection)
NRP-M,202101,Coll_Principal,37,999,ScaledCohortAvg,12,0.6356,Oct-Nov cohort calibration (reduce over-collection)
PRIME,202101,Coll_Principal,37,999,ScaledCohortAvg,12,0.6951,Oct-Nov cohort calibration (reduce over-collection)
NRP-M,202301,Coll_Principal,13,36,ScaledCohortAvg,12,0.8247,Oct-Nov cohort calibration (reduce over-collection)
NON PRIME,202506,Coll_Principal,1,12,ScaledCohortAvg,12,0.8870,Oct-Nov cohort calibration (reduce over-collection)
NON PRIME,202508,Coll_Principal,1,12,ScaledCohortAvg,12,0.8829,Oct-Nov cohort calibration (reduce over-collection)
NRP-S,202101,Coll_Principal,37,999,ScaledCohortAvg,12,0.6979,Oct-Nov cohort calibration (reduce over-collection)
NRP-M,202508,Coll_Principal,1,12,ScaledCohortAvg,12,0.7119,Oct-Nov cohort calibration (reduce over-collection)
NON PRIME,202503,Coll_Principal,1,12,ScaledCohortAvg,12,0.8887,Oct-Nov cohort calibration (reduce over-collection)
```

## 4) Apply in this order (largest first)

1. Add only ranks 1-3, rerun, check Oct+Nov principal total variance.
2. Then add ranks 4-6, rerun.
3. Then add ranks 7-10, rerun.

This avoids changing too many cohorts at once and lets you see exactly which cohorts are improving vs worsening.

## 5) Important caution

A few cohorts have **positive** variance (forecast not negative enough), e.g. NON PRIME 202412 and some NRP-M cohorts. Do **not** change those in the same batch; first neutralise the largest negative drivers above, then do a second pass for positive-variance cohorts.
