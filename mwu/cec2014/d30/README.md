# CEC2014, D=30

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
| 300000 | ARRDE | 22 | 6 | 2 | 30 |
| 300000 | BIPOP-CMA | 18 | 6 | 6 | 30 |
| 300000 | LSRTDE | 23 | 3 | 4 | 30 |
| 300000 | NLSHADE-RSP | 10 | 15 | 5 | 30 |
| 300000 | j2020 | 7 | 19 | 4 | 30 |
| 300000 | jSO | 22 | 5 | 3 | 30 |
| 1000000 | ARRDE | 22 | 5 | 3 | 30 |
| 1000000 | BIPOP-CMA | 17 | 7 | 6 | 30 |
| 1000000 | LSRTDE | 23 | 4 | 3 | 30 |
| 1000000 | NLSHADE-RSP | 10 | 17 | 3 | 30 |
| 1000000 | j2020 | 6 | 19 | 5 | 30 |
| 1000000 | jSO | 21 | 5 | 4 | 30 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
