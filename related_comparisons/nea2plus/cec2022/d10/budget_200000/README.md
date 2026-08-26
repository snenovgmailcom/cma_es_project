# CEC2022, D=10, B=2×10^5 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=2×10^5 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=2×10^5 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=5) | Mean | **0.434976** | 3.60925 |
|  | Median | **0.00371688** | 3.97988 |
|  | Minimum | 7.67819e-05 | **8.43688e-07** |
|  | Maximum | 7.10815 | **5.97044** |
|  | Std. | 1.27179 | **0.974167** |
|  | FBTC(B) | **4.04344** | 3.80584 |
| **Hybrid** (n=3) | Mean | **7.5793** | 32.8022 |
|  | Median | **2.04258** | 42.2343 |
|  | Minimum | **0.143136** | 1.22733 |
|  | Maximum | **42.7587** | 65.1325 |
|  | Std. | **13.8006** | 19.6437 |
|  | FBTC(B) | **0.864283** | 0.394848 |
| **Composition** (n=4) | Mean | **420.504** | 474.58 |
|  | Median | **422.65** | 493.115 |
|  | Minimum | 261.717 | **15.2924** |
|  | Maximum | 493.958 | **493.495** |
|  | Std. | 88.9606 | **78.8118** |
|  | FBTC(B) | **1.07113** | 0.990004 |
| **All** (n=12) | Mean | **428.518** | 510.992 |
|  | Median | **424.697** | 539.33 |
|  | Minimum | 261.86 | **16.5197** |
|  | Maximum | **543.824** | 564.598 |
|  | Std. | 104.033 | **99.4297** |
|  | FBTC(B) | **5.97885** | 5.1907 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **12 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary from the NEA2+ perspective: **1 ↓**, **9 ↑**, and **2 —**.

Composition subset: **0 ↓**, **2 ↑**, and **2 —** across 4 functions.

Direction is stated from the NEA2+ perspective: `↓` denotes a statistically significant shift toward lower terminal errors, `↑` a statistically significant shift toward higher terminal errors, and `—` no statistically significant difference after Bonferroni correction.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | Unimodal and simple multimodal | 2601 | 0 |
| f2 | Unimodal and simple multimodal | 2550 | 0.0196078 |
| f3 | Unimodal and simple multimodal | 77 | 0.970396 |
| f4 | Unimodal and simple multimodal | 2589 | 0.00461361 |
| f5 | Unimodal and simple multimodal | 1938 | 0.254902 |
| f6 | Hybrid | 2428 | 0.0665129 |
| f7 | Hybrid | 2393 | 0.0799692 |
| f8 | Hybrid | 1960 | 0.246444 |
| f9 | Composition | 2550 | 0.0196078 |
| f10 | Composition | 1691 | 0.349865 |
| f11 | Composition | 2601 | 0 |
| f12 | Composition | 1608 | 0.381776 |

### p_raw

| Function | p_raw |
|:--|--:|
| f1 | 6.25304e-19 |
| f2 | 1.53224e-17 |
| f3 | 2.71895e-16 |
| f4 | 3.50546e-18 |
| f5 | 1.68359e-05 |
| f6 | 4.60406e-14 |
| f7 | 2.70269e-13 |
| f8 | 1.03135e-05 |
| f9 | 7.7639e-18 |
| f10 | 0.0090501 |
| f11 | 3.30153e-18 |
| f12 | 0.038834 |

### p_Bonferroni and Direction

| Function | p_Bonferroni | Direction |
|:--|--:|:--:|
| f1 | **7.50365e-18** | **↑** |
| f2 | **1.83868e-16** | **↑** |
| f3 | **3.26273e-15** | **↓** |
| f4 | **4.20656e-17** | **↑** |
| f5 | **0.000202031** | **↑** |
| f6 | **5.52487e-13** | **↑** |
| f7 | **3.24323e-12** | **↑** |
| f8 | **0.000123762** | **↑** |
| f9 | **9.31668e-17** | **↑** |
| f10 | 0.108601 | **—** |
| f11 | **3.96184e-17** | **↑** |
| f12 | 0.466008 | **—** |

Full-precision MWU statistics are available in [`../../../mwu/details.csv`](../../../mwu/details.csv) relative to the NEA2+ comparison root.

<a id="deep-statistical-comparison"></a>

## Deep Statistical Comparison

DSC compares **MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES** using the 51 unmodified terminal errors per function. Per-function rankings use Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`, `monte_carlo_iterations=0`). The rank matrices are analyzed with the Friedman omnibus test separately for all functions and for the composition-function subset. When the omnibus null hypothesis is rejected, Holm-adjusted post-hoc comparisons are performed against the algorithm with the lowest mean DSC rank.

`★` means MSC-CMA-ES has the lowest mean DSC rank and the Friedman test rejects the null hypothesis; `≈` means the Friedman test rejects the null hypothesis but the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant; `↓` means the lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means the Friedman test does not reject the null hypothesis and no post-hoc interpretation is made.

### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | NEA2+ | BIPOP-CMA-ES |
|:--|--:|--:|--:|
| f1 | 2 | 3 | 1 |
| f2 | 2 | 1 | 3 |
| f3 | 3 | 2 | 1 |
| f4 | 1.5 | 3 | 1.5 |
| f5 | 3 | 2 | 1 |
| f6 | 1 | 3 | 2 |
| f7 | 1.5 | 3 | 1.5 |
| f8 | 1.5 | 3 | 1.5 |
| f9 | 1 | 2 | 3 |
| f10 | 1 | 2.5 | 2.5 |
| f11 | 2 | 3 | 1 |
| f12 | 3 | 1.5 | 1.5 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 12 | BIPOP-CMA-ES | 1.875 | 2.41667 | 1.70833 | 0.192852 | — | — | — | **O** |
| Composition | 4 | MSC-CMA-ES | 1.75 | 2.25 | 2 | 0.778801 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
