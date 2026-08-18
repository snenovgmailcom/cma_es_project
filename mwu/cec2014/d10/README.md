# CEC2014, D=10

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
| 100000 | ARRDE | 22 | 5 | 3 | 30 |
| 100000 | BIPOP-CMA | 12 | 10 | 8 | 30 |
| 100000 | LSRTDE | 19 | 4 | 7 | 30 |
| 100000 | NLSHADE-RSP | 14 | 9 | 7 | 30 |
| 100000 | j2020 | 11 | 13 | 6 | 30 |
| 100000 | jSO | 21 | 4 | 5 | 30 |
| 1000000 | ARRDE | 20 | 2 | 8 | 30 |
| 1000000 | BIPOP-CMA | 12 | 11 | 7 | 30 |
| 1000000 | LSRTDE | 12 | 8 | 10 | 30 |
| 1000000 | NLSHADE-RSP | 14 | 4 | 12 | 30 |
| 1000000 | j2020 | 13 | 7 | 10 | 30 |
| 1000000 | jSO | 16 | 6 | 8 | 30 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
