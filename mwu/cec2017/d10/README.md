# CEC2017 / D=10 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=29)

| Algorithm | 100K | 300K | 1M |
|:--|--:|--:|--:|
| ARRDE | 15 / 5 / 9 | 13 / 5 / 11 | 16 / 5 / 8 |
| BIPOP-CMA | 8 / 7 / 14 | 7 / 9 / 13 | 10 / 8 / 11 |
| LSRTDE | 17 / 8 / 4 | 13 / 9 / 7 | 11 / 12 / 6 |
| NLSHADE-RSP | 14 / 10 / 5 | 12 / 8 / 9 | 13 / 9 / 7 |
| j2020 | 10 / 10 / 9 | 10 / 11 / 8 | 14 / 8 / 7 |
| jSO | 15 / 8 / 6 | 12 / 11 / 6 | 11 / 12 / 6 |

## Unimodal and simple multimodal functions (n=9)

| Algorithm | 100K | 300K | 1M |
|:--|--:|--:|--:|
| ARRDE | 3 / 2 / 4 | 2 / 2 / 5 | 3 / 2 / 4 |
| BIPOP-CMA | 3 / 0 / 6 | 2 / 1 / 6 | 2 / 1 / 6 |
| LSRTDE | 5 / 2 / 2 | 4 / 2 / 3 | 2 / 3 / 4 |
| NLSHADE-RSP | 3 / 4 / 2 | 2 / 3 / 4 | 3 / 1 / 5 |
| j2020 | 3 / 4 / 2 | 2 / 3 / 4 | 4 / 1 / 4 |
| jSO | 3 / 2 / 4 | 2 / 4 / 3 | 2 / 4 / 3 |

## Hybrid functions (n=10)

| Algorithm | 100K | 300K | 1M |
|:--|--:|--:|--:|
| ARRDE | 9 / 0 / 1 | 8 / 0 / 2 | 9 / 0 / 1 |
| BIPOP-CMA | 4 / 2 / 4 | 4 / 1 / 5 | 5 / 0 / 5 |
| LSRTDE | 9 / 1 / 0 | 8 / 1 / 1 | 8 / 2 / 0 |
| NLSHADE-RSP | 7 / 1 / 2 | 8 / 1 / 1 | 8 / 1 / 1 |
| j2020 | 7 / 1 / 2 | 7 / 2 / 1 | 8 / 1 / 1 |
| jSO | 9 / 0 / 1 | 8 / 0 / 2 | 8 / 0 / 2 |

## Composition functions (n=10)

| Algorithm | 100K | 300K | 1M |
|:--|--:|--:|--:|
| ARRDE | 3 / 3 / 4 | 3 / 3 / 4 | 4 / 3 / 3 |
| BIPOP-CMA | 1 / 5 / 4 | 1 / 7 / 2 | 3 / 7 / 0 |
| LSRTDE | 3 / 5 / 2 | 1 / 6 / 3 | 1 / 7 / 2 |
| NLSHADE-RSP | 4 / 5 / 1 | 2 / 4 / 4 | 2 / 7 / 1 |
| j2020 | 0 / 5 / 5 | 1 / 6 / 3 | 2 / 6 / 2 |
| jSO | 3 / 6 / 1 | 2 / 7 / 1 | 1 / 8 / 1 |
