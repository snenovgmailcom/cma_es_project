# CEC2022, D=10

[MWU overview](../../README.md) · [Full results CSV](details.csv)

Contents: [Budget 2×10^5](#budget-200k) · [Budget 10^6](#budget-1m) · [Deep Statistical Comparison](#deep-statistical-comparison)

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

### Summary

| Budget / function scope | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| [2×10^5 / All functions](#budget-200k-all) | 2/4/6 | 2/7/3 | 2/6/4 | 4/8/0 | 5/7/0 | 3/8/1 |
| [2×10^5 / Composition functions](#budget-200k-composition) | 2/1/1 | 0/2/2 | 2/1/1 | 2/2/0 | 1/3/0 | 2/1/1 |
| [10^6 / All functions](#budget-1m-all) | 4/4/4 | 1/8/3 | 5/5/2 | 2/8/2 | 2/7/3 | 4/6/2 |
| [10^6 / Composition functions](#budget-1m-composition) | 3/1/0 | 0/3/1 | 3/1/0 | 1/3/0 | 0/3/1 | 3/1/0 |

All summary cells contain $n_{<}/n_{>}/n_{=}$ as defined above.

<a id="budget-200k"></a>

### Budget 2×10^5

<a id="budget-200k-all"></a>

#### All functions

Function scope: `all`. Holm family size: **12** per competitor.
Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **6.43248e-05 · `>`** | 1 · `=` | **5.00304e-05 · `>`** | **0.00396251 · `>`** | **1.07257e-16 · `<`** | **2.85888e-05 · `>`** |
| **f2** | **0.00145844 · `<`** | **0.00534929 · `<`** | 0.886233 · `=` | **0.0146176 · `<`** | **1.07257e-16 · `<`** | **0.00207607 · `>`** |
| **f3** | **1.66871e-19 · `>`** | **1.40074e-18 · `>`** | **3.21488e-18 · `>`** | **1.66871e-19 · `>`** | **1.84682e-17 · `>`** | **8.98037e-18 · `>`** |
| **f4** | 1 · `=` | **5.16506e-08 · `<`** | 0.205862 · `=` | **1.70346e-17 · `<`** | **1.78468e-17 · `<`** | **1.6596e-16 · `<`** |
| **f5** | **1.53801e-07 · `>`** | **3.7327e-07 · `>`** | **1.38421e-07 · `>`** | **9.93833e-06 · `>`** | **0.0248897 · `<`** | **7.69004e-08 · `>`** |
| **f6** | 0.153187 · `=` | **9.12479e-06 · `>`** | 0.205862 · `=` | **7.14611e-05 · `>`** | **0.0248897 · `>`** | **4.56092e-14 · `>`** |
| **f7** | 0.639568 · `=` | **4.7209e-16 · `>`** | **3.98852e-07 · `>`** | **2.59141e-14 · `>`** | **1.78468e-17 · `>`** | **2.96902e-11 · `>`** |
| **f8** | 0.232881 · `=` | **9.67334e-14 · `>`** | **0.0062411 · `>`** | **4.43759e-14 · `>`** | **2.83749e-09 · `>`** | **9.55362e-12 · `>`** |
| **f9** | **0.0163315 · `<`** | 0.470155 · `=` | **0.0116654 · `<`** | **0.0303986 · `<`** | **0.0248897 · `<`** | **0.00466615 · `<`** |
| **f10** | 0.137248 · `=` | 1 · `=` | 0.205862 · `=` | **6.2412e-16 · `>`** | **2.64295e-17 · `>`** | 0.0609362 · `=` |
| **f11** | **3.52686e-17 · `>`** | **2.43762e-18 · `>`** | **7.56617e-18 · `>`** | **3.06317e-19 · `>`** | **1.1662e-17 · `>`** | **1.04269e-17 · `>`** |
| **f12** | 1 · `=` | **2.97265e-13 · `>`** | **3.91624e-17 · `<`** | **1.66646e-05 · `<`** | **1.47391e-15 · `>`** | **3.27823e-15 · `<`** |
| $n_{<}/n_{>}/n_{=}$ | 2/4/6 | 2/7/3 | 2/6/4 | 4/8/0 | 5/7/0 | 3/8/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the compared algorithm's sample. The symbols above describe
the MSC-CMA-ES sample's mean-rank relation after Holm correction.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 867 | 1258 | 867 | 969 | 2541.5 | 867 |
| f2 | 1808 | 1725.5 | 1318.5 | 1661 | 2550 | 943.5 |
| f3 | 0 | 0 | 0 | 0 | 0 | 0 |
| f4 | 1291 | 2133.5 | 1067 | 2601 | 2601 | 2553.5 |
| f5 | 663 | 682 | 663 | 738 | 1667 | 663 |
| f6 | 1624 | 587 | 1009 | 659 | 934 | 133 |
| f7 | 1487 | 63 | 498 | 136 | 0 | 268 |
| f8 | 1584 | 145 | 810 | 135 | 379 | 241 |
| f9 | 1555.5 | 1450.5 | 1555.5 | 1494.5 | 1525 | 1555.5 |
| f10 | 1641 | 1331 | 1581 | 62 | 0 | 1581 |
| f11 | 0 | 0 | 0 | 0 | 0 | 0 |
| f12 | 1293 | 178.5 | 2571 | 1991.5 | 85.5 | 2491 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 7.1472e-06 | 0.727102 | 7.1472e-06 | 0.00132084 | 1.57161e-17 | 7.1472e-06 |
| f2 | 0.000182305 | 0.00133732 | 0.886233 | 0.00730878 | 1.53224e-17 | 0.000692024 |
| f3 | 1.39059e-20 | 1.16728e-19 | 2.67906e-19 | 1.39059e-20 | 2.05202e-18 | 7.48364e-19 |
| f4 | 0.947273 | 7.37865e-09 | 0.0763574 | 1.70346e-18 | 1.71111e-18 | 1.6596e-17 |
| f5 | 1.53801e-08 | 6.22117e-08 | 1.53801e-08 | 1.65639e-06 | 0.00829657 | 1.53801e-08 |
| f6 | 0.0306374 | 1.82496e-06 | 0.0514655 | 1.78653e-05 | 0.0143042 | 5.70115e-15 |
| f7 | 0.213189 | 4.7209e-17 | 4.98565e-08 | 3.23926e-15 | 1.62244e-18 | 4.94837e-12 |
| f8 | 0.0582202 | 1.07482e-14 | 0.00104018 | 6.33942e-15 | 7.09374e-10 | 1.3648e-12 |
| f9 | 0.00233307 | 0.156718 | 0.00233307 | 0.0303986 | 0.00966985 | 0.00233307 |
| f10 | 0.0228747 | 0.84087 | 0.0609362 | 6.93466e-17 | 3.30368e-18 | 0.0609362 |
| f11 | 3.20624e-18 | 2.21602e-19 | 6.87834e-19 | 2.7847e-20 | 9.71836e-19 | 9.47901e-19 |
| f12 | 0.961817 | 3.71581e-14 | 3.91624e-18 | 3.33292e-06 | 2.94781e-16 | 3.64248e-16 |

</details>

<a id="budget-200k-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **4** per competitor.
Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f9** | **0.00699922 · `<`** | 0.313437 · `=` | **0.00466615 · `<`** | **0.0303986 · `<`** | **0.00966985 · `<`** | **0.00466615 · `<`** |
| **f10** | **0.0457494 · `<`** | 0.84087 · `=` | 0.0609362 · `=` | **2.0804e-16 · `>`** | **9.91104e-18 · `>`** | 0.0609362 · `=` |
| **f11** | **1.2825e-17 · `>`** | **8.86407e-19 · `>`** | **2.75134e-18 · `>`** | **1.11388e-19 · `>`** | **3.88734e-18 · `>`** | **3.7916e-18 · `>`** |
| **f12** | 0.961817 · `=` | **1.11474e-13 · `>`** | **1.17487e-17 · `<`** | **6.66584e-06 · `<`** | **5.89563e-16 · `>`** | **1.09274e-15 · `<`** |
| $n_{<}/n_{>}/n_{=}$ | 2/1/1 | 0/2/2 | 2/1/1 | 2/2/0 | 1/3/0 | 2/1/1 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the compared algorithm's sample. The symbols above describe
the MSC-CMA-ES sample's mean-rank relation after Holm correction.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f9 | 1555.5 | 1450.5 | 1555.5 | 1494.5 | 1525 | 1555.5 |
| f10 | 1641 | 1331 | 1581 | 62 | 0 | 1581 |
| f11 | 0 | 0 | 0 | 0 | 0 | 0 |
| f12 | 1293 | 178.5 | 2571 | 1991.5 | 85.5 | 2491 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f9 | 0.00233307 | 0.156718 | 0.00233307 | 0.0303986 | 0.00966985 | 0.00233307 |
| f10 | 0.0228747 | 0.84087 | 0.0609362 | 6.93466e-17 | 3.30368e-18 | 0.0609362 |
| f11 | 3.20624e-18 | 2.21602e-19 | 6.87834e-19 | 2.7847e-20 | 9.71836e-19 | 9.47901e-19 |
| f12 | 0.961817 | 3.71581e-14 | 3.91624e-18 | 3.33292e-06 | 2.94781e-16 | 3.64248e-16 |

</details>

<a id="budget-1m"></a>

### Budget 10^6

<a id="budget-1m-all"></a>

#### All functions

Function scope: `all`. Holm family size: **12** per competitor.
Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1 · `=` | 0.980678 · `=` | 0.326893 · `=` | 0.326893 · `=` | 0.567513 · `=` | 0.326893 · `=` |
| **f2** | **0.000393053 · `<`** | 0.980678 · `=` | **0.000933083 · `<`** | 0.178778 · `=` | **2.17423e-19 · `<`** | 0.175501 · `=` |
| **f3** | **4.49821e-18 · `>`** | **5.04875e-18 · `>`** | **2.38578e-19 · `>`** | **1.66871e-19 · `>`** | **1.66871e-19 · `>`** | **6.19487e-18 · `>`** |
| **f4** | 1 · `=` | **6.45664e-10 · `<`** | **1.7199e-05 · `<`** | **1.71903e-19 · `<`** | **2.17423e-19 · `<`** | **9.26781e-20 · `<`** |
| **f5** | **6.36713e-05 · `>`** | **3.97945e-05 · `>`** | **3.97945e-05 · `>`** | **2.38767e-05 · `>`** | 0.161339 · `=` | **2.38767e-05 · `>`** |
| **f6** | **0.0114007 · `>`** | **1.33013e-16 · `>`** | **0.00257774 · `>`** | **1.65732e-13 · `>`** | **8.76836e-15 · `>`** | **8.34708e-16 · `>`** |
| **f7** | 1 · `=` | **3.51005e-18 · `>`** | 0.177332 · `=` | **1.66871e-19 · `>`** | **5.55872e-18 · `>`** | **3.35187e-18 · `>`** |
| **f8** | 1 · `=` | **3.7621e-17 · `>`** | **1.7199e-05 · `>`** | **2.10663e-16 · `>`** | **2.83749e-09 · `>`** | **3.67043e-15 · `>`** |
| **f9** | **2.48597e-13 · `<`** | **0.00136524 · `>`** | **2.20976e-13 · `<`** | **1.65732e-13 · `<`** | 0.36286 · `=` | **1.10488e-13 · `<`** |
| **f10** | **1.55129e-13 · `<`** | 0.980678 · `=` | **2.97331e-17 · `<`** | **9.17092e-18 · `>`** | **1.94767e-18 · `>`** | **2.31258e-17 · `<`** |
| **f11** | **2.09223e-17 · `>`** | **3.7485e-18 · `>`** | **3.06569e-19 · `>`** | **1.66871e-19 · `>`** | **2.50898e-19 · `>`** | **7.67838e-18 · `>`** |
| **f12** | **0.0392881 · `<`** | **1.26377e-18 · `>`** | **7.43887e-19 · `<`** | **7.16905e-07 · `>`** | **1.32392e-18 · `>`** | **4.1749e-19 · `<`** |
| $n_{<}/n_{>}/n_{=}$ | 4/4/4 | 1/8/3 | 5/5/2 | 2/8/2 | 2/7/3 | 4/6/2 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the compared algorithm's sample. The symbols above describe
the MSC-CMA-ES sample's mean-rank relation after Holm correction.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 1275 | 1275 | 1275 | 1275 | 1326 | 1275 |
| f2 | 1690.5 | 1275 | 1639 | 1404.5 | 2594.5 | 1405 |
| f3 | 0 | 0 | 0 | 0 | 0 | 0 |
| f4 | 1327 | 2081 | 1795 | 2601 | 2601 | 2601 |
| f5 | 867 | 867 | 867 | 867 | 1071 | 867 |
| f6 | 836 | 30 | 802 | 165 | 111 | 65 |
| f7 | 1417 | 0 | 1050 | 0 | 0 | 0 |
| f8 | 1129 | 6 | 596 | 38 | 379 | 95 |
| f9 | 2295 | 773 | 2295 | 2295 | 1494 | 2295 |
| f10 | 2449 | 1355 | 2601 | 40 | 0 | 2601 |
| f11 | 0 | 0 | 0 | 0 | 0 | 0 |
| f12 | 1627.5 | 0 | 2599 | 549.5 | 0 | 2599 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f1 | 0.326893 | 0.326893 | 0.326893 | 0.326893 | 0.567513 | 0.326893 |
| f2 | 5.61505e-05 | 0.326893 | 0.000233271 | 0.0893892 | 2.08959e-20 | 0.0877503 |
| f3 | 3.7485e-19 | 5.60972e-19 | 1.98815e-20 | 1.39059e-20 | 1.39059e-20 | 6.88319e-19 |
| f4 | 0.552159 | 1.07611e-10 | 2.48041e-06 | 1.91004e-20 | 1.97657e-20 | 7.72318e-21 |
| f5 | 7.95891e-06 | 7.95891e-06 | 7.95891e-06 | 7.95891e-06 | 0.0537797 | 7.95891e-06 |
| f6 | 0.00190011 | 1.90019e-17 | 0.000859247 | 3.04899e-14 | 1.75367e-15 | 1.39118e-16 |
| f7 | 0.43754 | 3.19096e-19 | 0.0886659 | 1.39059e-20 | 9.26454e-19 | 3.35187e-19 |
| f8 | 0.252436 | 4.70263e-18 | 2.457e-06 | 3.00947e-17 | 7.09374e-10 | 7.34085e-16 |
| f9 | 2.76219e-14 | 0.000341311 | 2.76219e-14 | 2.76219e-14 | 0.18143 | 2.76219e-14 |
| f10 | 1.55129e-14 | 0.717796 | 3.30368e-18 | 1.14636e-18 | 2.78238e-19 | 3.30368e-18 |
| f11 | 1.90203e-18 | 3.7485e-19 | 2.78699e-20 | 1.39059e-20 | 2.78775e-20 | 9.59798e-19 |
| f12 | 0.00785762 | 1.05314e-19 | 7.43887e-20 | 1.79226e-07 | 1.6549e-19 | 3.79536e-20 |

</details>

<a id="budget-1m-composition"></a>

#### Composition functions

Function scope: `composition`. Holm family size: **4** per competitor.
Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f9** | **5.52439e-14 · `<`** | **0.000682622 · `>`** | **2.76219e-14 · `<`** | **5.52439e-14 · `<`** | 0.18143 · `=` | **2.76219e-14 · `<`** |
| **f10** | **4.65387e-14 · `<`** | 0.717796 · `=` | **6.60736e-18 · `<`** | **3.43909e-18 · `>`** | **5.56476e-19 · `>`** | **6.60736e-18 · `<`** |
| **f11** | **7.60812e-18 · `>`** | **1.12455e-18 · `>`** | **1.11479e-19 · `>`** | **5.56235e-20 · `>`** | **1.1151e-19 · `>`** | **2.87939e-18 · `>`** |
| **f12** | **0.00785762 · `<`** | **4.21255e-19 · `>`** | **2.23166e-19 · `<`** | **1.79226e-07 · `>`** | **4.9647e-19 · `>`** | **1.51814e-19 · `<`** |
| $n_{<}/n_{>}/n_{=}$ | 3/1/0 | 0/3/1 | 3/1/0 | 1/3/0 | 0/3/1 | 3/1/0 |

<details>
<summary>U statistics and raw p-values</summary>

U is for the compared algorithm's sample. The symbols above describe
the MSC-CMA-ES sample's mean-rank relation after Holm correction.

##### U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f9 | 2295 | 773 | 2295 | 2295 | 1494 | 2295 |
| f10 | 2449 | 1355 | 2601 | 40 | 0 | 2601 |
| f11 | 0 | 0 | 0 | 0 | 0 | 0 |
| f12 | 1627.5 | 0 | 2599 | 549.5 | 0 | 2599 |

##### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| f9 | 2.76219e-14 | 0.000341311 | 2.76219e-14 | 2.76219e-14 | 0.18143 | 2.76219e-14 |
| f10 | 1.55129e-14 | 0.717796 | 3.30368e-18 | 1.14636e-18 | 2.78238e-19 | 3.30368e-18 |
| f11 | 1.90203e-18 | 3.7485e-19 | 2.78699e-20 | 1.39059e-20 | 2.78775e-20 | 9.59798e-19 |
| f12 | 0.00785762 | 1.05314e-19 | 7.43887e-20 | 1.79226e-07 | 1.6549e-19 | 3.79536e-20 |

</details>

The complete U statistics, raw and adjusted p-values, sample sizes,
descriptive medians, scopes, and family sizes are in [`details.csv`](details.csv).
The CSV `decision` field describes the compared algorithm's pooled mean rank
conditional on rejection after Holm correction: `higher` maps to `<` for
MSC-CMA-ES, `lower` to `>`, and `not significant` to `=`.

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

<a id="dsc-budget-200k"></a>

### Budget 2×10^5

<a id="dsc-budget-200k-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 1.5 | 5.5 | 1.5 | 5.5 | 5.5 | 3 | 5.5 |
| **f2** | 5.5 | 7 | 1.5 | 5.5 | 1.5 | 3 | 4 |
| **f3** | 7 | 4 | 6 | 2.5 | 1 | 5 | 2.5 |
| **f4** | 2 | 2 | 4 | 2 | 7 | 6 | 5 |
| **f5** | 7 | 3 | 3 | 3 | 3 | 6 | 3 |
| **f6** | 5 | 7 | 2 | 4 | 3 | 6 | 1 |
| **f7** | 6 | 7 | 4 | 5 | 2 | 1 | 3 |
| **f8** | 6.5 | 6.5 | 2 | 4.5 | 2 | 2 | 4.5 |
| **f9** | 1 | 6 | 2 | 6 | 3 | 4 | 6 |
| **f10** | 3 | 5 | 4 | 6.5 | 2 | 1 | 6.5 |
| **f11** | 7 | 6 | 4 | 2.5 | 1 | 5 | 2.5 |
| **f12** | 3.5 | 3.5 | 1.5 | 6.5 | 5 | 1.5 | 6.5 |

Composition-function set: `f9–f12`.

<a id="dsc-budget-200k-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 12 | ARRDE | 2.95833 | 4.58333 | 6/7 | 10.9643 | 0.0894865 | — | O |
| Composition functions | 4 | NL-SHADE-RSP | 2.75 | 3.625 | 4/7 | 7.95536 | 0.241392 | — | O |

<a id="dsc-budget-1m"></a>

### Budget 10^6

<a id="dsc-budget-1m-ranks"></a>

#### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive
fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **f1** | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| **f2** | 2 | 6 | 1 | 7 | 4 | 3 | 5 |
| **f3** | 7 | 4.5 | 6 | 2 | 2 | 2 | 4.5 |
| **f4** | 1.5 | 1.5 | 3.5 | 3.5 | 7 | 6 | 5 |
| **f5** | 6.5 | 3 | 3 | 3 | 3 | 6.5 | 3 |
| **f6** | 7 | 5.5 | 2 | 5.5 | 3.5 | 3.5 | 1 |
| **f7** | 5 | 7 | 2 | 6 | 1 | 3 | 4 |
| **f8** | 5.5 | 5.5 | 3.5 | 7 | 1.5 | 3.5 | 1.5 |
| **f9** | 2 | 5.5 | 1 | 5.5 | 5.5 | 3 | 5.5 |
| **f10** | 3.5 | 5 | 3.5 | 7 | 2 | 1 | 6 |
| **f11** | 7 | 6 | 4 | 1.5 | 1.5 | 5 | 3 |
| **f12** | 4 | 5 | 2 | 7 | 3 | 1 | 6 |

Composition-function set: `f9–f12`.

<a id="dsc-budget-1m-comparison"></a>

#### Statistical comparison

| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 12 | ARRDE | 2.95833 | 4.58333 | 5/7 | 10.3393 | 0.111072 | — | O |
| Composition functions | 4 | j2020 | 2.5 | 4.125 | 4/7 | 8.46429 | 0.206022 | — | O |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 2×10^5 | ARRDE · 6/7 · O | NL-SHADE-RSP · 4/7 · O |
| 10^6 | ARRDE · 5/7 · O | j2020 · 4/7 · O |
