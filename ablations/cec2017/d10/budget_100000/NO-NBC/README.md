# NO-NBC — CEC2017, D=10, B=10^5

## Ablation

This control removes nearest-better clustering and the basin-based restart structure. The Phase-0 Sobol points are ranked by objective value and CMA-ES restarts are launched sequentially from the ranked points until the budget is exhausted.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `ablations/experiments/cec2017/d10/NO-NBC/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=10^5 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NO-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | **60.6899** | 223.363 |
|  | Median | **32.7803** | 176.108 |
|  | Minimum | **3.17225** | 9.8976 |
|  | Maximum | **264.107** | 571.443 |
|  | Std. | **67.4759** | 145.398 |
|  | FBTC(B) | **5.14802** | 4.98885 |
| **Hybrid** (n=10) | Mean | **170.851** | 251.529 |
|  | Median | **202.261** | 250.344 |
|  | Minimum | **4.37748** | 30.5265 |
|  | Maximum | **423.371** | 876.672 |
|  | Std. | **123.599** | 170.354 |
|  | FBTC(B) | **2.34679** | 1.09112 |
| **Composition** (n=10) | Mean | **1891.37** | 2706.96 |
|  | Median | **2152.01** | 2602.5 |
|  | Minimum | **929.859** | 2215.19 |
|  | Maximum | **2696.97** | 3199.85 |
|  | Std. | 569.04 | **313.722** |
|  | FBTC(B) | **1.71396** | 0.261822 |
| **All** (n=29) | Mean | **2122.91** | 3181.86 |
|  | Median | **2387.06** | 3028.95 |
|  | Minimum | **937.409** | 2255.61 |
|  | Maximum | **3384.44** | 4647.97 |
|  | Std. | 760.115 | **629.475** |
|  | FBTC(B) | **9.20877** | 6.34179 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **NO-NBC** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary from the NO-NBC perspective: **↓ 5**, **↑ 17**, **— 7**.

Composition subset from the NO-NBC perspective: **↓ 0**, **↑ 6**, **— 4**.

`↓` denotes a statistically significant shift toward lower terminal errors for NO-NBC; `↑` denotes a statistically significant shift toward higher terminal errors; `—` denotes no statistically significant difference after Bonferroni correction.

| Function | Class | U (NO-NBC) | P(NO-NBC lower) | p_raw | p_Bonferroni | Direction |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | Unimodal and simple multimodal | 31 | 0.988082 | 1.51247e-18 | 4.38616e-17 | **↓** |
| f3 | Unimodal and simple multimodal | 867 | 0.666667 | 7.1472e-06 | 0.000207269 | **↓** |
| f4 | Unimodal and simple multimodal | 586.5 | 0.77451 | 1.08567e-09 | 3.14845e-08 | **↓** |
| f5 | Unimodal and simple multimodal | 2401.5 | 0.0767013 | 1.13716e-13 | 3.29778e-12 | **↑** |
| f6 | Unimodal and simple multimodal | 310 | 0.880815 | 3.45419e-11 | 1.00171e-09 | **↓** |
| f7 | Unimodal and simple multimodal | 1931 | 0.257593 | 2.48227e-05 | 0.000719859 | **↑** |
| f8 | Unimodal and simple multimodal | 2574.5 | 0.0101884 | 8.69018e-18 | 2.52015e-16 | **↑** |
| f9 | Unimodal and simple multimodal | 637.5 | 0.754902 | 6.86254e-09 | 1.99014e-07 | **↓** |
| f10 | Unimodal and simple multimodal | 2163.5 | 0.168205 | 7.80468e-09 | 2.26336e-07 | **↑** |
| f11 | Hybrid | 2555 | 0.0176855 | 3.94016e-17 | 1.14265e-15 | **↑** |
| f12 | Hybrid | 1346 | 0.482507 | 0.763261 | 1 | **—** |
| f13 | Hybrid | 1392 | 0.464821 | 0.542444 | 1 | **—** |
| f14 | Hybrid | 2521 | 0.0307574 | 3.21161e-16 | 9.31367e-15 | **↑** |
| f15 | Hybrid | 2399 | 0.0776624 | 2.00305e-13 | 5.80883e-12 | **↑** |
| f16 | Hybrid | 929 | 0.64283 | 0.0130283 | 0.377821 | **—** |
| f17 | Hybrid | 2250 | 0.134948 | 2.13393e-10 | 6.18839e-09 | **↑** |
| f18 | Hybrid | 2004 | 0.229527 | 2.53899e-06 | 7.36308e-05 | **↑** |
| f19 | Hybrid | 2343 | 0.0991926 | 3.0849e-12 | 8.94622e-11 | **↑** |
| f20 | Hybrid | 2402 | 0.076509 | 1.72338e-13 | 4.99779e-12 | **↑** |
| f21 | Composition | 1396 | 0.463283 | 0.524422 | 1 | **—** |
| f22 | Composition | 2034 | 0.217993 | 9.2557e-07 | 2.68415e-05 | **↑** |
| f23 | Composition | 1517 | 0.416763 | 0.14826 | 1 | **—** |
| f24 | Composition | 2562.5 | 0.014802 | 3.08744e-17 | 8.95358e-16 | **↑** |
| f25 | Composition | 2477 | 0.047674 | 3.36605e-15 | 9.76156e-14 | **↑** |
| f26 | Composition | 2483 | 0.0453672 | 2.53812e-15 | 7.36055e-14 | **↑** |
| f27 | Composition | 1679.5 | 0.354287 | 0.0110156 | 0.319452 | **—** |
| f28 | Composition | 2315.5 | 0.109765 | 1.11745e-11 | 3.24061e-10 | **↑** |
| f29 | Composition | 2499 | 0.0392157 | 1.076e-15 | 3.12041e-14 | **↑** |
| f30 | Composition | 1489 | 0.427528 | 0.208309 | 1 | **—** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

