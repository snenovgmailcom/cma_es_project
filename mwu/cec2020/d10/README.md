# CEC2020, D=10

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
| 1000000 | ARRDE | 6 | 3 | 1 | 10 |
| 1000000 | BIPOP-CMA | 5 | 4 | 1 | 10 |
| 1000000 | LSRTDE | 4 | 4 | 2 | 10 |
| 1000000 | NEA2PLUS-PY | 1 | 6 | 3 | 10 |
| 1000000 | NLSHADE-RSP | 4 | 2 | 4 | 10 |
| 1000000 | j2020 | 4 | 3 | 3 | 10 |
| 1000000 | jSO | 4 | 5 | 1 | 10 |
| 20000000 | ARRDE | 6 | 1 | 3 | 10 |
| 20000000 | BIPOP-CMA | 3 | 4 | 3 | 10 |
| 20000000 | LSRTDE | 2 | 6 | 2 | 10 |
| 20000000 | NLSHADE-RSP | 5 | 2 | 3 | 10 |
| 20000000 | j2020 | 7 | 2 | 1 | 10 |
| 20000000 | jSO | 4 | 5 | 1 | 10 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
