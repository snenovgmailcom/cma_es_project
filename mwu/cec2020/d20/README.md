# CEC2020 / D=20 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=10)

| Algorithm | 10M |
|:--|--:|
| ARRDE | 7 / 2 / 1 |
| BIPOP-CMA | 4 / 4 / 2 |
| LSRTDE | 5 / 4 / 1 |
| NLSHADE-RSP | 5 / 4 / 1 |
| j2020 | 5 / 4 / 1 |
| jSO | 4 / 5 / 1 |

## Unimodal and simple multimodal functions (n=4)

| Algorithm | 10M |
|:--|--:|
| ARRDE | 2 / 1 / 1 |
| BIPOP-CMA | 2 / 1 / 1 |
| LSRTDE | 2 / 1 / 1 |
| NLSHADE-RSP | 2 / 1 / 1 |
| j2020 | 2 / 1 / 1 |
| jSO | 2 / 1 / 1 |

## Hybrid functions (n=3)

| Algorithm | 10M |
|:--|--:|
| ARRDE | 3 / 0 / 0 |
| BIPOP-CMA | 2 / 0 / 1 |
| LSRTDE | 3 / 0 / 0 |
| NLSHADE-RSP | 1 / 2 / 0 |
| j2020 | 2 / 1 / 0 |
| jSO | 2 / 1 / 0 |

## Composition functions (n=3)

| Algorithm | 10M |
|:--|--:|
| ARRDE | 2 / 1 / 0 |
| BIPOP-CMA | 0 / 3 / 0 |
| LSRTDE | 0 / 3 / 0 |
| NLSHADE-RSP | 2 / 1 / 0 |
| j2020 | 1 / 2 / 0 |
| jSO | 0 / 3 / 0 |
