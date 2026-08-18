# CEC2017, D=30

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
| 300000 | ARRDE | 16 | 8 | 5 | 29 |
| 300000 | BIPOP-CMA | 14 | 9 | 6 | 29 |
| 300000 | LSRTDE | 25 | 2 | 2 | 29 |
| 300000 | NLSHADE-RSP | 7 | 16 | 6 | 29 |
| 300000 | j2020 | 8 | 19 | 2 | 29 |
| 300000 | jSO | 20 | 8 | 1 | 29 |
| 1000000 | ARRDE | 17 | 6 | 6 | 29 |
| 1000000 | BIPOP-CMA | 11 | 10 | 8 | 29 |
| 1000000 | LSRTDE | 23 | 3 | 3 | 29 |
| 1000000 | NLSHADE-RSP | 7 | 16 | 6 | 29 |
| 1000000 | j2020 | 4 | 23 | 2 | 29 |
| 1000000 | jSO | 17 | 8 | 4 | 29 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
