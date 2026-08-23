# NO-NBC — CEC2017, D=10, B=100K

## Ablation

This control removes nearest-better clustering and the basin-based restart structure. The Phase-0 Sobol points are ranked by objective value and CMA-ES restarts are launched sequentially from the ranked points until the budget is exhausted.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `ablations/experiments/cec2017/d10/NO-NBC/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=100,000 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | NO-NBC |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=9) | mean | **60.6899** | 223.363 |
|  | median | **32.7803** | 176.108 |
|  | best | **3.17225** | 9.8976 |
|  | worst | **264.107** | 571.443 |
|  | std | **67.4759** | 145.398 |
|  | FBTC(B) | **5.14802** | 4.98885 |
| **Hybrid** (n=10) | mean | **170.851** | 251.529 |
|  | median | **202.261** | 250.344 |
|  | best | **4.37748** | 30.5265 |
|  | worst | **423.371** | 876.672 |
|  | std | **123.599** | 170.354 |
|  | FBTC(B) | **2.34679** | 1.09112 |
| **Composition** (n=10) | mean | **1891.37** | 2706.96 |
|  | median | **2152.01** | 2602.5 |
|  | best | **929.859** | 2215.19 |
|  | worst | **2696.97** | 3199.85 |
|  | std | 569.04 | **313.722** |
|  | FBTC(B) | **1.71396** | 0.261822 |
| **ALL** (n=29) | mean | **2122.91** | 3181.86 |
|  | median | **2387.06** | 3028.95 |
|  | best | **937.409** | 2255.61 |
|  | worst | **3384.44** | 4647.97 |
|  | std | 760.115 | **629.475** |
|  | FBTC(B) | **9.20877** | 6.34179 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **NO-NBC** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary: NO-NBC significant on **5** functions; MSC-CMA-ES significant on **17**; not significant on **7**.

Composition subset: NO-NBC significant on **0** of 10 functions; MSC-CMA-ES significant on **6**; not significant on **4**.

`+` means NO-NBC has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant after Bonferroni adjustment.

| Function | Class | U (NO-NBC) | P(NO-NBC lower) | p_raw | p_Bonferroni | Result |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | basic | 31 | 0.988082 | 1.512468e-18 | 4.386156e-17 | **+** |
| f3 | basic | 867 | 0.666667 | 7.147199e-06 | 2.072688e-04 | **+** |
| f4 | basic | 586.5 | 0.77451 | 1.085672e-09 | 3.148450e-08 | **+** |
| f5 | basic | 2401.5 | 0.0767013 | 1.137164e-13 | 3.297775e-12 | **−** |
| f6 | basic | 310 | 0.880815 | 3.454187e-11 | 1.001714e-09 | **+** |
| f7 | basic | 1931 | 0.257593 | 2.482271e-05 | 7.198586e-04 | **−** |
| f8 | basic | 2574.5 | 0.0101884 | 8.690181e-18 | 2.520153e-16 | **−** |
| f9 | basic | 637.5 | 0.754902 | 6.862540e-09 | 1.990137e-07 | **+** |
| f10 | basic | 2163.5 | 0.168205 | 7.804680e-09 | 2.263357e-07 | **−** |
| f11 | hybrid | 2555 | 0.0176855 | 3.940159e-17 | 1.142646e-15 | **−** |
| f12 | hybrid | 1346 | 0.482507 | 0.763261 | 1 | **≈** |
| f13 | hybrid | 1392 | 0.464821 | 0.542444 | 1 | **≈** |
| f14 | hybrid | 2521 | 0.0307574 | 3.211612e-16 | 9.313674e-15 | **−** |
| f15 | hybrid | 2399 | 0.0776624 | 2.003046e-13 | 5.808833e-12 | **−** |
| f16 | hybrid | 929 | 0.64283 | 0.0130283 | 0.377821 | **≈** |
| f17 | hybrid | 2250 | 0.134948 | 2.133929e-10 | 6.188393e-09 | **−** |
| f18 | hybrid | 2004 | 0.229527 | 2.538992e-06 | 7.363078e-05 | **−** |
| f19 | hybrid | 2343 | 0.0991926 | 3.084903e-12 | 8.946218e-11 | **−** |
| f20 | hybrid | 2402 | 0.076509 | 1.723377e-13 | 4.997792e-12 | **−** |
| f21 | composition | 1396 | 0.463283 | 0.524422 | 1 | **≈** |
| f22 | composition | 2034 | 0.217993 | 9.255704e-07 | 2.684154e-05 | **−** |
| f23 | composition | 1517 | 0.416763 | 0.14826 | 1 | **≈** |
| f24 | composition | 2562.5 | 0.014802 | 3.087440e-17 | 8.953576e-16 | **−** |
| f25 | composition | 2477 | 0.047674 | 3.366054e-15 | 9.761558e-14 | **−** |
| f26 | composition | 2483 | 0.0453672 | 2.538120e-15 | 7.360549e-14 | **−** |
| f27 | composition | 1679.5 | 0.354287 | 0.0110156 | 0.319452 | **≈** |
| f28 | composition | 2315.5 | 0.109765 | 1.117453e-11 | 3.240613e-10 | **−** |
| f29 | composition | 2499 | 0.0392157 | 1.076004e-15 | 3.120411e-14 | **−** |
| f30 | composition | 1489 | 0.427528 | 0.208309 | 1 | **≈** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

