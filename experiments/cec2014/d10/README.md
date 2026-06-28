# CEC2014 / D=10 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = unimodal + simple multimodal (F1–F16), **Hybrid** = F17–F22, **Composition** = F23–F30. Total: 30 functions. Budget: 100,000 evaluations. **Bold** = best in row.

## Ranking across metrics

Parallel-coordinate rank of all seven algorithms on four aggregate metrics (worst-SUM, median-SUM, FBTC, best-SUM), per function class. Each line is one algorithm; for every axis the best value is at the top. MSC-CMA in red.

<table>
<tr>
<td><img src="rank_basic.png" width="320" alt="Basic"></td>
<td><img src="rank_hybrid.png" width="320" alt="Hybrid"></td>
<td><img src="rank_composition.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">Basic (F1–F16)</td>
<td align="center">Hybrid (F17–F22)</td>
<td align="center">Composition (F23–F30)</td>
</tr>
</table>

*Basic = unimodal (F1–F3) + simple multimodal (F4–F16), per the CEC2014 definition.*

## Budget scaling

FBTC by budget, monotone envelope (running maximum over budgets). Higher is better; each axis runs over the five common budgets (100k–1M evaluations). MSC-CMA in red.

<table>
<tr>
<td><img src="budget_basic.png" width="320" alt="Basic"></td>
<td><img src="budget_hybrid.png" width="320" alt="Hybrid"></td>
<td><img src="budget_composition.png" width="320" alt="Composition"></td>
</tr>
<tr>
<td align="center">Basic (F1–F16)</td>
<td align="center">Hybrid (F17–F22)</td>
<td align="center">Composition (F23–F30)</td>
</tr>
</table>

## Summary table

| Category | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=16) | mean | 98.5 | 133 |   | 132 | **52.7** | 138 | 118 | 83.6 |
|  | median | **68.8** | 118 |   | 146 | 69.8 | 145 | 91.6 | 77.4 |
|  | best | 26.8 | 5.67 |   | 4.37 | **0.539** | 8.82 | 11.4 | 4.22 |
|  | worst | 430 | 582 |   | 380 | **209** | 559 | 463 | 287 |
|  | std | 93.0 | 128 |   | 101 | **53.5** | 122 | 86.0 | 75.4 |
|  | FBTC | 6.810 | 7.890 |   | 8.960 | 8.730 | 8.430 | 7.080 | **9.040** |
| **Hybrid** (n=6) | mean | 40.7 | 88.3 |   | 6.58 | 3.77 | 39.8 | 16.5 | **2.47** |
|  | median | 31.2 | 55.1 |   | 2.65 | **1.90** | 24.7 | 9.45 | 2.30 |
|  | best | 2.45 | 0.790 |   | 0.0200 | 0.0220 | **0.0130** | 0.280 | 0.0230 |
|  | worst | 183 | 617 |   | 50.9 | 35.8 | 187 | 78.6 | **16.0** |
|  | std | 37.1 | 115 |   | 12.3 | 7.79 | 43.6 | 18.5 | **2.66** |
|  | FBTC | 1.040 | 0.910 |   | 1.660 | 1.730 | 1.610 | 1.430 | **1.820** |
| **Composition** (n=8) | mean | 1593 | 2008 |   | **1581** | 2000 | 1604 | 1798 | 1728 |
|  | median | 1696 | 2054 |   | 1695 | 2054 | 1752 | 1762 | **1693** |
|  | best | 896 | 1132 |   | **896** | 1573 | 952 | 1559 | 1573 |
|  | worst | 1856 | 2574 |   | **1769** | 2437 | 1883 | 2283 | 2166 |
|  | std | 276 | 314 |   | 230 | 341 | 299 | 174 | **120** |
|  | FBTC | 0.209 | 0.035 |   | 0.273 | 0.112 | **0.539** | 0.134 | 0.199 |
| **SUM** (n=30) | mean | 1732 | 2230 |   | **1720** | 2056 | 1782 | 1933 | 1814 |
|  | median | 1796 | 2227 |   | 1844 | 2126 | 1922 | 1863 | **1773** |
|  | best | 925 | 1138 |   | **900** | 1573 | 961 | 1571 | 1577 |
|  | worst | 2470 | 3773 |   | **2200** | 2682 | 2628 | 2824 | 2469 |
|  | std | 410 | 562 |   | 346 | 407 | 469 | 282 | **200** |
|  | FBTC | 8.058 | 8.840 |   | 10.892 | 10.574 | 10.571 | 8.647 | **11.059** |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
