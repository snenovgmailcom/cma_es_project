# CEC2014 — cross-dimension summary

Aggregated sums by function category, across the two completed dimensions. **Bold** = best in row.

Categories: **Basic** = unimodal + simple multimodal (F1–F16), **Hybrid** = F17–F22, **Composition** = F23–F30. Evaluation budgets: 100,000 (D=10), 300,000 (D=30). Each metric = sum across the functions of the category, computed over 51 independent runs.

## Median error (lower is better)

| Category | Dim | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Basic | 10 | **68.8** | 146 | 118 | 69.8 | 145 | 91.6 | 77.4 |
| Basic | 30 | 374 | 1739 | 1283 | **352** | 2.28e+05 | 3.03e+05 | 1407 |
| Hybrid | 10 | 31.2 | 2.65 | 55.1 | **1.90** | 24.7 | 9.45 | 2.30 |
| Hybrid | 30 | 1810 | 114 | 1813 | **43.9** | 1.39e+04 | 3369 | 111 |
| Composition | 10 | 1696 | 1695 | 2054 | 2054 | 1752 | 1762 | **1693** |
| Composition | 30 | 4330 | 3560 | 5013 | **2334** | 4621 | 5508 | 2501 |

## Best error (lower is better)

| Category | Dim | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Basic | 10 | 26.8 | 4.37 | 5.67 | **0.539** | 8.82 | 11.4 | 4.22 |
| Basic | 30 | 73.6 | 936 | 343 | **34.2** | 5.97e+04 | 1.12e+05 | 857 |
| Hybrid | 10 | 2.45 | 0.020 | 0.79 | 0.022 | **0.013** | 0.28 | 0.023 |
| Hybrid | 30 | 1168 | 43.7 | 321 | **26.0** | 1254 | 1635 | 62.9 |
| Composition | 10 | 895.9 | **895.8** | 1132 | 1573 | 952 | 1559 | 1573 |
| Composition | 30 | 3351 | 2969 | 3325 | **2168** | 3143 | 4206 | 2356 |

## Worst error (lower is better)

| Category | Dim | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Basic | 10 | 430 | 380 | 582 | **209** | 559 | 463 | 287 |
| Basic | 30 | **1414** | 3769 | 3603 | 1773 | 4.45e+06 | 1.95e+06 | 1884 |
| Hybrid | 10 | 183 | 50.9 | 617 | 35.8 | 187 | 78.6 | **16.0** |
| Hybrid | 30 | 3188 | 608 | 3660 | **194** | 1.48e+05 | 8668 | 289 |
| Composition | 10 | 1856 | **1769** | 2574 | 2437 | 1883 | 2283 | 2166 |
| Composition | 30 | 5288 | 4971 | 7019 | **2590** | 6130 | 8248 | 2797 |

## FBTC — Fixed-Budget Target Coverage (higher is better)

| Category | Dim | MSC-CMA | ARRDE | BIPOP-CMA | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--:|--:|--:|--:|--:|--:|--:|--:|
| Basic | 10 | 6.81 | 8.96 | 7.89 | 8.73 | 8.43 | 7.08 | **9.04** |
| Basic | 30 | 4.78 | 7.95 | 6.96 | 7.85 | 5.76 | 5.61 | **8.46** |
| Hybrid | 10 | 1.04 | 1.66 | 0.91 | 1.73 | 1.61 | 1.43 | **1.82** |
| Hybrid | 30 | 0.263 | 0.749 | 0.234 | **0.967** | 0.288 | 0.223 | 0.705 |
| Composition | 10 | 0.209 | 0.273 | 0.035 | 0.112 | **0.539** | 0.134 | 0.199 |
| Composition | 30 | 0.000 | 0.000 | 0.000 | 0.000 | **0.007** | 0.000 | 0.000 |

For full six-metric breakdowns per dimension, see [`d10/`](d10/) and [`d30/`](d30/).

*FBTC = Fixed-Budget Target Coverage (per-function sum across 51 log-uniform targets in [10²…10⁻⁸]); fixed-budget analogue of the COCO/BBOB ECDF.*
