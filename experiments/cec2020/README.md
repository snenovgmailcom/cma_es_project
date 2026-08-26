# CEC2020 — cross-dimension summary

Aggregated sums by function category, across dimensions. For simplicity the suite is presented per dimension. Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.

Official budgets — D=5: 5×10^4, D=10: 10^6, D=15: 3×10^6, D=20: 10^7.

## Ranking — D=5 (B = 5×10^4)

Parallel-coordinate rank on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM). The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 5×10^4 evaluations.

<table>
<tr>
<td><img src="d5/rank_d5_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d5/rank_d5_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d5/rank_d5_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Budget scaling — D=5

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. Official budget for D=5: B = 5×10^4 evaluations.

<table>
<tr>
<td><img src="d5/budget_d5_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d5/budget_d5_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d5/budget_d5_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking — D=10 (B = 10^6)

Parallel-coordinate rank on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM). The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 10^6 evaluations.

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

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. Official budget for D=10: B = 10^6 evaluations.

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

## Ranking — D=15 (B = 3×10^6)

Parallel-coordinate rank on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM). The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 3×10^6 evaluations.

<table>
<tr>
<td><img src="d15/rank_d15_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d15/rank_d15_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d15/rank_d15_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Budget scaling — D=15

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. Official budget for D=15: B = 3×10^6 evaluations.

<table>
<tr>
<td><img src="../spacer.png" width="300" height="1" alt=""></td>
<td><img src="../spacer.png" width="300" height="1" alt=""></td>
<td><img src="d15/budget_d15_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td></td>
<td></td>
<td align="center">Composition</td>
</tr>
</table>

## Ranking — D=20 (B = 10^7)

Parallel-coordinate rank on four aggregate metrics (Maximum-SUM, Median-SUM, FBTC(B), Minimum-SUM). The axes are oriented so smaller error-based sums and larger FBTC(B) values appear toward the top. MSC-CMA-ES is shown in red. Budget: B = 10^7 evaluations.

<table>
<tr>
<td><img src="d20/rank_d20_basic.png" width="300" alt="Unimodal and simple multimodal"></td>
<td><img src="d20/rank_d20_hybrid.png" width="300" alt="Hybrid"></td>
<td><img src="d20/rank_d20_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td align="center">Unimodal and simple multimodal</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Budget scaling — D=20

Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Larger FBTC(B) values indicate greater fixed-budget target coverage. Official budget for D=20: B = 10^7 evaluations.

<table>
<tr>
<td><img src="../spacer.png" width="300" height="1" alt=""></td>
<td><img src="../spacer.png" width="300" height="1" alt=""></td>
<td><img src="d20/budget_d20_composition.png" width="300" alt="Composition"></td>
</tr>
<tr>
<td></td>
<td></td>
<td align="center">Composition</td>
</tr>
</table>

## Median error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 5 | 4.13 | 8.66 | 5.77 | 5.87 | **1.77** | 5.84 | 5.5 |
| Unimodal and simple multimodal | 10 | **6.92** | 22.7 | 11.6 | 11.9 | 10.8 | 10.7 | 15.7 |
| Unimodal and simple multimodal | 15 | **11.7** | 23.1 | 18.3 | 19.7 | 15.7 | 15.8 | 26.8 |
| Unimodal and simple multimodal | 20 | **13.1** | 17.8 | 21 | 24.1 | 20.4 | 20.6 | 23.6 |
| Hybrid | 5 | 0.542 | 0.624 | **0** | **0** | **0** | **0** | **0** |
| Hybrid | 10 | 2.03 | 1.16 | 0.357 | 1.18 | 0.484 | 0.678 | **0.25** |
| Hybrid | 15 | 3.34 | 1.79 | **1.23** | 2.02 | 15.7 | 10.5 | 4.15 |
| Hybrid | 20 | 11.6 | 8.4 | **1.48** | 2 | 135 | 69.5 | 7.43 |
| Composition | 5 | **0** | 447 | 100 | 447 | 300 | 100 | 447 |
| Composition | 10 | **100** | 598 | 220 | 825 | 498 | 200 | 798 |
| Composition | 15 | **200** | 600 | 335 | 886 | 500 | 500 | 853 |
| Composition | 20 | **540** | 714 | 581 | 891 | 599 | 911 | 907 |

## Minimum error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 5 | 0.125 | 1.12 | 0.613 | **0** | **0** | **0** | 0.613 |
| Unimodal and simple multimodal | 10 | 1.03 | 0.125 | 6.16 | 10.5 | 0.0625 | **0** | 10.8 |
| Unimodal and simple multimodal | 15 | 1.22 | 0.125 | 15.9 | 16.3 | 15.6 | **0** | 15.8 |
| Unimodal and simple multimodal | 20 | 3.37 | 6.15 | 20.7 | 21.3 | 20.4 | **0.031** | 20.7 |
| Hybrid | 5 | 5.5e-7 | **0** | **0** | **0** | **0** | **0** | **0** |
| Hybrid | 10 | 0.636 | 0.0593 | **0.00333** | 0.0195 | 0.016 | 0.0292 | 0.0194 |
| Hybrid | 15 | 0.868 | 0.743 | **0.127** | 0.878 | 0.531 | 0.927 | 0.436 |
| Hybrid | 20 | 2.77 | 2.32 | 0.567 | 1.06 | **0.426** | 20.6 | 1.67 |
| Composition | 5 | **0** | 100 | **0** | 400 | **0** | **0** | 400 |
| Composition | 10 | **0** | 100 | 100 | 498 | 100 | 100 | 598 |
| Composition | 15 | **100** | 200 | 200 | 800 | 500 | 200 | 600 |
| Composition | 20 | 399 | 499 | **131** | 814 | 445 | 499 | 879 |

## Maximum error

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 5 | 165 | 132 | 125 | 452 | **12.1** | 37 | 12.9 |
| Unimodal and simple multimodal | 10 | 20.6 | 36.4 | 22.5 | 25.5 | 28.4 | **15** | 39.9 |
| Unimodal and simple multimodal | 15 | 28.2 | 61.2 | 33.3 | 154 | 141 | **18.2** | 149 |
| Unimodal and simple multimodal | 20 | 22 | 39.5 | 23 | 32.2 | 23.9 | **20.8** | 27.9 |
| Hybrid | 5 | 7.38 | 3.11 | 0.624 | 139 | **0** | 0.624 | 0.624 |
| Hybrid | 10 | 4.45 | 206 | **1.34** | 41.3 | 9.53 | 2.67 | 2.21 |
| Hybrid | 15 | 8.2 | 135 | **2.88** | 137 | 166 | 107 | 11.3 |
| Hybrid | 20 | 17.6 | 508 | **5.82** | 25 | 742 | 250 | 28.8 |
| Composition | 5 | **116** | 691 | 418 | 648 | 401 | 414 | 447 |
| Composition | 10 | **200** | 782 | 367 | 876 | 598 | 598 | 872 |
| Composition | 15 | **525** | 892 | 600 | 891 | 600 | 700 | 886 |
| Composition | 20 | **578** | 918 | 601 | 910 | 614 | 935 | 913 |

## FBTC(B) — Fixed-Budget Target Coverage

| Category | Dim | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Unimodal and simple multimodal | 5 | 1.693 | 1.695 | 1.846 | 1.905 | **2.726** | 1.897 | 1.880 |
| Unimodal and simple multimodal | 10 | 1.556 | 1.631 | 1.589 | 1.567 | **2.301** | 2.027 | 1.543 |
| Unimodal and simple multimodal | 15 | 1.530 | **2.432** | 1.552 | 1.440 | 2.271 | 2.219 | 1.446 |
| Unimodal and simple multimodal | 20 | 1.474 | 2.289 | 1.590 | 1.478 | **2.436** | 1.992 | 1.546 |
| Hybrid | 5 | 1.428 | 2.102 | 2.985 | 2.330 | **3.000** | 2.957 | 2.940 |
| Hybrid | 10 | 0.730 | 0.858 | **1.401** | 0.801 | 1.206 | 1.110 | 1.314 |
| Hybrid | 15 | 0.642 | 0.737 | **0.798** | 0.668 | 0.632 | 0.562 | 0.646 |
| Hybrid | 20 | 0.504 | 0.541 | **0.714** | 0.646 | 0.479 | 0.527 | 0.659 |
| Composition | 5 | **2.408** | 0.919 | 1.898 | 0.831 | 2.102 | 1.296 | 1.019 |
| Composition | 10 | **1.923** | 0.436 | 0.511 | 0.095 | 0.833 | 0.686 | 0.024 |
| Composition | 15 | **0.915** | 0.158 | 0.116 | 0.011 | 0.551 | 0.738 | 0.006 |
| Composition | 20 | **0.364** | 0.024 | 0.059 | 0.007 | 0.034 | 0.021 | 0.000 |

*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: for each function, the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors at that budget. The tables sum per-function FBTC(B) within each class. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-08-26 by analysis/suite_report.py.*
