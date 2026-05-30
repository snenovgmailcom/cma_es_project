# CEC2020 / D=2 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Composition** = F8–F10. Total: 7 functions (Hybrid F5–F7 not defined at D=2, omitted). Budget: 20,000 evaluations. **Bold** = best in row (ties bolded together).

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=4) | mean | 0.642 | 1.66 |   | 0.138 | 5.06 | **0.0986** | 0.476 | 1.33 |
| | median | **0** | 2.02 |   | **0** | 2.33 | **0** | 0.335 | 2.02 |
| | best | **0** | **0** |   | **0** | **0** | **0** | 9.55e-6 | **0** |
| | worst | 2.48 | 2.53 |   | 2.02 | 121 | 2.02 | **1.77** | 2.69 |
| | std | 0.843 | 0.849 |   | 0.446 | 17.3 | **0.411** | 0.568 | 1.15 |
| | FBTC | 3.487 | 3.025 |   | 3.914 | 2.625 | **3.952** | 2.665 | 3.279 |
| **Composition** (n=3) | mean | 7.27e-8 | 40.0 |   | 0.734 | 135 | **0** | 2.73 | 94.8 |
| | median | **0** | **0** |   | **0** | 100 | **0** | 0.950 | 100 |
| | best | **0** | **0** |   | **0** | **0** | **0** | **0** | **0** |
| | worst | 1.65e-6 | 144 |   | 28.9 | 200 | **0** | 26.4 | 200 |
| | std | 2.65e-7 | 51.9 |   | 4.16 | 63.0 | **0** | 4.96 | 86.1 |
| | FBTC | 2.971 | 2.535 |   | 2.964 | 1.674 | **3.000** | 1.722 | 2.040 |
| **SUM** (n=7) | mean | 0.642 | 41.6 |   | 0.872 | 140 | **0.0986** | 3.21 | 96.1 |
| | median | **0** | 2.02 |   | **0** | 102 | **0** | 1.29 | 102 |
| | best | **0** | **0** |   | **0** | **0** | **0** | 9.55e-6 | **0** |
| | worst | 2.48 | 146 |   | 30.9 | 321 | **2.02** | 28.1 | 203 |
| | std | 0.843 | 52.7 |   | 4.60 | 80.3 | **0.411** | 5.52 | 87.3 |
| | FBTC | 6.458 | 5.559 |   | 6.879 | 4.299 | **6.952** | 4.387 | 5.319 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
