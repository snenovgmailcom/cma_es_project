# CEC2022, D=20

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
| 1000000 | ARRDE | 7 | 2 | 3 | 12 |
| 1000000 | BIPOP-CMA | 4 | 5 | 3 | 12 |
| 1000000 | LSRTDE | 5 | 3 | 4 | 12 |
| 1000000 | NLSHADE-RSP | 3 | 5 | 4 | 12 |
| 1000000 | j2020 | 2 | 7 | 3 | 12 |
| 1000000 | jSO | 6 | 4 | 2 | 12 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
