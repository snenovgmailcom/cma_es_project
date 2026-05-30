# CEC2014 / D=30 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = unimodal + simple multimodal (F1–F16), **Hybrid** = F17–F22, **Composition** = F23–F30. Total: 30 functions. Budget: 300,000 evaluations. **Bold** = best in row.

⚠ NLSHADE-RSP and j2020 contain non-convergent runs that inflate their sums on Basic; values shown verbatim.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=16) | mean | 507 | 1390 |   | 1890 | **457** | 3.71e5 | 3.97e5 | 1410 |
|  | median | 374 | 1280 |   | 1740 | **352** | 2.28e5 | 3.03e5 | 1410 |
|  | best | 73.6 | 343 |   | 936 | **34.2** | 5.97e4 | 1.12e5 | 857 |
|  | worst | **1410** | 3600 |   | 3770 | 1770 | 4.45e6 | 1.95e6 | 1880 |
|  | std | 339 | 686 |   | 624 | 378 | 6.04e5 | 3.51e5 | **203** |
|  | FBTC | 4.780 | 6.960 |   | 7.950 | 7.850 | 5.760 | 5.610 | **8.460** |
| **Hybrid** (n=6) | mean | 1870 | 1840 |   | 166 | **89.2** | 2.11e4 | 3600 | 145 |
|  | median | 1810 | 1810 |   | 114 | **43.9** | 1.39e4 | 3370 | 111 |
|  | best | 1170 | 321 |   | 43.7 | **26.0** | 1250 | 1640 | 62.9 |
|  | worst | 3190 | 3660 |   | 608 | **194** | 1.48e5 | 8670 | 289 |
|  | std | 491 | 792 |   | 143 | **69.2** | 2.57e4 | 1230 | 74.0 |
|  | FBTC | 0.263 | 0.234 |   | 0.749 | **0.967** | 0.288 | 0.223 | 0.705 |
| **Composition** (n=8) | mean | 4350 | 4880 |   | 3600 | **2360** | 4620 | 5720 | 2510 |
|  | median | 4330 | 5010 |   | 3560 | **2330** | 4620 | 5510 | 2500 |
|  | best | 3350 | 3330 |   | 2970 | **2170** | 3140 | 4210 | 2360 |
|  | worst | 5290 | 7020 |   | 4970 | **2590** | 6130 | 8250 | 2800 |
|  | std | 427 | 910 |   | 407 | 110 | 601 | 1110 | **98.7** |
|  | FBTC | 0.000 | 0.000 |   | 0.000 | 0.000 | **0.007** | 0.000 | 0.000 |
| **SUM** (n=30) | mean | 6728 | 8113 |   | 5660 | **2905** | 3.97e5 | 4.06e5 | 4060 |
|  | median | 6514 | 8109 |   | 5413 | **2730** | 2.46e5 | 3.12e5 | 4019 |
|  | best | 4593 | 3989 |   | 3949 | **2228** | 6.41e4 | 1.17e5 | 3275 |
|  | worst | 9890 | 1.43e4 |   | 9347 | **4556** | 4.6e6 | 1.97e6 | 4969 |
|  | std | 1269 | 2411 |   | 1186 | 562 | 6.36e5 | 3.57e5 | **379** |
|  | FBTC | 5.046 | 7.195 |   | 8.701 | 8.815 | 6.058 | 5.832 | **9.168** |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
