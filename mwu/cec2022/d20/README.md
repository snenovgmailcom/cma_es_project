# CEC2022, D=20

## Mann–Whitney U tests on terminal errors

Independent, two-sided Mann–Whitney U tests compare each competitor
with MSC-CMA-ES on every function. Each sample contains 51 unmodified
run-wise terminal errors. Bonferroni adjustment is applied over all
functions separately for each budget and competitor.

The U statistic in [`details.csv`](details.csv) is for the competitor
sample. For minimization, `probability_competitor_lower` is
$P(X_{competitor}<X_{MSC})+\frac12P(X_{competitor}=X_{MSC})$.

Each function is reported with the U statistic, the raw two-sided
p-value, and the Bonferroni-adjusted p-value. In the adjusted-p rows,
`+` means that the competitor has significantly lower terminal errors,
`−` means that MSC-CMA-ES has significantly lower terminal errors, and
`≈` means that the difference is not significant at alpha=0.05.
Significant adjusted p-values are shown in bold.

### Budget 1M

Bonferroni family size: `12` functions.

| Function | Statistic | MSC-CMA-ES | BIPOP-CMA-ES |  | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **f1** | U | reference | 586.5 |  | 790.5 | 586.5 | 1109 | 2601 | 586.5 |
|  | p | — | 6.50844e-10 |  | 3.79743e-05 | 6.50844e-10 | 0.145877 | 8.83294e-19 | 6.50844e-10 |
|  | p_Bonf | — | **7.81013e-09 (+)** |  | **0.000455691 (+)** | **7.81013e-09 (+)** | 1 (≈) | **1.05995e-17 (−)** | **7.81013e-09 (+)** |
| **f2** | U | reference | 1948.5 |  | 1134.5 | 2601 | 2539 | 2439 | 2601 |
|  | p | — | 4.45116e-06 |  | 0.206732 | 5.88451e-21 | 2.92341e-17 | 1.26091e-14 | 4.01078e-19 |
|  | p_Bonf | — | **5.34139e-05 (−)** |  | 1 (≈) | **7.06142e-20 (−)** | **3.50809e-16 (−)** | **1.51309e-13 (−)** | **4.81294e-18 (−)** |
| **f3** | U | reference | 0 |  | 0 | 0 | 0 | 0 | 0 |
|  | p | — | 1.46792e-18 |  | 3.83658e-20 | 1.80926e-19 | 5.1777e-20 | 1.56647e-18 | 1.39059e-20 |
|  | p_Bonf | — | **1.7615e-17 (+)** |  | **4.6039e-19 (+)** | **2.17111e-18 (+)** | **6.21324e-19 (+)** | **1.87976e-17 (+)** | **1.66871e-19 (+)** |
| **f4** | U | reference | 1730 |  | 2351.5 | 890.5 | 2601 | 2601 | 2592 |
|  | p | — | 0.00325088 |  | 7.59803e-13 | 0.00490363 | 2.83933e-18 | 2.83995e-18 | 3.81592e-18 |
|  | p_Bonf | — | **0.0390106 (−)** |  | **9.11763e-12 (−)** | 0.0588435 (≈) | **3.4072e-17 (−)** | **3.40794e-17 (−)** | **4.5791e-17 (−)** |
| **f5** | U | reference | 484.5 |  | 484.5 | 484.5 | 848 | 1227 | 484.5 |
|  | p | — | 3.20091e-11 |  | 3.20091e-11 | 3.20091e-11 | 0.000980639 | 0.618453 | 3.20091e-11 |
|  | p_Bonf | — | **3.84109e-10 (+)** |  | **3.84109e-10 (+)** | **3.84109e-10 (+)** | **0.0117677 (+)** | 1 (≈) | **3.84109e-10 (+)** |
| **f6** | U | reference | 2359 |  | 1045 | 1173 | 2576 | 2532 | 899 |
|  | p | — | 1.43237e-12 |  | 0.0878889 | 0.387187 | 1.42352e-17 | 1.74059e-16 | 0.00727959 |
|  | p_Bonf | — | **1.71885e-11 (−)** |  | 1 (≈) | 1 (≈) | **1.70822e-16 (−)** | **2.08871e-15 (−)** | 0.0873551 (≈) |
| **f7** | U | reference | 1947 |  | 711 | 400 | 1061 | 1266 | 794 |
|  | p | — | 1.53581e-05 |  | 8.07584e-05 | 1.34264e-09 | 0.109697 | 0.819995 | 0.000707828 |
|  | p_Bonf | — | **0.000184297 (−)** |  | **0.0009691 (+)** | **1.61117e-08 (+)** | 1 (≈) | 1 (≈) | **0.00849393 (+)** |
| **f8** | U | reference | 1068 |  | 818 | 1441 | 1171 | 2090 | 813 |
|  | p | — | 0.120493 |  | 0.00125584 | 0.348769 | 0.38794 | 1.28799e-07 | 0.00111668 |
|  | p_Bonf | — | 1 (≈) |  | **0.0150701 (+)** | 1 (≈) | 1 (≈) | **1.54559e-06 (−)** | **0.0134002 (+)** |
| **f9** | U | reference | 1176 |  | 1530 | 1249.5 | 1300.5 | 2473.5 | 1275 |
|  | p | — | 0.0265276 |  | 0.00797047 | 0.159329 | 1 | 1.27527e-19 | 0.567513 |
|  | p_Bonf | — | 0.318332 (≈) |  | 0.0956457 (≈) | 1 (≈) | 1 (≈) | **1.53032e-18 (−)** | 1 (≈) |
| **f10** | U | reference | 2338 |  | 2476 | 2601 | 2 | 0 | 2601 |
|  | p | — | 3.91164e-12 |  | 3.72262e-15 | 3.30368e-18 | 5.91512e-20 | 3.30297e-18 | 3.30368e-18 |
|  | p_Bonf | — | **4.69397e-11 (−)** |  | **4.46715e-14 (−)** | **3.96442e-17 (−)** | **7.09814e-19 (+)** | **3.96356e-17 (+)** | **3.96442e-17 (−)** |
| **f11** | U | reference | 585 |  | 204 | 2550 | 2601 | 2601 | 2601 |
|  | p | — | 1.70733e-06 |  | 4.36125e-14 | 1.71722e-17 | 8.03761e-19 | 2.57847e-18 | 5.91538e-19 |
|  | p_Bonf | — | **2.04879e-05 (+)** |  | **5.2335e-13 (+)** | **2.06067e-16 (−)** | **9.64513e-18 (−)** | **3.09417e-17 (−)** | **7.09846e-18 (−)** |
| **f12** | U | reference | 1474.5 |  | 0 | 681 | 2064 | 1245.5 | 64 |
|  | p | — | 0.221491 |  | 1.80882e-18 | 2.93596e-05 | 2.68014e-07 | 0.713257 | 6.31274e-17 |
|  | p_Bonf | — | 1 (≈) |  | **2.17059e-17 (+)** | **0.000352316 (+)** | **3.21617e-06 (−)** | 1 (≈) | **7.57529e-16 (+)** |

Full-precision U statistics, raw and Bonferroni-adjusted p-values,
effect directions, sample medians, and family sizes are available in
[`details.csv`](details.csv).
