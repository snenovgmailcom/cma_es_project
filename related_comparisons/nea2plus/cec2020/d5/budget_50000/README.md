# CEC2020, D=5, B=5×10^4 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=5×10^4 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=5×10^4 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | 25.0693 | **22.8702** |
|  | Median | **4.13392** | 10.0833 |
|  | Minimum | **0.124899** | 0.737926 |
|  | Maximum | 165.056 | **126.305** |
|  | Std. | 43.1211 | **32.6754** |
|  | FBTC(B) | 1.69319 | **1.69358** |
| **Hybrid** (n=3) | Mean | **1.03224** | 5.3448 |
|  | Median | **0.542041** | 3.01012 |
|  | Minimum | 5.49722e-07 | **1.05193e-07** |
|  | Maximum | **7.38436** | 31.8726 |
|  | Std. | **1.40582** | 6.68246 |
|  | FBTC(B) | **1.4283** | 1.07113 |
| **Composition** (n=3) | Mean | **48.2654** | 137.622 |
|  | Median | **0** | 106.609 |
|  | Minimum | **0** | 4.64911e-08 |
|  | Maximum | **115.655** | 319.172 |
|  | Std. | **53.6787** | 94.3058 |
|  | FBTC(B) | **2.40792** | 1.21492 |
| **All** (n=10) | Mean | **74.367** | 165.837 |
|  | Median | **4.67597** | 119.703 |
|  | Minimum | **0.1249** | 0.737926 |
|  | Maximum | **288.095** | 477.349 |
|  | Std. | **98.2057** | 133.664 |
|  | FBTC(B) | **5.52941** | 3.97962 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **10 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary from the NEA2+ perspective: **2 ↓**, **4 ↑**, and **4 —**.

Composition subset: **0 ↓**, **3 ↑**, and **0 —** across 3 functions.

Direction is stated from the NEA2+ perspective: `↓` denotes a statistically significant shift toward lower terminal errors, `↑` a statistically significant shift toward higher terminal errors, and `—` no statistically significant difference after Bonferroni correction.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | Unimodal and simple multimodal | 1527 | 0.412918 |
| f2 | Unimodal and simple multimodal | 1498 | 0.424068 |
| f3 | Unimodal and simple multimodal | 1410 | 0.457901 |
| f4 | Unimodal and simple multimodal | 192.5 | 0.92599 |
| f5 | Hybrid | 2462 | 0.053441 |
| f6 | Hybrid | 871 | 0.665129 |
| f7 | Hybrid | 1174 | 0.548635 |
| f8 | Composition | 2403 | 0.0761246 |
| f9 | Composition | 2601 | 0 |
| f10 | Composition | 2152 | 0.172626 |

### p_raw

| Function | p_raw |
|:--|--:|
| f1 | 0.130078 |
| f2 | 0.187165 |
| f3 | 0.465574 |
| f4 | 1.24168e-13 |
| f5 | 6.67323e-15 |
| f6 | 0.00408943 |
| f7 | 0.39907 |
| f8 | 1.60745e-13 |
| f9 | 3.30225e-18 |
| f10 | 1.23015e-08 |

### p_Bonferroni and Direction

| Function | p_Bonferroni | Direction |
|:--|--:|:--:|
| f1 | 1 | **—** |
| f2 | 1 | **—** |
| f3 | 1 | **—** |
| f4 | **1.24168e-12** | **↓** |
| f5 | **6.67323e-14** | **↑** |
| f6 | **0.0408943** | **↓** |
| f7 | 1 | **—** |
| f8 | **1.60745e-12** | **↑** |
| f9 | **3.30225e-17** | **↑** |
| f10 | **1.23015e-07** | **↑** |

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
| f2 | 2 | 2 | 2 |
| f3 | 1.5 | 1.5 | 3 |
| f4 | 3 | 1 | 2 |
| f5 | 1.5 | 3 | 1.5 |
| f6 | 3 | 2 | 1 |
| f7 | 2 | 3 | 1 |
| f8 | 1 | 3 | 2 |
| f9 | 1 | 2 | 3 |
| f10 | 1 | 2 | 3 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | MSC-CMA-ES | 1.9 | 2.15 | 1.95 | 0.839457 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1 | 2.33333 | 2.66667 | 0.096972 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
