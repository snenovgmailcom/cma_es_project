# CEC2022 · D=20

[MWU overview](../../README.md) · [Full results CSV](details.csv)

[MWU summary](#mwu-summary) · [MWU results](#mwu-results) · [Deep Statistical Comparison](#deep-statistical-comparison)

## MWU summary

Counts are from the **MSC-CMA-ES perspective**, using 51 runs per algorithm and function. Cells report **lower / higher / not significant** pooled sample mean-rank comparisons after Holm correction:

- `<`: MSC-CMA-ES has a significantly lower pooled sample mean rank.
- `>`: MSC-CMA-ES has a significantly higher pooled sample mean rank.
- `=`: the null hypothesis is not rejected; this does not assert equality.

| Budget / function scope | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| [10^6 / All functions](#budget-1m-all) | 5/4/3 | 3/7/2 | 3/6/3 | 5/3/4 | 7/2/3 | 4/7/1 |
| [10^6 / Composition functions](#budget-1m-composition) | 1/1/2 | 2/2/0 | 2/1/1 | 2/1/1 | 2/1/1 | 2/1/1 |

All summary cells contain $n_{<}/n_{>}/n_{=}$ as defined above.

<details>
<summary>Statistical protocol and full MWU notation</summary>

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

**MWU symbols:**

For each comparison, $\bar R_M$ and $\bar R_A$ are the mean ranks of
the MSC-CMA-ES sample and the compared algorithm's sample in the pooled
sample, using average ranks for ties. These are the observation ranks
used by MWU, distinct from DSC ranks.

- **`<`**: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- **`>`**: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- **`=`**: $p_{\mathrm{Holm}}>0.05$; the null hypothesis is not rejected.

The symbol `=` denotes non-rejection of $H_0:F_M=F_A$; it does not
assert equality of the sample mean ranks.

Significance uses the full-precision adjusted p-value (`p_Holm <= 0.05`).
The mean-rank relation is obtained from U without rounding the input errors.
Summary cells contain $n_{<}/n_{>}/n_{=}$: counts of functions in the
three categories defined above.

CSV values retain full numerical precision. Only descriptive medians use
a separate copy with `abs(error) <= 1e-8` set to zero.

</details>

## MWU results

<a id="budget-1m"></a>

### Budget 10^6

<a id="budget-1m-all"></a>

#### All functions

<details>
<summary>Per-function comparisons, U statistics and raw p-values</summary>

Function scope: `all`. Holm family size: **12** per competitor.
Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **5.20675e-09 · `>`** | **0.000227846 · `>`** | **4.55591e-09 · `>`** | 0.438788 · `=` | **9.71624e-18 · `<`** | **3.25422e-09 · `>`** |
| **f2** | **2.6707e-05 · `<`** | 0.206732 · `=` | **7.06142e-20 · `<`** | **2.04638e-16 · `<`** | **6.30455e-14 · `<`** | **4.41186e-18 · `<`** |
| **f3** | **1.7615e-17 · `>`** | **4.6039e-19 · `>`** | **1.99019e-18 · `>`** | **6.21324e-19 · `>`** | **1.56647e-17 · `>`** | **1.66871e-19 · `>`** |
| **f4** | **0.0130035 · `<`** | **6.07842e-12 · `<`** | **0.0196145 · `>`** | **2.5554e-17 · `<`** | **2.32063e-17 · `<`** | **3.05274e-17 · `<`** |
| **f5** | **2.88082e-10 · `>`** | **2.24064e-10 · `>`** | **2.56073e-10 · `>`** | **0.0049032 · `>`** | 1 · `=` | **1.92054e-10 · `>`** |
| **f6** | **1.57561e-11 · `<`** | 0.175778 · `=` | 0.697539 · `=` | **1.13882e-16 · `<`** | **1.04435e-15 · `<`** | **0.0145592 · `>`** |
| **f7** | **7.67904e-05 · `<`** | **0.000403792 · `>`** | **8.05584e-09 · `>`** | 0.438788 · `=` | 1 · `=` | **0.00283131 · `>`** |
| **f8** | 0.240986 · `=` | **0.00502335 · `>`** | 0.697539 · `=` | 0.77588 · `=` | **5.15198e-07 · `<`** | **0.00335005 · `>`** |
| **f9** | 0.0795829 · `=` | **0.0239114 · `<`** | 0.477986 · `=` | 1 · `=` | **1.53032e-18 · `<`** | 0.567513 · `=` |
| **f10** | **3.91164e-11 · `<`** | **3.72262e-14 · `<`** | **3.30368e-17 · `<`** | **6.50663e-19 · `>`** | **2.32063e-17 · `>`** | **2.97331e-17 · `<`** |
| **f11** | **1.19513e-05 · `>`** | **3.92513e-13 · `>`** | **1.5455e-16 · `<`** | **8.03761e-18 · `<`** | **2.32063e-17 · `<`** | **5.91538e-18 · `<`** |
| **f12** | 0.240986 · `=` | **1.9897e-17 · `>`** | **0.000146798 · `>`** | **1.60808e-06 · `<`** | 1 · `=` | **4.41892e-16 · `>`** |
| $n_{<}/n_{>}/n_{=}$ | 5/4/3 | 3/7/2 | 3/6/3 | 5/3/4 | 7/2/3 | 4/7/1 |

##### U statistics and raw p-values

U is for the compared algorithm's sample. The symbols above describe
the MSC-CMA-ES sample's mean-rank relation after Holm correction.

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

<details>
<summary>Per-function comparisons, U statistics and raw p-values</summary>

Function scope: `composition`. Holm family size: **4** per competitor.
Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f9** | 0.0530553 · `=` | **0.00797047 · `<`** | 0.159329 · `=` | 1 · `=` | **5.10108e-19 · `<`** | 0.567513 · `=` |
| **f10** | **1.56466e-11 · `<`** | **1.11679e-14 · `<`** | **1.32147e-17 · `<`** | **2.36605e-19 · `>`** | **7.73542e-18 · `>`** | **9.91104e-18 · `<`** |
| **f11** | **5.12198e-06 · `>`** | **8.72251e-14 · `>`** | **5.15167e-17 · `<`** | **2.41128e-18 · `<`** | **7.73542e-18 · `<`** | **2.36615e-18 · `<`** |
| **f12** | 0.221491 · `=` | **7.23529e-18 · `>`** | **5.87193e-05 · `>`** | **5.36028e-07 · `<`** | 0.713257 · `=` | **1.26255e-16 · `>`** |
| $n_{<}/n_{>}/n_{=}$ | 1/1/2 | 2/2/0 | 2/1/1 | 2/1/1 | 2/1/1 | 2/1/1 |

##### U statistics and raw p-values

U is for the compared algorithm's sample. The symbols above describe
the MSC-CMA-ES sample's mean-rank relation after Holm correction.

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
The CSV `decision` field describes the compared algorithm's pooled mean rank
conditional on rejection after Holm correction: `higher` maps to `<` for
MSC-CMA-ES, `lower` to `>`, and `not significant` to `=`.

## Deep Statistical Comparison

`★` means that MSC-CMA-ES has the lowest mean DSC rank and the Friedman
test rejects the null hypothesis; `≈` means that the Friedman test
rejects the null hypothesis but the Holm-adjusted comparison between
MSC-CMA-ES and the lowest-mean-rank method is not significant; `↓` means
that the lowest-mean-rank method has a smaller mean DSC rank than
MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means
that the Friedman test does not reject the null hypothesis and no
post-hoc interpretation is made.

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 10^6 | L-SRTDE · 4/7 · O | MSC-CMA-ES · 1/7 · O |

<details>
<summary>DSC protocol</summary>

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

`p_Holm` is shown only when the lowest-mean-rank algorithm is not
MSC-CMA-ES and the Friedman test rejects the null hypothesis.

</details>

<a id="dsc-budget-1m"></a>
<a id="dsc-budget-1m-ranks"></a>
<a id="dsc-budget-1m-comparison"></a>

### Budget 10^6

<details>
<summary>DSC ranks by function and statistical comparison</summary>

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

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 12 | L-SRTDE | 3.08333 | 3.75 | 4/7 | 9.11607 | 0.167155 | — | O |
| Composition functions | 4 | MSC-CMA-ES | 3.125 | 3.125 | 1/7 | 1.63393 | 0.950107 | — | O |

</details>
