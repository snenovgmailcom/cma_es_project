# C-ONLY — CEC2017, D=10, B=100K

## Ablation

Only the C configuration is used. C/B alternation is disabled and therefore the cross-cycle Phase-0 reuse associated with the alternating schedule is also absent. NBC, staircase threshold selection, basin-dependent restart parameterization, exclusion, and final refinement are retained.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `experiments/cec2017/d10/MSC-CMA-Conly/maxevals_100000/`

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Benchmark results

Fixed-budget terminal results at **B=100,000 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | C-ONLY |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=9) | mean | **60.6899** | 247.949 |
|  | median | **32.7803** | 267.183 |
|  | best | **3.17225** | 13.6465 |
|  | worst | **264.107** | 418.666 |
|  | std | **67.4759** | 93.4645 |
|  | FBTC(B) | **5.14802** | 4.49366 |
| **Hybrid** (n=10) | mean | **170.851** | 244.49 |
|  | median | **202.261** | 249.214 |
|  | best | **4.37748** | 19.0497 |
|  | worst | **423.371** | 544.929 |
|  | std | **123.599** | 128.803 |
|  | FBTC(B) | **2.34679** | 1.13418 |
| **Composition** (n=10) | mean | 1891.37 | **1567.88** |
|  | median | 2152.01 | **1365.44** |
|  | best | 929.859 | **929.844** |
|  | worst | 2696.97 | **2354.48** |
|  | std | 569.04 | **478.129** |
|  | FBTC(B) | 1.71396 | **2.78201** |
| **ALL** (n=29) | mean | 2122.91 | **2060.31** |
|  | median | 2387.06 | **1881.84** |
|  | best | **937.409** | 962.54 |
|  | worst | 3384.44 | **3318.08** |
|  | std | 760.115 | **700.396** |
|  | FBTC(B) | **9.20877** | 8.40984 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **C-ONLY** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary: C-ONLY significant on **5** functions; MSC-CMA-ES significant on **13**; not significant on **11**.

Composition subset: C-ONLY significant on **2** of 10 functions; MSC-CMA-ES significant on **2**; not significant on **6**.

`+` means C-ONLY has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant after Bonferroni adjustment.

| Function | Class | U (C-ONLY) | P(C-ONLY lower) | p_raw | p_Bonferroni | Result |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | basic | 66.5 | 0.974433 | 1.510298e-16 | 4.379864e-15 | **+** |
| f3 | basic | 918 | 0.647059 | 1.499669e-04 | 0.00434904 | **+** |
| f4 | basic | 715.5 | 0.724913 | 1.830508e-06 | 5.308473e-05 | **+** |
| f5 | basic | 2418 | 0.0703576 | 4.891568e-14 | 1.418555e-12 | **−** |
| f6 | basic | 1868 | 0.281815 | 1.477833e-04 | 0.00428572 | **−** |
| f7 | basic | 1114 | 0.571703 | 0.213181 | 1 | **≈** |
| f8 | basic | 2572 | 0.0111496 | 1.002819e-17 | 2.908175e-16 | **−** |
| f9 | basic | 1175.5 | 0.548058 | 0.359615 | 1 | **≈** |
| f10 | basic | 2439.5 | 0.0620915 | 2.539880e-14 | 7.365652e-13 | **−** |
| f11 | hybrid | 2592 | 0.00346021 | 5.063282e-18 | 1.468352e-16 | **−** |
| f12 | hybrid | 1502.5 | 0.422338 | 0.177463 | 1 | **≈** |
| f13 | hybrid | 1381 | 0.46905 | 0.592362 | 1 | **≈** |
| f14 | hybrid | 2464 | 0.052672 | 7.047900e-15 | 2.043891e-13 | **−** |
| f15 | hybrid | 2348 | 0.0972703 | 2.430224e-12 | 7.047651e-11 | **−** |
| f16 | hybrid | 1351 | 0.480584 | 0.7379 | 1 | **≈** |
| f17 | hybrid | 2180 | 0.161861 | 4.031645e-09 | 1.169177e-07 | **−** |
| f18 | hybrid | 1859 | 0.285275 | 1.880656e-04 | 0.0054539 | **−** |
| f19 | hybrid | 2311 | 0.111496 | 1.383404e-11 | 4.011871e-10 | **−** |
| f20 | hybrid | 2455 | 0.0561323 | 1.132810e-14 | 3.285149e-13 | **−** |
| f21 | composition | 705.5 | 0.728758 | 6.775866e-05 | 0.001965 | **+** |
| f22 | composition | 1357 | 0.478278 | 0.707574 | 1 | **≈** |
| f23 | composition | 898.5 | 0.654556 | 0.00720608 | 0.208976 | **≈** |
| f24 | composition | 912 | 0.649366 | 0.00940686 | 0.272799 | **≈** |
| f25 | composition | 1166 | 0.551711 | 0.369813 | 1 | **≈** |
| f26 | composition | 856.5 | 0.670704 | 0.00299485 | 0.0868506 | **≈** |
| f27 | composition | 2344.5 | 0.0986159 | 2.805465e-12 | 8.135850e-11 | **−** |
| f28 | composition | 828.5 | 0.681469 | 0.00160138 | 0.0464399 | **+** |
| f29 | composition | 2323 | 0.106882 | 7.922254e-12 | 2.297454e-10 | **−** |
| f30 | composition | 1282.5 | 0.50692 | 0.906755 | 1 | **≈** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

