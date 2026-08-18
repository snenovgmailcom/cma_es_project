# CEC2017, D=10

## Mann–Whitney U tests on terminal errors

Independent, two-sided Mann–Whitney U tests compare each competitor
with MSC-CMA-ES on every function. Each sample contains 51 unmodified
run-wise terminal errors. Bonferroni adjustment is applied over all
functions separately for each budget and competitor.

The U statistic in [`details.csv`](details.csv) is for the competitor
sample. For minimization, `probability_competitor_lower` is
$P(X_{competitor}<X_{MSC})+\frac12P(X_{competitor}=X_{MSC})$.

| Budget | Competitor | Competitor better | MSC-CMA-ES better | Not significant | Functions |
|---:|---|---:|---:|---:|---:|
| 100000 | ARRDE | 16 | 7 | 6 | 29 |
| 100000 | BIPOP-CMA | 10 | 6 | 13 | 29 |
| 100000 | LSRTDE | 18 | 8 | 3 | 29 |
| 100000 | NEA2PLUS-PY | 2 | 21 | 6 | 29 |
| 100000 | NLSHADE-RSP | 14 | 9 | 6 | 29 |
| 100000 | j2020 | 9 | 11 | 9 | 29 |
| 100000 | jSO | 18 | 8 | 3 | 29 |
| 1000000 | ARRDE | 21 | 3 | 5 | 29 |
| 1000000 | BIPOP-CMA | 13 | 7 | 9 | 29 |
| 1000000 | LSRTDE | 12 | 11 | 6 | 29 |
| 1000000 | NLSHADE-RSP | 17 | 5 | 7 | 29 |
| 1000000 | j2020 | 14 | 8 | 7 | 29 |
| 1000000 | jSO | 14 | 12 | 3 | 29 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
