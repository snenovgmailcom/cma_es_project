# CEC2022 / D=10 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=12)

| Algorithm | 200K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 6 / 1 / 5 | 6 / 1 / 5 | 7 / 1 / 4 |
| BIPOP-CMA | 2 / 2 / 8 | 2 / 3 / 7 | 3 / 4 / 5 |
| LSRTDE | 4 / 3 / 5 | 4 / 5 / 3 | 4 / 5 / 3 |
| NLSHADE-RSP | 6 / 2 / 4 | 6 / 2 / 4 | 7 / 2 / 3 |
| j2020 | 7 / 3 / 2 | 7 / 1 / 4 | 7 / 1 / 4 |
| jSO | 5 / 3 / 4 | 5 / 4 / 3 | 5 / 4 / 3 |

## Unimodal and simple multimodal functions (n=5)

| Algorithm | 200K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 2 / 1 / 2 | 2 / 1 / 2 | 2 / 1 / 2 |
| BIPOP-CMA | 2 / 1 / 2 | 2 / 1 / 2 | 2 / 1 / 2 |
| LSRTDE | 2 / 1 / 2 | 2 / 2 / 1 | 2 / 2 / 1 |
| NLSHADE-RSP | 2 / 1 / 2 | 2 / 1 / 2 | 2 / 1 / 2 |
| j2020 | 2 / 2 / 1 | 2 / 1 / 2 | 2 / 1 / 2 |
| jSO | 2 / 1 / 2 | 2 / 1 / 2 | 2 / 1 / 2 |

## Hybrid functions (n=3)

| Algorithm | 200K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| BIPOP-CMA | 0 / 0 / 3 | 0 / 0 / 3 | 1 / 0 / 2 |
| LSRTDE | 2 / 0 / 1 | 2 / 0 / 1 | 2 / 0 / 1 |
| NLSHADE-RSP | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| j2020 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| jSO | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |

## Composition functions (n=4)

| Algorithm | 200K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 1 / 0 / 3 | 1 / 0 / 3 | 2 / 0 / 2 |
| BIPOP-CMA | 0 / 1 / 3 | 0 / 2 / 2 | 0 / 3 / 1 |
| LSRTDE | 0 / 2 / 2 | 0 / 3 / 1 | 0 / 3 / 1 |
| NLSHADE-RSP | 1 / 1 / 2 | 1 / 1 / 2 | 2 / 1 / 1 |
| j2020 | 2 / 1 / 1 | 2 / 0 / 2 | 2 / 0 / 2 |
| jSO | 0 / 2 / 2 | 0 / 3 / 1 | 0 / 3 / 1 |
