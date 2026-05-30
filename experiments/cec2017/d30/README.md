# CEC2017 / D=30 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = unimodal + simple multimodal (F1, F3–F10), **Hybrid** = F11–F20, **Composition** = F21–F30. **F2 is excluded per CEC2017 community convention** — documented numerical instability at high dimensions; the function is omitted from the canonical CEC2017 evaluation suite in current literature (ARRDE 2025, mLSHADE-SPACMA 2024, dmolina/cec2017real reference codebase). Total: 29 functions. Budget: 300,000 evaluations (CEC standard at D=30 = D × 10⁴). Each metric is summed over the functions of the category; the SUM block is the total across all 29 functions. **Bold** = best in row. All metrics: lower is better, except FBTC (higher is better).

| Category | Metric | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Basic** (n=9) | mean | 435 | 2145 | 1046 | **421** | 2491 | 3894 | 1713 |
| | median | 373 | 2173 | 998 | **352** | 2370 | 3708 | 1746 |
| | best | **28.9** | 1079 | 146 | 96.2 | 1625 | 2674 | 1162 |
| | worst | **1162** | 3318 | 2135 | 1230 | 5595 | 8310 | 2154 |
| | std | 283 | 542 | 443 | **253** | 793 | 1028 | 269 |
| | FBTC | 3.116 | 4.348 | **4.620** | 4.449 | 2.104 | 3.125 | 4.298 |
| **Hybrid** (n=10) | mean | 2775 | 696 | 1855 | **75.9** | 3.30e+04 | 4.87e+04 | 445 |
| | median | 2762 | 657 | 1672 | **64.3** | 2.31e+04 | 3.38e+04 | 422 |
| | best | 1096 | 84.7 | 718 | **4.71** | 6367 | 1.25e+04 | 81.2 |
| | worst | 4927 | 1529 | 4395 | **372** | 1.85e+05 | 4.18e+05 | 1134 |
| | std | 897 | 323 | 862 | **74.9** | 3.08e+04 | 5.73e+04 | 242 |
| | FBTC | 0.300 | 1.058 | 0.345 | **2.565** | 0.383 | 0.212 | 1.035 |
| **Composition** (n=10) | mean | 5322 | **5202** | 5818 | 5229 | 6321 | 9070 | 5562 |
| | median | 5288 | **4983** | 5385 | 5249 | 6189 | 8640 | 5575 |
| | best | 4596 | 4790 | **4271** | 4927 | 4840 | 6046 | 4797 |
| | worst | 6451 | 6085 | 1.02e+04 | **5599** | 8903 | 1.39e+04 | 5884 |
| | std | 374 | 443 | 1259 | **159** | 811 | 1827 | 186 |
| | FBTC | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| **SUM** (n=29) | mean | 8532 | 8043 | 8719 | **5726** | 4.18e+04 | 6.17e+04 | 7719 |
| | median | 8424 | 7813 | 8054 | **5666** | 3.17e+04 | 4.61e+04 | 7743 |
| | best | 5721 | 5954 | 5135 | **5028** | 1.28e+04 | 2.12e+04 | 6040 |
| | worst | 1.25e+04 | 1.09e+04 | 1.67e+04 | **7201** | 2.00e+05 | 4.40e+05 | 9172 |
| | std | 1553 | 1307 | 2564 | **487** | 3.24e+04 | 6.02e+04 | 697 |
| | FBTC | 3.416 | 5.406 | 4.965 | **7.014** | 2.487 | 3.337 | 5.334 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*
