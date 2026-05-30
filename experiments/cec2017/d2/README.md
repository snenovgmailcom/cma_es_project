# CEC2017 / D=2 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1, F3–F10, **Composition** = 6 of F21–F30. Budget: 20,000 evaluations (CEC standard at D=2 = D × 10⁴). F2 is excluded at all dimensions (CEC2017 community convention). The 10 **Hybrid** functions (F11–F20) are not run at D=2; SUM reflects the 15 functions present. **Bold** = best in row.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=9) | mean | 0.687 | 1.71 |   | 0.162 | 5.22 | **0.111** | 0.449 | 1.36 |
|  | median | 8.51e-6 | 2.33 |   | **0** | 2.33 | **0** | 0.111 | 2.02 |
|  | best | **0** | **0** |   | **0** | **0** | **0** | 3.58e-5 | **0** |
|  | worst | 3.84 | 2.84 |   | 2.33 | 49.9 | 2.33 | **2.27** | 2.69 |
|  | std | 1.05 | 0.899 |   | 0.530 | 9.09 | **0.472** | 0.662 | 1.14 |
|  | FBTC | 9.243 | 8.859 |   | 9.856 | 8.552 | **9.923** | 7.976 | 9.192 |
| **Composition** (n=6) | mean | **1.87e-6** | 89.9 |   | 0.734 | 236 | 7.84 | 5.20 | 134 |
|  | median | 7.64e-7 | 0.444 |   | **0** | 200 | **0** | 1.18 | 100 |
|  | best | 3.64e-8 | **0** |   | **0** | **0** | **0** | **0** | **0** |
|  | worst | **2.36e-5** | 365 |   | 28.9 | 700 | 100 | 61.1 | 400 |
|  | std | **3.71e-6** | 113 |   | 4.16 | 178 | 26.9 | 11.9 | 149 |
|  | FBTC | 5.773 | 4.850 |   | **5.964** | 3.863 | 5.922 | 3.625 | 4.731 |
| **SUM** (n=15) | mean | **0.687** | 91.6 |   | 0.896 | 242 | 7.95 | 5.64 | 135 |
|  | median | 9.28e-6 | 2.77 |   | **0** | 202 | **0** | 1.29 | 102 |
|  | best | 3.64e-8 | **0** |   | **0** | **0** | **0** | 3.58e-5 | **0** |
|  | worst | **3.84** | 368 |   | 31.2 | 750 | 102 | 63.4 | 403 |
|  | std | **1.05** | 114 |   | 4.69 | 187 | 27.4 | 12.5 | 150 |
|  | FBTC | 15.016 | 13.709 |   | 15.820 | 12.415 | **15.845** | 11.601 | 13.923 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
