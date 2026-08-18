# CEC2020, D=15

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

### Budget 3M

Bonferroni family size: `10` functions.

| Function | Statistic | MSC-CMA-ES | BIPOP-CMA-ES |  | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|--:|
| **f1** | U | reference | 1198.5 |  | 1198.5 | 1198.5 | 1308.5 | 1430 | 1198.5 | 2601 |
|  | p | — | 0.0433389 |  | 0.0433389 | 0.0433389 | 0.914246 | 0.13526 | 0.0433389 | 5.1777e-20 |
|  | p_Bonf | — | 0.433389 (≈) |  | 0.433389 (≈) | 0.433389 (≈) | 1 (≈) | 1 (≈) | 0.433389 (≈) | **5.1777e-19 (−)** |
| **f2** | U | reference | 2076 |  | 366 | 1084.5 | 182 | 4 | 1447 | 2571 |
|  | p | — | 2.13328e-07 |  | 4.02859e-10 | 0.14909 | 7.22964e-14 | 3.63294e-18 | 0.328447 | 1.89586e-17 |
|  | p_Bonf | — | **2.13328e-06 (−)** |  | **4.02859e-09 (+)** | 1 (≈) | **7.22964e-13 (+)** | **3.63294e-17 (+)** | 1 (≈) | **1.89586e-16 (−)** |
| **f3** | U | reference | 0 |  | 2601 | 2601 | 2601 | 1440 | 2601 | 2601 |
|  | p | — | 1.39059e-20 |  | 1.1644e-18 | 3.28725e-18 | 5.18597e-20 | 0.350386 | 3.29867e-18 | 3.30368e-18 |
|  | p_Bonf | — | **1.39059e-19 (+)** |  | **1.1644e-17 (−)** | **3.28725e-17 (−)** | **5.18597e-19 (−)** | 1 (≈) | **3.29867e-17 (−)** | **3.30368e-17 (−)** |
| **f4** | U | reference | 55 |  | 0 | 497 | 0 | 0 | 0 | 1 |
|  | p | — | 7.7892e-17 |  | 3.30368e-18 | 7.69047e-08 | 1.82566e-19 | 3.30368e-18 | 3.30297e-18 | 3.50432e-18 |
|  | p_Bonf | — | **7.7892e-16 (+)** |  | **3.30368e-17 (+)** | **7.69047e-07 (+)** | **1.82566e-18 (+)** | **3.30368e-17 (+)** | **3.30297e-17 (+)** | **3.50432e-17 (+)** |
| **f5** | U | reference | 714 |  | 800.5 | 1457 | 2575.5 | 2572 | 2459 | 2601 |
|  | p | — | 6.09086e-05 |  | 0.000731162 | 0.293701 | 1.3467e-17 | 1.6496e-17 | 8.34603e-15 | 3.02672e-18 |
|  | p_Bonf | — | **0.000609086 (+)** |  | **0.00731162 (+)** | 1 (≈) | **1.3467e-16 (−)** | **1.6496e-16 (−)** | **8.34603e-14 (−)** | **3.02672e-17 (−)** |
| **f6** | U | reference | 130 |  | 19 | 276 | 1 | 971 | 17 | 644 |
|  | p | — | 4.84862e-15 |  | 1.0051e-17 | 7.19734e-12 | 3.50432e-18 | 0.0276723 | 8.94691e-18 | 1.13134e-05 |
|  | p_Bonf | — | **4.84862e-14 (+)** |  | **1.0051e-16 (+)** | **7.19734e-11 (+)** | **3.50432e-17 (+)** | 0.276723 (≈) | **8.94691e-17 (+)** | **0.000113134 (+)** |
| **f7** | U | reference | 417 |  | 310 | 757 | 270 | 279 | 561 | 2236 |
|  | p | — | 3.41252e-09 |  | 3.4367e-11 | 0.000277058 | 5.44405e-12 | 8.30097e-12 | 7.57887e-07 | 3.90743e-10 |
|  | p_Bonf | — | **3.41252e-08 (+)** |  | **3.4367e-10 (+)** | **0.00277058 (+)** | **5.44405e-11 (+)** | **8.30097e-11 (+)** | **7.57887e-06 (+)** | **3.90743e-09 (−)** |
| **f8** | U | reference | 2237.5 |  | 2409 | 2601 | 1231.5 | 704 | 2601 | 2450 |
|  | p | — | 2.15299e-10 |  | 1.20766e-13 | 8.91523e-19 | 0.645806 | 5.7285e-05 | 5.59245e-19 | 1.46901e-14 |
|  | p_Bonf | — | **2.15299e-09 (−)** |  | **1.20766e-12 (−)** | **8.91523e-18 (−)** | 1 (≈) | **0.00057285 (+)** | **5.59245e-18 (−)** | **1.46901e-13 (−)** |
| **f9** | U | reference | 866 |  | 153 | 2601 | 153 | 537 | 2553 | 2553 |
|  | p | — | 0.00367286 |  | 6.35374e-16 | 2.97118e-18 | 4.08597e-15 | 2.89092e-07 | 4.74772e-17 | 5.31822e-17 |
|  | p_Bonf | — | **0.0367286 (+)** |  | **6.35374e-15 (+)** | **2.97118e-17 (−)** | **4.08597e-14 (+)** | **2.89092e-06 (+)** | **4.74772e-16 (−)** | **5.31822e-16 (−)** |
| **f10** | U | reference | 2155 |  | 1629 | 2193 | 2193 | 2185 | 2193 | 2452 |
|  | p | — | 3.37708e-09 |  | 0.0274953 | 1.74842e-10 | 1.74842e-10 | 5.36718e-10 | 2.8347e-10 | 1.3259e-14 |
|  | p_Bonf | — | **3.37708e-08 (−)** |  | 0.274953 (≈) | **1.74842e-09 (−)** | **1.74842e-09 (−)** | **5.36718e-09 (−)** | **2.8347e-09 (−)** | **1.3259e-13 (−)** |

Full-precision U statistics, raw and Bonferroni-adjusted p-values,
effect directions, sample medians, and family sizes are available in
[`details.csv`](details.csv).
