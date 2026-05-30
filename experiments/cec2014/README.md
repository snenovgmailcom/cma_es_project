# CEC2014 — cross-dimension summary

Aggregated sums by function category, across dimensions. **Bold** = best in row.

Categories: **Basic** = unimodal + simple multimodal (F1–F16), **Hybrid** = F17–F22, **Composition** = F23–F30. Evaluation budgets: 100,000 (D=10), 300,000 (D=30). Each metric = sum across the functions of the category.

## Median error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 10 | **68.8** | 118 |   | 146 | 69.8 | 145 | 91.6 | 77.4 |
| Basic | 30 | 374 | 1280 |   | 1740 | **352** | 2.28e5 | 3.03e5 | 1410 |
| Hybrid | 10 | 31.2 | 55.1 |   | 2.65 | **1.90** | 24.7 | 9.45 | 2.30 |
| Hybrid | 30 | 1810 | 1810 |   | 114 | **43.9** | 1.39e4 | 3370 | 111 |
| Composition | 10 | 1696 | 2054 |   | 1695 | 2054 | 1752 | 1762 | **1693** |
| Composition | 30 | 4330 | 5010 |   | 3560 | **2330** | 4620 | 5510 | 2500 |

## Best error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 10 | 26.8 | 5.67 |   | 4.37 | **0.539** | 8.82 | 11.4 | 4.22 |
| Basic | 30 | 73.6 | 343 |   | 936 | **34.2** | 5.97e4 | 1.12e5 | 857 |
| Hybrid | 10 | 2.45 | 0.790 |   | 0.0200 | 0.0220 | **0.0130** | 0.280 | 0.0230 |
| Hybrid | 30 | 1170 | 321 |   | 43.7 | **26.0** | 1250 | 1640 | 62.9 |
| Composition | 10 | 896 | 1132 |   | **896** | 1573 | 952 | 1559 | 1573 |
| Composition | 30 | 3350 | 3330 |   | 2970 | **2170** | 3140 | 4210 | 2360 |

## Worst error (lower is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 10 | 430 | 582 |   | 380 | **209** | 559 | 463 | 287 |
| Basic | 30 | **1410** | 3600 |   | 3770 | 1770 | 4.45e6 | 1.95e6 | 1880 |
| Hybrid | 10 | 183 | 617 |   | 50.9 | 35.8 | 187 | 78.6 | **16.0** |
| Hybrid | 30 | 3190 | 3660 |   | 608 | **194** | 1.48e5 | 8670 | 289 |
| Composition | 10 | 1856 | 2574 |   | **1769** | 2437 | 1883 | 2283 | 2166 |
| Composition | 30 | 5290 | 7020 |   | 4970 | **2590** | 6130 | 8250 | 2800 |

## FBTC — Fixed-Budget Target Coverage (higher is better)

| Category | Dim | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|:-:|--:|--:|--:|--:|--:|
| Basic | 10 | 6.810 | 7.890 |   | 8.960 | 8.730 | 8.430 | 7.080 | **9.040** |
| Basic | 30 | 4.780 | 6.960 |   | 7.950 | 7.850 | 5.760 | 5.610 | **8.460** |
| Hybrid | 10 | 1.040 | 0.910 |   | 1.660 | 1.730 | 1.610 | 1.430 | **1.820** |
| Hybrid | 30 | 0.263 | 0.234 |   | 0.749 | **0.967** | 0.288 | 0.223 | 0.705 |
| Composition | 10 | 0.209 | 0.035 |   | 0.273 | 0.112 | **0.539** | 0.134 | 0.199 |
| Composition | 30 | 0.000 | 0.000 |   | 0.000 | 0.000 | **0.007** | 0.000 | 0.000 |

For full six-metric breakdowns per dimension, see [`d10/`](d10/) and [`d30/`](d30/).

*FBTC = Fixed-Budget Target Coverage (per-function sum across 51 log-uniform targets in [10²…10⁻⁸]); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
