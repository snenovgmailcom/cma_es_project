<table align="right">
<tr><th align="left">Contents</th></tr>
<tr><td align="left">
<a href="#mannwhitney-u-tests-on-terminal-errors">Mann–Whitney U tests on terminal errors</a><br>
&nbsp;&nbsp;<a href="#budget-10m">Budget 10M</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-10m-u">Mann–Whitney U statistic</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-10m-raw-p">Raw two-sided p-value</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-10m-bonferroni">Bonferroni-adjusted p-value and decision</a><br>
<a href="#deep-statistical-comparison">Deep Statistical Comparison</a><br>
&nbsp;&nbsp;<a href="#dsc-budget-10m">Budget 10M</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#dsc-budget-10m-ranks">DSC ranks by function</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#dsc-budget-10m-comparison">Statistical comparison</a><br>
&nbsp;&nbsp;<a href="#dsc-cell-summary">Cell summary</a>
</td></tr>
</table>

# CEC2020, D=20

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

<a id="budget-10m"></a>

### Budget 10M

Bonferroni family size: `10` functions.

<a id="budget-10m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 688.5 | 688.5 | 688.5 | 688.5 | 739.5 | 688.5 |
| **f2** | 2316.5 | 0 | 20 | 3 | 0 | 7 |
| **f3** | 1 | 2601 | 2601 | 2601 | 2248 | 2601 |
| **f4** | 48 | 0 | 607 | 0 | 0 | 0 |
| **f5** | 841.5 | 383.5 | 568.5 | 2478.5 | 2601 | 2406.5 |
| **f6** | 1049 | 0 | 0 | 0 | 0 | 0 |
| **f7** | 432 | 84 | 846 | 1649 | 526 | 16 |
| **f8** | 2475 | 2447 | 2601 | 2567 | 2515 | 2601 |
| **f9** | 1660 | 49 | 2601 | 50 | 2351 | 2601 |
| **f10** | 2235 | 86 | 2397 | 766 | 342 | 2397 |

<a id="budget-10m-raw-p"></a>

#### Raw two-sided p-value

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 2.54573e-08 | 2.54573e-08 | 2.54573e-08 | 2.54573e-08 | 6.71656e-07 | 2.54573e-08 |
| **f2** | 1.05038e-11 | 2.92745e-18 | 1.02241e-17 | 3.09324e-18 | 2.13992e-18 | 4.73535e-18 |
| **f3** | 2.12535e-20 | 3.83762e-20 | 3.12849e-18 | 1.98815e-20 | 1.33453e-10 | 3.30368e-18 |
| **f4** | 5.32572e-17 | 3.30368e-18 | 3.51718e-06 | 3.83658e-20 | 3.30368e-18 | 3.30225e-18 |
| **f5** | 0.00213689 | 8.29214e-10 | 9.69259e-07 | 3.25069e-15 | 3.29724e-18 | 1.3657e-13 |
| **f6** | 0.0929827 | 3.30297e-18 | 2.89127e-18 | 3.30368e-18 | 3.30368e-18 | 3.30368e-18 |
| **f7** | 6.23653e-09 | 4.00304e-16 | 0.00235625 | 0.0198558 | 2.21701e-07 | 8.44063e-18 |
| **f8** | 1.38885e-15 | 1.49922e-14 | 6.88319e-19 | 9.02598e-18 | 4.30181e-17 | 1.39059e-20 |
| **f9** | 0.0162708 | 1.55841e-18 | 3.22089e-18 | 7.0352e-18 | 2.10204e-12 | 3.29653e-18 |
| **f10** | 3.90747e-10 | 4.17607e-16 | 8.44029e-14 | 0.000349447 | 1.42386e-10 | 6.6573e-14 |

<a id="budget-10m-bonferroni"></a>

#### Bonferroni-adjusted p-value and decision

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **2.54573e-07 (+)** | **2.54573e-07 (+)** | **2.54573e-07 (+)** | **2.54573e-07 (+)** | **6.71656e-06 (+)** | **2.54573e-07 (+)** |
| **f2** | **1.05038e-10 (−)** | **2.92745e-17 (+)** | **1.02241e-16 (+)** | **3.09324e-17 (+)** | **2.13992e-17 (+)** | **4.73535e-17 (+)** |
| **f3** | **2.12535e-19 (+)** | **3.83762e-19 (−)** | **3.12849e-17 (−)** | **1.98815e-19 (−)** | **1.33453e-09 (−)** | **3.30368e-17 (−)** |
| **f4** | **5.32572e-16 (+)** | **3.30368e-17 (+)** | **3.51718e-05 (+)** | **3.83658e-19 (+)** | **3.30368e-17 (+)** | **3.30225e-17 (+)** |
| **f5** | **0.0213689 (+)** | **8.29214e-09 (+)** | **9.69259e-06 (+)** | **3.25069e-14 (−)** | **3.29724e-17 (−)** | **1.3657e-12 (−)** |
| **f6** | 0.929827 (≈) | **3.30297e-17 (+)** | **2.89127e-17 (+)** | **3.30368e-17 (+)** | **3.30368e-17 (+)** | **3.30368e-17 (+)** |
| **f7** | **6.23653e-08 (+)** | **4.00304e-15 (+)** | **0.0235625 (+)** | 0.198558 (≈) | **2.21701e-06 (+)** | **8.44063e-17 (+)** |
| **f8** | **1.38885e-14 (−)** | **1.49922e-13 (−)** | **6.88319e-18 (−)** | **9.02598e-17 (−)** | **4.30181e-16 (−)** | **1.39059e-19 (−)** |
| **f9** | 0.162708 (≈) | **1.55841e-17 (+)** | **3.22089e-17 (−)** | **7.0352e-17 (+)** | **2.10204e-11 (−)** | **3.29653e-17 (−)** |
| **f10** | **3.90747e-09 (−)** | **4.17607e-15 (+)** | **8.44029e-13 (−)** | **0.00349447 (+)** | **1.42386e-09 (+)** | **6.6573e-13 (−)** |

Full-precision U statistics, raw and Bonferroni-adjusted p-values,
effect directions, sample medians, and family sizes are available in
[`details.csv`](details.csv).

## Deep Statistical Comparison

Following the fixed-budget analysis workflow described by
[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied
Deep Statistical Comparison through
[DSCTool](https://doi.org/10.1016/j.asoc.2019.105977) to the 51
run-wise terminal errors for each function.

IOHanalyzer: <https://iohanalyzer.liacs.nl/>; DSCTool service used for
the analysis: <https://ws.ijs.si/dsc/>.

Settings: Anderson–Darling comparisons at `alpha=0.05`, `epsilon=0`,
and `monte_carlo_iterations=0`; Friedman omnibus tests over functions;
and, after rejection of the omnibus null hypothesis, Holm-adjusted
post-hoc comparisons against the method with the best mean DSC rank.

`★` means that MSC-CMA-ES has the best mean DSC rank and the Friedman
test rejects the null hypothesis; `≈` means that the Friedman test
rejects the null hypothesis but MSC-CMA-ES is not significantly different
from the best-ranked method after Holm adjustment; `↓` means that the
best-ranked method is significantly better than MSC-CMA-ES after Holm
adjustment; and `O` means that the Friedman test does not reject the null
hypothesis and no post-hoc interpretation is made.

<a id="dsc-budget-10m"></a>

### Budget 10M

<a id="dsc-budget-10m-ranks"></a>

#### DSC ranks by function

Lower DSC ranks indicate better performance. Tied distributions
receive fractional ranks.

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

| Function set | n | Best-ranked method | Best mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p-value | Holm p-value | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 10 | ARRDE | 2.55 | 4.25 | 4/7 | 10.3821 | 0.109454 | — | O |
| Composition functions | 3 | ARRDE | 1.5 | 2.66667 | 3/7 | 13.2143 | 0.0397565 | 0.508332 | ≈ |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 10M | ARRDE · 4/7 · O | ARRDE · 3/7 · ≈ |
