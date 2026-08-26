# CEC2017 — cross-dimension summary

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
| Unimodal and simple multimodal | 10 | 32.8 | 39.4 | 43.1 | **16.8** | 138 | 78.1 | 135 |
| Unimodal and simple multimodal | 30 | 373 | 997 | 2173 | **352** | 2370 | 3708 | 1746 |
| Hybrid | 10 | 202 | 193 | 7.55 | 3.75 | 134 | 54.3 | **1.88** |
| Hybrid | 30 | 2770 | 1672 | 657 | **64.3** | 23114 | 33761 | 422 |
| Composition | 10 | **2152** | 2745 | 2317 | 2909 | 2193 | 2733 | 2844 |
| Composition | 30 | 5288 | 5385 | **4983** | 5249 | 6189 | 8640 | 5575 |

## Minimum error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | 3.17 | **1.94** | 7.04 | 10.5 | 13.3 | 5.19 | 10.9 |
| Unimodal and simple multimodal | 30 | **28.9** | 146 | 1079 | 96.2 | 1625 | 2674 | 1162 |
| Hybrid | 10 | 4.38 | 1.92 | 0.0315 | **0.0195** | 4.74 | 0.233 | 0.0426 |
| Hybrid | 30 | 1096 | 718 | 84.7 | **4.71** | 6367 | 12514 | 81.2 |
| Composition | 10 | **930** | 1812 | 1309 | 2508 | 1170 | 1480 | 2610 |
| Composition | 30 | 4596 | **4271** | 4790 | 4927 | 4840 | 6046 | 4797 |

## Maximum error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | 264 | 350 | 375 | **35.4** | 287 | 340 | 277 |
| Unimodal and simple multimodal | 30 | **1162** | 2135 | 3318 | 1230 | 5595 | 8310 | 2154 |
| Hybrid | 10 | 423 | 698 | 236 | 156 | 614 | 463 | **10.8** |
| Hybrid | 30 | 4934 | 4395 | 1529 | **372** | 185394 | 417453 | 1134 |
| Composition | 10 | **2697** | 3472 | 2783 | 820474 | 3446 | 4231 | 3297 |
| Composition | 30 | 6451 | 10157 | 6085 | **5599** | 8903 | 13911 | 5884 |

## FBTC(B) — Fixed-Budget Target Coverage

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 10 | 5.148 | **5.790** | 5.662 | 5.785 | 5.374 | 4.801 | 5.603 |
| Unimodal and simple multimodal | 30 | 3.115 | **4.620** | 4.348 | 4.449 | 2.104 | 3.125 | 4.298 |
| Hybrid | 10 | 2.347 | 2.372 | 4.780 | 4.304 | 4.173 | 3.770 | **5.862** |
| Hybrid | 30 | 0.300 | 0.345 | 1.058 | **2.565** | 0.383 | 0.212 | 1.035 |
| Composition | 10 | 1.714 | 0.143 | 0.635 | 0.070 | **1.785** | 0.500 | 0.011 |
| Composition | 30 | **0.000** | **0.000** | **0.000** | **0.000** | **0.000** | **0.000** | **0.000** |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. The tables sum per-function FBTC(B) within each class. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/suite_report.py.*
