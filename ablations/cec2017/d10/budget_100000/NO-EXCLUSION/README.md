# NO-EXCLUSION — CEC2017, D=10, B=100K

## Ablation

The k-NN convergence-tracking mechanism is retained for basin identification, but repeatedly resolved basins are not excluded from subsequent restarts.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `ablations/experiments/cec2017/d10/NO-EXCLUSION/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=100,000 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | NO-EXCLUSION |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=9) | mean | **60.6899** | 75.8207 |
|  | median | 32.7803 | **28.5904** |
|  | best | 3.17225 | **2.20863** |
|  | worst | **264.107** | 290.282 |
|  | std | **67.4759** | 85.7511 |
|  | FBTC(B) | 5.14802 | **5.3564** |
| **Hybrid** (n=10) | mean | **170.851** | 195.551 |
|  | median | **202.261** | 206.662 |
|  | best | **4.37748** | 5.98651 |
|  | worst | **423.371** | 502.228 |
|  | std | 123.599 | **122.876** |
|  | FBTC(B) | **2.34679** | 2.20684 |
| **Composition** (n=10) | mean | **1891.37** | 1915.6 |
|  | median | **2152.01** | 2152.48 |
|  | best | **929.859** | 1029.86 |
|  | worst | 2696.97 | **2668.73** |
|  | std | 569.04 | **533.178** |
|  | FBTC(B) | **1.71396** | 1.4802 |
| **ALL** (n=29) | mean | **2122.91** | 2186.97 |
|  | median | **2387.06** | 2387.74 |
|  | best | **937.409** | 1038.06 |
|  | worst | **3384.44** | 3461.24 |
|  | std | 760.115 | **741.805** |
|  | FBTC(B) | **9.20877** | 9.04344 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **NO-EXCLUSION** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary: NO-EXCLUSION significant on **1** functions; MSC-CMA-ES significant on **0**; not significant on **28**.

Composition subset: NO-EXCLUSION significant on **0** of 10 functions; MSC-CMA-ES significant on **0**; not significant on **10**.

`+` means NO-EXCLUSION has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant after Bonferroni adjustment.

| Function | Class | U (NO-EXCLUSION) | P(NO-EXCLUSION lower) | p_raw | p_Bonferroni | Result |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | basic | 1349 | 0.481353 | 0.748021 | 1 | **≈** |
| f3 | basic | 892.5 | 0.656863 | 3.624307e-05 | 0.00105105 | **+** |
| f4 | basic | 1151 | 0.557478 | 0.27535 | 1 | **≈** |
| f5 | basic | 1150.5 | 0.55767 | 0.304705 | 1 | **≈** |
| f6 | basic | 1245 | 0.521338 | 0.712799 | 1 | **≈** |
| f7 | basic | 1381 | 0.46905 | 0.592358 | 1 | **≈** |
| f8 | basic | 998.5 | 0.616109 | 0.0293401 | 0.850864 | **≈** |
| f9 | basic | 958 | 0.63168 | 0.00821476 | 0.238228 | **≈** |
| f10 | basic | 1391.5 | 0.465013 | 0.544684 | 1 | **≈** |
| f11 | hybrid | 1194 | 0.540946 | 0.471093 | 1 | **≈** |
| f12 | hybrid | 1420.5 | 0.453864 | 0.423835 | 1 | **≈** |
| f13 | hybrid | 1128 | 0.566321 | 0.249672 | 1 | **≈** |
| f14 | hybrid | 1688 | 0.351019 | 0.00959543 | 0.278267 | **≈** |
| f15 | hybrid | 1268 | 0.512495 | 0.830417 | 1 | **≈** |
| f16 | hybrid | 1066 | 0.590158 | 0.117327 | 1 | **≈** |
| f17 | hybrid | 1284.5 | 0.506151 | 0.917376 | 1 | **≈** |
| f18 | hybrid | 1519 | 0.415994 | 0.144562 | 1 | **≈** |
| f19 | hybrid | 1683 | 0.352941 | 0.0105696 | 0.306519 | **≈** |
| f20 | hybrid | 1231 | 0.52672 | 0.644227 | 1 | **≈** |
| f21 | composition | 1351.5 | 0.480392 | 0.735304 | 1 | **≈** |
| f22 | composition | 1269 | 0.512111 | 0.835541 | 1 | **≈** |
| f23 | composition | 1219 | 0.531334 | 0.587729 | 1 | **≈** |
| f24 | composition | 1458.5 | 0.439254 | 0.291789 | 1 | **≈** |
| f25 | composition | 1358 | 0.477893 | 0.702844 | 1 | **≈** |
| f26 | composition | 1465 | 0.436755 | 0.272375 | 1 | **≈** |
| f27 | composition | 1362 | 0.476355 | 0.681804 | 1 | **≈** |
| f28 | composition | 1493.5 | 0.425798 | 0.197617 | 1 | **≈** |
| f29 | composition | 1242.5 | 0.522299 | 0.700356 | 1 | **≈** |
| f30 | composition | 1267 | 0.51288 | 0.825195 | 1 | **≈** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

