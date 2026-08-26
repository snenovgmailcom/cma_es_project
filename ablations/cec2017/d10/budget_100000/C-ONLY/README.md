# C-ONLY — CEC2017, D=10, B=10^5

## Ablation

Only the C configuration is used. C/B alternation is disabled and therefore the cross-cycle Phase-0 reuse associated with the alternating schedule is also absent. NBC, staircase threshold selection, basin-dependent restart parameterization, exclusion, and final refinement are retained.

Reference: full MSC-CMA-ES at the same suite, dimension, budget, and 51-run protocol.

Raw ablation data: `experiments/cec2017/d10/MSC-CMA-Conly/maxevals_100000/`

Contents: [Cross-suite C-ONLY results](#cross-suite-c-only-results) · [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u)

## Cross-suite C-ONLY results

The C-ONLY extension was also evaluated on the composition-function subsets of eight suite–dimension–budget cells. Each linked page compares C-ONLY directly with full MSC-CMA-ES using 51 runs per function.

The cross-suite Mann–Whitney U tests use independent two-sided comparisons of raw terminal errors, with Bonferroni correction over the composition functions within each cell.

| Suite | D | Budget | C-ONLY ↓ / ↑ / — | Results |
|:--|--:|--:|:--:|:--|
| CEC2014 | 10 | 10^5 | 2 / 5 / 1 | [results](../../../../../related_comparisons/conly/cec2014/d10/budget_100000/README.md) |
| CEC2017 | 10 | 10^5 | 3 / 2 / 5 | [results](../../../../../related_comparisons/conly/cec2017/d10/budget_100000/README.md) |
| CEC2020 | 5 | 5×10^4 | 2 / 1 / 0 | [results](../../../../../related_comparisons/conly/cec2020/d5/budget_50000/README.md) |
| CEC2020 | 10 | 10^6 | 0 / 0 / 3 | [results](../../../../../related_comparisons/conly/cec2020/d10/budget_1000000/README.md) |
| CEC2020 | 15 | 3×10^6 | 0 / 1 / 2 | [results](../../../../../related_comparisons/conly/cec2020/d15/budget_3000000/README.md) |
| CEC2020 | 20 | 10^7 | 1 / 0 / 2 | [results](../../../../../related_comparisons/conly/cec2020/d20/budget_10000000/README.md) |
| CEC2022 | 10 | 2×10^5 | 1 / 2 / 1 | [results](../../../../../related_comparisons/conly/cec2022/d10/budget_200000/README.md) |
| CEC2022 | 20 | 10^6 | 0 / 2 / 2 | [results](../../../../../related_comparisons/conly/cec2022/d20/budget_1000000/README.md) |

From the C-ONLY perspective, ↓ denotes a statistically significant shift toward lower terminal errors, ↑ a statistically significant shift toward higher terminal errors, and — no statistically significant difference after Bonferroni correction.

For CEC2017 at D=10 and B=10^5, this cross-suite analysis uses Bonferroni correction over the 10 composition functions. The full ablation MWU analysis below uses correction over all 29 CEC2017 functions; therefore the composition-subset counts need not be identical.

## Benchmark results

Fixed-budget terminal results at **B=10^5 NFE**, using 51 runs per function.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for descriptive metrics; standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | C-ONLY |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | **60.6899** | 247.949 |
|  | Median | **32.7803** | 267.183 |
|  | Minimum | **3.17225** | 13.6465 |
|  | Maximum | **264.107** | 418.666 |
|  | Std. | **67.4759** | 93.4645 |
|  | FBTC(B) | **5.14802** | 4.49366 |
| **Hybrid** (n=10) | Mean | **170.851** | 244.49 |
|  | Median | **202.261** | 249.214 |
|  | Minimum | **4.37748** | 19.0497 |
|  | Maximum | **423.371** | 544.929 |
|  | Std. | **123.599** | 128.803 |
|  | FBTC(B) | **2.34679** | 1.13418 |
| **Composition** (n=10) | Mean | 1891.37 | **1567.88** |
|  | Median | 2152.01 | **1365.44** |
|  | Minimum | 929.859 | **929.844** |
|  | Maximum | 2696.97 | **2354.48** |
|  | Std. | 569.04 | **478.129** |
|  | FBTC(B) | 1.71396 | **2.78201** |
| **All** (n=29) | Mean | 2122.91 | **2060.31** |
|  | Median | 2387.06 | **1881.84** |
|  | Minimum | **937.409** | 962.54 |
|  | Maximum | 3384.44 | **3318.08** |
|  | Std. | 760.115 | **700.396** |
|  | FBTC(B) | **9.20877** | 8.40984 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare **C-ONLY** with **MSC-CMA-ES** on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 CEC2017 functions**.

Setting summary from the C-ONLY perspective: **↓ 5**, **↑ 13**, **— 11**.

Composition subset from the C-ONLY perspective: **↓ 2**, **↑ 2**, **— 6**.

`↓` denotes a statistically significant shift toward lower terminal errors for C-ONLY; `↑` denotes a statistically significant shift toward higher terminal errors; `—` denotes no statistically significant difference after Bonferroni correction.

| Function | Class | U (C-ONLY) | P(C-ONLY lower) | p_raw | p_Bonferroni | Direction |
|:--|:--|--:|--:|--:|--:|:--:|
| f1 | Unimodal and simple multimodal | 66.5 | 0.974433 | 1.5103e-16 | 4.37986e-15 | **↓** |
| f3 | Unimodal and simple multimodal | 918 | 0.647059 | 0.000149967 | 0.00434904 | **↓** |
| f4 | Unimodal and simple multimodal | 715.5 | 0.724913 | 1.83051e-06 | 5.30847e-05 | **↓** |
| f5 | Unimodal and simple multimodal | 2418 | 0.0703576 | 4.89157e-14 | 1.41855e-12 | **↑** |
| f6 | Unimodal and simple multimodal | 1868 | 0.281815 | 0.000147783 | 0.00428572 | **↑** |
| f7 | Unimodal and simple multimodal | 1114 | 0.571703 | 0.213181 | 1 | **—** |
| f8 | Unimodal and simple multimodal | 2572 | 0.0111496 | 1.00282e-17 | 2.90818e-16 | **↑** |
| f9 | Unimodal and simple multimodal | 1175.5 | 0.548058 | 0.359615 | 1 | **—** |
| f10 | Unimodal and simple multimodal | 2439.5 | 0.0620915 | 2.53988e-14 | 7.36565e-13 | **↑** |
| f11 | Hybrid | 2592 | 0.00346021 | 5.06328e-18 | 1.46835e-16 | **↑** |
| f12 | Hybrid | 1502.5 | 0.422338 | 0.177463 | 1 | **—** |
| f13 | Hybrid | 1381 | 0.46905 | 0.592362 | 1 | **—** |
| f14 | Hybrid | 2464 | 0.052672 | 7.0479e-15 | 2.04389e-13 | **↑** |
| f15 | Hybrid | 2348 | 0.0972703 | 2.43022e-12 | 7.04765e-11 | **↑** |
| f16 | Hybrid | 1351 | 0.480584 | 0.7379 | 1 | **—** |
| f17 | Hybrid | 2180 | 0.161861 | 4.03164e-09 | 1.16918e-07 | **↑** |
| f18 | Hybrid | 1859 | 0.285275 | 0.000188066 | 0.0054539 | **↑** |
| f19 | Hybrid | 2311 | 0.111496 | 1.3834e-11 | 4.01187e-10 | **↑** |
| f20 | Hybrid | 2455 | 0.0561323 | 1.13281e-14 | 3.28515e-13 | **↑** |
| f21 | Composition | 705.5 | 0.728758 | 6.77587e-05 | 0.001965 | **↓** |
| f22 | Composition | 1357 | 0.478278 | 0.707574 | 1 | **—** |
| f23 | Composition | 898.5 | 0.654556 | 0.00720608 | 0.208976 | **—** |
| f24 | Composition | 912 | 0.649366 | 0.00940686 | 0.272799 | **—** |
| f25 | Composition | 1166 | 0.551711 | 0.369813 | 1 | **—** |
| f26 | Composition | 856.5 | 0.670704 | 0.00299485 | 0.0868506 | **—** |
| f27 | Composition | 2344.5 | 0.0986159 | 2.80547e-12 | 8.13585e-11 | **↑** |
| f28 | Composition | 828.5 | 0.681469 | 0.00160138 | 0.0464399 | **↓** |
| f29 | Composition | 2323 | 0.106882 | 7.92225e-12 | 2.29745e-10 | **↑** |
| f30 | Composition | 1282.5 | 0.50692 | 0.906755 | 1 | **—** |

Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).

