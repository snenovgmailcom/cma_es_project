# CEC2022 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F5 (1 unimodal + 4 basic multimodal), **Hybrid** = F6–F8, **Composition** = F9–F12. Total: 12 functions. Budget: 200,000 evaluations. **Bold** = best in row.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=5) | mean | **0.435** | 2.41 |   | 1.31 | 1.60 | 11.7 | 6.20 | 2.54 |
|  | median | 3.74e-3 | 3.8e-5 |   | 0.995 | **0** | 11.0 | 5.97 | 1.99 |
|  | best | 7.68e-5 | **0** |   | **0** | **0** | 5.97 | 2.01 | 0.995 |
|  | worst | 7.11 | 5.98 |   | **2.99** | 10.9 | 18.9 | 14.1 | 7.97 |
|  | std | 1.26 | 2.70 |   | **0.800** | 2.82 | 3.45 | 2.42 | 1.63 |
|  | FBTC | 4.039 | 4.259 |   | 4.300 | **4.546** | 4.092 | 3.790 | 4.122 |
| **Hybrid** (n=3) | mean | 7.59 | 17.3 |   | 0.523 | 6.13 | 0.534 | 1.28 | **0.412** |
|  | median | 2.04 | 3.18 |   | 0.483 | 0.625 | 0.382 | 0.498 | **0.314** |
|  | best | 0.143 | 0.108 |   | **0.0382** | 0.0700 | 0.0559 | 0.0624 | 0.0512 |
|  | worst | 42.8 | 44.2 |   | **1.94** | 23.3 | 2.50 | 22.0 | 2.08 |
|  | std | 13.7 | 19.3 |   | 0.498 | 9.33 | 0.542 | 3.21 | **0.433** |
|  | FBTC | 0.864 | 0.747 |   | 1.546 | 1.141 | 1.545 | **1.569** | 1.465 |
| **Composition** (n=4) | mean | 421 | 480 |   | 438 | 494 | **385** | 387 | 494 |
|  | median | 423 | 493 |   | 489 | 494 | 393 | **391** | 494 |
|  | best | 262 | 399 |   | **159** | 492 | 159 | 259 | 492 |
|  | worst | 494 | 494 |   | 492 | 494 | 420 | **393** | 494 |
|  | std | 88.1 | 29.1 |   | 101 | **0.374** | 49.3 | 19.2 | 0.626 |
|  | FBTC | 1.071 | 1.013 |   | 1.100 | 1.000 | **1.665** | 1.371 | 1.000 |
| **SUM** (n=12) | mean | 428 | 500 |   | 440 | 502 | 397 | **395** | 497 |
|  | median | 425 | 496 |   | 490 | 495 | 404 | **397** | 497 |
|  | best | 262 | 399 |   | **159** | 492 | 165 | 261 | 493 |
|  | worst | 544 | 544 |   | 497 | 529 | 441 | **429** | 504 |
|  | std | 103 | 51.1 |   | 103 | 12.5 | 53.3 | 24.8 | **2.69** |
|  | FBTC | 5.974 | 6.020 |   | 6.945 | 6.687 | **7.302** | 6.731 | 6.587 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
