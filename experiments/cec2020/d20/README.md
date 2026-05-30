# CEC2020 / D=20 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Hybrid** = F5–F7, **Composition** = F8–F10. Total: 10 functions. Budget: 10,000,000 evaluations. **Bold** = best in row.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=4) | mean | **13.8** | 17.9 |   | 21.3 | 24.0 | 20.7 | 16.5 | 23.3 |
|  | median | **13.1** | 17.8 |   | 21.0 | 24.1 | 20.5 | 20.6 | 23.6 |
|  | best | 3.37 | 6.15 |   | 20.7 | 21.3 | 20.4 | **0.0310** | 20.7 |
|  | worst | 22.0 | 39.5 |   | 23.0 | 32.2 | 23.9 | **20.8** | 27.9 |
|  | std | 3.47 | 5.73 |   | **0.774** | 2.28 | 0.872 | 7.95 | 1.85 |
|  | FBTC | 1.474 | 2.289 |   | 1.590 | 1.478 | **2.436** | 1.992 | 1.546 |
| **Hybrid** (n=3) | mean | 9.82 | 23.3 |   | **1.82** | 4.86 | 152 | 95.2 | 8.30 |
|  | median | 11.6 | 8.40 |   | **1.48** | 2.00 | 135 | 69.5 | 7.43 |
|  | best | 2.77 | 2.32 |   | 0.567 | 1.06 | **0.426** | 20.6 | 1.67 |
|  | worst | 17.6 | 508 |   | **5.82** | 25.0 | 742 | 250 | 28.8 |
|  | std | 4.72 | 78.0 |   | **0.935** | 5.39 | 166 | 66.0 | 5.23 |
|  | FBTC | 0.504 | 0.541 |   | **0.714** | 0.646 | 0.479 | 0.527 | 0.659 |
| **Composition** (n=3) | mean | **533** | 724 |   | 567 | 874 | 593 | 853 | 905 |
|  | median | **540** | 714 |   | 581 | 891 | 599 | 911 | 907 |
|  | best | 399 | 499 |   | **131** | 814 | 445 | 499 | 879 |
|  | worst | **578** | 918 |   | 601 | 910 | 614 | 935 | 913 |
|  | std | 41.8 | 144 |   | 83.0 | 36.0 | 35.1 | 132 | **6.11** |
|  | FBTC | **0.364** | 0.024 |   | 0.059 | 0.007 | 0.034 | 0.021 | 0.000 |
| **SUM** (n=10) | mean | **557** | 765 |   | 590 | 902 | 766 | 965 | 936 |
|  | median | **564** | 740 |   | 604 | 917 | 755 | 1000 | 938 |
|  | best | 405 | 508 |   | **152** | 836 | 466 | 520 | 901 |
|  | worst | **618** | 1470 |   | 630 | 968 | 1380 | 1210 | 969 |
|  | std | 50.0 | 228 |   | 84.7 | 43.7 | 202 | 206 | **13.2** |
|  | FBTC | 2.343 | 2.854 |   | 2.363 | 2.131 | **2.948** | 2.539 | 2.205 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
