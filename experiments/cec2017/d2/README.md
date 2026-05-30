# CEC2017 / D=2 — by-category summary

Sums of per-function metrics, grouped by function class. Budget: 20,000 evaluations (CEC standard at D=2 = D × 10⁴).

**Coverage at D=2:** results available for 10 **Basic** functions (F1–F10) and 6 of the 10 **Composition** functions. The 10 **Hybrid** functions (F11–F20) are not run at this dimension and their rows are omitted. SUM reflects the 16 functions actually present.

**Bold** = best in row (ties bolded together). All metrics: lower is better, except FBTC (higher is better).

| Category | Metric | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| **Basic** (n=10) | mean | 0.687 | 0.162 | 1.71 | 5.22 | **0.111** | 0.449 | 1.36 |
| | median | 8.51e-06 | **0** | 2.33 | 2.33 | **0** | 0.111 | 2.02 |
| | best | **0** | **0** | **0** | **0** | **0** | 3.58e-05 | **0** |
| | worst | 3.84 | 2.33 | 2.84 | 49.9 | 2.33 | **2.27** | 2.69 |
| | std | 1.05 | 0.530 | 0.899 | 9.09 | **0.472** | 0.662 | 1.14 |
| | FBTC | 9.243 | 9.856 | 8.859 | 8.552 | **9.923** | 7.976 | 9.192 |
| **Composition** (n=6) | mean | **1.87e-06** | 0.734 | 89.9 | 236 | 7.84 | 5.20 | 134 |
| | median | 7.64e-07 | **0** | 0.444 | 200 | **0** | 1.18 | 100 |
| | best | 3.64e-08 | **0** | **0** | **0** | **0** | **0** | **0** |
| | worst | **2.36e-05** | 28.9 | 365 | 700 | 100 | 61.1 | 400 |
| | std | **3.71e-06** | 4.16 | 113 | 178 | 26.9 | 11.9 | 149 |
| | FBTC | 5.773 | **5.964** | 4.850 | 3.863 | 5.922 | 3.625 | 4.731 |
| **SUM** (n=16) | mean | **0.687** | 0.896 | 91.6 | 242 | 7.95 | 5.64 | 135 |
| | median | 9.28e-06 | **0** | 2.77 | 202 | **0** | 1.29 | 102 |
| | best | 3.64e-08 | **0** | **0** | **0** | **0** | 3.58e-05 | **0** |
| | worst | **3.84** | 31.2 | 368 | 750 | 102 | 63.4 | 403 |
| | std | **1.05** | 4.69 | 114 | 187 | 27.4 | 12.5 | 150 |
| | FBTC | 15.016 | 15.820 | 13.709 | 12.415 | **15.845** | 11.601 | 13.923 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*
