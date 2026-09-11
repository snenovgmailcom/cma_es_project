# CEC2020, D=5

[MWU overview](../../README.md) · [Full results CSV](details.csv)

Contents: [Budget 5×10^4](#budget-50k) · [Budget 10^6](#budget-1m) · [Deep Statistical Comparison](#deep-statistical-comparison)

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
| [5×10^4 / All functions](#budget-50k-all) | 3/5/2 | 2/8/0 | 3/6/1 | 1/8/1 | 3/5/2 | 3/7/0 |
| [5×10^4 / Composition functions](#budget-50k-composition) | 2/1/0 | 1/2/0 | 2/1/0 | 1/2/0 | 2/0/1 | 2/1/0 |
| [10^6 / All functions](#budget-1m-all) | 3/5/2 | 0/9/1 | 4/4/2 | 1/8/1 | 1/8/1 | 3/6/1 |
| [10^6 / Composition functions](#budget-1m-composition) | 1/1/1 | 0/3/0 | 2/1/0 | 1/2/0 | 1/2/0 | 2/1/0 |

All summary cells are **W/L/NS for MSC-CMA-ES**.

<a id="budget-50k"></a>

### Budget 5×10^4

<a id="budget-50k-all"></a>

#### All functions

Function scope: `all`. Holm family size: **10** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **2.48489e-13 · L** | **4.47483e-09 · L** | **7.09449e-11 · L** | **1.1044e-13 · L** | **0.00161195 · L** | **1.1044e-13 · L** |
| **f2** | 0.739872 · NS | **0.0100752 · L** | **2.6013e-07 · L** | **3.01965e-15 · L** | 0.227578 · NS | **2.68916e-08 · L** |
| **f3** | **2.63746e-05 · W** | **0.000200526 · W** | **2.98409e-08 · W** | 0.0513902 · NS | **0.00294845 · W** | **2.12184e-05 · W** |
| **f4** | **1.42516e-08 · L** | **4.75692e-15 · L** | **6.52803e-08 · L** | **8.69468e-18 · L** | **8.78713e-15 · L** | **5.17295e-15 · L** |
| **f5** | 0.739872 · NS | **1.55276e-08 · L** | 0.0685021 · NS | **5.03669e-12 · L** | **0.00294845 · L** | **3.11767e-09 · L** |
| **f6** | **7.77421e-12 · L** | **7.00808e-18 · L** | **2.24325e-09 · L** | **1.59008e-19 · L** | **1.42932e-17 · L** | **1.3902e-19 · L** |
| **f7** | **1.64358e-08 · L** | **3.83245e-19 · L** | **2.6013e-07 · L** | **1.34265e-19 · L** | **1.3902e-19 · L** | **1.3902e-19 · L** |
| **f8** | **0.00669505 · L** | **1.11456e-08 · L** | **1.48032e-07 · L** | **1.34265e-19 · L** | 0.84321 · NS | **2.45102e-19 · L** |
| **f9** | **4.02216e-08 · W** | **0.00966799 · L** | **1.98705e-19 · W** | **3.01965e-15 · L** | **1.91573e-05 · W** | **1.94982e-19 · W** |
| **f10** | **7.91671e-14 · W** | **1.23509e-05 · W** | **5.05953e-18 · W** | **4.9702e-07 · W** | **1.75589e-10 · W** | **1.59052e-19 · W** |
| **W/L/NS** | 3/5/2 | 2/8/0 | 3/6/1 | 1/8/1 | 3/5/2 | 3/7/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 306 | 426 | 396 | 306 | 763.5 | 306 |
| f2 | 1229.5 | 916.5 | 517.5 | 97 | 1064 | 455 |
| f3 | 1973 | 1895.5 | 2173 | 1013.5 | 1794.5 | 1927 |
| f4 | 404.5 | 92.5 | 452.5 | 30.5 | 102.5 | 101.5 |
| f5 | 1431.5 | 511.5 | 1041 | 408 | 814.5 | 504 |
| f6 | 234 | 0 | 394 | 0 | 0 | 0 |
| f7 | 411.5 | 0 | 525 | 0 | 0 | 0 |
| f8 | 846 | 408.5 | 505 | 0 | 1330.5 | 1.5 |
| f9 | 2162 | 879 | 2601 | 153 | 1996.5 | 2601 |
| f10 | 2451 | 1998 | 2601 | 2068 | 2298 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 2.76099e-14 | 6.39262e-10 | 8.86812e-12 | 2.76099e-14 | 0.00032239 | 2.76099e-14 |
| f2 | 0.63654 | 0.0100752 | 1.2511e-07 | 5.31351e-16 | 0.113789 | 1.34458e-08 |
| f3 | 6.59364e-06 | 6.6842e-05 | 4.97349e-09 | 0.0513902 | 0.000951347 | 2.12184e-05 |
| f4 | 2.03595e-09 | 5.94615e-16 | 1.30561e-08 | 1.2421e-18 | 1.09839e-15 | 1.03459e-15 |
| f5 | 0.369936 | 3.10552e-09 | 0.0685021 | 1.6789e-12 | 0.000737113 | 1.03922e-09 |
| f6 | 9.71776e-13 | 7.78675e-19 | 3.20464e-10 | 1.9876e-20 | 1.58813e-18 | 1.3902e-20 |
| f7 | 2.7393e-09 | 3.83245e-20 | 8.67099e-08 | 1.3902e-20 | 1.3902e-20 | 1.3902e-20 |
| f8 | 0.00223168 | 1.8576e-09 | 3.70081e-08 | 1.34265e-20 | 0.84321 | 4.08503e-20 |
| f9 | 8.04431e-09 | 0.004834 | 1.98705e-20 | 5.03275e-16 | 3.19288e-06 | 2.78546e-20 |
| f10 | 7.91671e-15 | 3.08773e-06 | 5.6217e-19 | 2.4851e-07 | 2.50841e-11 | 1.98815e-20 |

</details>

<a id="budget-50k-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **3** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f8** | **0.00223168 · L** | **5.57279e-09 · L** | **3.70081e-08 · L** | **4.02796e-20 · L** | 0.84321 · NS | **5.96446e-20 · L** |
| **f9** | **1.60886e-08 · W** | **0.004834 · L** | **5.96114e-20 · W** | **1.00655e-15 · L** | **6.38575e-06 · W** | **5.96446e-20 · W** |
| **f10** | **2.37501e-14 · W** | **6.17546e-06 · W** | **1.12434e-18 · W** | **2.4851e-07 · W** | **7.52523e-11 · W** | **5.96446e-20 · W** |
| **W/L/NS** | 2/1/0 | 1/2/0 | 2/1/0 | 1/2/0 | 2/0/1 | 2/1/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 846 | 408.5 | 505 | 0 | 1330.5 | 1.5 |
| f9 | 2162 | 879 | 2601 | 153 | 1996.5 | 2601 |
| f10 | 2451 | 1998 | 2601 | 2068 | 2298 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 0.00223168 | 1.8576e-09 | 3.70081e-08 | 1.34265e-20 | 0.84321 | 4.08503e-20 |
| f9 | 8.04431e-09 | 0.004834 | 1.98705e-20 | 5.03275e-16 | 3.19288e-06 | 2.78546e-20 |
| f10 | 7.91671e-15 | 3.08773e-06 | 5.6217e-19 | 2.4851e-07 | 2.50841e-11 | 1.98815e-20 |

</details>

<a id="budget-1m"></a>

### Budget 10^6

<a id="budget-1m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **10** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 0.653785 · NS | 0.326893 · NS | 1 · NS | 0.326893 · NS | 0.326893 · NS | 0.326893 · NS |
| **f2** | **0.00187974 · W** | **2.23166e-16 · L** | **0.0226807 · W** | **8.57185e-20 · L** | **3.23031e-17 · L** | **1.61317e-18 · L** |
| **f3** | **2.32236e-13 · W** | **0.000717782 · L** | **1.62999e-17 · W** | **0.0458967 · L** | **2.06209e-09 · L** | **2.38653e-14 · W** |
| **f4** | **9.33776e-18 · L** | **6.50377e-18 · L** | **0.000170973 · L** | **9.81862e-19 · L** | **2.84508e-15 · L** | **6.04848e-14 · L** |
| **f5** | **1.55888e-06 · L** | **1.16916e-06 · L** | 0.195805 · NS | **1.16916e-06 · L** | **1.16916e-06 · L** | **7.7944e-07 · L** |
| **f6** | **2.6418e-17 · L** | **1.24906e-19 · L** | **9.2054e-16 · L** | **1.11027e-19 · L** | **1.25153e-19 · L** | **1.39059e-19 · L** |
| **f7** | **2.6418e-17 · L** | **1.24906e-19 · L** | **1.27868e-05 · L** | **1.11027e-19 · L** | **1.25153e-19 · L** | **1.39059e-19 · L** |
| **f8** | **7.1447e-18 · L** | **1.08034e-19 · L** | **0.00365529 · L** | **9.72303e-20 · L** | **1.08034e-19 · L** | **2.08438e-15 · L** |
| **f9** | 0.653785 · NS | **1.24906e-19 · L** | **1.98429e-19 · W** | **1.11027e-19 · L** | **1.94716e-19 · L** | **4.58835e-18 · W** |
| **f10** | **4.16184e-15 · W** | **1.37368e-11 · L** | **6.74788e-18 · W** | **7.78903e-10 · W** | **0.000172005 · W** | **1.58875e-19 · W** |
| **W/L/NS** | 3/5/2 | 0/9/1 | 4/4/2 | 1/8/1 | 1/8/1 | 3/6/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 1275 | 1275 | 1301 | 1275 | 1275 | 1275 |
| f2 | 1805.5 | 78.5 | 1693 | 0 | 60 | 26.5 |
| f3 | 2410 | 841 | 2601 | 1001 | 561 | 2401 |
| f4 | 71 | 56.5 | 684 | 51 | 111 | 163 |
| f5 | 765 | 765 | 1521 | 765 | 765 | 765 |
| f6 | 0 | 0 | 126 | 0 | 0 | 0 |
| f7 | 1 | 0 | 612 | 0 | 0 | 0 |
| f8 | 53.5 | 0 | 816 | 0 | 0 | 153 |
| f9 | 1439 | 0 | 2601 | 0 | 0 | 2550 |
| f10 | 2507 | 306 | 2601 | 2244 | 1887 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 0.326893 | 0.326893 | 1 | 0.326893 | 0.326893 | 0.326893 |
| f2 | 0.000626582 | 4.46331e-17 | 0.00756024 | 8.57185e-21 | 5.38385e-18 | 2.30453e-19 |
| f3 | 4.64473e-14 | 0.000358891 | 2.03748e-18 | 0.0229483 | 5.15523e-10 | 5.96632e-15 |
| f4 | 1.03753e-18 | 1.08396e-18 | 3.41947e-05 | 1.96372e-19 | 5.69016e-16 | 2.01616e-14 |
| f5 | 3.8972e-07 | 3.8972e-07 | 0.0979026 | 3.8972e-07 | 3.8972e-07 | 3.8972e-07 |
| f6 | 3.30225e-18 | 1.39059e-20 | 1.31506e-16 | 1.39059e-20 | 1.39059e-20 | 1.39059e-20 |
| f7 | 3.47184e-18 | 1.39059e-20 | 2.13114e-06 | 1.39059e-20 | 1.39059e-20 | 1.39059e-20 |
| f8 | 7.1447e-19 | 1.08034e-20 | 0.000913823 | 1.08034e-20 | 1.08034e-20 | 4.16876e-16 |
| f9 | 0.354486 | 1.38784e-20 | 1.98429e-20 | 1.38784e-20 | 2.78165e-20 | 7.64725e-19 |
| f10 | 6.9364e-16 | 3.43419e-12 | 7.49765e-19 | 1.94726e-10 | 8.60027e-05 | 1.98594e-20 |

</details>

<a id="budget-1m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **3** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f8** | **2.14341e-18 · L** | **3.24101e-20 · L** | **0.000913823 · L** | **3.24101e-20 · L** | **3.24101e-20 · L** | **4.16876e-16 · L** |
| **f9** | 0.354486 · NS | **3.24101e-20 · L** | **5.95286e-20 · W** | **3.24101e-20 · L** | **5.5633e-20 · L** | **1.52945e-18 · W** |
| **f10** | **1.38728e-15 · W** | **3.43419e-12 · L** | **1.49953e-18 · W** | **1.94726e-10 · W** | **8.60027e-05 · W** | **5.95783e-20 · W** |
| **W/L/NS** | 1/1/1 | 0/3/0 | 2/1/0 | 1/2/0 | 1/2/0 | 2/1/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 53.5 | 0 | 816 | 0 | 0 | 153 |
| f9 | 1439 | 0 | 2601 | 0 | 0 | 2550 |
| f10 | 2507 | 306 | 2601 | 2244 | 1887 | 2601 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 7.1447e-19 | 1.08034e-20 | 0.000913823 | 1.08034e-20 | 1.08034e-20 | 4.16876e-16 |
| f9 | 0.354486 | 1.38784e-20 | 1.98429e-20 | 1.38784e-20 | 2.78165e-20 | 7.64725e-19 |
| f10 | 6.9364e-16 | 3.43419e-12 | 7.49765e-19 | 1.94726e-10 | 8.60027e-05 | 1.98594e-20 |

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

<a id="dsc-budget-50k"></a>

### Budget 5×10^4

<a id="dsc-budget-50k-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 3 | 5.5 | 1 | 5.5 | 5.5 | 2 | 5.5 |
| **f2** | 5.5 | 5.5 | 5.5 | 2.5 | 1 | 5.5 | 2.5 |
| **f3** | 2 | 5 | 4 | 7 | 1 | 3 | 6 |
| **f4** | 7 | 5.5 | 3 | 5.5 | 1 | 3 | 3 |
| **f5** | 5 | 6 | 2 | 7 | 1 | 3 | 4 |
| **f6** | 7 | 5 | 3 | 6 | 2 | 4 | 1 |
| **f7** | 6 | 5 | 2.5 | 7 | 2.5 | 2.5 | 2.5 |
| **f8** | 4 | 6 | 3 | 7 | 1 | 5 | 2 |
| **f9** | 1 | 5 | 3 | 6.5 | 2 | 4 | 6.5 |
| **f10** | 1 | 5 | 2.5 | 6 | 4 | 2.5 | 7 |

Composition-function set: `f8–f10`.

<a id="dsc-budget-50k-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | NL-SHADE-RSP | 2.1 | 4.15 | 5/7 | 23.2714 | 0.000710485 | 0.0676836 | ≈ |
| Composition functions | 3 | MSC-CMA-ES | 2 | 2 | 1/7 | 11.2857 | 0.0799374 | — | O |

<a id="dsc-budget-1m"></a>

### Budget 10^6

<a id="dsc-budget-1m-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| **f2** | 5 | 6 | 4 | 7 | 1 | 3 | 2 |
| **f3** | 2 | 5 | 3.5 | 7 | 3.5 | 1 | 6 |
| **f4** | 7 | 2 | 2 | 6 | 2 | 4 | 5 |
| **f5** | 6 | 3 | 3 | 7 | 3 | 3 | 3 |
| **f6** | 7 | 1 | 4 | 4 | 4 | 4 | 4 |
| **f7** | 6 | 5 | 2.5 | 7 | 2.5 | 2.5 | 2.5 |
| **f8** | 1 | 4 | 4 | 7 | 4 | 4 | 4 |
| **f9** | 4 | 5 | 2 | 6.5 | 2 | 2 | 6.5 |
| **f10** | 1 | 4 | 2 | 6 | 5 | 3 | 7 |

Composition-function set: `f8–f10`.

<a id="dsc-budget-1m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | j2020 | 3.05 | 4.3 | 5/7 | 15.8679 | 0.0144811 | 0.405746 | ≈ |
| Composition functions | 3 | MSC-CMA-ES | 2 | 2 | 1/7 | 10.6786 | 0.0988332 | — | O |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 5×10^4 | NL-SHADE-RSP · 5/7 · ≈ | MSC-CMA-ES · 1/7 · O |
| 10^6 | j2020 · 5/7 · ≈ | MSC-CMA-ES · 1/7 · O |
