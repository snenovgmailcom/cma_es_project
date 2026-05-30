# CEC2020 — cross-dimension summary

Aggregated sums by function category, across dimensions. **Bold** = best in row.

Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Hybrid** = F5–F7, **Composition** = F8–F10. Evaluation budgets: 50,000 (D=5), 1,000,000 (D=10), 3,000,000 (D=15), 10,000,000 (D=20). Each metric = sum across the functions of the category.

## Median error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 5 | 4.14 | 8.66 |   | 5.77 | 5.87 | **1.77** | 5.84 | 5.50 |
| Basic | 10 | **6.92** | 22.7 |   | 11.6 | 11.9 | 10.8 | 10.7 | 15.7 |
| Basic | 15 | **11.7** | 23.1 |   | 18.3 | 19.7 | 15.7 | 15.8 | 26.8 |
| Basic | 20 | **13.1** | 17.8 |   | 21.0 | 24.1 | 20.5 | 20.6 | 23.6 |
| Hybrid | 5 | 0.542 | 0.624 |   | **0** | **0** | **0** | **0** | **0** |
| Hybrid | 10 | 1.99 | 1.16 |   | 0.357 | 1.18 | 0.484 | 0.678 | **0.250** |
| Hybrid | 15 | 3.29 | 1.79 |   | **1.23** | 2.02 | 15.7 | 10.5 | 4.15 |
| Hybrid | 20 | 11.6 | 8.40 |   | **1.48** | 2.00 | 135 | 69.5 | 7.43 |
| Composition | 5 | **0** | 447 |   | 100 | 447 | 300 | 100 | 447 |
| Composition | 10 | **100** | 598 |   | 220 | 825 | 498 | 200 | 798 |
| Composition | 15 | **200** | 600 |   | 335 | 886 | 500 | 500 | 853 |
| Composition | 20 | **540** | 714 |   | 581 | 891 | 599 | 911 | 907 |

## Best error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 5 | 0.125 | 1.12 |   | 0.613 | **0** | **0** | **0** | 0.613 |
| Basic | 10 | 1.03 | 0.125 |   | 6.16 | 10.5 | 0.0624 | **0** | 10.8 |
| Basic | 15 | 1.22 | 0.125 |   | 15.9 | 16.3 | 15.6 | **0** | 15.8 |
| Basic | 20 | 3.37 | 6.15 |   | 20.7 | 21.3 | 20.4 | **0.0310** | 20.7 |
| Hybrid | 5 | 5.5e-7 | **0** |   | **0** | **0** | **0** | **0** | **0** |
| Hybrid | 10 | 0.636 | 0.0593 |   | **3.33e-3** | 0.0195 | 0.0160 | 0.0292 | 0.0194 |
| Hybrid | 15 | 0.915 | 0.743 |   | **0.127** | 0.878 | 0.531 | 0.927 | 0.436 |
| Hybrid | 20 | 2.77 | 2.32 |   | 0.567 | 1.06 | **0.426** | 20.6 | 1.67 |
| Composition | 5 | **0** | 100 |   | **0** | 400 | **0** | **0** | 400 |
| Composition | 10 | **0** | 100 |   | 100 | 498 | 100 | 100 | 598 |
| Composition | 15 | **100** | 200 |   | 200 | 800 | 500 | 200 | 600 |
| Composition | 20 | 399 | 499 |   | **131** | 814 | 445 | 499 | 879 |

## Worst error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 5 | 165 | 132 |   | 125 | 452 | **12.1** | 37.0 | 12.9 |
| Basic | 10 | 20.6 | 36.4 |   | 22.5 | 25.5 | 28.4 | **15.0** | 39.9 |
| Basic | 15 | 28.3 | 61.2 |   | 33.3 | 155 | 141 | **18.2** | 149 |
| Basic | 20 | 22.0 | 39.5 |   | 23.0 | 32.2 | 23.9 | **20.8** | 27.9 |
| Hybrid | 5 | 7.38 | 3.11 |   | 0.624 | 139 | **0** | 0.624 | 0.624 |
| Hybrid | 10 | 4.45 | 206 |   | **1.34** | 41.3 | 9.53 | 2.67 | 2.21 |
| Hybrid | 15 | 8.09 | 135 |   | **2.88** | 137 | 166 | 107 | 11.3 |
| Hybrid | 20 | 17.6 | 508 |   | **5.82** | 25.0 | 742 | 250 | 28.8 |
| Composition | 5 | **116** | 691 |   | 418 | 648 | 401 | 414 | 447 |
| Composition | 10 | **200** | 782 |   | 367 | 876 | 598 | 598 | 872 |
| Composition | 15 | **525** | 892 |   | 600 | 891 | 600 | 700 | 886 |
| Composition | 20 | **578** | 918 |   | 601 | 910 | 614 | 935 | 913 |

## FBTC — Fixed-Budget Target Coverage (higher is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 5 | 1.693 | 1.695 |   | 1.846 | 1.905 | **2.726** | 1.897 | 1.880 |
| Basic | 10 | 1.556 | 1.631 |   | 1.589 | 1.567 | **2.301** | 2.027 | 1.543 |
| Basic | 15 | 1.529 | **2.432** |   | 1.552 | 1.440 | 2.271 | 2.219 | 1.446 |
| Basic | 20 | 1.474 | 2.289 |   | 1.590 | 1.478 | **2.436** | 1.992 | 1.546 |
| Hybrid | 5 | 1.428 | 2.102 |   | 2.985 | 2.330 | **3.000** | 2.957 | 2.940 |
| Hybrid | 10 | 0.734 | 0.858 |   | **1.401** | 0.801 | 1.206 | 1.110 | 1.314 |
| Hybrid | 15 | 0.642 | 0.737 |   | **0.798** | 0.668 | 0.632 | 0.562 | 0.646 |
| Hybrid | 20 | 0.504 | 0.541 |   | **0.714** | 0.646 | 0.479 | 0.527 | 0.659 |
| Composition | 5 | **2.373** | 0.919 |   | 1.898 | 0.831 | 2.102 | 1.296 | 1.019 |
| Composition | 10 | **1.923** | 0.436 |   | 0.511 | 0.095 | 0.833 | 0.686 | 0.024 |
| Composition | 15 | **0.915** | 0.158 |   | 0.116 | 0.011 | 0.551 | 0.738 | 0.006 |
| Composition | 20 | **0.364** | 0.024 |   | 0.059 | 0.007 | 0.034 | 0.021 | 0.000 |

For full six-metric breakdowns per dimension, see [`d5/`](d5/) and [`d10/`](d10/) and [`d15/`](d15/) and [`d20/`](d20/).

*FBTC = Fixed-Budget Target Coverage (per-function sum across 51 log-uniform targets in [10²…10⁻⁸]); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
