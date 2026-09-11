# CEC2020, D=15

[MWU overview](../../README.md) · [Full results CSV](details.csv)

Contents: [Budget 3×10^6](#budget-3m) · [Deep Statistical Comparison](#deep-statistical-comparison)

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
| [3×10^6 / All functions](#budget-3m-all) | 3/7/0 | 2/6/2 | 4/3/3 | 3/5/2 | 2/5/3 | 5/3/2 |
| [3×10^6 / Composition functions](#budget-3m-composition) | 2/1/0 | 2/1/0 | 3/0/0 | 1/1/1 | 1/2/0 | 3/0/0 |

All summary cells are **W/L/NS for MSC-CMA-ES**.

<a id="budget-3m"></a>

### Budget 3×10^6

<a id="budget-3m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **10** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **0.0433389 · L** | 0.0549905 · NS | 0.130017 · NS | 1 · NS | 0.27052 · NS | 0.0866779 · NS |
| **f2** | **8.53312e-07 · W** | **1.61144e-09 · L** | 0.298181 · NS | **3.61482e-13 · L** | **3.30368e-17 · L** | 0.328447 · NS |
| **f3** | **1.39059e-19 · L** | **1.1644e-17 · W** | **2.67406e-17 · W** | **5.18597e-19 · W** | 0.350386 · NS | **2.9688e-17 · W** |
| **f4** | **7.01028e-16 · L** | **2.97331e-17 · L** | **3.84523e-07 · L** | **1.64309e-18 · L** | **3.30368e-17 · L** | **2.9688e-17 · L** |
| **f5** | **0.000182726 · L** | **0.00219348 · L** | 0.298181 · NS | **9.42688e-17 · W** | **1.31968e-16 · W** | **4.17302e-14 · W** |
| **f6** | **3.8789e-14 · L** | **8.04083e-17 · L** | **5.03814e-11 · L** | **2.80345e-17 · L** | 0.083017 · NS | **6.26283e-17 · L** |
| **f7** | **2.02625e-08 · L** | **1.71835e-10 · L** | **0.00110823 · L** | **2.17762e-11 · L** | **5.81068e-11 · L** | **2.27366e-06 · L** |
| **f8** | **1.50709e-09 · W** | **7.24596e-13 · W** | **8.91523e-18 · W** | 1 · NS | **0.00022914 · L** | **5.59245e-18 · W** |
| **f9** | **0.00734573 · L** | **4.44762e-15 · L** | **2.67406e-17 · W** | **2.45158e-14 · L** | **1.44546e-06 · L** | **2.84863e-16 · W** |
| **f10** | **2.02625e-08 · W** | 0.0549905 · NS | **1.04905e-09 · W** | **5.24525e-10 · W** | **3.22031e-09 · W** | **1.13388e-09 · W** |
| **W/L/NS** | 3/7/0 | 2/6/2 | 4/3/3 | 3/5/2 | 2/5/3 | 5/3/2 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 1198.5 | 1198.5 | 1198.5 | 1308.5 | 1430 | 1198.5 |
| f2 | 2076 | 366 | 1084.5 | 182 | 4 | 1447 |
| f3 | 0 | 2601 | 2601 | 2601 | 1440 | 2601 |
| f4 | 55 | 0 | 497 | 0 | 0 | 0 |
| f5 | 714 | 800.5 | 1457 | 2575.5 | 2572 | 2459 |
| f6 | 130 | 19 | 276 | 1 | 971 | 17 |
| f7 | 417 | 310 | 757 | 270 | 279 | 561 |
| f8 | 2237.5 | 2409 | 2601 | 1231.5 | 704 | 2601 |
| f9 | 866 | 153 | 2601 | 153 | 537 | 2553 |
| f10 | 2155 | 1629 | 2193 | 2193 | 2185 | 2193 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 0.0433389 | 0.0433389 | 0.0433389 | 0.914246 | 0.13526 | 0.0433389 |
| f2 | 2.13328e-07 | 4.02859e-10 | 0.14909 | 7.22964e-14 | 3.63294e-18 | 0.328447 |
| f3 | 1.39059e-20 | 1.1644e-18 | 3.28725e-18 | 5.18597e-20 | 0.350386 | 3.29867e-18 |
| f4 | 7.7892e-17 | 3.30368e-18 | 7.69047e-08 | 1.82566e-19 | 3.30368e-18 | 3.30297e-18 |
| f5 | 6.09086e-05 | 0.000731162 | 0.293701 | 1.3467e-17 | 1.6496e-17 | 8.34603e-15 |
| f6 | 4.84862e-15 | 1.0051e-17 | 7.19734e-12 | 3.50432e-18 | 0.0276723 | 8.94691e-18 |
| f7 | 3.41252e-09 | 3.4367e-11 | 0.000277058 | 5.44405e-12 | 8.30097e-12 | 7.57887e-07 |
| f8 | 2.15299e-10 | 1.20766e-13 | 8.91523e-19 | 0.645806 | 5.7285e-05 | 5.59245e-19 |
| f9 | 0.00367286 | 6.35374e-16 | 2.97118e-18 | 4.08597e-15 | 2.89092e-07 | 4.74772e-17 |
| f10 | 3.37708e-09 | 0.0274953 | 1.74842e-10 | 1.74842e-10 | 5.36718e-10 | 2.8347e-10 |

</details>

<a id="budget-3m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **3** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f8** | **6.45896e-10 · W** | **2.41532e-13 · W** | **2.67457e-18 · W** | 0.645806 · NS | **5.7285e-05 · L** | **1.67773e-18 · W** |
| **f9** | **0.00367286 · L** | **1.90612e-15 · L** | **5.94236e-18 · W** | **1.22579e-14 · L** | **5.78184e-07 · L** | **9.49544e-17 · W** |
| **f10** | **6.75416e-09 · W** | **0.0274953 · W** | **1.74842e-10 · W** | **3.49683e-10 · W** | **1.61015e-09 · W** | **2.8347e-10 · W** |
| **W/L/NS** | 2/1/0 | 2/1/0 | 3/0/0 | 1/1/1 | 1/2/0 | 3/0/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 2237.5 | 2409 | 2601 | 1231.5 | 704 | 2601 |
| f9 | 866 | 153 | 2601 | 153 | 537 | 2553 |
| f10 | 2155 | 1629 | 2193 | 2193 | 2185 | 2193 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 2.15299e-10 | 1.20766e-13 | 8.91523e-19 | 0.645806 | 5.7285e-05 | 5.59245e-19 |
| f9 | 0.00367286 | 6.35374e-16 | 2.97118e-18 | 4.08597e-15 | 2.89092e-07 | 4.74772e-17 |
| f10 | 3.37708e-09 | 0.0274953 | 1.74842e-10 | 1.74842e-10 | 5.36718e-10 | 2.8347e-10 |

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

<a id="dsc-budget-3m"></a>

### Budget 3×10^6

<a id="dsc-budget-3m-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 5 | 2.5 | 2.5 | 2.5 | 7 | 6 | 2.5 |
| **f2** | 4 | 5 | 2 | 6 | 3 | 1 | 7 |
| **f3** | 2 | 1 | 5 | 6 | 4 | 3 | 7 |
| **f4** | 7 | 5 | 4 | 6 | 1 | 2 | 3 |
| **f5** | 3.5 | 1.5 | 1.5 | 3.5 | 6.5 | 6.5 | 5 |
| **f6** | 6 | 4 | 3 | 5 | 1 | 7 | 2 |
| **f7** | 4 | 5.5 | 3 | 7 | 1.5 | 1.5 | 5.5 |
| **f8** | 1 | 5 | 4 | 6 | 2 | 3 | 7 |
| **f9** | 1 | 5 | 3 | 7 | 2 | 4 | 6 |
| **f10** | 1 | 3.5 | 2 | 6 | 6 | 3.5 | 6 |

Composition-function set: `f8–f10`.

<a id="dsc-budget-3m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | ARRDE | 3 | 3.45 | 3/7 | 11.1964 | 0.082492 | — | O |
| Composition functions | 3 | MSC-CMA-ES | 1 | 1 | 1/7 | 14.0357 | 0.0292397 | — | ★ |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 3×10^6 | ARRDE · 3/7 · O | MSC-CMA-ES · 1/7 · ★ |
