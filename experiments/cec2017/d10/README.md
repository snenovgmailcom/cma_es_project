# CEC2017 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = unimodal + simple multimodal (F1–F10), **Hybrid** = F11–F20, **Composition** = F21–F30 (equal 10/10/10 partition, unlike CEC2014). Budget: 100,000 evaluations. Each metric is summed over the functions of the category; the SUM block at the bottom is the total across all 30 functions. **Bold** = best in row. All metrics: lower is better, except FBTC (higher is better).

| Category | Metric | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Basic** (n=10) | mean | 60.7 | 108 | 81.9 | **17.2** | 113 | 106 | 97.8 |
| | median | 32.8 | 43.2 | 39.4 | **16.8** | 138 | 78.1 | 135 |
| | best | 3.17 | 7.04 | **1.94** | 10.5 | 13.3 | 5.19 | 10.9 |
| | worst | 264 | 375 | 350 | **35.4** | 287 | 340 | 277 |
| | std | 66.8 | 105 | 85.9 | **6.74** | 85.3 | 86.8 | 77.5 |
| | FBTC | 6.105 | 6.662 | **6.790** | 6.785 | 6.355 | 5.682 | 6.603 |
| **Hybrid** (n=10) | mean | 174 | 30.2 | 166 | 9.92 | 162 | 85.5 | **2.43** |
| | median | 202 | 7.55 | 193 | 3.75 | 134 | 54.3 | **1.88** |
| | best | 4.38 | 0.0315 | 1.92 | **0.0195** | 4.74 | 0.233 | 0.0426 |
| | worst | 453 | 236 | 698 | 156 | 614 | 463 | **10.8** |
| | std | 127 | 62.3 | 158 | 26.7 | 147 | 94.7 | **2.79** |
| | FBTC | 2.347 | 4.780 | 2.372 | 4.304 | 4.173 | 3.770 | **5.862** |
| **Composition** (n=10) | mean | **1891** | 2183 | 2754 | 3.50e+04 | 2292 | 2637 | 2799 |
| | median | **2150** | 2317 | 2745 | 2909 | 2193 | 2733 | 2844 |
| | best | **930** | 1309 | 1812 | 2508 | 1170 | 1480 | 2610 |
| | worst | **2697** | 2783 | 3472 | 8.21e+05 | 3446 | 4231 | 3297 |
| | std | 563 | 455 | 445 | 1.59e+05 | 662 | 720 | **205** |
| | FBTC | 1.714 | 0.635 | 0.143 | 0.070 | **1.785** | 0.500 | 0.011 |
| **SUM** (n=30) | mean | **2125** | 2322 | 3002 | 3.50e+04 | 2566 | 2828 | 2899 |
| | median | 2385 | **2368** | 2977 | 2930 | 2465 | 2865 | 2981 |
| | best | **937** | 1316 | 1816 | 2518 | 1188 | 1486 | 2621 |
| | worst | 3414 | **3394** | 4520 | 8.21e+05 | 4348 | 5034 | 3585 |
| | std | 757 | 622 | 689 | 1.59e+05 | 894 | 901 | **285** |
| | FBTC | 10.166 | 12.077 | 9.306 | 11.159 | 12.313 | 9.952 | **12.476** |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*
