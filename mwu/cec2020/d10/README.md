# CEC2020, D=10

Contents: [Mann–Whitney U tests on terminal errors](#mannwhitney-u-tests-on-terminal-errors) · [Deep Statistical Comparison](#deep-statistical-comparison)

## Mann–Whitney U tests on terminal errors

Independent, two-sided Mann–Whitney U tests compare each competitor
with MSC-CMA-ES on every function. Each sample contains 51 unmodified
run-wise terminal errors. Bonferroni adjustment is applied over all
functions separately for each budget and competitor.
The test is evaluated with SciPy's asymptotic Mann–Whitney U method
(`method="asymptotic"`) with continuity correction (`use_continuity=True`).

The U statistic in [`details.csv`](details.csv) is for the competitor
sample. For minimization, `probability_competitor_lower` is
$P(X_{competitor}<X_{MSC})+\frac12P(X_{competitor}=X_{MSC})$.

Each function is reported with the U statistic, p_raw, and
p_Bonferroni. Direction is stated from the competitor perspective:
`↓` denotes a statistically significant shift toward lower terminal
errors, `↑` a statistically significant shift toward higher terminal
errors, and `—` no statistically significant difference after
Bonferroni correction. Significant adjusted p-values are shown in bold.

<a id="budget-1m"></a>

### Budget 10^6

Bonferroni family size: `10` functions.

<a id="budget-1m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 841.5 | 841.5 | 841.5 | 945 | 1429.5 | 841.5 |
| **f2** | 2102 | 1482 | 1267 | 1155.5 | 397.5 | 1875.5 |
| **f3** | 1528.5 | 2436 | 2481 | 1945.5 | 1754 | 2589 |
| **f4** | 82 | 1 | 348 | 0 | 0 | 0 |
| **f5** | 456 | 318.5 | 1414.5 | 1624 | 1503.5 | 1076 |
| **f6** | 362 | 45 | 250 | 0 | 278 | 6 |
| **f7** | 226 | 5 | 438 | 0 | 5 | 5 |
| **f8** | 1734 | 1887 | 2397 | 1224 | 1122 | 2601 |
| **f9** | 2110.5 | 1764 | 2574 | 1596 | 1974 | 2394 |
| **f10** | 2495 | 441 | 2601 | 2520 | 2546 | 2601 |

<a id="budget-1m-raw-p"></a>

#### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 3.366e-06 | 3.366e-06 | 3.366e-06 | 0.000721674 | 0.313394 | 3.366e-06 |
| **f2** | 8.13174e-08 | 0.224822 | 0.825041 | 0.333305 | 1.45469e-09 | 0.00011956 |
| **f3** | 0.12694 | 3.04192e-14 | 2.82254e-15 | 1.58101e-05 | 0.00241918 | 6.68189e-18 |
| **f4** | 3.5845e-16 | 3.50432e-18 | 1.87218e-10 | 5.19011e-20 | 3.216e-18 | 3.24474e-18 |
| **f5** | 2.54857e-09 | 1.24452e-11 | 0.439064 | 0.0286571 | 0.166068 | 0.124506 |
| **f6** | 3.43487e-10 | 4.48966e-17 | 2.10504e-12 | 3.30368e-18 | 7.92225e-12 | 4.70263e-18 |
| **f7** | 6.57628e-13 | 4.43437e-18 | 7.96895e-09 | 3.30368e-18 | 4.43437e-18 | 4.43437e-18 |
| **f8** | 0.00345509 | 8.63374e-05 | 3.27262e-14 | 0.607591 | 0.231041 | 1.37029e-20 |
| **f9** | 6.01124e-08 | 0.00170514 | 1.54153e-17 | 0.0432385 | 3.54556e-06 | 2.31977e-13 |
| **f10** | 8.66868e-16 | 8.97194e-09 | 2.68584e-18 | 8.75562e-18 | 7.90484e-17 | 7.13469e-19 |

<a id="budget-1m-bonferroni"></a>

#### p_Bonferroni and Direction

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **3.366e-05 (↓)** | **3.366e-05 (↓)** | **3.366e-05 (↓)** | **0.00721674 (↓)** | 1 (—) | **3.366e-05 (↓)** |
| **f2** | **8.13174e-07 (↑)** | 1 (—) | 1 (—) | 1 (—) | **1.45469e-08 (↓)** | **0.0011956 (↑)** |
| **f3** | 1 (—) | **3.04192e-13 (↑)** | **2.82254e-14 (↑)** | **0.000158101 (↑)** | **0.0241918 (↑)** | **6.68189e-17 (↑)** |
| **f4** | **3.5845e-15 (↓)** | **3.50432e-17 (↓)** | **1.87218e-09 (↓)** | **5.19011e-19 (↓)** | **3.216e-17 (↓)** | **3.24474e-17 (↓)** |
| **f5** | **2.54857e-08 (↓)** | **1.24452e-10 (↓)** | 1 (—) | 0.286571 (—) | 1 (—) | 1 (—) |
| **f6** | **3.43487e-09 (↓)** | **4.48966e-16 (↓)** | **2.10504e-11 (↓)** | **3.30368e-17 (↓)** | **7.92225e-11 (↓)** | **4.70263e-17 (↓)** |
| **f7** | **6.57628e-12 (↓)** | **4.43437e-17 (↓)** | **7.96895e-08 (↓)** | **3.30368e-17 (↓)** | **4.43437e-17 (↓)** | **4.43437e-17 (↓)** |
| **f8** | **0.0345509 (↑)** | **0.000863374 (↑)** | **3.27262e-13 (↑)** | 1 (—) | 1 (—) | **1.37029e-19 (↑)** |
| **f9** | **6.01124e-07 (↑)** | **0.0170514 (↑)** | **1.54153e-16 (↑)** | 0.432385 (—) | **3.54556e-05 (↑)** | **2.31977e-12 (↑)** |
| **f10** | **8.66868e-15 (↑)** | **8.97194e-08 (↓)** | **2.68584e-17 (↑)** | **8.75562e-17 (↑)** | **7.90484e-16 (↑)** | **7.13469e-18 (↑)** |

<a id="budget-20m"></a>

### Budget 2×10^7

Bonferroni family size: `10` functions.

<a id="budget-20m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1300.5 | 1300.5 | 1300.5 | 1300.5 | 1326 | 1300.5 |
| **f2** | 2483.5 | 899 | 2099 | 1408.5 | 0 | 2143.5 |
| **f3** | 1818 | 1410.5 | 2601 | 957 | 0 | 2601 |
| **f4** | 14 | 0 | 753 | 0 | 0 | 0 |
| **f5** | 1665.5 | 688.5 | 2250 | 789 | 715.5 | 793.5 |
| **f6** | 446 | 0 | 695 | 0 | 12 | 0 |
| **f7** | 550 | 0 | 1128 | 0 | 0 | 8 |
| **f8** | 1479 | 51 | 2448 | 459 | 0 | 2601 |
| **f9** | 2443 | 153 | 2601 | 1887 | 2142 | 2601 |
| **f10** | 2597 | 2450 | 2601 | 2598 | 2569 | 2601 |

<a id="budget-20m-raw-p"></a>

#### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1 | 1 | 1 | 1 | 0.326893 | 1 |
| **f2** | 2.17535e-15 | 0.00676453 | 7.91891e-08 | 0.470943 | 1.21537e-20 | 1.53224e-08 |
| **f3** | 0.00049801 | 0.463519 | 3.28867e-18 | 0.020057 | 1.38941e-20 | 3.30153e-18 |
| **f4** | 4.2902e-18 | 3.26451e-18 | 0.000251269 | 1.39059e-20 | 1.21577e-18 | 2.86988e-18 |
| **f5** | 0.00872225 | 3.63724e-08 | 7.37524e-11 | 1.32778e-05 | 3.19494e-07 | 1.97364e-05 |
| **f6** | 1.09336e-08 | 3.30368e-18 | 5.14176e-05 | 3.30368e-18 | 6.68332e-18 | 3.30368e-18 |
| **f7** | 5.17979e-07 | 3.30368e-18 | 0.249672 | 3.30368e-18 | 3.30368e-18 | 5.28812e-18 |
| **f8** | 0.231357 | 5.48887e-19 | 1.70113e-15 | 5.30406e-09 | 1.12702e-19 | 1.35871e-20 |
| **f9** | 2.0533e-14 | 7.96141e-16 | 3.19581e-18 | 5.90847e-05 | 7.40332e-09 | 9.55596e-19 |
| **f10** | 2.91285e-18 | 2.67662e-16 | 2.67938e-18 | 4.67216e-20 | 2.13179e-17 | 6.2826e-19 |

<a id="budget-20m-bonferroni"></a>

#### p_Bonferroni and Direction

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1 (—) | 1 (—) | 1 (—) | 1 (—) | 1 (—) | 1 (—) |
| **f2** | **2.17535e-14 (↑)** | 0.0676453 (—) | **7.91891e-07 (↑)** | 1 (—) | **1.21537e-19 (↓)** | **1.53224e-07 (↑)** |
| **f3** | **0.0049801 (↑)** | 1 (—) | **3.28867e-17 (↑)** | 0.20057 (—) | **1.38941e-19 (↓)** | **3.30153e-17 (↑)** |
| **f4** | **4.2902e-17 (↓)** | **3.26451e-17 (↓)** | **0.00251269 (↓)** | **1.39059e-19 (↓)** | **1.21577e-17 (↓)** | **2.86988e-17 (↓)** |
| **f5** | 0.0872225 (—) | **3.63724e-07 (↓)** | **7.37524e-10 (↑)** | **0.000132778 (↓)** | **3.19494e-06 (↓)** | **0.000197364 (↓)** |
| **f6** | **1.09336e-07 (↓)** | **3.30368e-17 (↓)** | **0.000514176 (↓)** | **3.30368e-17 (↓)** | **6.68332e-17 (↓)** | **3.30368e-17 (↓)** |
| **f7** | **5.17979e-06 (↓)** | **3.30368e-17 (↓)** | 1 (—) | **3.30368e-17 (↓)** | **3.30368e-17 (↓)** | **5.28812e-17 (↓)** |
| **f8** | 1 (—) | **5.48887e-18 (↓)** | **1.70113e-14 (↑)** | **5.30406e-08 (↓)** | **1.12702e-18 (↓)** | **1.35871e-19 (↑)** |
| **f9** | **2.0533e-13 (↑)** | **7.96141e-15 (↓)** | **3.19581e-17 (↑)** | **0.000590847 (↑)** | **7.40332e-08 (↑)** | **9.55596e-18 (↑)** |
| **f10** | **2.91285e-17 (↑)** | **2.67662e-15 (↑)** | **2.67938e-17 (↑)** | **4.67216e-19 (↑)** | **2.13179e-16 (↑)** | **6.2826e-18 (↑)** |

Full-precision U statistics, raw and Bonferroni-adjusted p-values,
effect directions, sample medians, and family sizes are available in
[`details.csv`](details.csv).

## Deep Statistical Comparison

Following the fixed-budget analysis workflow described by
[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied
[Deep Statistical Comparison (Eftimov et al., 2017)](https://doi.org/10.1016/j.ins.2017.07.015)
through [DSCTool (Eftimov et al., 2020)](https://doi.org/10.1016/j.asoc.2019.105977)
to the 51 run-wise terminal errors for each function.

IOHanalyzer: <https://iohanalyzer.liacs.nl/>; DSCTool service used for
the analysis: <https://ws.ijs.si/dsc/>.

Settings: Anderson–Darling comparisons at `alpha=0.05`, `epsilon=0`,
and `monte_carlo_iterations=0`; Friedman omnibus tests over functions;
and, after rejection of the omnibus null hypothesis, Holm-adjusted
post-hoc comparisons against the method with the lowest mean DSC rank.

`★` means that MSC-CMA-ES has the lowest mean DSC rank and the Friedman
test rejects the null hypothesis; `≈` means that the Friedman test
rejects the null hypothesis but the Holm-adjusted comparison between
MSC-CMA-ES and the lowest-mean-rank method is not significant; `↓` means
that the lowest-mean-rank method has a smaller mean DSC rank than
MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means
that the Friedman test does not reject the null hypothesis and no
post-hoc interpretation is made.

<a id="dsc-budget-1m"></a>

### Budget 10^6

<a id="dsc-budget-1m-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 1.5 | 5 | 5 | 5 | 5 | 1.5 | 5 |
| **f2** | 3.5 | 7 | 3.5 | 3.5 | 3.5 | 1 | 6 |
| **f3** | 1 | 2 | 5 | 6 | 4 | 3 | 7 |
| **f4** | 7 | 5 | 4 | 6 | 1 | 2 | 3 |
| **f5** | 3 | 7 | 1 | 6 | 5 | 2 | 4 |
| **f6** | 7 | 5 | 3 | 5 | 1.5 | 5 | 1.5 |
| **f7** | 7 | 5.5 | 3 | 5.5 | 3 | 3 | 1 |
| **f8** | 1 | 5 | 4 | 6.5 | 3 | 2 | 6.5 |
| **f9** | 1 | 5 | 3 | 7 | 2 | 4 | 6 |
| **f10** | 1 | 5.5 | 2 | 7 | 4 | 3 | 5.5 |

Composition-function set: `f8–f10`.

<a id="dsc-budget-1m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | j2020 | 2.65 | 3.3 | 3/7 | 17.5286 | 0.00752491 | 0.703075 | ≈ |
| Composition functions | 3 | MSC-CMA-ES | 1 | 1 | 1/7 | 16.3214 | 0.0121289 | — | ★ |

<a id="dsc-budget-20m"></a>

### Budget 2×10^7

<a id="dsc-budget-20m-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| **f2** | 2.5 | 7 | 2.5 | 5.5 | 4 | 1 | 5.5 |
| **f3** | 2.5 | 5 | 2.5 | 6 | 4 | 1 | 7 |
| **f4** | 7 | 3.5 | 2 | 6 | 1 | 3.5 | 5 |
| **f5** | 5 | 7 | 1 | 6 | 3.5 | 2 | 3.5 |
| **f6** | 7 | 5.5 | 1 | 5.5 | 4 | 2.5 | 2.5 |
| **f7** | 6.5 | 5 | 1.5 | 6.5 | 1.5 | 3 | 4 |
| **f8** | 3 | 5 | 2 | 6.5 | 4 | 1 | 6.5 |
| **f9** | 1 | 4 | 2 | 7 | 3 | 5.5 | 5.5 |
| **f10** | 1 | 4.5 | 2 | 7 | 6 | 3 | 4.5 |

Composition-function set: `f8–f10`.

<a id="dsc-budget-20m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | ARRDE | 2.05 | 3.95 | 4/7 | 24.9 | 0.000356322 | 0.073829 | ≈ |
| Composition functions | 3 | MSC-CMA-ES | 1.66667 | 1.66667 | 1/7 | 13.3571 | 0.0377023 | — | ★ |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 10^6 | j2020 · 3/7 · ≈ | MSC-CMA-ES · 1/7 · ★ |
| 2×10^7 | ARRDE · 4/7 · ≈ | MSC-CMA-ES · 1/7 · ★ |
