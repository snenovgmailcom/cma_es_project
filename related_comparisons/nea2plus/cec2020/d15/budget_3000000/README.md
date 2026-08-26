# CEC2020, D=15, B=3×10^6 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=3×10^6 NFE.
- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U with Bonferroni adjustment over the functions in this setting.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=3×10^6 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | **11.1224** | 163.616 |
|  | Median | **11.7104** | 161.511 |
|  | Minimum | **1.2221** | 12.1911 |
|  | Maximum | **28.2452** | 327.833 |
|  | Std. | **6.36379** | 91.4264 |
|  | FBTC(B) | **1.53018** | 1.36217 |
| **Hybrid** (n=3) | Mean | **3.61562** | 125.75 |
|  | Median | **3.34178** | 97.9907 |
|  | Minimum | **0.868499** | 13.104 |
|  | Maximum | **8.19824** | 398.034 |
|  | Std. | **1.53154** | 98.9172 |
|  | FBTC(B) | **0.641676** | 0.31411 |
| **Composition** (n=3) | Mean | **266.142** | 493.43 |
|  | Median | **200.007** | 524.247 |
|  | Minimum | **100.002** | 100.002 |
|  | Maximum | **525.082** | 549.346 |
|  | Std. | 145.79 | **109.576** |
|  | FBTC(B) | **0.914648** | 0.188774 |
| **All** (n=10) | Mean | **280.88** | 782.796 |
|  | Median | **215.06** | 783.748 |
|  | Minimum | **102.092** | 125.297 |
|  | Maximum | **561.526** | 1275.21 |
|  | Std. | **153.685** | 299.919 |
|  | FBTC(B) | **3.08651** | 1.86505 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare NEA2+ with MSC-CMA-ES on each function. Each sample contains 51 unmodified run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used. Bonferroni adjustment is applied over the **10 functions** in this setting.

For minimization, `probability_nea2plus_lower` is $P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.

Setting summary from the NEA2+ perspective: **2 ↓**, **8 ↑**, and **0 —**.

Composition subset: **0 ↓**, **3 ↑**, and **0 —** across 3 functions.

Direction is stated from the NEA2+ perspective: `↓` denotes a statistically significant shift toward lower terminal errors, `↑` a statistically significant shift toward higher terminal errors, and `—` no statistically significant difference after Bonferroni correction.

### Mann–Whitney U statistic

| Function | Class | U (NEA2+) | P(NEA2+ lower) |
|:--|:--|--:|--:|
| f1 | Unimodal and simple multimodal | 2601 | 0 |
| f2 | Unimodal and simple multimodal | 2571 | 0.011534 |
| f3 | Unimodal and simple multimodal | 2601 | 0 |
| f4 | Unimodal and simple multimodal | 1 | 0.999616 |
| f5 | Hybrid | 2601 | 0 |
| f6 | Hybrid | 644 | 0.752403 |
| f7 | Hybrid | 2236 | 0.140331 |
| f8 | Composition | 2450 | 0.0580546 |
| f9 | Composition | 2553 | 0.0184544 |
| f10 | Composition | 2452 | 0.0572857 |

### p_raw

| Function | p_raw |
|:--|--:|
| f1 | 5.1777e-20 |
| f2 | 1.89586e-17 |
| f3 | 3.30368e-18 |
| f4 | 3.50432e-18 |
| f5 | 3.02672e-18 |
| f6 | 1.13134e-05 |
| f7 | 3.90743e-10 |
| f8 | 1.46901e-14 |
| f9 | 5.31822e-17 |
| f10 | 1.3259e-14 |

### p_Bonferroni and Direction

| Function | p_Bonferroni | Direction |
|:--|--:|:--:|
| f1 | **5.1777e-19** | **↑** |
| f2 | **1.89586e-16** | **↑** |
| f3 | **3.30368e-17** | **↑** |
| f4 | **3.50432e-17** | **↓** |
| f5 | **3.02672e-17** | **↑** |
| f6 | **0.000113134** | **↓** |
| f7 | **3.90743e-09** | **↑** |
| f8 | **1.46901e-13** | **↑** |
| f9 | **5.31822e-16** | **↑** |
| f10 | **1.3259e-13** | **↑** |

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
| f3 | 2 | 3 | 1 |
| f4 | 3 | 1 | 2 |
| f5 | 2 | 3 | 1 |
| f6 | 3 | 2 | 1 |
| f7 | 1 | 3 | 2 |
| f8 | 1 | 2 | 3 |
| f9 | 1 | 2 | 3 |
| f10 | 1 | 2 | 3 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | MSC-CMA-ES | 1.7 | 2.4 | 1.9 | 0.272532 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1 | 2 | 3 | 0.0497871 | MSC-CMA-ES | — | 0.110336 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
