# CEC2022, D=10, B=2×10^5 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=2×10^5 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
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

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and NEA2+ samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; zeros returned by the algorithms are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 12 functions** and to the **4 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and NEA2+ samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 12 | 11 | 1 | 0 |
| Composition | 4 | 4 | 0 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **7.50365e-18** | **`<`** |
| f2 | Unimodal and simple multimodal | **1.22579e-16** | **`<`** |
| f3 | Unimodal and simple multimodal | **1.90326e-15** | **`>`** |
| f4 | Unimodal and simple multimodal | **3.63169e-17** | **`<`** |
| f5 | Unimodal and simple multimodal | **5.05077e-05** | **`<`** |
| f6 | Hybrid | **2.76243e-13** | **`<`** |
| f7 | Hybrid | **1.35134e-12** | **`<`** |
| f8 | Hybrid | **4.1254e-05** | **`<`** |
| f9 | Composition | **6.98751e-17** | **`<`** |
| f10 | Composition | **0.0181002** | **`<`** |
| f11 | Composition | **3.63169e-17** | **`<`** |
| f12 | Composition | **0.038834** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f9 | Composition | **2.32917e-17** | **`<`** |
| f10 | Composition | **0.0181002** | **`<`** |
| f11 | Composition | **1.32061e-17** | **`<`** |
| f12 | Composition | **0.038834** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_nea2plus_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (NEA2+) | $\bar R_M$ | $\bar R_A$ | P(NEA2+ lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 2601 | 26 | 77 | 0 | 6.25304e-19 |
| f2 | 2550 | 27 | 76 | 0.0196078 | 1.53224e-17 |
| f3 | 77 | 75.4902 | 27.5098 | 0.970396 | 2.71895e-16 |
| f4 | 2589 | 26.2353 | 76.7647 | 0.00461361 | 3.50546e-18 |
| f5 | 1938 | 39 | 64 | 0.254902 | 1.68359e-05 |
| f6 | 2428 | 29.3922 | 73.6078 | 0.0665129 | 4.60406e-14 |
| f7 | 2393 | 30.0784 | 72.9216 | 0.0799692 | 2.70269e-13 |
| f8 | 1960 | 38.5686 | 64.4314 | 0.246444 | 1.03135e-05 |
| f9 | 2550 | 27 | 76 | 0.0196078 | 7.7639e-18 |
| f10 | 1691 | 43.8431 | 59.1569 | 0.349865 | 0.0090501 |
| f11 | 2601 | 26 | 77 | 0 | 3.30153e-18 |
| f12 | 1608 | 45.4706 | 57.5294 | 0.381776 | 0.038834 |

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
