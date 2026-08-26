# CEC2014 — cross-dimension summary

Aggregated sums by function category, across dimensions. For simplicity the suite is presented per dimension. Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.

Official budgets — D=10: 10^5, D=30: 3×10^5.

## Ranking — D=10 (B = 10^5)

Parallel-coordinate rank on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM). The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 10^5 evaluations.

<table>
<tr>
<td><img src="d10/rank_d10_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d10/rank_d10_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d10/rank_d10_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Budget scaling — D=10

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. Official budget for D=10: B = 10^5 evaluations.

<table>
<tr>
<td><img src="d10/budget_d10_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d10/budget_d10_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d10/budget_d10_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking — D=10 (B = 10^6)

Same rank, recomputed at B = 10^6 evaluations. Only classes with full 7-algorithm coverage at B = 10^6 are shown.

<table>
<tr>
<td><img src="d10/rank_d10_basic_1M.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d10/rank_d10_hybrid_1M.png" width="300" alt="Hybrid"></td>
<td><img src="d10/rank_d10_composition_1M.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking — D=10 (B = 10^7)

Same rank, recomputed at B = 10^7 evaluations. Only classes with full 7-algorithm coverage at B = 10^7 are shown.

<table>
<tr>
<td><img src="../spacer.png" width="300" height="1" alt=""></td>
<td><img src="../spacer.png" width="300" height="1" alt=""></td>
<td><img src="d10/rank_d10_composition_10M.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td></td>
<td></td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking — D=30 (B = 3×10^5)

Parallel-coordinate rank on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM). The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 3×10^5 evaluations.

<table>
<tr>
<td><img src="d30/rank_d30_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d30/rank_d30_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d30/rank_d30_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Budget scaling — D=30

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. Official budget for D=30: B = 3×10^5 evaluations.

<table>
<tr>
<td><img src="d30/budget_d30_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d30/budget_d30_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d30/budget_d30_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking — D=30 (B = 10^6)

Same rank, recomputed at B = 10^6 evaluations. Only classes with full 7-algorithm coverage at B = 10^6 are shown.

<table>
<tr>
<td><img src="d30/rank_d30_basic_1M.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d30/rank_d30_hybrid_1M.png" width="300" alt="Hybrid"></td>
<td><img src="d30/rank_d30_composition_1M.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Median error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | **69** | 118 | 146 | 69.8 | 145 | 91.6 | 77.4 |
| Unimodal and simple multimodal | 30 | 377 | 1283 | 1739 | **352** | 227493 | 302835 | 1407 |
| Hybrid | 10 | 31.2 | 55.2 | 2.65 | **1.9** | 24.7 | 9.45 | 2.3 |
| Hybrid | 30 | 1795 | 1813 | 114 | **43.9** | 13858 | 3369 | 110 |
| Composition | 10 | 1695 | 2054 | 1695 | 2054 | 1752 | 1762 | **1693** |
| Composition | 30 | 4330 | 5013 | 3560 | **2334** | 4621 | 5508 | 2501 |

## Minimum error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | 27.8 | 5.67 | 4.37 | **0.539** | 8.82 | 11.4 | 4.22 |
| Unimodal and simple multimodal | 30 | 74.2 | 343 | 936 | **34.2** | 59682 | 111591 | 857 |
| Hybrid | 10 | 2.45 | 0.788 | 0.0202 | 0.0215 | **0.0125** | 0.278 | 0.0226 |
| Hybrid | 30 | 1168 | 321 | 43.7 | **26** | 1254 | 1635 | 62.9 |
| Composition | 10 | 896 | 1132 | **896** | 1573 | 952 | 1559 | 1573 |
| Composition | 30 | 3351 | 3325 | 2969 | **2168** | 3143 | 4206 | 2356 |

## Maximum error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | 430 | 582 | 380 | **209** | 559 | 462 | 287 |
| Unimodal and simple multimodal | 30 | **1414** | 3603 | 3769 | 1773 | 4447100 | 1949051 | 1884 |
| Hybrid | 10 | 183 | 617 | 50.9 | 35.8 | 187 | 78.6 | **16** |
| Hybrid | 30 | 3188 | 3660 | 608 | **194** | 148061 | 8668 | 289 |
| Composition | 10 | 1856 | 2574 | **1769** | 2437 | 1883 | 2283 | 2166 |
| Composition | 30 | 5288 | 7019 | 4971 | **2590** | 6130 | 8248 | 2797 |

## FBTC(B) — Fixed-Budget Target Coverage

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | 6.754 | 7.890 | 8.963 | 8.730 | 8.427 | 7.084 | **9.045** |
| Unimodal and simple multimodal | 30 | 4.768 | 6.962 | 7.952 | 7.848 | 5.763 | 5.609 | **8.462** |
| Hybrid | 10 | 1.038 | 0.915 | 1.656 | 1.732 | 1.606 | 1.428 | **1.815** |
| Hybrid | 30 | 0.264 | 0.234 | 0.749 | **0.967** | 0.288 | 0.223 | 0.705 |
| Composition | 10 | 0.210 | 0.035 | 0.273 | 0.112 | **0.539** | 0.134 | 0.199 |
| Composition | 30 | 0.000 | 0.000 | 0.000 | 0.000 | **0.007** | 0.000 | 0.000 |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. The tables sum per-function FBTC(B) within each class. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/suite_report.py.*
