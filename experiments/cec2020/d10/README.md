# CEC2020 / D=10 — by-category summary

## Ranking — D=10 (B = 10^6)

Parallel-coordinate rank of all 7 algorithms on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM), per function class. Each line is one algorithm. The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 10^6 evaluations.

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

## Budget scaling — D=10

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. The budget axis is per class: a budget is shown only where all 7 algorithms cover the whole class. MSC-CMA-ES is shown in red. Official budget for this cell: B = 10^6 evaluations.

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

## Ranking — D=10 (B = 2×10^7)

Same parallel-coordinate rank, recomputed at B = 2×10^7 evaluations. Only classes with full 7-algorithm coverage at B = 2×10^7 are shown. MSC-CMA-ES is shown in red.

<table>
<tr>
<td><img src="rank_basic_20M.png" width="320" alt="Unimodal and simple multimodal"></td>
<td><img src="rank_hybrid_20M.png" width="320" alt="Hybrid"></td>
<td><img src="rank_composition_20M.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Summary table

Sums of per-function metrics, grouped by function class. Budget: 10^6 evaluations. Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.

| Category | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | 8.67 | 17.1 | 13.3 | 14 | 11.8 | **8.22** | 17.6 |
|  | Median | **6.92** | 22.7 | 11.6 | 11.9 | 10.8 | 10.7 | 15.7 |
|  | Minimum | 1.03 | 0.125 | 6.16 | 10.5 | 0.0625 | **0** | 10.8 |
|  | Maximum | 20.6 | 36.4 | 22.5 | 25.5 | 28.4 | **15** | 39.9 |
|  | Std. | 5.2 | 11.6 | 3.97 | **3.83** | 7.82 | 4.96 | 5.76 |
|  | FBTC(B) | 1.556 | 1.631 | 1.589 | 1.567 | **2.301** | 2.027 | 1.543 |
| **Hybrid** (n=3) | Mean | 2.12 | 6.06 | **0.367** | 3.48 | 1.16 | 0.765 | 0.41 |
|  | Median | 2.03 | 1.16 | 0.357 | 1.18 | 0.484 | 0.678 | **0.25** |
|  | Minimum | 0.636 | 0.0593 | **0.00333** | 0.0195 | 0.016 | 0.0292 | 0.0194 |
|  | Maximum | 4.45 | 206 | **1.34** | 41.3 | 9.53 | 2.67 | 2.21 |
|  | Std. | 0.836 | 29.6 | **0.409** | 6.98 | 1.83 | 0.588 | 0.471 |
|  | FBTC(B) | 0.730 | 0.858 | **1.401** | 0.801 | 1.206 | 1.110 | 1.314 |
| **Composition** (n=3) | Mean | **106** | 512 | 205 | 814 | 462 | 244 | 719 |
|  | Median | **100** | 598 | 220 | 825 | 498 | 200 | 798 |
|  | Minimum | **0** | 100 | 100 | 498 | 100 | 100 | 598 |
|  | Maximum | **200** | 782 | 367 | 876 | 598 | 598 | 872 |
|  | Std. | **71** | 205 | 79.8 | 102 | 150 | 148 | 121 |
|  | FBTC(B) | **1.923** | 0.436 | 0.511 | 0.095 | 0.833 | 0.686 | 0.024 |
| **All** (n=10) | Mean | **117** | 535 | 219 | 832 | 474 | 253 | 737 |
|  | Median | **109** | 622 | 232 | 838 | 509 | 211 | 814 |
|  | Minimum | **1.66** | 100 | 106 | 508 | 100 | 100 | 609 |
|  | Maximum | **225** | 1023 | 391 | 943 | 636 | 616 | 914 |
|  | Std. | **77** | 246 | 84.2 | 113 | 160 | 154 | 128 |
|  | FBTC(B) | 4.210 | 2.924 | 3.502 | 2.464 | **4.339** | 3.822 | 2.881 |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. Class and All rows add the per-function FBTC(B) values. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/cell_report.py from `*/maxevals_1000000/f*.pkl` (table) and all common budgets (budget scaling).*
