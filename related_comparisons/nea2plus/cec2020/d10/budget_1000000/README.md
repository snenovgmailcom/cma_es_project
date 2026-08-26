# CEC2020, D=10, B=10^6 — MSC-CMA-ES vs NEA2+

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
| **Unimodal and simple multimodal** (n=4) | Mean | **8.66991** | 37.1509 |
|  | Median | **6.91823** | 27.5249 |
|  | Minimum | **1.02758** | 6.41203 |
|  | Maximum | **20.6261** | 153.505 |
|  | Std. | **5.19961** | 28.3903 |
|  | FBTC(B) | **1.55556** | 1.46713 |
| **Hybrid** (n=3) | Mean | **2.12353** | 27.4388 |
|  | Median | **2.03107** | 21.0404 |
|  | Minimum | **0.63611** | 2.49304 |
|  | Maximum | **4.4467** | 126.949 |
|  | Std. | **0.835994** | 23.537 |
|  | FBTC(B) | **0.730488** | 0.500192 |
| **Composition** (n=3) | Mean | **106.147** | 182.338 |
|  | Median | **100.004** | 211.401 |
|  | Minimum | **0** | 1.73571e-07 |
|  | Maximum | **200.02** | 424.336 |
|  | Std. | **70.9661** | 88.128 |
|  | FBTC(B) | **1.92349** | 0.764321 |
| **All** (n=10) | Mean | **116.94** | 246.928 |
|  | Median | **108.953** | 259.966 |
|  | Minimum | **1.66369** | 8.90507 |
|  | Maximum | **225.093** | 704.79 |
|  | Std. | **77.0017** | 140.055 |
|  | FBTC(B) | **4.20953** | 2.73164 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **10 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary from the NEA2+ perspective: **1 ↓**, **6 ↑**, and **3 —**.

Composition subset: **0 ↓**, **2 ↑**, and **1 —** across 3 functions.

Direction is stated from the NEA2+ perspective: `↓` denotes a statistically significant shift toward lower terminal errors, `↑` a statistically significant shift toward higher terminal errors, and `—` no statistically significant difference after Bonferroni correction.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | Unimodal and simple multimodal | 2601 | 0 |
| f2 | Unimodal and simple multimodal | 2581 | 0.00768935 |
| f3 | Unimodal and simple multimodal | 1059 | 0.592849 |
| f4 | Unimodal and simple multimodal | 39 | 0.985006 |
| f5 | Hybrid | 2601 | 0 |
| f6 | Hybrid | 1820 | 0.300269 |
| f7 | Hybrid | 1050 | 0.596309 |
| f8 | Composition | 2601 | 0 |
| f9 | Composition | 2451 | 0.0576701 |
| f10 | Composition | 1480 | 0.430988 |

### p_raw

| Function | p_raw |
|:--|--:|
| f1 | 6.88319e-19 |
| f2 | 1.04836e-17 |
| f3 | 0.106756 |
| f4 | 3.18687e-17 |
| f5 | 1.46361e-18 |
| f6 | 0.000513688 |
| f7 | 0.0942925 |
| f8 | 3.26664e-18 |
| f9 | 1.39648e-14 |
| f10 | 0.230919 |

### p_Bonferroni and Direction

| Function | p_Bonferroni | Direction |
|:--|--:|:--:|
| f1 | **6.88319e-18** | **↑** |
| f2 | **1.04836e-16** | **↑** |
| f3 | 1 | **—** |
| f4 | **3.18687e-16** | **↓** |
| f5 | **1.46361e-17** | **↑** |
| f6 | **0.00513688** | **↑** |
| f7 | 0.942925 | **—** |
| f8 | **3.26664e-17** | **↑** |
| f9 | **1.39648e-13** | **↑** |
| f10 | 1 | **—** |

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
| f2 | 1 | 3 | 2 |
| f3 | 2 | 1 | 3 |
| f4 | 3 | 1 | 2 |
| f5 | 1 | 3 | 2 |
| f6 | 2 | 3 | 1 |
| f7 | 2.5 | 2.5 | 1 |
| f8 | 1 | 2 | 3 |
| f9 | 1 | 2 | 3 |
| f10 | 1.5 | 1.5 | 3 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | MSC-CMA-ES | 1.7 | 2.2 | 2.1 | 0.496585 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1.16667 | 1.83333 | 3 | 0.0755218 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
