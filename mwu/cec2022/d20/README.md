# CEC2022, D=20

[MWU overview](../../README.md) · [Full results CSV](details.csv)

Contents: [Budget 10^6](#budget-1m) · [Deep Statistical Comparison](#deep-statistical-comparison)

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
| [10^6 / All functions](#budget-1m-all) | 5/4/3 | 3/7/2 | 3/6/3 | 5/3/4 | 7/2/3 | 4/7/1 |
| [10^6 / Composition functions](#budget-1m-composition) | 1/1/2 | 2/2/0 | 2/1/1 | 2/1/1 | 2/1/1 | 2/1/1 |

All summary cells are **W/L/NS for MSC-CMA-ES**.

<a id="budget-1m"></a>

### Budget 10^6

<a id="budget-1m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **12** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **5.20675e-09 · L** | **0.000227846 · L** | **4.55591e-09 · L** | 0.438788 · NS | **9.71624e-18 · W** | **3.25422e-09 · L** |
| **f2** | **2.6707e-05 · W** | 0.206732 · NS | **7.06142e-20 · W** | **2.04638e-16 · W** | **6.30455e-14 · W** | **4.41186e-18 · W** |
| **f3** | **1.7615e-17 · L** | **4.6039e-19 · L** | **1.99019e-18 · L** | **6.21324e-19 · L** | **1.56647e-17 · L** | **1.66871e-19 · L** |
| **f4** | **0.0130035 · W** | **6.07842e-12 · W** | **0.0196145 · L** | **2.5554e-17 · W** | **2.32063e-17 · W** | **3.05274e-17 · W** |
| **f5** | **2.88082e-10 · L** | **2.24064e-10 · L** | **2.56073e-10 · L** | **0.0049032 · L** | 1 · NS | **1.92054e-10 · L** |
| **f6** | **1.57561e-11 · W** | 0.175778 · NS | 0.697539 · NS | **1.13882e-16 · W** | **1.04435e-15 · W** | **0.0145592 · L** |
| **f7** | **7.67904e-05 · W** | **0.000403792 · L** | **8.05584e-09 · L** | 0.438788 · NS | 1 · NS | **0.00283131 · L** |
| **f8** | 0.240986 · NS | **0.00502335 · L** | 0.697539 · NS | 0.77588 · NS | **5.15198e-07 · W** | **0.00335005 · L** |
| **f9** | 0.0795829 · NS | **0.0239114 · W** | 0.477986 · NS | 1 · NS | **1.53032e-18 · W** | 0.567513 · NS |
| **f10** | **3.91164e-11 · W** | **3.72262e-14 · W** | **3.30368e-17 · W** | **6.50663e-19 · L** | **2.32063e-17 · L** | **2.97331e-17 · W** |
| **f11** | **1.19513e-05 · L** | **3.92513e-13 · L** | **1.5455e-16 · W** | **8.03761e-18 · W** | **2.32063e-17 · W** | **5.91538e-18 · W** |
| **f12** | 0.240986 · NS | **1.9897e-17 · L** | **0.000146798 · L** | **1.60808e-06 · W** | 1 · NS | **4.41892e-16 · L** |
| **W/L/NS** | 5/4/3 | 3/7/2 | 3/6/3 | 5/3/4 | 7/2/3 | 4/7/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 586.5 | 790.5 | 586.5 | 1109 | 2601 | 586.5 |
| f2 | 1948.5 | 1134.5 | 2601 | 2539 | 2439 | 2601 |
| f3 | 0 | 0 | 0 | 0 | 0 | 0 |
| f4 | 1730 | 2351.5 | 890.5 | 2601 | 2601 | 2592 |
| f5 | 484.5 | 484.5 | 484.5 | 848 | 1227 | 484.5 |
| f6 | 2359 | 1045 | 1173 | 2576 | 2532 | 899 |
| f7 | 1947 | 711 | 400 | 1061 | 1266 | 794 |
| f8 | 1068 | 818 | 1441 | 1171 | 2090 | 813 |
| f9 | 1176 | 1530 | 1249.5 | 1300.5 | 2473.5 | 1275 |
| f10 | 2338 | 2476 | 2601 | 2 | 0 | 2601 |
| f11 | 585 | 204 | 2550 | 2601 | 2601 | 2601 |
| f12 | 1474.5 | 0 | 681 | 2064 | 1245.5 | 64 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 6.50844e-10 | 3.79743e-05 | 6.50844e-10 | 0.145877 | 8.83294e-19 | 6.50844e-10 |
| f2 | 4.45116e-06 | 0.206732 | 5.88451e-21 | 2.92341e-17 | 1.26091e-14 | 4.01078e-19 |
| f3 | 1.46792e-18 | 3.83658e-20 | 1.80926e-19 | 5.1777e-20 | 1.56647e-18 | 1.39059e-20 |
| f4 | 0.00325088 | 7.59803e-13 | 0.00490363 | 2.83933e-18 | 2.83995e-18 | 3.81592e-18 |
| f5 | 3.20091e-11 | 3.20091e-11 | 3.20091e-11 | 0.000980639 | 0.618453 | 3.20091e-11 |
| f6 | 1.43237e-12 | 0.0878889 | 0.387187 | 1.42352e-17 | 1.74059e-16 | 0.00727959 |
| f7 | 1.53581e-05 | 8.07584e-05 | 1.34264e-09 | 0.109697 | 0.819995 | 0.000707828 |
| f8 | 0.120493 | 0.00125584 | 0.348769 | 0.38794 | 1.28799e-07 | 0.00111668 |
| f9 | 0.0265276 | 0.00797047 | 0.159329 | 1 | 1.27527e-19 | 0.567513 |
| f10 | 3.91164e-12 | 3.72262e-15 | 3.30368e-18 | 5.91512e-20 | 3.30297e-18 | 3.30368e-18 |
| f11 | 1.70733e-06 | 4.36125e-14 | 1.71722e-17 | 8.03761e-19 | 2.57847e-18 | 5.91538e-19 |
| f12 | 0.221491 | 1.80882e-18 | 2.93596e-05 | 2.68014e-07 | 0.713257 | 6.31274e-17 |

</details>

<a id="budget-1m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **4** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f9** | 0.0530553 · NS | **0.00797047 · W** | 0.159329 · NS | 1 · NS | **5.10108e-19 · W** | 0.567513 · NS |
| **f10** | **1.56466e-11 · W** | **1.11679e-14 · W** | **1.32147e-17 · W** | **2.36605e-19 · L** | **7.73542e-18 · L** | **9.91104e-18 · W** |
| **f11** | **5.12198e-06 · L** | **8.72251e-14 · L** | **5.15167e-17 · W** | **2.41128e-18 · W** | **7.73542e-18 · W** | **2.36615e-18 · W** |
| **f12** | 0.221491 · NS | **7.23529e-18 · L** | **5.87193e-05 · L** | **5.36028e-07 · W** | 0.713257 · NS | **1.26255e-16 · L** |
| **W/L/NS** | 1/1/2 | 2/2/0 | 2/1/1 | 2/1/1 | 2/1/1 | 2/1/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f9 | 1176 | 1530 | 1249.5 | 1300.5 | 2473.5 | 1275 |
| f10 | 2338 | 2476 | 2601 | 2 | 0 | 2601 |
| f11 | 585 | 204 | 2550 | 2601 | 2601 | 2601 |
| f12 | 1474.5 | 0 | 681 | 2064 | 1245.5 | 64 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f9 | 0.0265276 | 0.00797047 | 0.159329 | 1 | 1.27527e-19 | 0.567513 |
| f10 | 3.91164e-12 | 3.72262e-15 | 3.30368e-18 | 5.91512e-20 | 3.30297e-18 | 3.30368e-18 |
| f11 | 1.70733e-06 | 4.36125e-14 | 1.71722e-17 | 8.03761e-19 | 2.57847e-18 | 5.91538e-19 |
| f12 | 0.221491 | 1.80882e-18 | 2.93596e-05 | 2.68014e-07 | 0.713257 | 6.31274e-17 |

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
| **f1** | 5 | 2 | 4 | 2 | 7 | 6 | 2 |
| **f2** | 1.5 | 4 | 1.5 | 5.5 | 5.5 | 3 | 7 |
| **f3** | 7 | 4 | 6 | 1 | 2 | 5 | 3 |
| **f4** | 2 | 3 | 4 | 1 | 7 | 6 | 5 |
| **f5** | 6 | 2.5 | 2.5 | 2.5 | 7 | 5 | 2.5 |
| **f6** | 4 | 6 | 2 | 3 | 7 | 5 | 1 |
| **f7** | 6 | 7 | 3 | 1 | 4 | 5 | 2 |
| **f8** | 1 | 5 | 4 | 2 | 6 | 7 | 3 |
| **f9** | 3 | 3 | 6 | 3 | 3 | 7 | 3 |
| **f10** | 3 | 4 | 5 | 6 | 2 | 1 | 7 |
| **f11** | 1 | 3 | 2 | 7 | 5 | 4 | 6 |
| **f12** | 5.5 | 5.5 | 1 | 3 | 7 | 4 | 2 |

Composition-function set: `f9–f12`.

<a id="dsc-budget-1m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 12 | L-SRTDE | 3.08333 | 3.75 | 4/7 | 9.11607 | 0.167155 | — | O |
| Composition functions | 4 | MSC-CMA-ES | 3.125 | 3.125 | 1/7 | 1.63393 | 0.950107 | — | O |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 10^6 | L-SRTDE · 4/7 · O | MSC-CMA-ES · 1/7 · O |
