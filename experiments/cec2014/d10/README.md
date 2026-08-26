# CEC2014 / D=10 — by-category summary

## Ranking — D=10 (B = 10^5)

Parallel-coordinate rank of all 7 algorithms on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM), per function class. Each line is one algorithm. The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 10^5 evaluations.

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

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. The budget axis is per class: a budget is shown only where all 7 algorithms cover the whole class. MSC-CMA-ES is shown in red. Official budget for this cell: B = 10^5 evaluations.

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

## Ranking — D=10 (B = 10^7)

Same parallel-coordinate rank, recomputed at B = 10^7 evaluations. Only classes with full 7-algorithm coverage at B = 10^7 are shown. MSC-CMA-ES is shown in red.

<table>
<tr>
<td><img src="../../spacer.png" width="320" height="1" alt=""></td>
<td><img src="../../spacer.png" width="320" height="1" alt=""></td>
<td><img src="rank_composition_10M.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td></td>
<td></td>
<td align="center">Composition</td>
</tr>
</table>

## Summary table

Sums of per-function metrics, grouped by function class. Budget: 10^5 evaluations. Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.

| Category | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Unimodal and simple multimodal** (n=16) | Mean | 98.9 | 133 | 132 | **52.7** | 138 | 118 | 83.6 |
|  | Median | **69** | 118 | 146 | 69.8 | 145 | 91.6 | 77.4 |
|  | Minimum | 27.8 | 5.67 | 4.37 | **0.539** | 8.82 | 11.4 | 4.22 |
|  | Maximum | 430 | 582 | 380 | **209** | 559 | 462 | 287 |
|  | Std. | 93.9 | 129 | 102 | **54** | 123 | 86.8 | 76.2 |
|  | FBTC(B) | 6.754 | 7.890 | 8.963 | 8.730 | 8.427 | 7.084 | **9.045** |
| **Hybrid** (n=6) | Mean | 40.7 | 88.3 | 6.58 | 3.77 | 39.8 | 16.5 | **2.47** |
|  | Median | 31.2 | 55.2 | 2.65 | **1.9** | 24.7 | 9.45 | 2.3 |
|  | Minimum | 2.45 | 0.788 | 0.0202 | 0.0215 | **0.0125** | 0.278 | 0.0226 |
|  | Maximum | 183 | 617 | 50.9 | 35.8 | 187 | 78.6 | **16** |
|  | Std. | 37.4 | 116 | 12.4 | 7.86 | 44 | 18.7 | **2.68** |
|  | FBTC(B) | 1.038 | 0.915 | 1.656 | 1.732 | 1.606 | 1.428 | **1.815** |
| **Composition** (n=8) | Mean | 1592 | 2008 | **1581** | 2000 | 1604 | 1798 | 1728 |
|  | Median | 1695 | 2054 | 1695 | 2054 | 1752 | 1762 | **1693** |
|  | Minimum | 896 | 1132 | **896** | 1573 | 952 | 1559 | 1573 |
|  | Maximum | 1856 | 2574 | **1769** | 2437 | 1883 | 2283 | 2166 |
|  | Std. | 279 | 317 | 232 | 345 | 302 | 176 | **121** |
|  | FBTC(B) | 0.210 | 0.035 | 0.273 | 0.112 | **0.539** | 0.134 | 0.199 |
| **All** (n=30) | Mean | 1732 | 2230 | **1720** | 2056 | 1782 | 1933 | 1814 |
|  | Median | 1795 | 2227 | 1844 | 2126 | 1922 | 1863 | **1773** |
|  | Minimum | 926 | 1138 | **900** | 1573 | 961 | 1571 | 1577 |
|  | Maximum | 2470 | 3773 | **2200** | 2682 | 2628 | 2824 | 2469 |
|  | Std. | 410 | 562 | 346 | 407 | 469 | 282 | **200** |
|  | FBTC(B) | 8.002 | 8.840 | 10.892 | 10.574 | 10.571 | 8.647 | **11.059** |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. Class and All rows add the per-function FBTC(B) values. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/cell_report.py from `*/maxevals_100000/f*.pkl` (table) and all common budgets (budget scaling).*
