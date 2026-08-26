# CEC2014 / D=30 — by-category summary

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
| **Unimodal and simple multimodal** (n=16) | Mean | 513 | 1386 | 1892 | **457** | 370944 | 397092 | 1407 |
|  | Median | 377 | 1283 | 1739 | **352** | 227493 | 302835 | 1407 |
|  | Minimum | 74.2 | 343 | 936 | **34.2** | 59682 | 111591 | 857 |
|  | Maximum | **1414** | 3603 | 3769 | 1773 | 4447100 | 1949051 | 1884 |
|  | Std. | 345 | 693 | 630 | 381 | 609748 | 354740 | **205** |
|  | FBTC(B) | 4.768 | 6.962 | 7.952 | 7.848 | 5.763 | 5.609 | **8.462** |
| **Hybrid** (n=6) | Mean | 1866 | 1844 | 166 | **89.2** | 21111 | 3604 | 145 |
|  | Median | 1795 | 1813 | 114 | **43.9** | 13858 | 3369 | 110 |
|  | Minimum | 1168 | 321 | 43.7 | **26** | 1254 | 1635 | 62.9 |
|  | Maximum | 3188 | 3660 | 608 | **194** | 148061 | 8668 | 289 |
|  | Std. | 496 | 800 | 145 | **69.9** | 25977 | 1241 | 74.8 |
|  | FBTC(B) | 0.264 | 0.234 | 0.749 | **0.967** | 0.288 | 0.223 | 0.705 |
| **Composition** (n=8) | Mean | 4356 | 4883 | 3602 | **2359** | 4623 | 5716 | 2508 |
|  | Median | 4330 | 5013 | 3560 | **2334** | 4621 | 5508 | 2501 |
|  | Minimum | 3351 | 3325 | 2969 | **2168** | 3143 | 4206 | 2356 |
|  | Maximum | 5288 | 7019 | 4971 | **2590** | 6130 | 8248 | 2797 |
|  | Std. | 430 | 919 | 411 | 111 | 607 | 1119 | **99.7** |
|  | FBTC(B) | 0.000 | 0.000 | 0.000 | 0.000 | **0.007** | 0.000 | 0.000 |
| **All** (n=30) | Mean | 6735 | 8113 | 5660 | **2905** | 396677 | 406412 | 4060 |
|  | Median | 6502 | 8109 | 5413 | **2730** | 245971 | 311712 | 4019 |
|  | Minimum | 4593 | 3989 | 3949 | **2228** | 64080 | 117432 | 3275 |
|  | Maximum | 9890 | 14282 | 9347 | **4556** | 4601292 | 1965967 | 4969 |
|  | Std. | 1271 | 2411 | 1186 | 562 | 636332 | 357099 | **379** |
|  | FBTC(B) | 5.032 | 7.195 | 8.701 | 8.815 | 6.058 | 5.832 | **9.168** |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. Class and All rows add the per-function FBTC(B) values. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/cell_report.py from `*/maxevals_300000/f*.pkl` (table) and all common budgets (budget scaling).*
