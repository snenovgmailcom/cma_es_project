# CEC2020 / D=5 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=10)

| Algorithm | 50K | 100K | 300K | 500K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 5 / 3 / 2 | 5 / 1 / 4 | 5 / 1 / 4 | 5 / 1 / 4 | 6 / 1 / 3 |
| BIPOP-CMA | 3 / 3 / 4 | 3 / 4 / 3 | 3 / 3 / 4 | 4 / 3 / 3 | 4 / 4 / 2 |
| LSRTDE | 4 / 3 / 3 | 4 / 4 / 2 | 2 / 5 / 3 | 2 / 5 / 3 | 2 / 6 / 2 |
| NLSHADE-RSP | 6 / 1 / 3 | 5 / 1 / 4 | 5 / 1 / 4 | 5 / 1 / 4 | 5 / 1 / 4 |
| j2020 | 4 / 4 / 2 | 4 / 2 / 4 | 6 / 1 / 3 | 6 / 1 / 3 | 6 / 1 / 3 |
| jSO | 6 / 3 / 1 | 5 / 3 / 2 | 4 / 3 / 3 | 5 / 3 / 2 | 5 / 3 / 2 |

## Unimodal and simple multimodal functions (n=4)

| Algorithm | 50K | 100K | 300K | 500K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 2 / 1 / 1 | 2 / 0 / 2 | 2 / 0 / 2 | 2 / 0 / 2 | 3 / 0 / 1 |
| BIPOP-CMA | 1 / 1 / 2 | 1 / 1 / 2 | 1 / 1 / 2 | 1 / 1 / 2 | 1 / 2 / 1 |
| LSRTDE | 2 / 1 / 1 | 2 / 1 / 1 | 1 / 1 / 2 | 1 / 1 / 2 | 1 / 2 / 1 |
| NLSHADE-RSP | 2 / 0 / 2 | 2 / 0 / 2 | 2 / 0 / 2 | 2 / 0 / 2 | 2 / 0 / 2 |
| j2020 | 1 / 1 / 2 | 1 / 0 / 3 | 3 / 0 / 1 | 3 / 0 / 1 | 3 / 0 / 1 |
| jSO | 2 / 1 / 1 | 2 / 1 / 1 | 2 / 1 / 1 | 2 / 1 / 1 | 2 / 1 / 1 |

## Hybrid functions (n=3)

| Algorithm | 50K | 100K | 300K | 500K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| BIPOP-CMA | 2 / 0 / 1 | 2 / 0 / 1 | 2 / 0 / 1 | 3 / 0 / 0 | 3 / 0 / 0 |
| LSRTDE | 2 / 0 / 1 | 2 / 0 / 1 | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
| NLSHADE-RSP | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| j2020 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| jSO | 3 / 0 / 0 | 3 / 0 / 0 | 2 / 0 / 1 | 3 / 0 / 0 | 3 / 0 / 0 |

## Composition functions (n=3)

| Algorithm | 50K | 100K | 300K | 500K | 1M |
|:--|--:|--:|--:|--:|--:|
| ARRDE | 0 / 2 / 1 | 0 / 1 / 2 | 0 / 1 / 2 | 0 / 1 / 2 | 0 / 1 / 2 |
| BIPOP-CMA | 0 / 2 / 1 | 0 / 3 / 0 | 0 / 2 / 1 | 0 / 2 / 1 | 0 / 2 / 1 |
| LSRTDE | 0 / 2 / 1 | 0 / 3 / 0 | 0 / 3 / 0 | 0 / 3 / 0 | 0 / 3 / 0 |
| NLSHADE-RSP | 1 / 1 / 1 | 0 / 1 / 2 | 0 / 1 / 2 | 0 / 1 / 2 | 0 / 1 / 2 |
| j2020 | 0 / 3 / 0 | 0 / 2 / 1 | 0 / 1 / 2 | 0 / 1 / 2 | 0 / 1 / 2 |
| jSO | 1 / 2 / 0 | 0 / 2 / 1 | 0 / 2 / 1 | 0 / 2 / 1 | 0 / 2 / 1 |
