# FIXED-PHI — CEC2017, D=10, B=10^5

## Ablation

The automatic staircase selection of the NBC cutting threshold is disabled and a fixed `phi = 2` is used. The remaining MSC-CMA-ES structure is retained.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `ablations/experiments/cec2017/d10/FIXED-PHI/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=10^5 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | FIXED-PHI |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | 60.6899 | **44.0413** |
|  | Median | 32.7803 | **28.2142** |
|  | Minimum | **3.17225** | 3.8941 |
|  | Maximum | 264.107 | **153.426** |
|  | Std. | 67.4759 | **45.1441** |
|  | FBTC(B) | 5.14802 | **5.31373** |
| **Hybrid** (n=10) | Mean | 170.851 | **71.4095** |
|  | Median | 202.261 | **40.3337** |
|  | Minimum | 4.37748 | **4.34418** |
|  | Maximum | 423.371 | **349.313** |
|  | Std. | 123.599 | **90.6048** |
|  | FBTC(B) | 2.34679 | **2.61246** |
| **Composition** (n=10) | Mean | **1891.37** | 2322.4 |
|  | Median | **2152.01** | 2435.75 |
|  | Minimum | **929.859** | 1060.83 |
|  | Maximum | **2696.97** | 2725.48 |
|  | Std. | 569.04 | **403.422** |
|  | FBTC(B) | **1.71396** | 1.12149 |
| **All** (n=29) | Mean | **2122.91** | 2437.85 |
|  | Median | **2387.06** | 2504.3 |
|  | Minimum | **937.409** | 1069.07 |
|  | Maximum | 3384.44 | **3228.22** |
|  | Std. | 760.115 | **539.171** |
|  | FBTC(B) | **9.20877** | 9.04767 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **FIXED-PHI** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary from the FIXED-PHI perspective: **↓ 4**, **↑ 2**, **— 23**.

Composition subset from the FIXED-PHI perspective: **↓ 0**, **↑ 2**, **— 8**.

`↓` denotes a statistically significant shift toward lower terminal errors for FIXED-PHI; `↑` denotes a statistically significant shift toward higher terminal errors; `—` denotes no statistically significant difference after Bonferroni correction.

| Function | Class | U (FIXED-PHI) | P(FIXED-PHI lower) | p_raw | p_Bonferroni | Direction |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | Unimodal and simple multimodal | 1272.5 | 0.510765 | 0.85396 | 1 | **—** |
| f3 | Unimodal and simple multimodal | 892.5 | 0.656863 | 3.62431e-05 | 0.00105105 | **↓** |
| f4 | Unimodal and simple multimodal | 1529.5 | 0.411957 | 0.106321 | 1 | **—** |
| f5 | Unimodal and simple multimodal | 1258.5 | 0.516148 | 0.776962 | 1 | **—** |
| f6 | Unimodal and simple multimodal | 1234 | 0.525567 | 0.658693 | 1 | **—** |
| f7 | Unimodal and simple multimodal | 1136.5 | 0.563053 | 0.273841 | 1 | **—** |
| f8 | Unimodal and simple multimodal | 847 | 0.674356 | 0.000887769 | 0.0257453 | **↓** |
| f9 | Unimodal and simple multimodal | 1216 | 0.532488 | 0.539513 | 1 | **—** |
| f10 | Unimodal and simple multimodal | 1168 | 0.550942 | 0.376968 | 1 | **—** |
| f11 | Hybrid | 1555.5 | 0.401961 | 0.086648 | 1 | **—** |
| f12 | Hybrid | 491 | 0.811226 | 6.14945e-08 | 1.78334e-06 | **↓** |
| f13 | Hybrid | 947 | 0.635909 | 0.0181509 | 0.526376 | **—** |
| f14 | Hybrid | 1238 | 0.524029 | 0.67818 | 1 | **—** |
| f15 | Hybrid | 1056 | 0.594002 | 0.102465 | 1 | **—** |
| f16 | Hybrid | 1176 | 0.547866 | 0.406598 | 1 | **—** |
| f17 | Hybrid | 1217 | 0.532103 | 0.578556 | 1 | **—** |
| f18 | Hybrid | 470 | 0.8193 | 2.77696e-08 | 8.05318e-07 | **↓** |
| f19 | Hybrid | 1084 | 0.583237 | 0.148282 | 1 | **—** |
| f20 | Hybrid | 1039 | 0.600538 | 0.0806726 | 1 | **—** |
| f21 | Composition | 971 | 0.626682 | 0.0275352 | 0.798521 | **—** |
| f22 | Composition | 972.5 | 0.626105 | 0.0283237 | 0.821388 | **—** |
| f23 | Composition | 1401 | 0.461361 | 0.503287 | 1 | **—** |
| f24 | Composition | 1657 | 0.362937 | 0.017179 | 0.498192 | **—** |
| f25 | Composition | 2465.5 | 0.0520953 | 6.5074e-15 | 1.88715e-13 | **↑** |
| f26 | Composition | 1584.5 | 0.390811 | 0.0577761 | 1 | **—** |
| f27 | Composition | 1552.5 | 0.403114 | 0.0917328 | 1 | **—** |
| f28 | Composition | 2055 | 0.209919 | 4.4984e-07 | 1.30454e-05 | **↑** |
| f29 | Composition | 1216 | 0.532488 | 0.573988 | 1 | **—** |
| f30 | Composition | 1316 | 0.494041 | 0.920034 | 1 | **—** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

