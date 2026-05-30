# CEC2017 — cross-dimension summary

Aggregated sums by function category, across dimensions. **Bold** = best in row.

Categories: **Basic** = F1, F3–F10 (F2 excluded), **Hybrid** = F11–F20, **Composition** = F21–F30. Evaluation budgets: 20,000 (D=2), 100,000 (D=10), 300,000 (D=30). Each metric = sum across the functions of the category.

## Median error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 2 | 8.51e-6 | 2.33 |   | **0** | 2.33 | **0** | 0.111 | 2.02 |
| Basic | 10 | 32.8 | 39.4 |   | 43.2 | **16.8** | 138 | 78.1 | 135 |
| Basic | 30 | 373 | 998 |   | 2173 | **352** | 2370 | 3708 | 1746 |
| Hybrid | 10 | 202 | 193 |   | 7.55 | 3.75 | 134 | 54.3 | **1.88** |
| Hybrid | 30 | 2762 | 1672 |   | 657 | **64.3** | 2.31e4 | 3.38e4 | 422 |
| Composition | 2 | 7.64e-7 | 0.444 |   | **0** | 200 | **0** | 1.18 | 100 |
| Composition | 10 | **2150** | 2745 |   | 2317 | 2909 | 2193 | 2733 | 2844 |
| Composition | 30 | 5288 | 5385 |   | **4983** | 5249 | 6189 | 8640 | 5575 |

## Best error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 2 | **0** | **0** |   | **0** | **0** | **0** | 3.58e-5 | **0** |
| Basic | 10 | 3.17 | **1.94** |   | 7.04 | 10.5 | 13.3 | 5.19 | 10.9 |
| Basic | 30 | **28.9** | 146 |   | 1079 | 96.2 | 1625 | 2674 | 1162 |
| Hybrid | 10 | 4.38 | 1.92 |   | 0.0315 | **0.0195** | 4.74 | 0.233 | 0.0426 |
| Hybrid | 30 | 1096 | 718 |   | 84.7 | **4.71** | 6367 | 1.25e4 | 81.2 |
| Composition | 2 | 3.64e-8 | **0** |   | **0** | **0** | **0** | **0** | **0** |
| Composition | 10 | **930** | 1812 |   | 1309 | 2508 | 1170 | 1480 | 2610 |
| Composition | 30 | 4596 | **4271** |   | 4790 | 4927 | 4840 | 6046 | 4797 |

## Worst error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 2 | 3.84 | 2.84 |   | 2.33 | 49.9 | 2.33 | **2.27** | 2.69 |
| Basic | 10 | 264 | 350 |   | 375 | **35.4** | 287 | 340 | 277 |
| Basic | 30 | **1162** | 2135 |   | 3318 | 1230 | 5595 | 8310 | 2154 |
| Hybrid | 10 | 453 | 698 |   | 236 | 156 | 614 | 463 | **10.8** |
| Hybrid | 30 | 4927 | 4395 |   | 1529 | **372** | 1.85e5 | 4.18e5 | 1134 |
| Composition | 2 | **2.36e-5** | 365 |   | 28.9 | 700 | 100 | 61.1 | 400 |
| Composition | 10 | **2697** | 3472 |   | 2783 | 8.21e5 | 3446 | 4231 | 3297 |
| Composition | 30 | 6451 | 1.02e4 |   | 6085 | **5599** | 8903 | 1.39e4 | 5884 |

## FBTC — Fixed-Budget Target Coverage (higher is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 2 | 9.243 | 8.859 |   | 9.856 | 8.552 | **9.923** | 7.976 | 9.192 |
| Basic | 10 | 6.105 | **6.790** |   | 6.662 | 6.785 | 6.355 | 5.682 | 6.603 |
| Basic | 30 | 3.116 | **4.620** |   | 4.348 | 4.449 | 2.104 | 3.125 | 4.298 |
| Hybrid | 10 | 2.347 | 2.372 |   | 4.780 | 4.304 | 4.173 | 3.770 | **5.862** |
| Hybrid | 30 | 0.300 | 0.345 |   | 1.058 | **2.565** | 0.383 | 0.212 | 1.035 |
| Composition | 2 | 5.773 | 4.850 |   | **5.964** | 3.863 | 5.922 | 3.625 | 4.731 |
| Composition | 10 | 1.714 | 0.143 |   | 0.635 | 0.070 | **1.785** | 0.500 | 0.011 |
| Composition | 30 | 0.000 | 0.000 |   | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

For full six-metric breakdowns per dimension, see [`d2/`](d2/) and [`d10/`](d10/) and [`d30/`](d30/).

*FBTC = Fixed-Budget Target Coverage (per-function sum across 51 log-uniform targets in [10²…10⁻⁸]); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
