# NO-EXCLUSION — CEC2017, D=10, B=10^5

## Ablation

The k-NN convergence-tracking mechanism is retained for basin identification, but repeatedly resolved basins are not excluded from subsequent restarts.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `ablations/experiments/cec2017/d10/NO-EXCLUSION/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=10^5 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NO-EXCLUSION |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | **60.6899** | 75.8207 |
|  | Median | 32.7803 | **28.5904** |
|  | Minimum | 3.17225 | **2.20863** |
|  | Maximum | **264.107** | 290.282 |
|  | Std. | **67.4759** | 85.7511 |
|  | FBTC(B) | 5.14802 | **5.3564** |
| **Hybrid** (n=10) | Mean | **170.851** | 195.551 |
|  | Median | **202.261** | 206.662 |
|  | Minimum | **4.37748** | 5.98651 |
|  | Maximum | **423.371** | 502.228 |
|  | Std. | 123.599 | **122.876** |
|  | FBTC(B) | **2.34679** | 2.20684 |
| **Composition** (n=10) | Mean | **1891.37** | 1915.6 |
|  | Median | **2152.01** | 2152.48 |
|  | Minimum | **929.859** | 1029.86 |
|  | Maximum | 2696.97 | **2668.73** |
|  | Std. | 569.04 | **533.178** |
|  | FBTC(B) | **1.71396** | 1.4802 |
| **All** (n=29) | Mean | **2122.91** | 2186.97 |
|  | Median | **2387.06** | 2387.74 |
|  | Minimum | **937.409** | 1038.06 |
|  | Maximum | **3384.44** | 3461.24 |
|  | Std. | 760.115 | **741.805** |
|  | FBTC(B) | **9.20877** | 9.04344 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **NO-EXCLUSION** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary from the NO-EXCLUSION perspective: **↓ 1**, **↑ 0**, **— 28**.

Composition subset from the NO-EXCLUSION perspective: **↓ 0**, **↑ 0**, **— 10**.

`↓` denotes a statistically significant shift toward lower terminal errors for NO-EXCLUSION; `↑` denotes a statistically significant shift toward higher terminal errors; `—` denotes no statistically significant difference after Bonferroni correction.

| Function | Class | U (NO-EXCLUSION) | P(NO-EXCLUSION lower) | p_raw | p_Bonferroni | Direction |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | Unimodal and simple multimodal | 1349 | 0.481353 | 0.748021 | 1 | **—** |
| f3 | Unimodal and simple multimodal | 892.5 | 0.656863 | 3.62431e-05 | 0.00105105 | **↓** |
| f4 | Unimodal and simple multimodal | 1151 | 0.557478 | 0.27535 | 1 | **—** |
| f5 | Unimodal and simple multimodal | 1150.5 | 0.55767 | 0.304705 | 1 | **—** |
| f6 | Unimodal and simple multimodal | 1245 | 0.521338 | 0.712799 | 1 | **—** |
| f7 | Unimodal and simple multimodal | 1381 | 0.46905 | 0.592358 | 1 | **—** |
| f8 | Unimodal and simple multimodal | 998.5 | 0.616109 | 0.0293401 | 0.850864 | **—** |
| f9 | Unimodal and simple multimodal | 958 | 0.63168 | 0.00821476 | 0.238228 | **—** |
| f10 | Unimodal and simple multimodal | 1391.5 | 0.465013 | 0.544684 | 1 | **—** |
| f11 | Hybrid | 1194 | 0.540946 | 0.471093 | 1 | **—** |
| f12 | Hybrid | 1420.5 | 0.453864 | 0.423835 | 1 | **—** |
| f13 | Hybrid | 1128 | 0.566321 | 0.249672 | 1 | **—** |
| f14 | Hybrid | 1688 | 0.351019 | 0.00959543 | 0.278267 | **—** |
| f15 | Hybrid | 1268 | 0.512495 | 0.830417 | 1 | **—** |
| f16 | Hybrid | 1066 | 0.590158 | 0.117327 | 1 | **—** |
| f17 | Hybrid | 1284.5 | 0.506151 | 0.917376 | 1 | **—** |
| f18 | Hybrid | 1519 | 0.415994 | 0.144562 | 1 | **—** |
| f19 | Hybrid | 1683 | 0.352941 | 0.0105696 | 0.306519 | **—** |
| f20 | Hybrid | 1231 | 0.52672 | 0.644227 | 1 | **—** |
| f21 | Composition | 1351.5 | 0.480392 | 0.735304 | 1 | **—** |
| f22 | Composition | 1269 | 0.512111 | 0.835541 | 1 | **—** |
| f23 | Composition | 1219 | 0.531334 | 0.587729 | 1 | **—** |
| f24 | Composition | 1458.5 | 0.439254 | 0.291789 | 1 | **—** |
| f25 | Composition | 1358 | 0.477893 | 0.702844 | 1 | **—** |
| f26 | Composition | 1465 | 0.436755 | 0.272375 | 1 | **—** |
| f27 | Composition | 1362 | 0.476355 | 0.681804 | 1 | **—** |
| f28 | Composition | 1493.5 | 0.425798 | 0.197617 | 1 | **—** |
| f29 | Composition | 1242.5 | 0.522299 | 0.700356 | 1 | **—** |
| f30 | Composition | 1267 | 0.51288 | 0.825195 | 1 | **—** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

