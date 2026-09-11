# CEC2020, D=15, B=3×10^6 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=3×10^6 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
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

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and NEA2+ samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; zeros returned by the algorithms are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 10 functions** and to the **3 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and NEA2+ samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 10 | 8 | 2 | 0 |
| Composition | 3 | 3 | 0 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **5.1777e-19** | **`<`** |
| f2 | Unimodal and simple multimodal | **1.13752e-16** | **`<`** |
| f3 | Unimodal and simple multimodal | **2.72404e-17** | **`<`** |
| f4 | Unimodal and simple multimodal | **2.72404e-17** | **`>`** |
| f5 | Hybrid | **2.72404e-17** | **`<`** |
| f6 | Hybrid | **1.13134e-05** | **`>`** |
| f7 | Hybrid | **7.81486e-10** | **`<`** |
| f8 | Composition | **5.30361e-14** | **`<`** |
| f9 | Composition | **2.65911e-16** | **`<`** |
| f10 | Composition | **5.30361e-14** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **2.6518e-14** | **`<`** |
| f9 | Composition | **1.59547e-16** | **`<`** |
| f10 | Composition | **2.6518e-14** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_nea2plus_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (NEA2+) | $\bar R_M$ | $\bar R_A$ | P(NEA2+ lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 2601 | 26 | 77 | 0 | 5.1777e-20 |
| f2 | 2571 | 26.5882 | 76.4118 | 0.011534 | 1.89586e-17 |
| f3 | 2601 | 26 | 77 | 0 | 3.30368e-18 |
| f4 | 1 | 76.9804 | 26.0196 | 0.999616 | 3.50432e-18 |
| f5 | 2601 | 26 | 77 | 0 | 3.02672e-18 |
| f6 | 644 | 64.3725 | 38.6275 | 0.752403 | 1.13134e-05 |
| f7 | 2236 | 33.1569 | 69.8431 | 0.140331 | 3.90743e-10 |
| f8 | 2450 | 28.9608 | 74.0392 | 0.0580546 | 1.46901e-14 |
| f9 | 2553 | 26.9412 | 76.0588 | 0.0184544 | 5.31822e-17 |
| f10 | 2452 | 28.9216 | 74.0784 | 0.0572857 | 1.3259e-14 |

</details>

Full-precision MWU statistics for both scopes are available in [`mwu/details.csv`](../../../mwu/details.csv).

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
