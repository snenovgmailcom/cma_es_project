# CEC2020, D=10, B=10^6 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=10^6 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
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

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and NEA2+ samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; zeros returned by the algorithms are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 10 functions** and to the **3 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and NEA2+ samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 10 | 6 | 1 | 3 |
| Composition | 3 | 2 | 0 | 1 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **6.88319e-18** | **`<`** |
| f2 | Unimodal and simple multimodal | **7.33849e-17** | **`<`** |
| f3 | Unimodal and simple multimodal | 0.282877 | `=` |
| f4 | Unimodal and simple multimodal | **1.91212e-16** | **`>`** |
| f5 | Hybrid | **1.31725e-17** | **`<`** |
| f6 | Hybrid | **0.00205475** | **`<`** |
| f7 | Hybrid | 0.282877 | `=` |
| f8 | Composition | **2.61331e-17** | **`<`** |
| f9 | Composition | **6.98242e-14** | **`<`** |
| f10 | Composition | 0.282877 | `=` |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **9.79992e-18** | **`<`** |
| f9 | Composition | **2.79297e-14** | **`<`** |
| f10 | Composition | 0.230919 | `=` |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_nea2plus_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (NEA2+) | $\bar R_M$ | $\bar R_A$ | P(NEA2+ lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 2601 | 26 | 77 | 0 | 6.88319e-19 |
| f2 | 2581 | 26.3922 | 76.6078 | 0.00768935 | 1.04836e-17 |
| f3 | 1059 | 56.2353 | 46.7647 | 0.592849 | 0.106756 |
| f4 | 39 | 76.2353 | 26.7647 | 0.985006 | 3.18687e-17 |
| f5 | 2601 | 26 | 77 | 0 | 1.46361e-18 |
| f6 | 1820 | 41.3137 | 61.6863 | 0.300269 | 0.000513688 |
| f7 | 1050 | 56.4118 | 46.5882 | 0.596309 | 0.0942925 |
| f8 | 2601 | 26 | 77 | 0 | 3.26664e-18 |
| f9 | 2451 | 28.9412 | 74.0588 | 0.0576701 | 1.39648e-14 |
| f10 | 1480 | 47.9804 | 55.0196 | 0.430988 | 0.230919 |

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
