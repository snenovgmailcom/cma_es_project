# CEC2014 / D=30 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = unimodal + simple multimodal (F1–F16), **Hybrid** = F17–F22, **Composition** = F23–F30. Budget: 300,000 evaluations. **Bold** = best in row. 

⚠ NLSHADE-RSP and j2020 contain non-convergent runs that inflate their sums on Basic; values shown verbatim.

| Category | Metric | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Basic** (n=16) | mean | 5.07e+02 | 1.89e+03 | 1.39e+03 | **4.57e+02** | 3.71e+05 | 3.97e+05 | 1.41e+03 |
| | median | 3.74e+02 | 1.74e+03 | 1.28e+03 | **3.52e+02** | 2.28e+05 | 3.03e+05 | 1.41e+03 |
| | best | 7.36e+01 | 9.36e+02 | 3.43e+02 | **3.42e+01** | 5.97e+04 | 1.12e+05 | 8.57e+02 |
| | worst | **1.41e+03** | 3.77e+03 | 3.60e+03 | 1.77e+03 | 4.45e+06 | 1.95e+06 | 1.88e+03 |
| | std | 3.39e+02 | 6.24e+02 | 6.86e+02 | 3.78e+02 | 6.04e+05 | 3.51e+05 | **2.03e+02** |
| | FBTC | 4.78 | 7.95 | 6.96 | 7.85 | 5.76 | 5.61 | **8.46** |
| **Hybrid** (n=6) | mean | 1.87e+03 | 1.66e+02 | 1.84e+03 | **8.92e+01** | 2.11e+04 | 3.60e+03 | 1.45e+02 |
| | median | 1.81e+03 | 1.14e+02 | 1.81e+03 | **4.39e+01** | 1.39e+04 | 3.37e+03 | 1.11e+02 |
| | best | 1.17e+03 | 4.37e+01 | 3.21e+02 | **2.60e+01** | 1.25e+03 | 1.64e+03 | 6.29e+01 |
| | worst | 3.19e+03 | 6.08e+02 | 3.66e+03 | **1.94e+02** | 1.48e+05 | 8.67e+03 | 2.89e+02 |
| | std | 4.91e+02 | 1.43e+02 | 7.92e+02 | **6.92e+01** | 2.57e+04 | 1.23e+03 | 7.40e+01 |
| | FBTC | 0.263 | 0.749 | 0.234 | **0.967** | 0.288 | 0.223 | 0.705 |
| **Composition** (n=8) | mean | 4.35e+03 | 3.60e+03 | 4.88e+03 | **2.36e+03** | 4.62e+03 | 5.72e+03 | 2.51e+03 |
| | median | 4.33e+03 | 3.56e+03 | 5.01e+03 | **2.33e+03** | 4.62e+03 | 5.51e+03 | 2.50e+03 |
| | best | 3.35e+03 | 2.97e+03 | 3.33e+03 | **2.17e+03** | 3.14e+03 | 4.21e+03 | 2.36e+03 |
| | worst | 5.29e+03 | 4.97e+03 | 7.02e+03 | **2.59e+03** | 6.13e+03 | 8.25e+03 | 2.80e+03 |
| | std | 4.27e+02 | 4.07e+02 | 9.10e+02 | 1.10e+02 | 6.01e+02 | 1.11e+03 | **9.87e+01** |
| | FBTC | 0.000 | 0.000 | 0.000 | 0.000 | **0.007** | 0.000 | 0.000 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*