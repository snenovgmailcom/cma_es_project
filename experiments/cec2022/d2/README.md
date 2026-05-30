# CEC2022 / D=2 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F5 (1 unimodal + 4 basic multimodal), **Composition** = F9–F12. Total: 9 functions (Hybrid F6–F8 not defined at D=2, omitted). Budget: 20,000 evaluations. **Bold** = best in row (ties bolded together).

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=5) | mean | 7.17e-3 | 0.0101 |   | **0** | 0.0195 | **0** | 0.0226 | **0** |
| | median | 8.51e-6 | **0** |   | **0** | **0** | **0** | 7.46e-6 | **0** |
| | best | **0** | **0** |   | **0** | **0** | **0** | **0** | **0** |
| | worst | 0.363 | 0.187 |   | **0** | 0.995 | **0** | 0.370 | **0** |
| | std | 0.0503 | 0.0405 |   | **0** | 0.138 | **0** | 0.0703 | **0** |
| | FBTC | 4.799 | 4.958 |   | **5.000** | 4.978 | **5.000** | 4.502 | **5.000** |
| **Composition** (n=4) | mean | 0.0635 | 44.6 |   | **0.0184** | 130 | 5.88 | 0.134 | 78.5 |
| | median | 6.04e-7 | 16.8 |   | **0** | 100 | **0** | 0.0269 | 100 |
| | best | 2.03e-8 | **0** |   | **0** | 0.625 | **0** | **0** | **0** |
| | worst | **0.332** | 167 |   | 0.625 | 300 | 100 | 0.955 | 300 |
| | std | 0.129 | 58.1 |   | **0.0960** | 112 | 23.5 | 0.244 | 94.2 |
| | FBTC | 3.674 | 2.819 |   | **3.970** | 2.782 | 3.941 | 2.586 | 3.201 |
| **SUM** (n=9) | mean | 0.0707 | 44.6 |   | **0.0184** | 130 | 5.88 | 0.156 | 78.5 |
| | median | 9.12e-6 | 16.8 |   | **0** | 100 | **0** | 0.0269 | 100 |
| | best | 2.03e-8 | **0** |   | **0** | 0.625 | **0** | **0** | **0** |
| | worst | 0.695 | 167 |   | **0.625** | 301 | 100 | 1.32 | 300 |
| | std | 0.179 | 58.1 |   | **0.0960** | 112 | 23.5 | 0.314 | 94.2 |
| | FBTC | 8.473 | 7.777 |   | **8.970** | 7.760 | 8.941 | 7.088 | 8.201 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
