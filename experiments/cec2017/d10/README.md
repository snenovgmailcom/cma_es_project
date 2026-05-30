# CEC2017 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1, F3–F10, **Hybrid** = F11–F20, **Composition** = F21–F30 (equal partition, unlike CEC2014). Total: 29 functions. Budget: 100,000 evaluations. F2 is excluded at all dimensions (CEC2017 community convention). **Bold** = best in row.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=9) | mean | 60.7 | 81.9 |   | 108 | **17.2** | 113 | 106 | 97.8 |
|  | median | 32.8 | 39.4 |   | 43.2 | **16.8** | 138 | 78.1 | 135 |
|  | best | 3.17 | **1.94** |   | 7.04 | 10.5 | 13.3 | 5.19 | 10.9 |
|  | worst | 264 | 350 |   | 375 | **35.4** | 287 | 340 | 277 |
|  | std | 66.8 | 85.9 |   | 105 | **6.74** | 85.3 | 86.8 | 77.5 |
|  | FBTC | 6.105 | **6.790** |   | 6.662 | 6.785 | 6.355 | 5.682 | 6.603 |
| **Hybrid** (n=10) | mean | 174 | 166 |   | 30.2 | 9.92 | 162 | 85.5 | **2.43** |
|  | median | 202 | 193 |   | 7.55 | 3.75 | 134 | 54.3 | **1.88** |
|  | best | 4.38 | 1.92 |   | 0.0315 | **0.0195** | 4.74 | 0.233 | 0.0426 |
|  | worst | 453 | 698 |   | 236 | 156 | 614 | 463 | **10.8** |
|  | std | 127 | 158 |   | 62.3 | 26.7 | 147 | 94.7 | **2.79** |
|  | FBTC | 2.347 | 2.372 |   | 4.780 | 4.304 | 4.173 | 3.770 | **5.862** |
| **Composition** (n=10) | mean | **1891** | 2754 |   | 2183 | 3.5e4 | 2292 | 2637 | 2799 |
|  | median | **2150** | 2745 |   | 2317 | 2909 | 2193 | 2733 | 2844 |
|  | best | **930** | 1812 |   | 1309 | 2508 | 1170 | 1480 | 2610 |
|  | worst | **2697** | 3472 |   | 2783 | 8.21e5 | 3446 | 4231 | 3297 |
|  | std | 563 | 445 |   | 455 | 1.59e5 | 662 | 720 | **205** |
|  | FBTC | 1.714 | 0.143 |   | 0.635 | 0.070 | **1.785** | 0.500 | 0.011 |
| **SUM** (n=29) | mean | **2125** | 3002 |   | 2322 | 3.5e4 | 2566 | 2828 | 2899 |
|  | median | 2385 | 2977 |   | **2368** | 2930 | 2465 | 2865 | 2981 |
|  | best | **937** | 1816 |   | 1316 | 2518 | 1188 | 1486 | 2621 |
|  | worst | 3414 | 4520 |   | **3394** | 8.21e5 | 4348 | 5034 | 3585 |
|  | std | 757 | 689 |   | 622 | 1.59e5 | 894 | 901 | **285** |
|  | FBTC | 10.166 | 9.306 |   | 12.077 | 11.159 | 12.313 | 9.952 | **12.476** |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
