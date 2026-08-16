# CEC2022 / D=20 — Mann–Whitney U tests on terminal errors

Reference algorithm: **MSC-CMA**. Each comparison uses independent, two-sided Mann–Whitney U tests on the run-wise terminal errors. For each fixed budget and competitor, Holm–Bonferroni correction is applied across all functions at family-wise level `0.05`. Values with absolute error at most `1e-08` are treated as zero.

Every table entry is `competitor better / reference better / n.s.`. The class tables are filtered summaries of the all-functions analysis; the Holm correction is not recomputed within a class.

Complete per-function statistics (`U`, effect size, raw p-value, Holm-adjusted p-value, and decision) are in [details.csv](details.csv).

## All functions (n=12)

| Algorithm | 1M |
|:--|--:|
| ARRDE | 5 / 3 / 4 |
| BIPOP-CMA | 2 / 6 / 4 |
| LSRTDE | 4 / 3 / 5 |
| NLSHADE-RSP | 3 / 6 / 3 |
| j2020 | 3 / 6 / 3 |
| jSO | 6 / 4 / 2 |

## Unimodal and simple multimodal functions (n=5)

| Algorithm | 1M |
|:--|--:|
| ARRDE | 2 / 1 / 2 |
| BIPOP-CMA | 2 / 2 / 1 |
| LSRTDE | 2 / 1 / 2 |
| NLSHADE-RSP | 2 / 3 / 0 |
| j2020 | 2 / 2 / 1 |
| jSO | 2 / 2 / 1 |

## Hybrid functions (n=3)

| Algorithm | 1M |
|:--|--:|
| ARRDE | 2 / 0 / 1 |
| BIPOP-CMA | 0 / 2 / 1 |
| LSRTDE | 1 / 0 / 2 |
| NLSHADE-RSP | 0 / 1 / 2 |
| j2020 | 0 / 2 / 1 |
| jSO | 3 / 0 / 0 |

## Composition functions (n=4)

| Algorithm | 1M |
|:--|--:|
| ARRDE | 1 / 2 / 1 |
| BIPOP-CMA | 0 / 2 / 2 |
| LSRTDE | 1 / 2 / 1 |
| NLSHADE-RSP | 1 / 2 / 1 |
| j2020 | 1 / 2 / 1 |
| jSO | 1 / 2 / 1 |
