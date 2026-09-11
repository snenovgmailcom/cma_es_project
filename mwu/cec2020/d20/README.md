# CEC2020, D=20

[MWU overview](../../README.md) · [Full results CSV](details.csv)

Contents: [Budget 10^7](#budget-10m) · [Deep Statistical Comparison](#deep-statistical-comparison)

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
| [10^7 / All functions](#budget-10m-all) | 4/5/1 | 2/8/0 | 4/6/0 | 4/6/0 | 4/6/0 | 5/5/0 |
| [10^7 / Composition functions](#budget-10m-composition) | 3/0/0 | 1/2/0 | 3/0/0 | 1/2/0 | 2/1/0 | 3/0/0 |

All summary cells are **W/L/NS for MSC-CMA-ES**.

<a id="budget-10m"></a>

### Budget 10^7

<a id="budget-10m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **10** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **1.01829e-07 · L** | **2.54573e-08 · L** | **1.01829e-07 · L** | **7.6372e-08 · L** | **6.71656e-07 · L** | **2.54573e-08 · L** |
| **f2** | **7.35265e-11 · W** | **2.34196e-17 · L** | **6.13448e-17 · L** | **2.47459e-17 · L** | **2.13992e-17 · L** | **2.96687e-17 · L** |
| **f3** | **2.12535e-19 · L** | **3.83762e-19 · W** | **2.60214e-17 · W** | **1.98815e-19 · W** | **5.33813e-10 · W** | **2.96687e-17 · W** |
| **f4** | **4.79314e-16 · L** | **2.34196e-17 · L** | **7.03436e-06 · L** | **3.45293e-19 · L** | **2.96752e-17 · L** | **2.96687e-17 · L** |
| **f5** | **0.00641066 · L** | **1.65843e-09 · L** | **2.90778e-06 · L** | **1.30027e-14 · W** | **2.96752e-17 · W** | **2.7314e-13 · W** |
| **f6** | 0.0929827 · NS | **2.34196e-17 · L** | **2.60214e-17 · L** | **2.47459e-17 · L** | **2.96752e-17 · L** | **2.96687e-17 · L** |
| **f7** | **3.11826e-08 · L** | **2.00152e-15 · L** | **0.00235625 · L** | **0.0198558 · W** | **4.43402e-07 · L** | **3.37625e-17 · L** |
| **f8** | **1.11108e-14 · W** | **4.49767e-14 · W** | **6.88319e-18 · W** | **4.51299e-17 · W** | **2.58109e-16 · W** | **1.39059e-19 · W** |
| **f9** | **0.0325416 · W** | **1.40257e-17 · L** | **2.60214e-17 · W** | **4.22112e-17 · L** | **1.05102e-11 · W** | **2.96687e-17 · W** |
| **f10** | **2.34448e-09 · W** | **2.00152e-15 · L** | **4.22015e-13 · W** | **0.000698893 · L** | **5.33813e-10 · L** | **1.99719e-13 · W** |
| **W/L/NS** | 4/5/1 | 2/8/0 | 4/6/0 | 4/6/0 | 4/6/0 | 5/5/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 688.5 | 688.5 | 688.5 | 688.5 | 739.5 | 688.5 |
| f2 | 2316.5 | 0 | 20 | 3 | 0 | 7 |
| f3 | 1 | 2601 | 2601 | 2601 | 2248 | 2601 |
| f4 | 48 | 0 | 607 | 0 | 0 | 0 |
| f5 | 841.5 | 383.5 | 568.5 | 2478.5 | 2601 | 2406.5 |
| f6 | 1049 | 0 | 0 | 0 | 0 | 0 |
| f7 | 432 | 84 | 846 | 1649 | 526 | 16 |
| f8 | 2475 | 2447 | 2601 | 2567 | 2515 | 2601 |
| f9 | 1660 | 49 | 2601 | 50 | 2351 | 2601 |
| f10 | 2235 | 86 | 2397 | 766 | 342 | 2397 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 2.54573e-08 | 2.54573e-08 | 2.54573e-08 | 2.54573e-08 | 6.71656e-07 | 2.54573e-08 |
| f2 | 1.05038e-11 | 2.92745e-18 | 1.02241e-17 | 3.09324e-18 | 2.13992e-18 | 4.73535e-18 |
| f3 | 2.12535e-20 | 3.83762e-20 | 3.12849e-18 | 1.98815e-20 | 1.33453e-10 | 3.30368e-18 |
| f4 | 5.32572e-17 | 3.30368e-18 | 3.51718e-06 | 3.83658e-20 | 3.30368e-18 | 3.30225e-18 |
| f5 | 0.00213689 | 8.29214e-10 | 9.69259e-07 | 3.25069e-15 | 3.29724e-18 | 1.3657e-13 |
| f6 | 0.0929827 | 3.30297e-18 | 2.89127e-18 | 3.30368e-18 | 3.30368e-18 | 3.30368e-18 |
| f7 | 6.23653e-09 | 4.00304e-16 | 0.00235625 | 0.0198558 | 2.21701e-07 | 8.44063e-18 |
| f8 | 1.38885e-15 | 1.49922e-14 | 6.88319e-19 | 9.02598e-18 | 4.30181e-17 | 1.39059e-20 |
| f9 | 0.0162708 | 1.55841e-18 | 3.22089e-18 | 7.0352e-18 | 2.10204e-12 | 3.29653e-18 |
| f10 | 3.90747e-10 | 4.17607e-16 | 8.44029e-14 | 0.000349447 | 1.42386e-10 | 6.6573e-14 |

</details>

<a id="budget-10m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **3** per competitor.
Each cell reports **p_Holm · outcome for MSC-CMA-ES**.

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f8** | **4.16656e-15 · W** | **1.49922e-14 · W** | **2.06496e-18 · W** | **2.11056e-17 · W** | **1.29054e-16 · W** | **4.17177e-20 · W** |
| **f9** | **0.0162708 · W** | **4.67524e-18 · L** | **6.44178e-18 · W** | **2.11056e-17 · L** | **4.20409e-12 · W** | **6.59305e-18 · W** |
| **f10** | **7.81494e-10 · W** | **8.35213e-16 · L** | **8.44029e-14 · W** | **0.000349447 · L** | **1.42386e-10 · L** | **6.6573e-14 · W** |
| **W/L/NS** | 3/0/0 | 1/2/0 | 3/0/0 | 1/2/0 | 2/1/0 | 3/0/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the competitor sample; the W/L/NS outcomes above are for MSC-CMA-ES.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 2475 | 2447 | 2601 | 2567 | 2515 | 2601 |
| f9 | 1660 | 49 | 2601 | 50 | 2351 | 2601 |
| f10 | 2235 | 86 | 2397 | 766 | 342 | 2397 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f8 | 1.38885e-15 | 1.49922e-14 | 6.88319e-19 | 9.02598e-18 | 4.30181e-17 | 1.39059e-20 |
| f9 | 0.0162708 | 1.55841e-18 | 3.22089e-18 | 7.0352e-18 | 2.10204e-12 | 3.29653e-18 |
| f10 | 3.90747e-10 | 4.17607e-16 | 8.44029e-14 | 0.000349447 | 1.42386e-10 | 6.6573e-14 |

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

<a id="dsc-budget-10m"></a>

### Budget 10^7

<a id="dsc-budget-10m-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 7 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 |
| **f2** | 6 | 7 | 3 | 4.5 | 2 | 1 | 4.5 |
| **f3** | 2 | 1 | 4 | 6 | 4 | 4 | 7 |
| **f4** | 7 | 5 | 4 | 6 | 1 | 2 | 3 |
| **f5** | 3 | 4 | 1.5 | 1.5 | 7 | 6 | 5 |
| **f6** | 6.5 | 6.5 | 3 | 4 | 1 | 2 | 5 |
| **f7** | 3 | 5.5 | 2 | 5.5 | 7 | 4 | 1 |
| **f8** | 1 | 6.5 | 2 | 3.5 | 3.5 | 5 | 6.5 |
| **f9** | 3 | 4 | 1.5 | 6 | 1.5 | 5 | 7 |
| **f10** | 4 | 5 | 1 | 6.5 | 2.5 | 2.5 | 6.5 |

Composition-function set: `f8–f10`.

<a id="dsc-budget-10m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | ARRDE | 2.55 | 4.25 | 4/7 | 10.3821 | 0.109454 | — | O |
| Composition functions | 3 | ARRDE | 1.5 | 2.66667 | 3/7 | 13.2143 | 0.0397565 | 0.508332 | ≈ |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 10^7 | ARRDE · 4/7 · O | ARRDE · 3/7 · ≈ |
