# CEC2022, D=20, B=10^6 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=10^6 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=10^6 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=5) | Mean | **2.42056** | 11.9054 |
|  | Median | **1.11164** | 11.9403 |
|  | Minimum | **0.000339707** | 6.96474 |
|  | Maximum | 33.1114 | **15.9246** |
|  | Std. | 5.43605 | **2.02193** |
|  | FBTC(B) | 3.26413 | **3.6113** |
| **Hybrid** (n=3) | Mean | **29.3505** | 79.0861 |
|  | Median | **41.3614** | 72.9828 |
|  | Minimum | **0.841482** | 37.463 |
|  | Maximum | **72.7505** | 130.324 |
|  | Std. | 22.1657 | **21.1051** |
|  | FBTC(B) | **0.461361** | 0.20915 |
| **Composition** (n=4) | Mean | **434.705** | 516.751 |
|  | Median | **435.034** | 516.701 |
|  | Minimum | **422.005** | 512.659 |
|  | Maximum | **451.984** | 523.528 |
|  | Std. | 6.89616 | **2.06369** |
|  | FBTC(B) | **1.08228** | 0.881584 |
| **All** (n=12) | Mean | **466.476** | 607.742 |
|  | Median | **477.507** | 601.624 |
|  | Minimum | **422.847** | 557.087 |
|  | Maximum | **557.846** | 669.777 |
|  | Std. | 34.4979 | **25.1907** |
|  | FBTC(B) | **4.80777** | 4.70204 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **12 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary from the NEA2+ perspective: **1 ↓**, **8 ↑**, and **3 —**.

Composition subset: **0 ↓**, **3 ↑**, and **1 —** across 4 functions.

Direction is stated from the NEA2+ perspective: `↓` denotes a statistically significant shift toward lower terminal errors, `↑` a statistically significant shift toward higher terminal errors, and `—` no statistically significant difference after Bonferroni correction.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | Unimodal and simple multimodal | 2601 | 0 |
| f2 | Unimodal and simple multimodal | 2346 | 0.0980392 |
| f3 | Unimodal and simple multimodal | 123 | 0.95271 |
| f4 | Unimodal and simple multimodal | 2601 | 0 |
| f5 | Unimodal and simple multimodal | 1275 | 0.509804 |
| f6 | Hybrid | 2574 | 0.0103806 |
| f7 | Hybrid | 2552 | 0.0188389 |
| f8 | Hybrid | 1263 | 0.514418 |
| f9 | Composition | 2601 | 0 |
| f10 | Composition | 2601 | 0 |
| f11 | Composition | 2601 | 0 |
| f12 | Composition | 1473 | 0.433679 |

### p_raw

| Function | p_raw |
|:--|--:|
| f1 | 9.2624e-19 |
| f2 | 1.44523e-12 |
| f3 | 3.34487e-15 |
| f4 | 2.83995e-18 |
| f5 | 0.866655 |
| f6 | 1.59806e-17 |
| f7 | 5.63717e-17 |
| f8 | 0.804421 |
| f9 | 2.78699e-20 |
| f10 | 3.30368e-18 |
| f11 | 3.30368e-18 |
| f12 | 0.246155 |

### p_Bonferroni and Direction

| Function | p_Bonferroni | Direction |
|:--|--:|:--:|
| f1 | **1.11149e-17** | **↑** |
| f2 | **1.73428e-11** | **↑** |
| f3 | **4.01384e-14** | **↓** |
| f4 | **3.40794e-17** | **↑** |
| f5 | 1 | **—** |
| f6 | **1.91768e-16** | **↑** |
| f7 | **6.76461e-16** | **↑** |
| f8 | 1 | **—** |
| f9 | **3.34438e-19** | **↑** |
| f10 | **3.96442e-17** | **↑** |
| f11 | **3.96442e-17** | **↑** |
| f12 | 1 | **—** |

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
| f4 | 1 | 3 | 2 |
| f5 | 3 | 2 | 1 |
| f6 | 1 | 3 | 2 |
| f7 | 1 | 3 | 2 |
| f8 | 1 | 3 | 2 |
| f9 | 1 | 3 | 2 |
| f10 | 1 | 3 | 2 |
| f11 | 1 | 2 | 3 |
| f12 | 1.5 | 3 | 1.5 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 12 | MSC-CMA-ES | 1.54167 | 2.58333 | 1.875 | 0.0335126 | MSC-CMA-ES | — | 0.0107244 | **★** |
| Composition | 4 | MSC-CMA-ES | 1.125 | 2.75 | 2.125 | 0.0680509 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
