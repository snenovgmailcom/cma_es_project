# CEC2014 / D=30 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=30)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 23 / 5 / 2 | 21 / 4 / 5 | 21 / 4 / 5 |
| BIPOP-CMA | 19 / 8 / 3 | 14 / 9 / 7 | 14 / 7 / 9 |
| LSRTDE | 23 / 3 / 4 | 19 / 2 / 9 | 21 / 4 / 5 |
| NLSHADE-RSP | 12 / 15 / 3 | 7 / 17 / 6 | 8 / 17 / 5 |
| j2020 | 8 / 18 / 4 | 5 / 18 / 7 | 7 / 17 / 6 |
| jSO | 22 / 5 / 3 | 19 / 5 / 6 | 18 / 5 / 7 |

## Unimodal and simple multimodal functions (n=16)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 13 / 3 / 0 | 10 / 3 / 3 | 10 / 3 / 3 |
| BIPOP-CMA | 12 / 3 / 1 | 9 / 2 / 5 | 9 / 2 / 5 |
| LSRTDE | 12 / 3 / 1 | 9 / 2 / 5 | 10 / 2 / 4 |
| NLSHADE-RSP | 8 / 7 / 1 | 5 / 7 / 4 | 6 / 6 / 4 |
| j2020 | 6 / 7 / 3 | 4 / 6 / 6 | 6 / 5 / 5 |
| jSO | 12 / 3 / 1 | 9 / 3 / 4 | 9 / 3 / 4 |

## Hybrid functions (n=6)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 5 / 0 / 1 | 6 / 0 / 0 | 6 / 0 / 0 |
| BIPOP-CMA | 3 / 2 / 1 | 1 / 4 / 1 | 1 / 2 / 3 |
| LSRTDE | 5 / 0 / 1 | 5 / 0 / 1 | 6 / 0 / 0 |
| NLSHADE-RSP | 2 / 3 / 1 | 1 / 5 / 0 | 1 / 5 / 0 |
| j2020 | 2 / 4 / 0 | 1 / 5 / 0 | 1 / 5 / 0 |
| jSO | 5 / 1 / 0 | 5 / 0 / 1 | 4 / 0 / 2 |

## Composition functions (n=8)

| Algorithm | 300K | 600K | 1M |
|:--|--:|--:|--:|
| ARRDE | 5 / 2 / 1 | 5 / 1 / 2 | 5 / 1 / 2 |
| BIPOP-CMA | 4 / 3 / 1 | 4 / 3 / 1 | 4 / 3 / 1 |
| LSRTDE | 6 / 0 / 2 | 5 / 0 / 3 | 5 / 2 / 1 |
| NLSHADE-RSP | 2 / 5 / 1 | 1 / 5 / 2 | 1 / 6 / 1 |
| j2020 | 0 / 7 / 1 | 0 / 7 / 1 | 0 / 7 / 1 |
| jSO | 5 / 1 / 2 | 5 / 2 / 1 | 5 / 2 / 1 |
