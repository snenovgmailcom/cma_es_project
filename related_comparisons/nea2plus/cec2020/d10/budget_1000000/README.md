# CEC2020, D=10, B=1M — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=1,000,000 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=1,000,000 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=4) | mean | **8.66991** | 37.1509 |
|  | median | **6.91823** | 27.5249 |
|  | best | **1.02758** | 6.41203 |
|  | worst | **20.6261** | 153.505 |
|  | std | **5.19961** | 28.3903 |
|  | FBTC(B) | **1.55556** | 1.46713 |
| **Hybrid** (n=3) | mean | **2.12353** | 27.4388 |
|  | median | **2.03107** | 21.0404 |
|  | best | **0.63611** | 2.49304 |
|  | worst | **4.4467** | 126.949 |
|  | std | **0.835994** | 23.537 |
|  | FBTC(B) | **0.730488** | 0.500192 |
| **Composition** (n=3) | mean | **106.147** | 182.338 |
|  | median | **100.004** | 211.401 |
|  | best | **0** | 1.735712e-07 |
|  | worst | **200.02** | 424.336 |
|  | std | **70.9661** | 88.128 |
|  | FBTC(B) | **1.92349** | 0.764321 |
| **ALL** (n=10) | mean | **116.94** | 246.928 |
|  | median | **108.953** | 259.966 |
|  | best | **1.66369** | 8.90507 |
|  | worst | **225.093** | 704.79 |
|  | std | **77.0017** | 140.055 |
|  | FBTC(B) | **4.20953** | 2.73164 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These descriptive values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **10 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary: NEA2+ significant on **1** functions; MSC-CMA-ES significant on **6**; not significant on **3**.

Composition subset: NEA2+ significant on **0** of 3 functions; MSC-CMA-ES significant on **2**; not significant on **1**.

`+` means NEA2+ has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant at `alpha=0.05` after Bonferroni adjustment.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | basic | 2601 | 0 |
| f2 | basic | 2581 | 0.00768935 |
| f3 | basic | 1059 | 0.592849 |
| f4 | basic | 39 | 0.985006 |
| f5 | hybrid | 2601 | 0 |
| f6 | hybrid | 1820 | 0.300269 |
| f7 | hybrid | 1050 | 0.596309 |
| f8 | composition | 2601 | 0 |
| f9 | composition | 2451 | 0.0576701 |
| f10 | composition | 1480 | 0.430988 |

### Raw two-sided p-value

| Function | p_raw |
|:--|--:|
| f1 | 6.883187e-19 |
| f2 | 1.048356e-17 |
| f3 | 0.106756 |
| f4 | 3.186872e-17 |
| f5 | 1.463610e-18 |
| f6 | 0.000513688 |
| f7 | 0.0942925 |
| f8 | 3.266640e-18 |
| f9 | 1.396484e-14 |
| f10 | 0.230919 |

### Bonferroni-adjusted p-value and decision

| Function | p_Bonferroni | Decision |
|:--|--:|:--:|
| f1 | **6.883187e-18** | **−** |
| f2 | **1.048356e-16** | **−** |
| f3 | 1 | **≈** |
| f4 | **3.186872e-16** | **+** |
| f5 | **1.463610e-17** | **−** |
| f6 | **0.00513688** | **−** |
| f7 | 0.942925 | **≈** |
| f8 | **3.266640e-17** | **−** |
| f9 | **1.396484e-13** | **−** |
| f10 | 1 | **≈** |

Full-precision MWU statistics are available in [`../../../mwu/details.csv`](../../../mwu/details.csv) relative to the NEA2+ comparison root.

<a id="deep-statistical-comparison"></a>

## Deep Statistical Comparison

DSC compares **MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES** using the 51 unmodified terminal errors per function. Per-function rankings use Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`, `monte_carlo_iterations=0`). The rank matrices are analyzed with the Friedman omnibus test separately for all functions and for the composition-function subset. When the omnibus null hypothesis is rejected, Holm-adjusted post-hoc comparisons are performed against the algorithm with the best mean DSC rank.

`★` means MSC-CMA-ES has the best mean DSC rank and Friedman rejects; `≈` means Friedman rejects but the Holm-adjusted comparison between MSC-CMA-ES and the best-ranked method is not significant; `↓` means the best-ranked method differs significantly from MSC-CMA-ES after Holm adjustment; `O` means Friedman does not reject and no post-hoc interpretation is made.

### DSC ranks by function

Lower DSC rank indicates better performance; tied distributions receive fractional ranks.

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

| Scope | n | Best-ranked algorithm | MSC mean rank | NEA2+ mean rank | BIPOP mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| all | 10 | MSC-CMA-ES | 1.7 | 2.2 | 2.1 | 0.496585 | — | — | — | **O** |
| composition | 3 | MSC-CMA-ES | 1.16667 | 1.83333 | 3 | 0.0755218 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
