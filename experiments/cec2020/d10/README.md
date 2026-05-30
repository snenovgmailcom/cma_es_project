# CEC2020 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Hybrid** = F5–F7, **Composition** = F8–F10. Total: 10 functions. Budget: 1,000,000 evaluations (CEC2020 standard for D=10).

**Methodological note.** Columns 1–2 are the CMA-ES family: MSC-CMA and its parent BIPOP-CMA-pycma. The primary comparison is MSC-CMA vs its parent — does the proposed modification improve the underlying CMA-ES design. Columns 3–7 are state-of-the-art DE-family algorithms, included as reference baselines representing the current frontier of evolutionary numerical optimization, not as direct methodological competitors.

Each metric is summed over the functions of the category; the SUM block is the total across all 10 functions. **Bold** = best in row across all 7 algorithms. All metrics: lower is better, except FBTC (higher is better).

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=4) | mean | 8.64 | 17.1 |   | 13.3 | 14.0 | 11.8 | **8.22** | 17.6 |
| | median | **6.92** | 22.7 |   | 11.6 | 11.9 | 10.8 | 10.7 | 15.7 |
| | best | 1.03 | 0.125 |   | 6.16 | 10.5 | 0.0624 | **0** | 10.8 |
| | worst | 20.6 | 36.4 |   | 22.5 | 25.5 | 28.4 | **15.0** | 39.9 |
| | std | 5.15 | 11.5 |   | 3.93 | **3.79** | 7.75 | 4.91 | 5.71 |
| | FBTC | 1.556 | 1.631 |   | 1.589 | 1.567 | **2.301** | 2.027 | 1.543 |
| **Hybrid** (n=3) | mean | 2.08 | 6.06 |   | **0.368** | 3.48 | 1.17 | 0.765 | 0.410 |
| | median | 1.99 | 1.16 |   | 0.357 | 1.18 | 0.484 | 0.678 | **0.250** |
| | best | 0.636 | 0.0593 |   | **0.00333** | 0.0195 | 0.0160 | 0.0292 | 0.0194 |
| | worst | 4.45 | 206 |   | **1.34** | 41.3 | 9.53 | 2.67 | 2.21 |
| | std | 0.813 | 29.3 |   | **0.405** | 6.91 | 1.81 | 0.582 | 0.466 |
| | FBTC | 0.734 | 0.858 |   | **1.401** | 0.801 | 1.206 | 1.110 | 1.314 |
| **Composition** (n=3) | mean | **106** | 512 |   | 205 | 814 | 462 | 244 | 719 |
| | median | **100** | 598 |   | 220 | 825 | 498 | 200 | 798 |
| | best | **0** | 100 |   | 100 | 498 | 100 | 100 | 598 |
| | worst | **200** | 782 |   | 367 | 876 | 598 | 598 | 872 |
| | std | **70.3** | 203 |   | 79.0 | 101 | 149 | 147 | 120 |
| | FBTC | **1.923** | 0.436 |   | 0.511 | 0.095 | 0.833 | 0.686 | 0.024 |
| **SUM** (n=10) | mean | **117** | 535 |   | 219 | 832 | 474 | 253 | 737 |
| | median | **109** | 622 |   | 232 | 838 | 509 | 211 | 814 |
| | best | **1.66** | 100 |   | 106 | 508 | 100 | 100 | 609 |
| | worst | **225** | 1023 |   | 391 | 943 | 636 | 616 | 914 |
| | std | **76.2** | 244 |   | 83.3 | 112 | 158 | 152 | 126 |
| | FBTC | 4.213 | 2.924 |   | 3.502 | 2.464 | **4.339** | 3.822 | 2.881 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*
