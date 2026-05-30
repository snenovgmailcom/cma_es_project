# CEC2020 / D=5 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Hybrid** = F5–F7, **Composition** = F8–F10. Total: 10 functions. Budget: 50,000 evaluations (CEC2020 standard for D=5 = 5 × 10⁴).

**Methodological note.** Columns 1–2 are the CMA-ES family: MSC-CMA and its parent BIPOP-CMA-pycma. The primary comparison is MSC-CMA vs its parent — does the proposed modification improve the underlying CMA-ES design. Columns 3–7 are state-of-the-art DE-family algorithms, included as reference baselines representing the current frontier of evolutionary numerical optimization, not as direct methodological competitors.

Each metric is summed over the functions of the category; the SUM block is the total across all 10 functions. **Bold** = best in row across all 7 algorithms (ties bolded together). All metrics: lower is better, except FBTC (higher is better).

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=4) | mean | 25.1 | 18.7 |   | 14.3 | 14.9 | **3.00** | 9.25 | 5.64 |
| | median | 4.14 | 8.66 |   | 5.77 | 5.87 | **1.77** | 5.84 | 5.50 |
| | best | 0.125 | 1.12 |   | 0.613 | **0** | **0** | **0** | 0.613 |
| | worst | 165 | 132 |   | 125 | 452 | **12.1** | 37.0 | 12.9 |
| | std | 42.7 | 28.2 |   | 29.0 | 62.8 | 3.34 | 8.07 | **1.64** |
| | FBTC | 1.693 | 1.695 |   | 1.846 | 1.905 | **2.726** | 1.897 | 1.880 |
| **Hybrid** (n=3) | mean | 1.03 | 0.754 |   | 0.0122 | 5.62 | **0** | 0.0131 | 0.0490 |
| | median | 0.542 | 0.624 |   | **0** | **0** | **0** | **0** | **0** |
| | best | 5.50e-07 | **0** |   | **0** | **0** | **0** | **0** | **0** |
| | worst | 7.38 | 3.11 |   | 0.624 | 139 | **0** | 0.624 | 0.624 |
| | std | 1.39 | 0.956 |   | 0.0865 | 26.1 | **0** | 0.0866 | 0.168 |
| | FBTC | 1.428 | 2.102 |   | 2.985 | 2.330 | **3.000** | 2.957 | 2.940 |
| **Composition** (n=3) | mean | **48.7** | 372 |   | 145 | 462 | 224 | 180 | 446 |
| | median | **0** | 447 |   | 100 | 447 | 300 | 100 | 447 |
| | best | **0** | 100 |   | **0** | 400 | **0** | **0** | 400 |
| | worst | **116** | 691 |   | 418 | 648 | 401 | 414 | 447 |
| | std | 53.5 | 164 |   | 125 | 57.4 | 134 | 142 | **6.57** |
| | FBTC | **2.373** | 0.919 |   | 1.898 | 0.831 | 2.102 | 1.296 | 1.019 |
| **SUM** (n=10) | mean | **74.8** | 391 |   | 159 | 482 | 227 | 189 | 452 |
| | median | **4.68** | 457 |   | 106 | 453 | 302 | 106 | 453 |
| | best | 0.125 | 101 |   | 0.613 | 400 | **0** | **0** | 401 |
| | worst | **288** | 826 |   | 544 | 1239 | 413 | 452 | 461 |
| | std | 97.6 | 193 |   | 154 | 146 | 137 | 150 | **8.38** |
| | FBTC | 5.494 | 4.717 |   | 6.729 | 5.066 | **7.828** | 6.150 | 5.839 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*
