# CEC2022, D=10, B=200K — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=200,000 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=200,000 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=5) | mean | **0.434976** | 3.60925 |
|  | median | **0.00371688** | 3.97988 |
|  | best | 7.678191e-05 | **8.436883e-07** |
|  | worst | 7.10815 | **5.97044** |
|  | std | 1.27179 | **0.974167** |
|  | FBTC(B) | **4.04344** | 3.80584 |
| **Hybrid** (n=3) | mean | **7.5793** | 32.8022 |
|  | median | **2.04258** | 42.2343 |
|  | best | **0.143136** | 1.22733 |
|  | worst | **42.7587** | 65.1325 |
|  | std | **13.8006** | 19.6437 |
|  | FBTC(B) | **0.864283** | 0.394848 |
| **Composition** (n=4) | mean | **420.504** | 474.58 |
|  | median | **422.65** | 493.115 |
|  | best | 261.717 | **15.2924** |
|  | worst | 493.958 | **493.495** |
|  | std | 88.9606 | **78.8118** |
|  | FBTC(B) | **1.07113** | 0.990004 |
| **ALL** (n=12) | mean | **428.518** | 510.992 |
|  | median | **424.697** | 539.33 |
|  | best | 261.86 | **16.5197** |
|  | worst | **543.824** | 564.598 |
|  | std | 104.033 | **99.4297** |
|  | FBTC(B) | **5.97885** | 5.1907 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These descriptive values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **12 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary: NEA2+ significant on **1** functions; MSC-CMA-ES significant on **9**; not significant on **2**.

Composition subset: NEA2+ significant on **0** of 4 functions; MSC-CMA-ES significant on **2**; not significant on **2**.

`+` means NEA2+ has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant at `alpha=0.05` after Bonferroni adjustment.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | basic | 2601 | 0 |
| f2 | basic | 2550 | 0.0196078 |
| f3 | basic | 77 | 0.970396 |
| f4 | basic | 2589 | 0.00461361 |
| f5 | basic | 1938 | 0.254902 |
| f6 | hybrid | 2428 | 0.0665129 |
| f7 | hybrid | 2393 | 0.0799692 |
| f8 | hybrid | 1960 | 0.246444 |
| f9 | composition | 2550 | 0.0196078 |
| f10 | composition | 1691 | 0.349865 |
| f11 | composition | 2601 | 0 |
| f12 | composition | 1608 | 0.381776 |

### Raw two-sided p-value

| Function | p_raw |
|:--|--:|
| f1 | 6.253038e-19 |
| f2 | 1.532237e-17 |
| f3 | 2.718945e-16 |
| f4 | 3.505463e-18 |
| f5 | 1.683589e-05 |
| f6 | 4.604058e-14 |
| f7 | 2.702688e-13 |
| f8 | 1.031350e-05 |
| f9 | 7.763903e-18 |
| f10 | 0.0090501 |
| f11 | 3.301534e-18 |
| f12 | 0.038834 |

### Bonferroni-adjusted p-value and decision

| Function | p_Bonferroni | Decision |
|:--|--:|:--:|
| f1 | **7.503645e-18** | **−** |
| f2 | **1.838684e-16** | **−** |
| f3 | **3.262734e-15** | **+** |
| f4 | **4.206555e-17** | **−** |
| f5 | **0.000202031** | **−** |
| f6 | **5.524870e-13** | **−** |
| f7 | **3.243225e-12** | **−** |
| f8 | **0.000123762** | **−** |
| f9 | **9.316684e-17** | **−** |
| f10 | 0.108601 | **≈** |
| f11 | **3.961840e-17** | **−** |
| f12 | 0.466008 | **≈** |

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

| Scope | n | Best-ranked algorithm | MSC mean rank | NEA2+ mean rank | BIPOP mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| all | 12 | BIPOP-CMA-ES | 1.875 | 2.41667 | 1.70833 | 0.192852 | — | — | — | **O** |
| composition | 4 | MSC-CMA-ES | 1.75 | 2.25 | 2 | 0.778801 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
