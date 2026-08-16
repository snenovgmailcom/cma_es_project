# CEC2017 / D=30 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=29)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 18 / 8 / 3 | 16 / 6 / 7 | 17 / 5 / 7 |
| BIPOP-CMA | 14 / 9 / 6 | 10 / 10 / 9 | 9 / 10 / 10 |
| LSRTDE | 25 / 2 / 2 | 23 / 2 / 4 | 21 / 3 / 5 |
| NLSHADE-RSP | 7 / 16 / 6 | 7 / 16 / 6 | 7 / 18 / 4 |
| j2020 | 8 / 20 / 1 | 4 / 22 / 3 | 4 / 22 / 3 |
| jSO | 19 / 8 / 2 | 16 / 7 / 6 | 15 / 8 / 6 |

## Unimodal and simple multimodal functions (n=9)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 4 / 4 / 1 | 2 / 4 / 3 | 3 / 4 / 2 |
| BIPOP-CMA | 5 / 2 / 2 | 4 / 1 / 4 | 4 / 1 / 4 |
| LSRTDE | 6 / 1 / 2 | 4 / 1 / 4 | 4 / 1 / 4 |
| NLSHADE-RSP | 2 / 7 / 0 | 3 / 6 / 0 | 3 / 6 / 0 |
| j2020 | 3 / 6 / 0 | 2 / 6 / 1 | 2 / 4 / 3 |
| jSO | 4 / 4 / 1 | 2 / 4 / 3 | 2 / 4 / 3 |

## Hybrid functions (n=10)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 7 / 2 / 1 | 8 / 2 / 0 | 8 / 1 / 1 |
| BIPOP-CMA | 5 / 3 / 2 | 2 / 5 / 3 | 2 / 5 / 3 |
| LSRTDE | 10 / 0 / 0 | 10 / 0 / 0 | 10 / 0 / 0 |
| NLSHADE-RSP | 4 / 5 / 1 | 1 / 6 / 3 | 0 / 8 / 2 |
| j2020 | 4 / 5 / 1 | 1 / 8 / 1 | 0 / 10 / 0 |
| jSO | 7 / 2 / 1 | 7 / 1 / 2 | 7 / 1 / 2 |

## Composition functions (n=10)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 7 / 2 / 1 | 6 / 0 / 4 | 6 / 0 / 4 |
| BIPOP-CMA | 4 / 4 / 2 | 4 / 4 / 2 | 3 / 4 / 3 |
| LSRTDE | 9 / 1 / 0 | 9 / 1 / 0 | 7 / 2 / 1 |
| NLSHADE-RSP | 1 / 4 / 5 | 3 / 4 / 3 | 4 / 4 / 2 |
| j2020 | 1 / 9 / 0 | 1 / 8 / 1 | 2 / 8 / 0 |
| jSO | 8 / 2 / 0 | 7 / 2 / 1 | 6 / 3 / 1 |
