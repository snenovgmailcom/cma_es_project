# CEC2017 / D=30 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1, F3–F10, **Hybrid** = F11–F20, **Composition** = F21–F30. Total: 29 functions. Budget: 300,000 evaluations. **F2 is excluded at all dimensions** (CEC2017 community convention; documented numerical instability at high dimensions). **Bold** = best in row.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=9) | mean | 435 | 1046 |   | 2145 | **421** | 2491 | 3894 | 1713 |
|  | median | 373 | 998 |   | 2173 | **352** | 2370 | 3708 | 1746 |
|  | best | **28.9** | 146 |   | 1079 | 96.2 | 1625 | 2674 | 1162 |
|  | worst | **1162** | 2135 |   | 3318 | 1230 | 5595 | 8310 | 2154 |
|  | std | 283 | 443 |   | 542 | **253** | 793 | 1028 | 269 |
|  | FBTC | 3.116 | **4.620** |   | 4.348 | 4.449 | 2.104 | 3.125 | 4.298 |
| **Hybrid** (n=10) | mean | 2775 | 1855 |   | 696 | **75.9** | 3.3e4 | 4.87e4 | 445 |
|  | median | 2762 | 1672 |   | 657 | **64.3** | 2.31e4 | 3.38e4 | 422 |
|  | best | 1096 | 718 |   | 84.7 | **4.71** | 6367 | 1.25e4 | 81.2 |
|  | worst | 4927 | 4395 |   | 1529 | **372** | 1.85e5 | 4.18e5 | 1134 |
|  | std | 897 | 862 |   | 323 | **74.9** | 3.08e4 | 5.73e4 | 242 |
|  | FBTC | 0.300 | 0.345 |   | 1.058 | **2.565** | 0.383 | 0.212 | 1.035 |
| **Composition** (n=10) | mean | 5322 | 5818 |   | **5202** | 5229 | 6321 | 9070 | 5562 |
|  | median | 5288 | 5385 |   | **4983** | 5249 | 6189 | 8640 | 5575 |
|  | best | 4596 | **4271** |   | 4790 | 4927 | 4840 | 6046 | 4797 |
|  | worst | 6451 | 1.02e4 |   | 6085 | **5599** | 8903 | 1.39e4 | 5884 |
|  | std | 374 | 1259 |   | 443 | **159** | 811 | 1827 | 186 |
|  | FBTC | 0.000 | 0.000 |   | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| **SUM** (n=29) | mean | 8532 | 8719 |   | 8043 | **5726** | 4.18e4 | 6.17e4 | 7719 |
|  | median | 8424 | 8054 |   | 7813 | **5666** | 3.17e4 | 4.61e4 | 7743 |
|  | best | 5721 | 5135 |   | 5954 | **5028** | 1.28e4 | 2.12e4 | 6040 |
|  | worst | 1.25e4 | 1.67e4 |   | 1.09e4 | **7201** | 2e5 | 4.4e5 | 9172 |
|  | std | 1553 | 2564 |   | 1307 | **487** | 3.24e4 | 6.02e4 | 697 |
|  | FBTC | 3.416 | 4.965 |   | 5.406 | **7.014** | 2.487 | 3.337 | 5.334 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
