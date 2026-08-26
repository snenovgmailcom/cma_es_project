# CEC2020, D=15

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

<a id="budget-3m"></a>

### Budget 3×10^6

Bonferroni family size: `10` functions.

<a id="budget-3m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1198.5 | 1198.5 | 1198.5 | 1308.5 | 1430 | 1198.5 |
| **f2** | 2076 | 366 | 1084.5 | 182 | 4 | 1447 |
| **f3** | 0 | 2601 | 2601 | 2601 | 1440 | 2601 |
| **f4** | 55 | 0 | 497 | 0 | 0 | 0 |
| **f5** | 714 | 800.5 | 1457 | 2575.5 | 2572 | 2459 |
| **f6** | 130 | 19 | 276 | 1 | 971 | 17 |
| **f7** | 417 | 310 | 757 | 270 | 279 | 561 |
| **f8** | 2237.5 | 2409 | 2601 | 1231.5 | 704 | 2601 |
| **f9** | 866 | 153 | 2601 | 153 | 537 | 2553 |
| **f10** | 2155 | 1629 | 2193 | 2193 | 2185 | 2193 |

<a id="budget-3m-raw-p"></a>

#### p_raw

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 0.0433389 | 0.0433389 | 0.0433389 | 0.914246 | 0.13526 | 0.0433389 |
| **f2** | 2.13328e-07 | 4.02859e-10 | 0.14909 | 7.22964e-14 | 3.63294e-18 | 0.328447 |
| **f3** | 1.39059e-20 | 1.1644e-18 | 3.28725e-18 | 5.18597e-20 | 0.350386 | 3.29867e-18 |
| **f4** | 7.7892e-17 | 3.30368e-18 | 7.69047e-08 | 1.82566e-19 | 3.30368e-18 | 3.30297e-18 |
| **f5** | 6.09086e-05 | 0.000731162 | 0.293701 | 1.3467e-17 | 1.6496e-17 | 8.34603e-15 |
| **f6** | 4.84862e-15 | 1.0051e-17 | 7.19734e-12 | 3.50432e-18 | 0.0276723 | 8.94691e-18 |
| **f7** | 3.41252e-09 | 3.4367e-11 | 0.000277058 | 5.44405e-12 | 8.30097e-12 | 7.57887e-07 |
| **f8** | 2.15299e-10 | 1.20766e-13 | 8.91523e-19 | 0.645806 | 5.7285e-05 | 5.59245e-19 |
| **f9** | 0.00367286 | 6.35374e-16 | 2.97118e-18 | 4.08597e-15 | 2.89092e-07 | 4.74772e-17 |
| **f10** | 3.37708e-09 | 0.0274953 | 1.74842e-10 | 1.74842e-10 | 5.36718e-10 | 2.8347e-10 |

<a id="budget-3m-bonferroni"></a>

#### p_Bonferroni and Direction

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 0.433389 (—) | 0.433389 (—) | 0.433389 (—) | 1 (—) | 1 (—) | 0.433389 (—) |
| **f2** | **2.13328e-06 (↑)** | **4.02859e-09 (↓)** | 1 (—) | **7.22964e-13 (↓)** | **3.63294e-17 (↓)** | 1 (—) |
| **f3** | **1.39059e-19 (↓)** | **1.1644e-17 (↑)** | **3.28725e-17 (↑)** | **5.18597e-19 (↑)** | 1 (—) | **3.29867e-17 (↑)** |
| **f4** | **7.7892e-16 (↓)** | **3.30368e-17 (↓)** | **7.69047e-07 (↓)** | **1.82566e-18 (↓)** | **3.30368e-17 (↓)** | **3.30297e-17 (↓)** |
| **f5** | **0.000609086 (↓)** | **0.00731162 (↓)** | 1 (—) | **1.3467e-16 (↑)** | **1.6496e-16 (↑)** | **8.34603e-14 (↑)** |
| **f6** | **4.84862e-14 (↓)** | **1.0051e-16 (↓)** | **7.19734e-11 (↓)** | **3.50432e-17 (↓)** | 0.276723 (—) | **8.94691e-17 (↓)** |
| **f7** | **3.41252e-08 (↓)** | **3.4367e-10 (↓)** | **0.00277058 (↓)** | **5.44405e-11 (↓)** | **8.30097e-11 (↓)** | **7.57887e-06 (↓)** |
| **f8** | **2.15299e-09 (↑)** | **1.20766e-12 (↑)** | **8.91523e-18 (↑)** | 1 (—) | **0.00057285 (↓)** | **5.59245e-18 (↑)** |
| **f9** | **0.0367286 (↓)** | **6.35374e-15 (↓)** | **2.97118e-17 (↑)** | **4.08597e-14 (↓)** | **2.89092e-06 (↓)** | **4.74772e-16 (↑)** |
| **f10** | **3.37708e-08 (↑)** | 0.274953 (—) | **1.74842e-09 (↑)** | **1.74842e-09 (↑)** | **5.36718e-09 (↑)** | **2.8347e-09 (↑)** |

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
