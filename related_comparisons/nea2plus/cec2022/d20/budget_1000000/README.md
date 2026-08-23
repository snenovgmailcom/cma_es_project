# CEC2022, D=20, B=1M — MSC-CMA-ES vs NEA2+

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
| **unimodal and simple multimodal** (n=5) | mean | **2.42056** | 11.9054 |
|  | median | **1.11164** | 11.9403 |
|  | best | **0.000339707** | 6.96474 |
|  | worst | 33.1114 | **15.9246** |
|  | std | 5.43605 | **2.02193** |
|  | FBTC(B) | 3.26413 | **3.6113** |
| **Hybrid** (n=3) | mean | **29.3505** | 79.0861 |
|  | median | **41.3614** | 72.9828 |
|  | best | **0.841482** | 37.463 |
|  | worst | **72.7505** | 130.324 |
|  | std | 22.1657 | **21.1051** |
|  | FBTC(B) | **0.461361** | 0.20915 |
| **Composition** (n=4) | mean | **434.705** | 516.751 |
|  | median | **435.034** | 516.701 |
|  | best | **422.005** | 512.659 |
|  | worst | **451.984** | 523.528 |
|  | std | 6.89616 | **2.06369** |
|  | FBTC(B) | **1.08228** | 0.881584 |
| **ALL** (n=12) | mean | **466.476** | 607.742 |
|  | median | **477.507** | 601.624 |
|  | best | **422.847** | 557.087 |
|  | worst | **557.846** | 669.777 |
|  | std | 34.4979 | **25.1907** |
|  | FBTC(B) | **4.80777** | 4.70204 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These descriptive values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **12 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary: NEA2+ significant on **1** functions; MSC-CMA-ES significant on **8**; not significant on **3**.

Composition subset: NEA2+ significant on **0** of 4 functions; MSC-CMA-ES significant on **3**; not significant on **1**.

`+` means NEA2+ has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant at `alpha=0.05` after Bonferroni adjustment.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | basic | 2601 | 0 |
| f2 | basic | 2346 | 0.0980392 |
| f3 | basic | 123 | 0.95271 |
| f4 | basic | 2601 | 0 |
| f5 | basic | 1275 | 0.509804 |
| f6 | hybrid | 2574 | 0.0103806 |
| f7 | hybrid | 2552 | 0.0188389 |
| f8 | hybrid | 1263 | 0.514418 |
| f9 | composition | 2601 | 0 |
| f10 | composition | 2601 | 0 |
| f11 | composition | 2601 | 0 |
| f12 | composition | 1473 | 0.433679 |

### Raw two-sided p-value

| Function | p_raw |
|:--|--:|
| f1 | 9.262396e-19 |
| f2 | 1.445230e-12 |
| f3 | 3.344868e-15 |
| f4 | 2.839952e-18 |
| f5 | 0.866655 |
| f6 | 1.598064e-17 |
| f7 | 5.637172e-17 |
| f8 | 0.804421 |
| f9 | 2.786987e-20 |
| f10 | 3.303682e-18 |
| f11 | 3.303682e-18 |
| f12 | 0.246155 |

### Bonferroni-adjusted p-value and decision

| Function | p_Bonferroni | Decision |
|:--|--:|:--:|
| f1 | **1.111488e-17** | **−** |
| f2 | **1.734276e-11** | **−** |
| f3 | **4.013841e-14** | **+** |
| f4 | **3.407943e-17** | **−** |
| f5 | 1 | **≈** |
| f6 | **1.917677e-16** | **−** |
| f7 | **6.764607e-16** | **−** |
| f8 | 1 | **≈** |
| f9 | **3.344384e-19** | **−** |
| f10 | **3.964418e-17** | **−** |
| f11 | **3.964418e-17** | **−** |
| f12 | 1 | **≈** |

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

| Scope | n | Best-ranked algorithm | MSC mean rank | NEA2+ mean rank | BIPOP mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| all | 12 | MSC-CMA-ES | 1.54167 | 2.58333 | 1.875 | 0.0335126 | MSC-CMA-ES | — | 0.0107244 | **★** |
| composition | 4 | MSC-CMA-ES | 1.125 | 2.75 | 2.125 | 0.0680509 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
