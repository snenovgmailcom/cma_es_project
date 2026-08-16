# CEC2020 / D=15 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=10)

| Algorithm | 3M |
|:--|--:|
| ARRDE | 6 / 2 / 2 |
| BIPOP-CMA | 6 / 3 / 1 |
| LSRTDE | 3 / 4 / 3 |
| NLSHADE-RSP | 5 / 4 / 1 |
| j2020 | 4 / 2 / 4 |
| jSO | 3 / 5 / 2 |

## Unimodal and simple multimodal functions (n=4)

| Algorithm | 3M |
|:--|--:|
| ARRDE | 2 / 1 / 1 |
| BIPOP-CMA | 2 / 1 / 1 |
| LSRTDE | 1 / 1 / 2 |
| NLSHADE-RSP | 2 / 1 / 1 |
| j2020 | 2 / 0 / 2 |
| jSO | 1 / 1 / 2 |

## Hybrid functions (n=3)

| Algorithm | 3M |
|:--|--:|
| ARRDE | 3 / 0 / 0 |
| BIPOP-CMA | 3 / 0 / 0 |
| LSRTDE | 2 / 0 / 1 |
| NLSHADE-RSP | 2 / 1 / 0 |
| j2020 | 1 / 1 / 1 |
| jSO | 2 / 1 / 0 |

## Composition functions (n=3)

| Algorithm | 3M |
|:--|--:|
| ARRDE | 1 / 1 / 1 |
| BIPOP-CMA | 1 / 2 / 0 |
| LSRTDE | 0 / 3 / 0 |
| NLSHADE-RSP | 1 / 2 / 0 |
| j2020 | 1 / 1 / 1 |
| jSO | 0 / 3 / 0 |
