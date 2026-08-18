# CEC2020, D=5

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
| 50000 | ARRDE | 7 | 2 | 1 | 10 |
| 50000 | BIPOP-CMA | 5 | 3 | 2 | 10 |
| 50000 | LSRTDE | 6 | 3 | 1 | 10 |
| 50000 | NEA2PLUS-PY | 2 | 4 | 4 | 10 |
| 50000 | NLSHADE-RSP | 8 | 1 | 1 | 10 |
| 50000 | j2020 | 5 | 3 | 2 | 10 |
| 50000 | jSO | 7 | 3 | 0 | 10 |
| 1000000 | ARRDE | 9 | 0 | 1 | 10 |
| 1000000 | BIPOP-CMA | 5 | 3 | 2 | 10 |
| 1000000 | LSRTDE | 4 | 3 | 3 | 10 |
| 1000000 | NLSHADE-RSP | 7 | 1 | 2 | 10 |
| 1000000 | j2020 | 8 | 1 | 1 | 10 |
| 1000000 | jSO | 6 | 3 | 1 | 10 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
