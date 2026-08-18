<table align="right">
<tr><th align="left">Contents</th></tr>
<tr><td align="left">
<a href="#mannwhitney-u-tests-on-terminal-errors">Mann–Whitney U tests on terminal errors</a><br>
&nbsp;&nbsp;<a href="#budget-1m">Budget 1M</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-1m-u">Mann–Whitney U statistic</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-1m-raw-p">Raw two-sided p-value</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-1m-bonferroni">Bonferroni-adjusted p-value and decision</a><br>
<a href="#deep-statistical-comparison">Deep Statistical Comparison</a><br>
&nbsp;&nbsp;<a href="#dsc-budget-1m">Budget 1M</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#dsc-budget-1m-ranks">DSC ranks by function</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#dsc-budget-1m-comparison">Statistical comparison</a><br>
&nbsp;&nbsp;<a href="#dsc-cell-summary">Cell summary</a>
</td></tr>
</table>

# CEC2022, D=20

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

<a id="budget-1m"></a>

### Budget 1M

Bonferroni family size: `12` functions.

<a id="budget-1m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 586.5 | 790.5 | 586.5 | 1109 | 2601 | 586.5 |
| **f2** | 1948.5 | 1134.5 | 2601 | 2539 | 2439 | 2601 |
| **f3** | 0 | 0 | 0 | 0 | 0 | 0 |
| **f4** | 1730 | 2351.5 | 890.5 | 2601 | 2601 | 2592 |
| **f5** | 484.5 | 484.5 | 484.5 | 848 | 1227 | 484.5 |
| **f6** | 2359 | 1045 | 1173 | 2576 | 2532 | 899 |
| **f7** | 1947 | 711 | 400 | 1061 | 1266 | 794 |
| **f8** | 1068 | 818 | 1441 | 1171 | 2090 | 813 |
| **f9** | 1176 | 1530 | 1249.5 | 1300.5 | 2473.5 | 1275 |
| **f10** | 2338 | 2476 | 2601 | 2 | 0 | 2601 |
| **f11** | 585 | 204 | 2550 | 2601 | 2601 | 2601 |
| **f12** | 1474.5 | 0 | 681 | 2064 | 1245.5 | 64 |

<a id="budget-1m-raw-p"></a>

#### Raw two-sided p-value

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 6.50844e-10 | 3.79743e-05 | 6.50844e-10 | 0.145877 | 8.83294e-19 | 6.50844e-10 |
| **f2** | 4.45116e-06 | 0.206732 | 5.88451e-21 | 2.92341e-17 | 1.26091e-14 | 4.01078e-19 |
| **f3** | 1.46792e-18 | 3.83658e-20 | 1.80926e-19 | 5.1777e-20 | 1.56647e-18 | 1.39059e-20 |
| **f4** | 0.00325088 | 7.59803e-13 | 0.00490363 | 2.83933e-18 | 2.83995e-18 | 3.81592e-18 |
| **f5** | 3.20091e-11 | 3.20091e-11 | 3.20091e-11 | 0.000980639 | 0.618453 | 3.20091e-11 |
| **f6** | 1.43237e-12 | 0.0878889 | 0.387187 | 1.42352e-17 | 1.74059e-16 | 0.00727959 |
| **f7** | 1.53581e-05 | 8.07584e-05 | 1.34264e-09 | 0.109697 | 0.819995 | 0.000707828 |
| **f8** | 0.120493 | 0.00125584 | 0.348769 | 0.38794 | 1.28799e-07 | 0.00111668 |
| **f9** | 0.0265276 | 0.00797047 | 0.159329 | 1 | 1.27527e-19 | 0.567513 |
| **f10** | 3.91164e-12 | 3.72262e-15 | 3.30368e-18 | 5.91512e-20 | 3.30297e-18 | 3.30368e-18 |
| **f11** | 1.70733e-06 | 4.36125e-14 | 1.71722e-17 | 8.03761e-19 | 2.57847e-18 | 5.91538e-19 |
| **f12** | 0.221491 | 1.80882e-18 | 2.93596e-05 | 2.68014e-07 | 0.713257 | 6.31274e-17 |

<a id="budget-1m-bonferroni"></a>

#### Bonferroni-adjusted p-value and decision

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **7.81013e-09 (+)** | **0.000455691 (+)** | **7.81013e-09 (+)** | 1 (≈) | **1.05995e-17 (−)** | **7.81013e-09 (+)** |
| **f2** | **5.34139e-05 (−)** | 1 (≈) | **7.06142e-20 (−)** | **3.50809e-16 (−)** | **1.51309e-13 (−)** | **4.81294e-18 (−)** |
| **f3** | **1.7615e-17 (+)** | **4.6039e-19 (+)** | **2.17111e-18 (+)** | **6.21324e-19 (+)** | **1.87976e-17 (+)** | **1.66871e-19 (+)** |
| **f4** | **0.0390106 (−)** | **9.11763e-12 (−)** | 0.0588435 (≈) | **3.4072e-17 (−)** | **3.40794e-17 (−)** | **4.5791e-17 (−)** |
| **f5** | **3.84109e-10 (+)** | **3.84109e-10 (+)** | **3.84109e-10 (+)** | **0.0117677 (+)** | 1 (≈) | **3.84109e-10 (+)** |
| **f6** | **1.71885e-11 (−)** | 1 (≈) | 1 (≈) | **1.70822e-16 (−)** | **2.08871e-15 (−)** | 0.0873551 (≈) |
| **f7** | **0.000184297 (−)** | **0.0009691 (+)** | **1.61117e-08 (+)** | 1 (≈) | 1 (≈) | **0.00849393 (+)** |
| **f8** | 1 (≈) | **0.0150701 (+)** | 1 (≈) | 1 (≈) | **1.54559e-06 (−)** | **0.0134002 (+)** |
| **f9** | 0.318332 (≈) | 0.0956457 (≈) | 1 (≈) | 1 (≈) | **1.53032e-18 (−)** | 1 (≈) |
| **f10** | **4.69397e-11 (−)** | **4.46715e-14 (−)** | **3.96442e-17 (−)** | **7.09814e-19 (+)** | **3.96356e-17 (+)** | **3.96442e-17 (−)** |
| **f11** | **2.04879e-05 (+)** | **5.2335e-13 (+)** | **2.06067e-16 (−)** | **9.64513e-18 (−)** | **3.09417e-17 (−)** | **7.09846e-18 (−)** |
| **f12** | 1 (≈) | **2.17059e-17 (+)** | **0.000352316 (+)** | **3.21617e-06 (−)** | 1 (≈) | **7.57529e-16 (+)** |

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

<a id="dsc-budget-1m"></a>

### Budget 1M

<a id="dsc-budget-1m-ranks"></a>

#### DSC ranks by function

Lower DSC ranks indicate better performance. Tied distributions
receive fractional ranks.

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

| Function set | n | Best-ranked method | Best mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p-value | Holm p-value | Result |
|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|
| All functions | 12 | L-SRTDE | 3.08333 | 3.75 | 4/7 | 9.11607 | 0.167155 | — | O |
| Composition functions | 4 | MSC-CMA-ES | 3.125 | 3.125 | 1/7 | 1.63393 | 0.950107 | — | O |

<a id="dsc-cell-summary"></a>

### Cell summary

| Budget | All functions | Composition functions |
|--:|:--|:--|
| 1M | L-SRTDE · 4/7 · O | MSC-CMA-ES · 1/7 · O |
