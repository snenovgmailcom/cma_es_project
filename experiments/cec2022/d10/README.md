# CEC2022 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Budget: 200,000 evaluations. **Bold** = best in row.

## Ranking across metrics (budget 200K)

Parallel-coordinate rank of all seven algorithms on four aggregate metrics (worst-SUM, median-SUM, FBTC, best-SUM), per function class. Each line is one algorithm; for every axis the best value is at the top. MSC-CMA in red.

<table>
<tr>
<td><img src="rank_basic.png" width="320" alt="USM"></td>
<td><img src="rank_hybrid.png" width="320" alt="Hybrid"></td>
<td><img src="rank_composition.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">USM</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

*USM = unimodal and simple multimodal, per the CEC2022 definition.*

## Budget scaling

FBTC by budget, monotone envelope (running maximum over budgets). Higher is better. The budget axis is per class: a budget is shown only where all seven algorithms cover the whole class. MSC-CMA in red.

<table>
<tr>
<td><img src="budget_basic.png" width="320" alt="USM"></td>
<td><img src="budget_hybrid.png" width="320" alt="Hybrid"></td>
<td><img src="budget_composition.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">USM</td>
<td align="center">Hybrid</td>
<td align="center">Composition</td>
</tr>
</table>

## Summary table

| Category | Metric | MSC-CMA-ES | BIPOP-CMA-ES |  | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **USM** (n=5) | mean | **0.435** | 2.41 |    | 1.31 | 1.6 | 11.7 | 6.2 | 2.54 |
|  | median | 0.00372 | 3.8e-5 |    | 0.995 | **0** | 11 | 5.97 | 1.99 |
|  | best | 7.7e-5 | **0** |    | **0** | **0** | 5.97 | 2.01 | 0.995 |
|  | worst | 7.11 | 5.98 |    | **2.98** | 10.9 | 18.9 | 14.1 | 7.97 |
|  | std | 1.27 | 2.73 |    | **0.808** | 2.85 | 3.49 | 2.44 | 1.65 |
|  | FBTC | 4.043 | 4.259 |    | 4.300 | **4.546** | 4.092 | 3.790 | 4.122 |
| **Hybrid** (n=3) | mean | 7.58 | 17.3 |    | 0.523 | 6.13 | 0.534 | 1.28 | **0.412** |
|  | median | 2.04 | 3.18 |    | 0.483 | 0.625 | 0.382 | 0.498 | **0.314** |
|  | best | 0.143 | 0.108 |    | **0.0382** | 0.07 | 0.0559 | 0.0624 | 0.0511 |
|  | worst | 42.8 | 44.2 |    | **1.94** | 23.3 | 2.5 | 22 | 2.08 |
|  | std | 13.8 | 19.5 |    | 0.503 | 9.42 | 0.547 | 3.24 | **0.438** |
|  | FBTC | 0.864 | 0.747 |    | 1.546 | 1.141 | 1.545 | **1.569** | 1.465 |
| **Composition** (n=4) | mean | 421 | 480 |    | 438 | 494 | **385** | 387 | 494 |
|  | median | 423 | 493 |    | 489 | 494 | 393 | **391** | 494 |
|  | best | 262 | 399 |    | **159** | 492 | 159 | 259 | 492 |
|  | worst | 494 | 494 |    | 492 | 494 | 420 | **393** | 494 |
|  | std | 89 | 29.4 |    | 102 | **0.378** | 49.8 | 19.4 | 0.632 |
|  | FBTC | 1.071 | 1.013 |    | 1.100 | 1.000 | **1.665** | 1.371 | 1.000 |
| **SUM** (n=12) | mean | 429 | 500 |    | 440 | 502 | 397 | **395** | 497 |
|  | median | 425 | 496 |    | 490 | 495 | 404 | **397** | 497 |
|  | best | 262 | 399 |    | **159** | 492 | 165 | 261 | 493 |
|  | worst | 544 | 544 |    | 497 | 529 | 441 | **429** | 504 |
|  | std | 104 | 51.6 |    | 104 | 12.6 | 53.9 | 25.1 | **2.72** |
|  | FBTC | 5.979 | 6.020 |    | 6.945 | 6.687 | **7.302** | 6.731 | 6.587 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.

*Generated 2026-07-14 by analysis/cell_report.py from `*/maxevals_200000/f*.pkl` (table) and all common budgets (budget scaling).*
