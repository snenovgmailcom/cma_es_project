# CEC2017 / D=30 — by-category summary

## Ranking across metrics (budget 3×10^5)

Parallel-coordinate rank of all 7 algorithms on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM), per function class. Each line is one algorithm. The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red.

<table>
<tr>
<td><img src="rank_basic.png" width="320" alt="Unimodal and simple multimodal"></td>
<td><img src="rank_hybrid.png" width="320" alt="Hybrid"></td>
<td><img src="rank_composition.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Budget scaling

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. The budget axis is per class: a budget is shown only where all 7 algorithms cover the whole class. MSC-CMA-ES is shown in red.

<table>
<tr>
<td><img src="budget_basic.png" width="320" alt="Unimodal and simple multimodal"></td>
<td><img src="budget_hybrid.png" width="320" alt="Hybrid"></td>
<td><img src="budget_composition.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking across metrics (budget 10^6)

Same parallel-coordinate rank, recomputed at 10^6 evaluations. Only classes with full 7-algorithm coverage at 10^6 are shown. MSC-CMA-ES is shown in red.

<table>
<tr>
<td><img src="rank_basic_1M.png" width="320" alt="Unimodal and simple multimodal"></td>
<td><img src="rank_hybrid_1M.png" width="320" alt="Hybrid"></td>
<td><img src="rank_composition_1M.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Summary table

Sums of per-function metrics, grouped by function class. Budget: 3×10^5 evaluations. Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.

| Category | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | 435 | 1046 | 2145 | **421** | 2491 | 3894 | 1713 |
|  | Median | 373 | 997 | 2173 | **352** | 2370 | 3708 | 1746 |
|  | Minimum | **28.9** | 146 | 1079 | 96.2 | 1625 | 2674 | 1162 |
|  | Maximum | **1162** | 2135 | 3318 | 1230 | 5595 | 8310 | 2154 |
|  | Std. | 285 | 447 | 548 | **256** | 801 | 1038 | 272 |
|  | FBTC(B) | 3.115 | **4.620** | 4.348 | 4.449 | 2.104 | 3.125 | 4.298 |
| **Hybrid** (n=10) | Mean | 2779 | 1855 | 696 | **75.9** | 32985 | 48737 | 445 |
|  | Median | 2770 | 1672 | 657 | **64.3** | 23114 | 33761 | 422 |
|  | Minimum | 1096 | 718 | 84.7 | **4.71** | 6367 | 12514 | 81.2 |
|  | Maximum | 4934 | 4395 | 1529 | **372** | 185394 | 417453 | 1134 |
|  | Std. | 909 | 871 | 326 | **75.6** | 31129 | 57907 | 245 |
|  | FBTC(B) | 0.300 | 0.345 | 1.058 | **2.565** | 0.383 | 0.212 | 1.035 |
| **Composition** (n=10) | Mean | 5323 | 5818 | **5202** | 5229 | 6321 | 9070 | 5562 |
|  | Median | 5288 | 5385 | **4983** | 5249 | 6189 | 8640 | 5575 |
|  | Minimum | 4596 | **4271** | 4790 | 4927 | 4840 | 6046 | 4797 |
|  | Maximum | 6451 | 10157 | 6085 | **5599** | 8903 | 13911 | 5884 |
|  | Std. | 379 | 1271 | 447 | **161** | 819 | 1845 | 188 |
|  | FBTC(B) | **0.000** | **0.000** | **0.000** | **0.000** | **0.000** | **0.000** | **0.000** |
| **All** (n=29) | Mean | 8538 | 8719 | 8043 | **5726** | 41797 | 61700 | 7719 |
|  | Median | 8431 | 8054 | 7813 | **5666** | 31673 | 46109 | 7743 |
|  | Minimum | 5721 | 5135 | 5954 | **5028** | 12832 | 21234 | 6040 |
|  | Maximum | 12548 | 16687 | 10932 | **7201** | 199892 | 439674 | 9172 |
|  | Std. | 1573 | 2589 | 1320 | **492** | 32750 | 60790 | 704 |
|  | FBTC(B) | 3.416 | 4.965 | 5.406 | **7.014** | 2.487 | 3.337 | 5.334 |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. Class and All rows add the per-function FBTC(B) values. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/cell_report.py from `*/maxevals_300000/f*.pkl` (table) and all common budgets (budget scaling).*
