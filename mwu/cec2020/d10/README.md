# CEC2020, D=10

[MWU overview](../../README.md) · [Full results CSV](details.csv)

Contents: [Budget 10^6](#budget-1m) · [Budget 2×10^7](#budget-20m) · [Deep Statistical Comparison](#deep-statistical-comparison)

## Mann–Whitney U tests on terminal errors

Each competitor is compared with MSC-CMA-ES using independent, two-sided
Mann–Whitney U tests on 51 stored run-wise terminal errors at the stated budget.
The tests use the asymptotic method with tie and continuity corrections.
No zero threshold or rounding is applied to the MWU inputs; zeros already
present in the stored samples are retained.

Holm–Bonferroni correction is applied separately for each competitor, suite,
dimension, budget, and function scope, at `alpha=0.05`.
All-function and composition-function results use independent corrections
of the same raw p-values. For CEC2017 the family sizes are 29 and 10,
respectively; withdrawn function f2 is excluded.

**MWU legend — all outcomes are from the MSC-CMA-ES perspective:**

- **W**: significant result in favour of MSC-CMA-ES (lower terminal errors).
- **L**: significant result in favour of the competitor.
- **NS**: no statistically significant difference after Holm correction.

Significance uses the full-precision adjusted p-value (`p_Holm <= 0.05`).
Direction follows U, not rounded medians. W/L/NS summary cells contain
counts of functions; NS does not assert equality of the algorithms.

CSV values retain full numerical precision. Only descriptive medians use
a separate copy with `abs(error) <= 1e-8` set to zero.

### Summary

| Budget / function scope | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| [10^6 / All functions](#budget-1m-all) | 4/5/1 | 3/6/1 | 4/4/2 | 2/4/4 | 3/4/3 | 5/4/1 |
| [10^6 / Composition functions](#budget-1m-composition) | 3/0/0 | 2/1/0 | 3/0/0 | 1/0/2 | 2/0/1 | 3/0/0 |
| [2×10^7 / All functions](#budget-20m-all) | 5/3/2 | 1/7/2 | 6/2/2 | 2/5/3 | 2/7/1 | 5/4/1 |
| [2×10^7 / Composition functions](#budget-20m-composition) | 2/0/1 | 1/2/0 | 3/0/0 | 2/1/0 | 2/1/0 | 3/0/0 |

All summary cells are **W/L/NS for MSC-CMA-ES**.

<a id="budget-1m"></a>

### Budget 10^6

<a id="budget-1m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **10** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **1.0098e-05 · L** | **1.3464e-05 · L** | **1.0098e-05 · L** | **0.00360837 · L** | 0.498203 · NS | **1.0098e-05 · L** |
| **f2** | **3.25269e-07 · W** | 0.224822 · NS | 0.878128 · NS | 0.666609 · NS | **8.72815e-09 · L** | **0.000239119 · W** |
| **f3** | 0.12694 · NS | **2.12934e-13 · W** | **2.25803e-14 · W** | **9.48604e-05 · W** | **0.0096767 · W** | **3.34095e-17 · W** |
| **f4** | **3.5845e-15 · L** | **3.50432e-17 · L** | **9.36092e-10 · L** | **5.19011e-19 · L** | **3.216e-17 · L** | **2.5958e-17 · L** |
| **f5** | **1.52914e-08 · L** | **7.46709e-11 · L** | 0.878128 · NS | 0.114628 · NS | 0.498203 · NS | 0.124506 · NS |
| **f6** | **2.40441e-09 · L** | **3.59172e-16 · L** | **1.26302e-11 · L** | **2.97331e-17 · L** | **5.54558e-11 · L** | **3.10406e-17 · L** |
| **f7** | **5.26103e-12 · L** | **3.99093e-17 · L** | **3.18758e-08 · L** | **2.97331e-17 · L** | **3.99093e-17 · L** | **3.10406e-17 · L** |
| **f8** | **0.00691018 · W** | **0.000259012 · W** | **2.29083e-13 · W** | 0.666609 · NS | 0.498203 · NS | **1.37029e-19 · W** |
| **f9** | **3.00562e-07 · W** | **0.00341027 · W** | **1.38738e-16 · W** | 0.129715 · NS | **1.77278e-05 · W** | **9.27906e-13 · W** |
| **f10** | **7.80182e-15 · W** | **4.48597e-08 · L** | **2.68584e-17 · W** | **6.12894e-17 · W** | **6.32388e-16 · W** | **6.42122e-18 · W** |
| **W/L/NS** | 4/5/1 | 3/6/1 | 4/4/2 | 2/4/4 | 3/4/3 | 5/4/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 841.5 | 841.5 | 841.5 | 945 | 1429.5 | 841.5 |
| f2 | 2102 | 1482 | 1267 | 1155.5 | 397.5 | 1875.5 |
| f3 | 1528.5 | 2436 | 2481 | 1945.5 | 1754 | 2589 |
| f4 | 82 | 1 | 348 | 0 | 0 | 0 |
| f5 | 456 | 318.5 | 1414.5 | 1624 | 1503.5 | 1076 |
| f6 | 362 | 45 | 250 | 0 | 278 | 6 |
| f7 | 226 | 5 | 438 | 0 | 5 | 5 |
| f8 | 1734 | 1887 | 2397 | 1224 | 1122 | 2601 |
| f9 | 2110.5 | 1764 | 2574 | 1596 | 1974 | 2394 |
| f10 | 2495 | 441 | 2601 | 2520 | 2546 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 3.366e-06 | 3.366e-06 | 3.366e-06 | 0.000721674 | 0.313394 | 3.366e-06 |
| f2 | 8.13174e-08 | 0.224822 | 0.825041 | 0.333305 | 1.45469e-09 | 0.00011956 |
| f3 | 0.12694 | 3.04192e-14 | 2.82254e-15 | 1.58101e-05 | 0.00241918 | 6.68189e-18 |
| f4 | 3.5845e-16 | 3.50432e-18 | 1.87218e-10 | 5.19011e-20 | 3.216e-18 | 3.24474e-18 |
| f5 | 2.54857e-09 | 1.24452e-11 | 0.439064 | 0.0286571 | 0.166068 | 0.124506 |
| f6 | 3.43487e-10 | 4.48966e-17 | 2.10504e-12 | 3.30368e-18 | 7.92225e-12 | 4.70263e-18 |
| f7 | 6.57628e-13 | 4.43437e-18 | 7.96895e-09 | 3.30368e-18 | 4.43437e-18 | 4.43437e-18 |
| f8 | 0.00345509 | 8.63374e-05 | 3.27262e-14 | 0.607591 | 0.231041 | 1.37029e-20 |
| f9 | 6.01124e-08 | 0.00170514 | 1.54153e-17 | 0.0432385 | 3.54556e-06 | 2.31977e-13 |
| f10 | 8.66868e-16 | 8.97194e-09 | 2.68584e-18 | 8.75562e-18 | 7.90484e-17 | 7.13469e-19 |

</details>

<a id="budget-1m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **3** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f8** | **0.00345509 · W** | **0.000172675 · W** | **3.27262e-14 · W** | 0.607591 · NS | 0.231041 · NS | **4.11087e-20 · W** |
| **f9** | **1.20225e-07 · W** | **0.00170514 · W** | **3.08307e-17 · W** | 0.086477 · NS | **7.09111e-06 · W** | **2.31977e-13 · W** |
| **f10** | **2.60061e-15 · W** | **2.69158e-08 · L** | **8.05753e-18 · W** | **2.62669e-17 · W** | **2.37145e-16 · W** | **1.42694e-18 · W** |
| **W/L/NS** | 3/0/0 | 2/1/0 | 3/0/0 | 1/0/2 | 2/0/1 | 3/0/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 1734 | 1887 | 2397 | 1224 | 1122 | 2601 |
| f9 | 2110.5 | 1764 | 2574 | 1596 | 1974 | 2394 |
| f10 | 2495 | 441 | 2601 | 2520 | 2546 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 0.00345509 | 8.63374e-05 | 3.27262e-14 | 0.607591 | 0.231041 | 1.37029e-20 |
| f9 | 6.01124e-08 | 0.00170514 | 1.54153e-17 | 0.0432385 | 3.54556e-06 | 2.31977e-13 |
| f10 | 8.66868e-16 | 8.97194e-09 | 2.68584e-18 | 8.75562e-18 | 7.90484e-17 | 7.13469e-19 |

</details>

<a id="budget-20m"></a>

### Budget 2×10^7

<a id="budget-20m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **10** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1 · NS | 1 · NS | 1 · NS | 1 · NS | 0.326893 · NS | 1 · NS |
| **f2** | **1.74028e-14 · W** | **0.0202936 · L** | **3.95945e-07 · W** | 0.941886 · NS | **1.21537e-19 · L** | **4.59671e-08 · W** |
| **f3** | **0.00199204 · W** | 0.927038 · NS | **2.87623e-17 · W** | 0.0601711 · NS | **1.25047e-19 · L** | **2.00892e-17 · W** |
| **f4** | **3.86118e-17 · L** | **2.93806e-17 · L** | **0.000753808 · L** | **1.39059e-19 · L** | **8.51037e-18 · L** | **2.00892e-17 · L** |
| **f5** | **0.0261667 · W** | **1.4549e-07 · L** | **4.42514e-10 · W** | **6.63892e-05 · L** | **6.38987e-07 · L** | **3.94728e-05 · L** |
| **f6** | **6.56013e-08 · L** | **2.93806e-17 · L** | **0.00020567 · L** | **2.64295e-17 · L** | **3.34166e-17 · L** | **2.00892e-17 · L** |
| **f7** | **2.5899e-06 · L** | **2.93806e-17 · L** | 0.499345 · NS | **2.64295e-17 · L** | **1.98221e-17 · L** | **2.11525e-17 · L** |
| **f8** | 0.462714 · NS | **5.48887e-18 · L** | **1.19079e-14 · W** | **3.18244e-08 · L** | **9.01618e-19 · L** | **1.35871e-19 · W** |
| **f9** | **1.43731e-13 · W** | **3.9807e-15 · L** | **2.87623e-17 · W** | **0.000236339 · W** | **2.221e-08 · W** | **7.64477e-18 · W** |
| **f10** | **2.91285e-17 · W** | **1.60597e-15 · W** | **2.67938e-17 · W** | **4.20495e-19 · W** | **8.52717e-17 · W** | **5.65434e-18 · W** |
| **W/L/NS** | 5/3/2 | 1/7/2 | 6/2/2 | 2/5/3 | 2/7/1 | 5/4/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 1300.5 | 1300.5 | 1300.5 | 1300.5 | 1326 | 1300.5 |
| f2 | 2483.5 | 899 | 2099 | 1408.5 | 0 | 2143.5 |
| f3 | 1818 | 1410.5 | 2601 | 957 | 0 | 2601 |
| f4 | 14 | 0 | 753 | 0 | 0 | 0 |
| f5 | 1665.5 | 688.5 | 2250 | 789 | 715.5 | 793.5 |
| f6 | 446 | 0 | 695 | 0 | 12 | 0 |
| f7 | 550 | 0 | 1128 | 0 | 0 | 8 |
| f8 | 1479 | 51 | 2448 | 459 | 0 | 2601 |
| f9 | 2443 | 153 | 2601 | 1887 | 2142 | 2601 |
| f10 | 2597 | 2450 | 2601 | 2598 | 2569 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 1 | 1 | 1 | 1 | 0.326893 | 1 |
| f2 | 2.17535e-15 | 0.00676453 | 7.91891e-08 | 0.470943 | 1.21537e-20 | 1.53224e-08 |
| f3 | 0.00049801 | 0.463519 | 3.28867e-18 | 0.020057 | 1.38941e-20 | 3.30153e-18 |
| f4 | 4.2902e-18 | 3.26451e-18 | 0.000251269 | 1.39059e-20 | 1.21577e-18 | 2.86988e-18 |
| f5 | 0.00872225 | 3.63724e-08 | 7.37524e-11 | 1.32778e-05 | 3.19494e-07 | 1.97364e-05 |
| f6 | 1.09336e-08 | 3.30368e-18 | 5.14176e-05 | 3.30368e-18 | 6.68332e-18 | 3.30368e-18 |
| f7 | 5.17979e-07 | 3.30368e-18 | 0.249672 | 3.30368e-18 | 3.30368e-18 | 5.28812e-18 |
| f8 | 0.231357 | 5.48887e-19 | 1.70113e-15 | 5.30406e-09 | 1.12702e-19 | 1.35871e-20 |
| f9 | 2.0533e-14 | 7.96141e-16 | 3.19581e-18 | 5.90847e-05 | 7.40332e-09 | 9.55596e-19 |
| f10 | 2.91285e-18 | 2.67662e-16 | 2.67938e-18 | 4.67216e-20 | 2.13179e-17 | 6.2826e-19 |

</details>

<a id="budget-20m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **3** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f8** | 0.231357 · NS | **1.64666e-18 · L** | **1.70113e-15 · W** | **1.06081e-08 · L** | **3.38107e-19 · L** | **4.07613e-20 · W** |
| **f9** | **4.1066e-14 · W** | **7.96141e-16 · L** | **8.03813e-18 · W** | **5.90847e-05 · W** | **7.40332e-09 · W** | **1.25652e-18 · W** |
| **f10** | **8.73855e-18 · W** | **5.35323e-16 · W** | **8.03813e-18 · W** | **1.40165e-19 · W** | **4.26359e-17 · W** | **1.25652e-18 · W** |
| **W/L/NS** | 2/0/1 | 1/2/0 | 3/0/0 | 2/1/0 | 2/1/0 | 3/0/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 1479 | 51 | 2448 | 459 | 0 | 2601 |
| f9 | 2443 | 153 | 2601 | 1887 | 2142 | 2601 |
| f10 | 2597 | 2450 | 2601 | 2598 | 2569 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 0.231357 | 5.48887e-19 | 1.70113e-15 | 5.30406e-09 | 1.12702e-19 | 1.35871e-20 |
| f9 | 2.0533e-14 | 7.96141e-16 | 3.19581e-18 | 5.90847e-05 | 7.40332e-09 | 9.55596e-19 |
| f10 | 2.91285e-18 | 2.67662e-16 | 2.67938e-18 | 4.67216e-20 | 2.13179e-17 | 6.2826e-19 |

</details>

The complete U statistics, raw and adjusted p-values, sample sizes,
descriptive medians, scopes, and family sizes are in [`details.csv`](details.csv).
The CSV `decision` field describes the competitor: `higher` maps to W for
MSC-CMA-ES, `lower` to L, and `not significant` to NS.

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

`p_Holm` is shown only when the lowest-mean-rank algorithm is not
MSC-CMA-ES and the Friedman test rejects the null hypothesis.

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
