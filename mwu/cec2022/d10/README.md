# CEC2022, D=10

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

<a id="budget-200k"></a>

### Budget 2×10^5

Bonferroni family size: `12` functions.

<a id="budget-200k-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 867 | 1258 | 867 | 969 | 2541.5 | 867 |
| **f2** | 1808 | 1725.5 | 1318.5 | 1661 | 2550 | 943.5 |
| **f3** | 0 | 0 | 0 | 0 | 0 | 0 |
| **f4** | 1291 | 2133.5 | 1067 | 2601 | 2601 | 2553.5 |
| **f5** | 663 | 682 | 663 | 738 | 1667 | 663 |
| **f6** | 1624 | 587 | 1009 | 659 | 934 | 133 |
| **f7** | 1487 | 63 | 498 | 136 | 0 | 268 |
| **f8** | 1584 | 145 | 810 | 135 | 379 | 241 |
| **f9** | 1555.5 | 1450.5 | 1555.5 | 1494.5 | 1525 | 1555.5 |
| **f10** | 1641 | 1331 | 1581 | 62 | 0 | 1581 |
| **f11** | 0 | 0 | 0 | 0 | 0 | 0 |
| **f12** | 1293 | 178.5 | 2571 | 1991.5 | 85.5 | 2491 |

<a id="budget-200k-raw-p"></a>

#### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 7.1472e-06 | 0.727102 | 7.1472e-06 | 0.00132084 | 1.57161e-17 | 7.1472e-06 |
| **f2** | 0.000182305 | 0.00133732 | 0.886233 | 0.00730878 | 1.53224e-17 | 0.000692024 |
| **f3** | 1.39059e-20 | 1.16728e-19 | 2.67906e-19 | 1.39059e-20 | 2.05202e-18 | 7.48364e-19 |
| **f4** | 0.947273 | 7.37865e-09 | 0.0763574 | 1.70346e-18 | 1.71111e-18 | 1.6596e-17 |
| **f5** | 1.53801e-08 | 6.22117e-08 | 1.53801e-08 | 1.65639e-06 | 0.00829657 | 1.53801e-08 |
| **f6** | 0.0306374 | 1.82496e-06 | 0.0514655 | 1.78653e-05 | 0.0143042 | 5.70115e-15 |
| **f7** | 0.213189 | 4.7209e-17 | 4.98565e-08 | 3.23926e-15 | 1.62244e-18 | 4.94837e-12 |
| **f8** | 0.0582202 | 1.07482e-14 | 0.00104018 | 6.33942e-15 | 7.09374e-10 | 1.3648e-12 |
| **f9** | 0.00233307 | 0.156718 | 0.00233307 | 0.0303986 | 0.00966985 | 0.00233307 |
| **f10** | 0.0228747 | 0.84087 | 0.0609362 | 6.93466e-17 | 3.30368e-18 | 0.0609362 |
| **f11** | 3.20624e-18 | 2.21602e-19 | 6.87834e-19 | 2.7847e-20 | 9.71836e-19 | 9.47901e-19 |
| **f12** | 0.961817 | 3.71581e-14 | 3.91624e-18 | 3.33292e-06 | 2.94781e-16 | 3.64248e-16 |

<a id="budget-200k-bonferroni"></a>

#### p_Bonferroni and Direction

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **8.57664e-05 (↓)** | 1 (—) | **8.57664e-05 (↓)** | **0.0158501 (↓)** | **1.88594e-16 (↑)** | **8.57664e-05 (↓)** |
| **f2** | **0.00218766 (↑)** | **0.0160479 (↑)** | 1 (—) | 0.0877054 (—) | **1.83868e-16 (↑)** | **0.00830429 (↓)** |
| **f3** | **1.66871e-19 (↓)** | **1.40074e-18 (↓)** | **3.21488e-18 (↓)** | **1.66871e-19 (↓)** | **2.46243e-17 (↓)** | **8.98037e-18 (↓)** |
| **f4** | 1 (—) | **8.85438e-08 (↑)** | 0.916289 (—) | **2.04415e-17 (↑)** | **2.05334e-17 (↑)** | **1.99152e-16 (↑)** |
| **f5** | **1.84561e-07 (↓)** | **7.4654e-07 (↓)** | **1.84561e-07 (↓)** | **1.98767e-05 (↓)** | 0.0995588 (—) | **1.84561e-07 (↓)** |
| **f6** | 0.367649 (—) | **2.18995e-05 (↓)** | 0.617586 (—) | **0.000214383 (↓)** | 0.171651 (—) | **6.84138e-14 (↓)** |
| **f7** | 1 (—) | **5.66508e-16 (↓)** | **5.98278e-07 (↓)** | **3.88711e-14 (↓)** | **1.94692e-17 (↓)** | **5.93804e-11 (↓)** |
| **f8** | 0.698642 (—) | **1.28978e-13 (↓)** | **0.0124822 (↓)** | **7.6073e-14 (↓)** | **8.51248e-09 (↓)** | **1.63776e-11 (↓)** |
| **f9** | **0.0279969 (↑)** | 1 (—) | **0.0279969 (↑)** | 0.364783 (—) | 0.116038 (—) | **0.0279969 (↑)** |
| **f10** | 0.274497 (—) | 1 (—) | 0.731234 (—) | **8.3216e-16 (↓)** | **3.96442e-17 (↓)** | 0.731234 (—) |
| **f11** | **3.84749e-17 (↓)** | **2.65922e-18 (↓)** | **8.25401e-18 (↓)** | **3.34164e-19 (↓)** | **1.1662e-17 (↓)** | **1.13748e-17 (↓)** |
| **f12** | 1 (—) | **4.45897e-13 (↓)** | **4.69949e-17 (↑)** | **3.9995e-05 (↑)** | **3.53738e-15 (↓)** | **4.37098e-15 (↑)** |

<a id="budget-1m"></a>

### Budget 10^6

Bonferroni family size: `12` functions.

<a id="budget-1m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1275 | 1275 | 1275 | 1275 | 1326 | 1275 |
| **f2** | 1690.5 | 1275 | 1639 | 1404.5 | 2594.5 | 1405 |
| **f3** | 0 | 0 | 0 | 0 | 0 | 0 |
| **f4** | 1327 | 2081 | 1795 | 2601 | 2601 | 2601 |
| **f5** | 867 | 867 | 867 | 867 | 1071 | 867 |
| **f6** | 836 | 30 | 802 | 165 | 111 | 65 |
| **f7** | 1417 | 0 | 1050 | 0 | 0 | 0 |
| **f8** | 1129 | 6 | 596 | 38 | 379 | 95 |
| **f9** | 2295 | 773 | 2295 | 2295 | 1494 | 2295 |
| **f10** | 2449 | 1355 | 2601 | 40 | 0 | 2601 |
| **f11** | 0 | 0 | 0 | 0 | 0 | 0 |
| **f12** | 1627.5 | 0 | 2599 | 549.5 | 0 | 2599 |

<a id="budget-1m-raw-p"></a>

#### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 0.326893 | 0.326893 | 0.326893 | 0.326893 | 0.567513 | 0.326893 |
| **f2** | 5.61505e-05 | 0.326893 | 0.000233271 | 0.0893892 | 2.08959e-20 | 0.0877503 |
| **f3** | 3.7485e-19 | 5.60972e-19 | 1.98815e-20 | 1.39059e-20 | 1.39059e-20 | 6.88319e-19 |
| **f4** | 0.552159 | 1.07611e-10 | 2.48041e-06 | 1.91004e-20 | 1.97657e-20 | 7.72318e-21 |
| **f5** | 7.95891e-06 | 7.95891e-06 | 7.95891e-06 | 7.95891e-06 | 0.0537797 | 7.95891e-06 |
| **f6** | 0.00190011 | 1.90019e-17 | 0.000859247 | 3.04899e-14 | 1.75367e-15 | 1.39118e-16 |
| **f7** | 0.43754 | 3.19096e-19 | 0.0886659 | 1.39059e-20 | 9.26454e-19 | 3.35187e-19 |
| **f8** | 0.252436 | 4.70263e-18 | 2.457e-06 | 3.00947e-17 | 7.09374e-10 | 7.34085e-16 |
| **f9** | 2.76219e-14 | 0.000341311 | 2.76219e-14 | 2.76219e-14 | 0.18143 | 2.76219e-14 |
| **f10** | 1.55129e-14 | 0.717796 | 3.30368e-18 | 1.14636e-18 | 2.78238e-19 | 3.30368e-18 |
| **f11** | 1.90203e-18 | 3.7485e-19 | 2.78699e-20 | 1.39059e-20 | 2.78775e-20 | 9.59798e-19 |
| **f12** | 0.00785762 | 1.05314e-19 | 7.43887e-20 | 1.79226e-07 | 1.6549e-19 | 3.79536e-20 |

<a id="budget-1m-bonferroni"></a>

#### p_Bonferroni and Direction

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1 (—) | 1 (—) | 1 (—) | 1 (—) | 1 (—) | 1 (—) |
| **f2** | **0.000673806 (↑)** | 1 (—) | **0.00279925 (↑)** | 1 (—) | **2.50751e-19 (↑)** | 1 (—) |
| **f3** | **4.49821e-18 (↓)** | **6.73166e-18 (↓)** | **2.38578e-19 (↓)** | **1.66871e-19 (↓)** | **1.66871e-19 (↓)** | **8.25982e-18 (↓)** |
| **f4** | 1 (—) | **1.29133e-09 (↑)** | **2.97649e-05 (↑)** | **2.29205e-19 (↑)** | **2.37189e-19 (↑)** | **9.26781e-20 (↑)** |
| **f5** | **9.55069e-05 (↓)** | **9.55069e-05 (↓)** | **9.55069e-05 (↓)** | **9.55069e-05 (↓)** | 0.645357 (—) | **9.55069e-05 (↓)** |
| **f6** | **0.0228014 (↓)** | **2.28022e-16 (↓)** | **0.010311 (↓)** | **3.65879e-13 (↓)** | **2.10441e-14 (↓)** | **1.66942e-15 (↓)** |
| **f7** | 1 (—) | **3.82915e-18 (↓)** | 1 (—) | **1.66871e-19 (↓)** | **1.11174e-17 (↓)** | **4.02225e-18 (↓)** |
| **f8** | 1 (—) | **5.64316e-17 (↓)** | **2.9484e-05 (↓)** | **3.61136e-16 (↓)** | **8.51248e-09 (↓)** | **8.80902e-15 (↓)** |
| **f9** | **3.31463e-13 (↑)** | **0.00409573 (↓)** | **3.31463e-13 (↑)** | **3.31463e-13 (↑)** | 1 (—) | **3.31463e-13 (↑)** |
| **f10** | **1.86155e-13 (↑)** | 1 (—) | **3.96442e-17 (↑)** | **1.37564e-17 (↓)** | **3.33886e-18 (↓)** | **3.96442e-17 (↑)** |
| **f11** | **2.28243e-17 (↓)** | **4.49821e-18 (↓)** | **3.34438e-19 (↓)** | **1.66871e-19 (↓)** | **3.3453e-19 (↓)** | **1.15176e-17 (↓)** |
| **f12** | 0.0942915 (—) | **1.26377e-18 (↓)** | **8.92665e-19 (↑)** | **2.15071e-06 (↓)** | **1.98588e-18 (↓)** | **4.55443e-19 (↑)** |

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
