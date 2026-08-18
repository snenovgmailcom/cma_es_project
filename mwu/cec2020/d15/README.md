# CEC2020, D=15

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
| 3000000 | ARRDE | 6 | 2 | 2 | 10 |
| 3000000 | BIPOP-CMA | 6 | 3 | 1 | 10 |
| 3000000 | LSRTDE | 3 | 4 | 3 | 10 |
| 3000000 | NEA2PLUS-PY | 2 | 8 | 0 | 10 |
| 3000000 | NLSHADE-RSP | 5 | 3 | 2 | 10 |
| 3000000 | j2020 | 5 | 2 | 3 | 10 |
| 3000000 | jSO | 3 | 5 | 2 | 10 |

Complete per-function U statistics, raw p-values, Bonferroni-adjusted
p-values, effect directions, and sample medians are available in
[`details.csv`](details.csv).
