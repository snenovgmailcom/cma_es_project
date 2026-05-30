# CEC2020 / D=15 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Hybrid** = F5–F7, **Composition** = F8–F10. Total: 10 functions. Budget: 3,000,000 evaluations. **Bold** = best in row.

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=4) | mean | 11.2 | 24.8 |   | 18.8 | 50.8 | 19.2 | **8.82** | 62.0 |
|  | median | **11.7** | 23.1 |   | 18.3 | 19.7 | 15.7 | 15.8 | 26.8 |
|  | best | 1.22 | 0.125 |   | 15.9 | 16.3 | 15.6 | **0** | 15.8 |
|  | worst | 28.3 | 61.2 |   | 33.3 | 155 | 141 | **18.2** | 149 |
|  | std | 6.30 | 16.2 |   | **3.80** | 52.3 | 17.4 | 8.12 | 55.9 |
|  | FBTC | 1.529 | **2.432** |   | 1.552 | 1.440 | 2.271 | 2.219 | 1.446 |
| **Hybrid** (n=3) | mean | 3.60 | 4.30 |   | **1.30** | 5.42 | 23.4 | 17.0 | 4.40 |
|  | median | 3.29 | 1.79 |   | **1.23** | 2.02 | 15.7 | 10.5 | 4.15 |
|  | best | 0.915 | 0.743 |   | **0.127** | 0.878 | 0.531 | 0.927 | 0.436 |
|  | worst | 8.09 | 135 |   | **2.88** | 137 | 166 | 107 | 11.3 |
|  | std | 1.51 | 18.7 |   | **0.533** | 19.5 | 30.5 | 18.9 | 2.22 |
|  | FBTC | 0.642 | 0.737 |   | **0.798** | 0.668 | 0.632 | 0.562 | 0.646 |
| **Composition** (n=3) | mean | **266** | 609 |   | 388 | 882 | 521 | 531 | 840 |
|  | median | **200** | 600 |   | 335 | 886 | 500 | 500 | 853 |
|  | best | **100** | 200 |   | 200 | 800 | 500 | 200 | 600 |
|  | worst | **525** | 892 |   | 600 | 891 | 600 | 700 | 886 |
|  | std | 144 | 155 |   | 123 | **17.9** | 29.7 | 117 | 50.9 |
|  | FBTC | **0.915** | 0.158 |   | 0.116 | 0.011 | 0.551 | 0.738 | 0.006 |
| **SUM** (n=10) | mean | **281** | 638 |   | 408 | 938 | 563 | 557 | 907 |
|  | median | **215** | 625 |   | 354 | 908 | 532 | 526 | 884 |
|  | best | **102** | 201 |   | 216 | 817 | 516 | 201 | 616 |
|  | worst | **561** | 1088 |   | 636 | 1182 | 907 | 825 | 1046 |
|  | std | 152 | 190 |   | 127 | 89.7 | **77.6** | 144 | 109 |
|  | FBTC | 3.086 | 3.327 |   | 2.466 | 2.119 | 3.455 | **3.519** | 2.097 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
