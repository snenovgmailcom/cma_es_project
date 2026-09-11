# CEC2020, D=5, B=5×10^4 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=5×10^4 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
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

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and NEA2+ samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; zeros returned by the algorithms are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 10 functions** and to the **3 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and NEA2+ samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 10 | 4 | 2 | 4 |
| Composition | 3 | 3 | 0 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | 0.520313 | `=` |
| f2 | Unimodal and simple multimodal | 0.561496 | `=` |
| f3 | Unimodal and simple multimodal | 0.79814 | `=` |
| f4 | Unimodal and simple multimodal | **9.93341e-13** | **`>`** |
| f5 | Hybrid | **6.0059e-14** | **`<`** |
| f6 | Hybrid | **0.0204472** | **`>`** |
| f7 | Hybrid | 0.79814 | `=` |
| f8 | Composition | **1.12521e-12** | **`<`** |
| f9 | Composition | **3.30225e-17** | **`<`** |
| f10 | Composition | **7.38091e-08** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **3.21489e-13** | **`<`** |
| f9 | Composition | **9.90675e-18** | **`<`** |
| f10 | Composition | **1.23015e-08** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_nea2plus_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (NEA2+) | $\bar R_M$ | $\bar R_A$ | P(NEA2+ lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 1527 | 47.0588 | 55.9412 | 0.412918 | 0.130078 |
| f2 | 1498 | 47.6275 | 55.3725 | 0.424068 | 0.187165 |
| f3 | 1410 | 49.3529 | 53.6471 | 0.457901 | 0.465574 |
| f4 | 192.5 | 73.2255 | 29.7745 | 0.92599 | 1.24168e-13 |
| f5 | 2462 | 28.7255 | 74.2745 | 0.053441 | 6.67323e-15 |
| f6 | 871 | 59.9216 | 43.0784 | 0.665129 | 0.00408943 |
| f7 | 1174 | 53.9804 | 49.0196 | 0.548635 | 0.39907 |
| f8 | 2403 | 29.8824 | 73.1176 | 0.0761246 | 1.60745e-13 |
| f9 | 2601 | 26 | 77 | 0 | 3.30225e-18 |
| f10 | 2152 | 34.8039 | 68.1961 | 0.172626 | 1.23015e-08 |

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
