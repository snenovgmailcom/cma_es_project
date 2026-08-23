# CEC2017, D=10, B=100K — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=100,000 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=100,000 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=9) | mean | **60.6899** | 253.871 |
|  | median | **32.7803** | 255.547 |
|  | best | **3.17225** | 13.5536 |
|  | worst | **264.107** | 517.27 |
|  | std | **67.4759** | 137.663 |
|  | FBTC(B) | **5.14802** | 5.00654 |
| **Hybrid** (n=10) | mean | **170.851** | 323.305 |
|  | median | **202.261** | 292.218 |
|  | best | **4.37748** | 39.8943 |
|  | worst | **423.371** | 739.73 |
|  | std | **123.599** | 167.318 |
|  | FBTC(B) | **2.34679** | 1.04921 |
| **Composition** (n=10) | mean | **1891.37** | 2393.13 |
|  | median | **2152.01** | 2479.15 |
|  | best | **929.859** | 1415.54 |
|  | worst | **2696.97** | 3030.94 |
|  | std | 569.04 | **422.432** |
|  | FBTC(B) | **1.71396** | 0.358324 |
| **ALL** (n=29) | mean | **2122.91** | 2970.31 |
|  | median | **2387.06** | 3026.91 |
|  | best | **937.409** | 1468.99 |
|  | worst | **3384.44** | 4287.94 |
|  | std | 760.115 | **727.413** |
|  | FBTC(B) | **9.20877** | 6.41407 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These descriptive values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **29 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary: NEA2+ significant on **2** functions; MSC-CMA-ES significant on **21**; not significant on **6**.

Composition subset: NEA2+ significant on **0** of 10 functions; MSC-CMA-ES significant on **8**; not significant on **2**.

`+` means NEA2+ has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant at `alpha=0.05` after Bonferroni adjustment.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | basic | 150 | 0.94233 |
| f3 | basic | 2601 | 0 |
| f4 | basic | 2277 | 0.124567 |
| f5 | basic | 2556 | 0.017301 |
| f6 | basic | 223 | 0.914264 |
| f7 | basic | 1470 | 0.434833 |
| f8 | basic | 2592 | 0.00346021 |
| f9 | basic | 1683 | 0.352941 |
| f10 | basic | 2335 | 0.102268 |
| f11 | hybrid | 2601 | 0 |
| f12 | hybrid | 1857 | 0.286044 |
| f13 | hybrid | 1861 | 0.284506 |
| f14 | hybrid | 2534 | 0.0257593 |
| f15 | hybrid | 2237 | 0.139946 |
| f16 | hybrid | 1440 | 0.446367 |
| f17 | hybrid | 2280 | 0.123414 |
| f18 | hybrid | 1308 | 0.497116 |
| f19 | hybrid | 1846 | 0.290273 |
| f20 | hybrid | 2520 | 0.0311419 |
| f21 | composition | 2140 | 0.17724 |
| f22 | composition | 2294 | 0.118032 |
| f23 | composition | 1825 | 0.298347 |
| f24 | composition | 2490 | 0.0426759 |
| f25 | composition | 2208 | 0.151096 |
| f26 | composition | 2335 | 0.102268 |
| f27 | composition | 1414 | 0.456363 |
| f28 | composition | 2505 | 0.0369089 |
| f29 | composition | 2398 | 0.0780469 |
| f30 | composition | 1225 | 0.529027 |

### Raw two-sided p-value

| Function | p_raw |
|:--|--:|
| f1 | 1.397198e-14 |
| f3 | 6.253038e-19 |
| f4 | 4.543041e-11 |
| f5 | 3.723914e-17 |
| f6 | 5.676054e-13 |
| f7 | 0.258027 |
| f8 | 3.882229e-18 |
| f9 | 0.00997579 |
| f10 | 4.505062e-12 |
| f11 | 2.988716e-18 |
| f12 | 0.000198321 |
| f13 | 0.00017831 |
| f14 | 1.556245e-16 |
| f15 | 3.743259e-10 |
| f16 | 0.352223 |
| f17 | 5.671055e-11 |
| f18 | 0.962634 |
| f19 | 0.000264778 |
| f20 | 3.394628e-16 |
| f21 | 1.961218e-08 |
| f22 | 3.002649e-11 |
| f23 | 0.000453209 |
| f24 | 1.752079e-15 |
| f25 | 1.276830e-09 |
| f26 | 4.508174e-12 |
| f27 | 0.449365 |
| f28 | 7.752592e-16 |
| f29 | 2.105828e-13 |
| f30 | 0.615701 |

### Bonferroni-adjusted p-value and decision

| Function | p_Bonferroni | Decision |
|:--|--:|:--:|
| f1 | **4.051873e-13** | **+** |
| f3 | **1.813381e-17** | **−** |
| f4 | **1.317482e-09** | **−** |
| f5 | **1.079935e-15** | **−** |
| f6 | **1.646056e-11** | **+** |
| f7 | 1 | **≈** |
| f8 | **1.125846e-16** | **−** |
| f9 | 0.289298 | **≈** |
| f10 | **1.306468e-10** | **−** |
| f11 | **8.667278e-17** | **−** |
| f12 | **0.00575132** | **−** |
| f13 | **0.00517099** | **−** |
| f14 | **4.513110e-15** | **−** |
| f15 | **1.085545e-08** | **−** |
| f16 | 1 | **≈** |
| f17 | **1.644606e-09** | **−** |
| f18 | 1 | **≈** |
| f19 | **0.00767856** | **−** |
| f20 | **9.844422e-15** | **−** |
| f21 | **5.687533e-07** | **−** |
| f22 | **8.707681e-10** | **−** |
| f23 | **0.0131431** | **−** |
| f24 | **5.081029e-14** | **−** |
| f25 | **3.702807e-08** | **−** |
| f26 | **1.307370e-10** | **−** |
| f27 | 1 | **≈** |
| f28 | **2.248252e-14** | **−** |
| f29 | **6.106901e-12** | **−** |
| f30 | 1 | **≈** |

Full-precision MWU statistics are available in [`../../../mwu/details.csv`](../../../mwu/details.csv) relative to the NEA2+ comparison root.

<a id="deep-statistical-comparison"></a>

## Deep Statistical Comparison

DSC compares **MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES** using the 51 unmodified terminal errors per function. Per-function rankings use Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`, `monte_carlo_iterations=0`). The rank matrices are analyzed with the Friedman omnibus test separately for all functions and for the composition-function subset. When the omnibus null hypothesis is rejected, Holm-adjusted post-hoc comparisons are performed against the algorithm with the best mean DSC rank.

`★` means MSC-CMA-ES has the best mean DSC rank and Friedman rejects; `≈` means Friedman rejects but the Holm-adjusted comparison between MSC-CMA-ES and the best-ranked method is not significant; `↓` means the best-ranked method differs significantly from MSC-CMA-ES after Holm adjustment; `O` means Friedman does not reject and no post-hoc interpretation is made.

### DSC ranks by function

Lower DSC rank indicates better performance; tied distributions receive fractional ranks.

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

| Scope | n | Best-ranked algorithm | MSC mean rank | NEA2+ mean rank | BIPOP mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| all | 29 | MSC-CMA-ES | 1.65517 | 2.58621 | 1.75862 | 0.000525204 | MSC-CMA-ES | — | 0.000392206 | **★** |
| composition | 10 | MSC-CMA-ES | 1.15 | 2.35 | 2.5 | 0.00419023 | MSC-CMA-ES | — | 0.00364518 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
