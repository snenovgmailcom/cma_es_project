# CEC2014 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = unimodal + simple multimodal (F1–F16), **Hybrid** = F17–F22, **Composition** = F23–F30. Budget: 100,000 evaluations. **Bold** = best in row. 

| Category | Metric | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Basic** (n=16) | mean | 98.5 | 132 | 133 | **52.7** | 138 | 118 | 83.6 |
| | median | **68.8** | 146 | 118 | 69.8 | 145 | 91.6 | 77.4 |
| | best | 26.8 | 4.37 | 5.67 | **0.539** | 8.82 | 11.4 | 4.22 |
| | worst | 430 | 380 | 582 | **209** | 559 | 463 | 287 |
| | std | 93.0 | 101 | 128 | **53.5** | 122 | 86.0 | 75.4 |
| | FBTC | 6.81 | 8.96 | 7.89 | 8.73 | 8.43 | 7.08 | **9.04** |
| **Hybrid** (n=6) | mean | 40.7 | 6.58 | 88.3 | 3.77 | 39.8 | 16.5 | **2.47** |
| | median | 31.2 | 2.65 | 55.1 | **1.90** | 24.7 | 9.45 | 2.30 |
| | best | 2.45 | 0.020 | 0.79 | 0.022 | **0.013** | 0.28 | 0.023 |
| | worst | 183 | 50.9 | 617 | 35.8 | 187 | 78.6 | **16.0** |
| | std | 37.1 | 12.3 | 115 | 7.79 | 43.6 | 18.5 | **2.66** |
| | FBTC | 1.04 | 1.66 | 0.91 | 1.73 | 1.61 | 1.43 | **1.82** |
| **Composition** (n=8) | mean | 1593 | **1581** | 2008 | 2000 | 1604 | 1798 | 1728 |
| | median | 1696 | 1695 | 2054 | 2054 | 1752 | 1762 | **1693** |
| | best | 895.9 | **895.8** | 1132 | 1573 | 952 | 1559 | 1573 |
| | worst | 1856 | **1769** | 2574 | 2437 | 1883 | 2283 | 2166 |
| | std | 276 | 230 | 314 | 341 | 299 | 174 | **120** |
| | FBTC | 0.209 | 0.273 | 0.035 | 0.112 | **0.539** | 0.134 | 0.199 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*