<table align="right">
<tr><th align="left">Contents</th></tr>
<tr><td align="left">
<a href="#mannwhitney-u-tests-on-terminal-errors">Mann–Whitney U tests on terminal errors</a><br>
&nbsp;&nbsp;<a href="#budget-50k">Budget 50K</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-50k-u">Mann–Whitney U statistic</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-50k-raw-p">Raw two-sided p-value</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-50k-bonferroni">Bonferroni-adjusted p-value and decision</a><br>
&nbsp;&nbsp;<a href="#budget-1m">Budget 1M</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-1m-u">Mann–Whitney U statistic</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-1m-raw-p">Raw two-sided p-value</a><br>
&nbsp;&nbsp;&nbsp;&nbsp;<a href="#budget-1m-bonferroni">Bonferroni-adjusted p-value and decision</a><br>
<a href="#deep-statistical-comparison">Deep Statistical Comparison</a>
</td></tr>
</table>

# CEC2020, D=5

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

<a id="budget-50k"></a>

### Budget 50K

Bonferroni family size: `10` functions.

<a id="budget-50k-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 306 | 426 | 396 | 306 | 763.5 | 306 |
| **f2** | 1229.5 | 916.5 | 517.5 | 97 | 1064 | 455 |
| **f3** | 1973 | 1895.5 | 2173 | 1013.5 | 1794.5 | 1927 |
| **f4** | 404.5 | 92.5 | 452.5 | 30.5 | 102.5 | 101.5 |
| **f5** | 1431.5 | 511.5 | 1041 | 408 | 814.5 | 504 |
| **f6** | 234 | 0 | 394 | 0 | 0 | 0 |
| **f7** | 411.5 | 0 | 525 | 0 | 0 | 0 |
| **f8** | 846 | 408.5 | 505 | 0 | 1330.5 | 1.5 |
| **f9** | 2162 | 879 | 2601 | 153 | 1996.5 | 2601 |
| **f10** | 2451 | 1998 | 2601 | 2068 | 2298 | 2601 |

<a id="budget-50k-raw-p"></a>

#### Raw two-sided p-value

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 2.76099e-14 | 6.39262e-10 | 8.86812e-12 | 2.76099e-14 | 0.00032239 | 2.76099e-14 |
| **f2** | 0.63654 | 0.0100752 | 1.2511e-07 | 5.31351e-16 | 0.113789 | 1.34458e-08 |
| **f3** | 6.59364e-06 | 6.6842e-05 | 4.97349e-09 | 0.0513902 | 0.000951347 | 2.12184e-05 |
| **f4** | 2.03595e-09 | 5.94615e-16 | 1.30561e-08 | 1.2421e-18 | 1.09839e-15 | 1.03459e-15 |
| **f5** | 0.369936 | 3.10552e-09 | 0.0685021 | 1.6789e-12 | 0.000737113 | 1.03922e-09 |
| **f6** | 9.71776e-13 | 7.78675e-19 | 3.20464e-10 | 1.9876e-20 | 1.58813e-18 | 1.3902e-20 |
| **f7** | 2.7393e-09 | 3.83245e-20 | 8.67099e-08 | 1.3902e-20 | 1.3902e-20 | 1.3902e-20 |
| **f8** | 0.00223168 | 1.8576e-09 | 3.70081e-08 | 1.34265e-20 | 0.84321 | 4.08503e-20 |
| **f9** | 8.04431e-09 | 0.004834 | 1.98705e-20 | 5.03275e-16 | 3.19288e-06 | 2.78546e-20 |
| **f10** | 7.91671e-15 | 3.08773e-06 | 5.6217e-19 | 2.4851e-07 | 2.50841e-11 | 1.98815e-20 |

<a id="budget-50k-bonferroni"></a>

#### Bonferroni-adjusted p-value and decision

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | **2.76099e-13 (+)** | **6.39262e-09 (+)** | **8.86812e-11 (+)** | **2.76099e-13 (+)** | **0.0032239 (+)** | **2.76099e-13 (+)** |
| **f2** | 1 (≈) | 0.100752 (≈) | **1.2511e-06 (+)** | **5.31351e-15 (+)** | 1 (≈) | **1.34458e-07 (+)** |
| **f3** | **6.59364e-05 (−)** | **0.00066842 (−)** | **4.97349e-08 (−)** | 0.513902 (≈) | **0.00951347 (−)** | **0.000212184 (−)** |
| **f4** | **2.03595e-08 (+)** | **5.94615e-15 (+)** | **1.30561e-07 (+)** | **1.2421e-17 (+)** | **1.09839e-14 (+)** | **1.03459e-14 (+)** |
| **f5** | 1 (≈) | **3.10552e-08 (+)** | 0.685021 (≈) | **1.6789e-11 (+)** | **0.00737113 (+)** | **1.03922e-08 (+)** |
| **f6** | **9.71776e-12 (+)** | **7.78675e-18 (+)** | **3.20464e-09 (+)** | **1.9876e-19 (+)** | **1.58813e-17 (+)** | **1.3902e-19 (+)** |
| **f7** | **2.7393e-08 (+)** | **3.83245e-19 (+)** | **8.67099e-07 (+)** | **1.3902e-19 (+)** | **1.3902e-19 (+)** | **1.3902e-19 (+)** |
| **f8** | **0.0223168 (+)** | **1.8576e-08 (+)** | **3.70081e-07 (+)** | **1.34265e-19 (+)** | 1 (≈) | **4.08503e-19 (+)** |
| **f9** | **8.04431e-08 (−)** | **0.04834 (+)** | **1.98705e-19 (−)** | **5.03275e-15 (+)** | **3.19288e-05 (−)** | **2.78546e-19 (−)** |
| **f10** | **7.91671e-14 (−)** | **3.08773e-05 (−)** | **5.6217e-18 (−)** | **2.4851e-06 (−)** | **2.50841e-10 (−)** | **1.98815e-19 (−)** |

<a id="budget-1m"></a>

### Budget 1M

Bonferroni family size: `10` functions.

<a id="budget-1m-u"></a>

#### Mann–Whitney U statistic

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1275 | 1275 | 1301 | 1275 | 1275 | 1275 |
| **f2** | 1805.5 | 78.5 | 1693 | 0 | 60 | 26.5 |
| **f3** | 2410 | 841 | 2601 | 1001 | 561 | 2401 |
| **f4** | 71 | 56.5 | 684 | 51 | 111 | 163 |
| **f5** | 765 | 765 | 1521 | 765 | 765 | 765 |
| **f6** | 0 | 0 | 126 | 0 | 0 | 0 |
| **f7** | 1 | 0 | 612 | 0 | 0 | 0 |
| **f8** | 53.5 | 0 | 816 | 0 | 0 | 153 |
| **f9** | 1439 | 0 | 2601 | 0 | 0 | 2550 |
| **f10** | 2507 | 306 | 2601 | 2244 | 1887 | 2601 |

<a id="budget-1m-raw-p"></a>

#### Raw two-sided p-value

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 0.326893 | 0.326893 | 1 | 0.326893 | 0.326893 | 0.326893 |
| **f2** | 0.000626582 | 4.46331e-17 | 0.00756024 | 8.57185e-21 | 5.38385e-18 | 2.30453e-19 |
| **f3** | 4.64473e-14 | 0.000358891 | 2.03748e-18 | 0.0229483 | 5.15523e-10 | 5.96632e-15 |
| **f4** | 1.03753e-18 | 1.08396e-18 | 3.41947e-05 | 1.96372e-19 | 5.69016e-16 | 2.01616e-14 |
| **f5** | 3.8972e-07 | 3.8972e-07 | 0.0979026 | 3.8972e-07 | 3.8972e-07 | 3.8972e-07 |
| **f6** | 3.30225e-18 | 1.39059e-20 | 1.31506e-16 | 1.39059e-20 | 1.39059e-20 | 1.39059e-20 |
| **f7** | 3.47184e-18 | 1.39059e-20 | 2.13114e-06 | 1.39059e-20 | 1.39059e-20 | 1.39059e-20 |
| **f8** | 7.1447e-19 | 1.08034e-20 | 0.000913823 | 1.08034e-20 | 1.08034e-20 | 4.16876e-16 |
| **f9** | 0.354486 | 1.38784e-20 | 1.98429e-20 | 1.38784e-20 | 2.78165e-20 | 7.64725e-19 |
| **f10** | 6.9364e-16 | 3.43419e-12 | 7.49765e-19 | 1.94726e-10 | 8.60027e-05 | 1.98594e-20 |

<a id="budget-1m-bonferroni"></a>

#### Bonferroni-adjusted p-value and decision

| Function | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|
| **f1** | 1 (≈) | 1 (≈) | 1 (≈) | 1 (≈) | 1 (≈) | 1 (≈) |
| **f2** | **0.00626582 (−)** | **4.46331e-16 (+)** | 0.0756024 (≈) | **8.57185e-20 (+)** | **5.38385e-17 (+)** | **2.30453e-18 (+)** |
| **f3** | **4.64473e-13 (−)** | **0.00358891 (+)** | **2.03748e-17 (−)** | 0.229483 (≈) | **5.15523e-09 (+)** | **5.96632e-14 (−)** |
| **f4** | **1.03753e-17 (+)** | **1.08396e-17 (+)** | **0.000341947 (+)** | **1.96372e-18 (+)** | **5.69016e-15 (+)** | **2.01616e-13 (+)** |
| **f5** | **3.8972e-06 (+)** | **3.8972e-06 (+)** | 0.979026 (≈) | **3.8972e-06 (+)** | **3.8972e-06 (+)** | **3.8972e-06 (+)** |
| **f6** | **3.30225e-17 (+)** | **1.39059e-19 (+)** | **1.31506e-15 (+)** | **1.39059e-19 (+)** | **1.39059e-19 (+)** | **1.39059e-19 (+)** |
| **f7** | **3.47184e-17 (+)** | **1.39059e-19 (+)** | **2.13114e-05 (+)** | **1.39059e-19 (+)** | **1.39059e-19 (+)** | **1.39059e-19 (+)** |
| **f8** | **7.1447e-18 (+)** | **1.08034e-19 (+)** | **0.00913823 (+)** | **1.08034e-19 (+)** | **1.08034e-19 (+)** | **4.16876e-15 (+)** |
| **f9** | 1 (≈) | **1.38784e-19 (+)** | **1.98429e-19 (−)** | **1.38784e-19 (+)** | **2.78165e-19 (+)** | **7.64725e-18 (−)** |
| **f10** | **6.9364e-15 (−)** | **3.43419e-11 (+)** | **7.49765e-18 (−)** | **1.94726e-09 (−)** | **0.000860027 (−)** | **1.98594e-19 (−)** |

Full-precision U statistics, raw and Bonferroni-adjusted p-values,
effect directions, sample medians, and family sizes are available in
[`details.csv`](details.csv).

## Deep Statistical Comparison
