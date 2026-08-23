# FIXED-PHI — CEC2017, D=10, B=100K

## Ablation

The automatic staircase selection of the NBC cutting threshold is disabled and a fixed `phi = 2` is used. The remaining MSC-CMA-ES structure is retained.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `ablations/experiments/cec2017/d10/FIXED-PHI/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=100,000 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | FIXED-PHI |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=9) | mean | 60.6899 | **44.0413** |
|  | median | 32.7803 | **28.2142** |
|  | best | **3.17225** | 3.8941 |
|  | worst | 264.107 | **153.426** |
|  | std | 67.4759 | **45.1441** |
|  | FBTC(B) | 5.14802 | **5.31373** |
| **Hybrid** (n=10) | mean | 170.851 | **71.4095** |
|  | median | 202.261 | **40.3337** |
|  | best | 4.37748 | **4.34418** |
|  | worst | 423.371 | **349.313** |
|  | std | 123.599 | **90.6048** |
|  | FBTC(B) | 2.34679 | **2.61246** |
| **Composition** (n=10) | mean | **1891.37** | 2322.4 |
|  | median | **2152.01** | 2435.75 |
|  | best | **929.859** | 1060.83 |
|  | worst | **2696.97** | 2725.48 |
|  | std | 569.04 | **403.422** |
|  | FBTC(B) | **1.71396** | 1.12149 |
| **ALL** (n=29) | mean | **2122.91** | 2437.85 |
|  | median | **2387.06** | 2504.3 |
|  | best | **937.409** | 1069.07 |
|  | worst | 3384.44 | **3228.22** |
|  | std | 760.115 | **539.171** |
|  | FBTC(B) | **9.20877** | 9.04767 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **FIXED-PHI** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary: FIXED-PHI significant on **4** functions; MSC-CMA-ES significant on **2**; not significant on **23**.

Composition subset: FIXED-PHI significant on **0** of 10 functions; MSC-CMA-ES significant on **2**; not significant on **8**.

`+` means FIXED-PHI has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant after Bonferroni adjustment.

| Function | Class | U (FIXED-PHI) | P(FIXED-PHI lower) | p_raw | p_Bonferroni | Result |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | basic | 1272.5 | 0.510765 | 0.85396 | 1 | **≈** |
| f3 | basic | 892.5 | 0.656863 | 3.624307e-05 | 0.00105105 | **+** |
| f4 | basic | 1529.5 | 0.411957 | 0.106321 | 1 | **≈** |
| f5 | basic | 1258.5 | 0.516148 | 0.776962 | 1 | **≈** |
| f6 | basic | 1234 | 0.525567 | 0.658693 | 1 | **≈** |
| f7 | basic | 1136.5 | 0.563053 | 0.273841 | 1 | **≈** |
| f8 | basic | 847 | 0.674356 | 8.877685e-04 | 0.0257453 | **+** |
| f9 | basic | 1216 | 0.532488 | 0.539513 | 1 | **≈** |
| f10 | basic | 1168 | 0.550942 | 0.376968 | 1 | **≈** |
| f11 | hybrid | 1555.5 | 0.401961 | 0.086648 | 1 | **≈** |
| f12 | hybrid | 491 | 0.811226 | 6.149448e-08 | 1.783340e-06 | **+** |
| f13 | hybrid | 947 | 0.635909 | 0.0181509 | 0.526376 | **≈** |
| f14 | hybrid | 1238 | 0.524029 | 0.67818 | 1 | **≈** |
| f15 | hybrid | 1056 | 0.594002 | 0.102465 | 1 | **≈** |
| f16 | hybrid | 1176 | 0.547866 | 0.406598 | 1 | **≈** |
| f17 | hybrid | 1217 | 0.532103 | 0.578556 | 1 | **≈** |
| f18 | hybrid | 470 | 0.8193 | 2.776959e-08 | 8.053180e-07 | **+** |
| f19 | hybrid | 1084 | 0.583237 | 0.148282 | 1 | **≈** |
| f20 | hybrid | 1039 | 0.600538 | 0.0806726 | 1 | **≈** |
| f21 | composition | 971 | 0.626682 | 0.0275352 | 0.798521 | **≈** |
| f22 | composition | 972.5 | 0.626105 | 0.0283237 | 0.821388 | **≈** |
| f23 | composition | 1401 | 0.461361 | 0.503287 | 1 | **≈** |
| f24 | composition | 1657 | 0.362937 | 0.017179 | 0.498192 | **≈** |
| f25 | composition | 2465.5 | 0.0520953 | 6.507404e-15 | 1.887147e-13 | **−** |
| f26 | composition | 1584.5 | 0.390811 | 0.0577761 | 1 | **≈** |
| f27 | composition | 1552.5 | 0.403114 | 0.0917328 | 1 | **≈** |
| f28 | composition | 2055 | 0.209919 | 4.498400e-07 | 1.304536e-05 | **−** |
| f29 | composition | 1216 | 0.532488 | 0.573988 | 1 | **≈** |
| f30 | composition | 1316 | 0.494041 | 0.920034 | 1 | **≈** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

