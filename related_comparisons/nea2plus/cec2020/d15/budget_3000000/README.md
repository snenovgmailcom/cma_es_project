# CEC2020, D=15, B=3M — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=3,000,000 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=3,000,000 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **unimodal and simple multimodal** (n=4) | mean | **11.1224** | 163.616 |
|  | median | **11.7104** | 161.511 |
|  | best | **1.2221** | 12.1911 |
|  | worst | **28.2452** | 327.833 |
|  | std | **6.36379** | 91.4264 |
|  | FBTC(B) | **1.53018** | 1.36217 |
| **Hybrid** (n=3) | mean | **3.61562** | 125.75 |
|  | median | **3.34178** | 97.9907 |
|  | best | **0.868499** | 13.104 |
|  | worst | **8.19824** | 398.034 |
|  | std | **1.53154** | 98.9172 |
|  | FBTC(B) | **0.641676** | 0.31411 |
| **Composition** (n=3) | mean | **266.142** | 493.43 |
|  | median | **200.007** | 524.247 |
|  | best | **100.002** | 100.002 |
|  | worst | **525.082** | 549.346 |
|  | std | 145.79 | **109.576** |
|  | FBTC(B) | **0.914648** | 0.188774 |
| **ALL** (n=10) | mean | **280.88** | 782.796 |
|  | median | **215.06** | 783.748 |
|  | best | **102.092** | 125.297 |
|  | worst | **561.526** | 1275.21 |
|  | std | **153.685** | 299.919 |
|  | FBTC(B) | **3.08651** | 1.86505 |

*Bold indicates the better descriptive value in that row (lower for error metrics and std; higher for FBTC(B)). These descriptive values are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **10 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary: NEA2+ significant on **2** functions; MSC-CMA-ES significant on **8**; not significant on **0**.

Composition subset: NEA2+ significant on **0** of 3 functions; MSC-CMA-ES significant on **3**; not significant on **0**.

`+` means NEA2+ has significantly lower terminal errors; `−` means MSC-CMA-ES has significantly lower terminal errors; `≈` means the difference is not significant at `alpha=0.05` after Bonferroni adjustment.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | basic | 2601 | 0 |
| f2 | basic | 2571 | 0.011534 |
| f3 | basic | 2601 | 0 |
| f4 | basic | 1 | 0.999616 |
| f5 | hybrid | 2601 | 0 |
| f6 | hybrid | 644 | 0.752403 |
| f7 | hybrid | 2236 | 0.140331 |
| f8 | composition | 2450 | 0.0580546 |
| f9 | composition | 2553 | 0.0184544 |
| f10 | composition | 2452 | 0.0572857 |

### Raw two-sided p-value

| Function | p_raw |
|:--|--:|
| f1 | 5.177701e-20 |
| f2 | 1.895863e-17 |
| f3 | 3.303682e-18 |
| f4 | 3.504317e-18 |
| f5 | 3.026716e-18 |
| f6 | 1.131340e-05 |
| f7 | 3.907431e-10 |
| f8 | 1.469013e-14 |
| f9 | 5.318218e-17 |
| f10 | 1.325902e-14 |

### Bonferroni-adjusted p-value and decision

| Function | p_Bonferroni | Decision |
|:--|--:|:--:|
| f1 | **5.177701e-19** | **−** |
| f2 | **1.895863e-16** | **−** |
| f3 | **3.303682e-17** | **−** |
| f4 | **3.504317e-17** | **+** |
| f5 | **3.026716e-17** | **−** |
| f6 | **0.000113134** | **+** |
| f7 | **3.907431e-09** | **−** |
| f8 | **1.469013e-13** | **−** |
| f9 | **5.318218e-16** | **−** |
| f10 | **1.325902e-13** | **−** |

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
| f3 | 2 | 3 | 1 |
| f4 | 3 | 1 | 2 |
| f5 | 2 | 3 | 1 |
| f6 | 3 | 2 | 1 |
| f7 | 1 | 3 | 2 |
| f8 | 1 | 2 | 3 |
| f9 | 1 | 2 | 3 |
| f10 | 1 | 2 | 3 |

### Statistical comparison

| Scope | n | Best-ranked algorithm | MSC mean rank | NEA2+ mean rank | BIPOP mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| all | 10 | MSC-CMA-ES | 1.7 | 2.4 | 1.9 | 0.272532 | — | — | — | **O** |
| composition | 3 | MSC-CMA-ES | 1 | 2 | 3 | 0.0497871 | MSC-CMA-ES | — | 0.110336 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
