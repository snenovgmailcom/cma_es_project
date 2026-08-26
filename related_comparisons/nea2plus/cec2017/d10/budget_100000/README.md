# CEC2017, D=10, B=10^5 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=10^5 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=10^5 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | **60.6899** | 253.871 |
|  | Median | **32.7803** | 255.547 |
|  | Minimum | **3.17225** | 13.5536 |
|  | Maximum | **264.107** | 517.27 |
|  | Std. | **67.4759** | 137.663 |
|  | FBTC(B) | **5.14802** | 5.00654 |
| **Hybrid** (n=10) | Mean | **170.851** | 323.305 |
|  | Median | **202.261** | 292.218 |
|  | Minimum | **4.37748** | 39.8943 |
|  | Maximum | **423.371** | 739.73 |
|  | Std. | **123.599** | 167.318 |
|  | FBTC(B) | **2.34679** | 1.04921 |
| **Composition** (n=10) | Mean | **1891.37** | 2393.13 |
|  | Median | **2152.01** | 2479.15 |
|  | Minimum | **929.859** | 1415.54 |
|  | Maximum | **2696.97** | 3030.94 |
|  | Std. | 569.04 | **422.432** |
|  | FBTC(B) | **1.71396** | 0.358324 |
| **All** (n=29) | Mean | **2122.91** | 2970.31 |
|  | Median | **2387.06** | 3026.91 |
|  | Minimum | **937.409** | 1468.99 |
|  | Maximum | **3384.44** | 4287.94 |
|  | Std. | 760.115 | **727.413** |
|  | FBTC(B) | **9.20877** | 6.41407 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary from the NEA2+ perspective: **2 ↓**, **21 ↑**, and **6 —**.

Composition subset: **0 ↓**, **8 ↑**, and **2 —** across 10 functions.

Direction is stated from the NEA2+ perspective: `↓` denotes a statistically significant shift toward lower terminal errors, `↑` a statistically significant shift toward higher terminal errors, and `—` no statistically significant difference after Bonferroni correction.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | Unimodal and simple multimodal | 150 | 0.94233 |
| f3 | Unimodal and simple multimodal | 2601 | 0 |
| f4 | Unimodal and simple multimodal | 2277 | 0.124567 |
| f5 | Unimodal and simple multimodal | 2556 | 0.017301 |
| f6 | Unimodal and simple multimodal | 223 | 0.914264 |
| f7 | Unimodal and simple multimodal | 1470 | 0.434833 |
| f8 | Unimodal and simple multimodal | 2592 | 0.00346021 |
| f9 | Unimodal and simple multimodal | 1683 | 0.352941 |
| f10 | Unimodal and simple multimodal | 2335 | 0.102268 |
| f11 | Hybrid | 2601 | 0 |
| f12 | Hybrid | 1857 | 0.286044 |
| f13 | Hybrid | 1861 | 0.284506 |
| f14 | Hybrid | 2534 | 0.0257593 |
| f15 | Hybrid | 2237 | 0.139946 |
| f16 | Hybrid | 1440 | 0.446367 |
| f17 | Hybrid | 2280 | 0.123414 |
| f18 | Hybrid | 1308 | 0.497116 |
| f19 | Hybrid | 1846 | 0.290273 |
| f20 | Hybrid | 2520 | 0.0311419 |
| f21 | Composition | 2140 | 0.17724 |
| f22 | Composition | 2294 | 0.118032 |
| f23 | Composition | 1825 | 0.298347 |
| f24 | Composition | 2490 | 0.0426759 |
| f25 | Composition | 2208 | 0.151096 |
| f26 | Composition | 2335 | 0.102268 |
| f27 | Composition | 1414 | 0.456363 |
| f28 | Composition | 2505 | 0.0369089 |
| f29 | Composition | 2398 | 0.0780469 |
| f30 | Composition | 1225 | 0.529027 |

### p_raw

| Function | p_raw |
|:--|--:|
| f1 | 1.3972e-14 |
| f3 | 6.25304e-19 |
| f4 | 4.54304e-11 |
| f5 | 3.72391e-17 |
| f6 | 5.67605e-13 |
| f7 | 0.258027 |
| f8 | 3.88223e-18 |
| f9 | 0.00997579 |
| f10 | 4.50506e-12 |
| f11 | 2.98872e-18 |
| f12 | 0.000198321 |
| f13 | 0.00017831 |
| f14 | 1.55624e-16 |
| f15 | 3.74326e-10 |
| f16 | 0.352223 |
| f17 | 5.67105e-11 |
| f18 | 0.962634 |
| f19 | 0.000264778 |
| f20 | 3.39463e-16 |
| f21 | 1.96122e-08 |
| f22 | 3.00265e-11 |
| f23 | 0.000453209 |
| f24 | 1.75208e-15 |
| f25 | 1.27683e-09 |
| f26 | 4.50817e-12 |
| f27 | 0.449365 |
| f28 | 7.75259e-16 |
| f29 | 2.10583e-13 |
| f30 | 0.615701 |

### p_Bonferroni and Direction

| Function | p_Bonferroni | Direction |
|:--|--:|:--:|
| f1 | **4.05187e-13** | **↓** |
| f3 | **1.81338e-17** | **↑** |
| f4 | **1.31748e-09** | **↑** |
| f5 | **1.07994e-15** | **↑** |
| f6 | **1.64606e-11** | **↓** |
| f7 | 1 | **—** |
| f8 | **1.12585e-16** | **↑** |
| f9 | 0.289298 | **—** |
| f10 | **1.30647e-10** | **↑** |
| f11 | **8.66728e-17** | **↑** |
| f12 | **0.00575132** | **↑** |
| f13 | **0.00517099** | **↑** |
| f14 | **4.51311e-15** | **↑** |
| f15 | **1.08555e-08** | **↑** |
| f16 | 1 | **—** |
| f17 | **1.64461e-09** | **↑** |
| f18 | 1 | **—** |
| f19 | **0.00767856** | **↑** |
| f20 | **9.84442e-15** | **↑** |
| f21 | **5.68753e-07** | **↑** |
| f22 | **8.70768e-10** | **↑** |
| f23 | **0.0131431** | **↑** |
| f24 | **5.08103e-14** | **↑** |
| f25 | **3.70281e-08** | **↑** |
| f26 | **1.30737e-10** | **↑** |
| f27 | 1 | **—** |
| f28 | **2.24825e-14** | **↑** |
| f29 | **6.1069e-12** | **↑** |
| f30 | 1 | **—** |

Full-precision MWU statistics are available in [`../../../mwu/details.csv`](../../../mwu/details.csv) relative to the NEA2+ comparison root.

<a id="deep-statistical-comparison"></a>

## Deep Statistical Comparison

DSC compares **MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES** using the 51 unmodified terminal errors per function. Per-function rankings use Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`, `monte_carlo_iterations=0`). The rank matrices are analyzed with the Friedman omnibus test separately for all functions and for the composition-function subset. When the omnibus null hypothesis is rejected, Holm-adjusted post-hoc comparisons are performed against the algorithm with the lowest mean DSC rank.

`★` means MSC-CMA-ES has the lowest mean DSC rank and the Friedman test rejects the null hypothesis; `≈` means the Friedman test rejects the null hypothesis but the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant; `↓` means the lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means the Friedman test does not reject the null hypothesis and no post-hoc interpretation is made.

### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | NEA2+ | BIPOP-CMA-ES |
|:--|--:|--:|--:|
| f1 | 3 | 2 | 1 |
| f3 | 2 | 3 | 1 |
| f4 | 3 | 2 | 1 |
| f5 | 1 | 3 | 2 |
| f6 | 3 | 2 | 1 |
| f7 | 1.5 | 3 | 1.5 |
| f8 | 1.5 | 3 | 1.5 |
| f9 | 3 | 2 | 1 |
| f10 | 1.5 | 3 | 1.5 |
| f11 | 1 | 3 | 2 |
| f12 | 1.5 | 3 | 1.5 |
| f13 | 2 | 3 | 1 |
| f14 | 1.5 | 3 | 1.5 |
| f15 | 2 | 3 | 1 |
| f16 | 2.5 | 2.5 | 1 |
| f17 | 1.5 | 3 | 1.5 |
| f18 | 2 | 2 | 2 |
| f19 | 2 | 3 | 1 |
| f20 | 1 | 3 | 2 |
| f21 | 1 | 2 | 3 |
| f22 | 1 | 2 | 3 |
| f23 | 1.5 | 3 | 1.5 |
| f24 | 1 | 2 | 3 |
| f25 | 1 | 2 | 3 |
| f26 | 1 | 2 | 3 |
| f27 | 2 | 3 | 1 |
| f28 | 1 | 2 | 3 |
| f29 | 1 | 2.5 | 2.5 |
| f30 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 29 | MSC-CMA-ES | 1.65517 | 2.58621 | 1.75862 | 0.000525204 | MSC-CMA-ES | — | 0.000392206 | **★** |
| Composition | 10 | MSC-CMA-ES | 1.15 | 2.35 | 2.5 | 0.00419023 | MSC-CMA-ES | — | 0.00364518 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
