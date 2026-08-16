# CEC2014 / D=10 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=30)

| Algorithm | 100K | 300K | 500K | 600K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 22 / 3 / 5 | 20 / 2 / 8 | 20 / 2 / 8 | 20 / 2 / 8 | 23 / 2 / 5 |
| BIPOP-CMA | 11 / 11 / 8 | 11 / 12 / 7 | 12 / 12 / 6 | 12 / 10 / 8 | 12 / 11 / 7 |
| LSRTDE | 18 / 4 / 8 | 13 / 6 / 11 | 13 / 7 / 10 | 12 / 7 / 11 | 12 / 10 / 8 |
| NLSHADE-RSP | 14 / 8 / 8 | 14 / 7 / 9 | 15 / 5 / 10 | 16 / 6 / 8 | 14 / 3 / 13 |
| j2020 | 11 / 13 / 6 | 11 / 11 / 8 | 12 / 9 / 9 | 13 / 6 / 11 | 13 / 4 / 13 |
| jSO | 20 / 4 / 6 | 16 / 5 / 9 | 17 / 6 / 7 | 17 / 7 / 6 | 16 / 7 / 7 |

## Unimodal and simple multimodal functions (n=16)

| Algorithm | 100K | 300K | 500K | 600K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 11 / 3 / 2 | 9 / 2 / 5 | 9 / 2 / 5 | 9 / 2 / 5 | 9 / 2 / 5 |
| BIPOP-CMA | 9 / 4 / 3 | 7 / 6 / 3 | 7 / 6 / 3 | 7 / 5 / 4 | 7 / 5 / 4 |
| LSRTDE | 9 / 2 / 5 | 7 / 2 / 7 | 6 / 3 / 7 | 6 / 3 / 7 | 6 / 4 / 6 |
| NLSHADE-RSP | 8 / 4 / 4 | 8 / 3 / 5 | 9 / 2 / 5 | 10 / 2 / 4 | 9 / 1 / 6 |
| j2020 | 7 / 6 / 3 | 7 / 5 / 4 | 8 / 4 / 4 | 8 / 2 / 6 | 7 / 1 / 8 |
| jSO | 10 / 3 / 3 | 9 / 3 / 4 | 10 / 3 / 3 | 10 / 3 / 3 | 9 / 3 / 4 |

## Hybrid functions (n=6)

| Algorithm | 100K | 300K | 500K | 600K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 6 / 0 / 0 | 5 / 0 / 1 | 6 / 0 / 0 | 5 / 0 / 1 | 6 / 0 / 0 |
| BIPOP-CMA | 1 / 1 / 4 | 3 / 0 / 3 | 4 / 0 / 2 | 4 / 0 / 2 | 4 / 0 / 2 |
| LSRTDE | 6 / 0 / 0 | 5 / 0 / 1 | 5 / 0 / 1 | 5 / 0 / 1 | 5 / 1 / 0 |
| NLSHADE-RSP | 4 / 2 / 0 | 5 / 1 / 0 | 5 / 1 / 0 | 5 / 1 / 0 | 5 / 0 / 1 |
| j2020 | 4 / 1 / 1 | 4 / 2 / 0 | 4 / 1 / 1 | 4 / 1 / 1 | 5 / 0 / 1 |
| jSO | 6 / 0 / 0 | 5 / 0 / 1 | 5 / 0 / 1 | 5 / 0 / 1 | 5 / 0 / 1 |

## Composition functions (n=8)

| Algorithm | 100K | 300K | 500K | 600K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 5 / 0 / 3 | 6 / 0 / 2 | 5 / 0 / 3 | 6 / 0 / 2 | 8 / 0 / 0 |
| BIPOP-CMA | 1 / 6 / 1 | 1 / 6 / 1 | 1 / 6 / 1 | 1 / 5 / 2 | 1 / 6 / 1 |
| LSRTDE | 3 / 2 / 3 | 1 / 4 / 3 | 2 / 4 / 2 | 1 / 4 / 3 | 1 / 5 / 2 |
| NLSHADE-RSP | 2 / 2 / 4 | 1 / 3 / 4 | 1 / 2 / 5 | 1 / 3 / 4 | 0 / 2 / 6 |
| j2020 | 0 / 6 / 2 | 0 / 4 / 4 | 0 / 4 / 4 | 1 / 3 / 4 | 1 / 3 / 4 |
| jSO | 4 / 1 / 3 | 2 / 2 / 4 | 2 / 3 / 3 | 2 / 4 / 2 | 2 / 4 / 2 |
