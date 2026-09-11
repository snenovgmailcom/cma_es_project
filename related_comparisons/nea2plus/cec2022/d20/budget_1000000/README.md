# CEC2022, D=20, B=10^6 — MSC-CMA-ES vs NEA2+

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
| **Unimodal and simple multimodal** (n=5) | Mean | **2.42056** | 11.9054 |
|  | Median | **1.11164** | 11.9403 |
|  | Minimum | **0.000339707** | 6.96474 |
|  | Maximum | 33.1114 | **15.9246** |
|  | Std. | 5.43605 | **2.02193** |
|  | FBTC(B) | 3.26413 | **3.6113** |
| **Hybrid** (n=3) | Mean | **29.3505** | 79.0861 |
|  | Median | **41.3614** | 72.9828 |
|  | Minimum | **0.841482** | 37.463 |
|  | Maximum | **72.7505** | 130.324 |
|  | Std. | 22.1657 | **21.1051** |
|  | FBTC(B) | **0.461361** | 0.20915 |
| **Composition** (n=4) | Mean | **434.705** | 516.751 |
|  | Median | **435.034** | 516.701 |
|  | Minimum | **422.005** | 512.659 |
|  | Maximum | **451.984** | 523.528 |
|  | Std. | 6.89616 | **2.06369** |
|  | FBTC(B) | **1.08228** | 0.881584 |
| **All** (n=12) | Mean | **466.476** | 607.742 |
|  | Median | **477.507** | 601.624 |
|  | Minimum | **422.847** | 557.087 |
|  | Maximum | **557.846** | 669.777 |
|  | Std. | 34.4979 | **25.1907** |
|  | FBTC(B) | **4.80777** | 4.70204 |

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
| All | 12 | 8 | 1 | 3 |
| Composition | 4 | 3 | 0 | 1 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **1.01886e-17** | **`<`** |
| f2 | Unimodal and simple multimodal | **5.78092e-12** | **`<`** |
| f3 | Unimodal and simple multimodal | **1.67243e-14** | **`>`** |
| f4 | Unimodal and simple multimodal | **2.83995e-17** | **`<`** |
| f5 | Unimodal and simple multimodal | 1 | `=` |
| f6 | Hybrid | **1.11864e-16** | **`<`** |
| f7 | Hybrid | **3.3823e-16** | **`<`** |
| f8 | Hybrid | 1 | `=` |
| f9 | Composition | **3.34438e-19** | **`<`** |
| f10 | Composition | **2.97331e-17** | **`<`** |
| f11 | Composition | **2.97331e-17** | **`<`** |
| f12 | Composition | 0.738466 | `=` |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f9 | Composition | **1.11479e-19** | **`<`** |
| f10 | Composition | **9.91104e-18** | **`<`** |
| f11 | Composition | **9.91104e-18** | **`<`** |
| f12 | Composition | 0.246155 | `=` |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_nea2plus_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (NEA2+) | $\bar R_M$ | $\bar R_A$ | P(NEA2+ lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 2601 | 26 | 77 | 0 | 9.2624e-19 |
| f2 | 2346 | 31 | 72 | 0.0980392 | 1.44523e-12 |
| f3 | 123 | 74.5882 | 28.4118 | 0.95271 | 3.34487e-15 |
| f4 | 2601 | 26 | 77 | 0 | 2.83995e-18 |
| f5 | 1275 | 52 | 51 | 0.509804 | 0.866655 |
| f6 | 2574 | 26.5294 | 76.4706 | 0.0103806 | 1.59806e-17 |
| f7 | 2552 | 26.9608 | 76.0392 | 0.0188389 | 5.63717e-17 |
| f8 | 1263 | 52.2353 | 50.7647 | 0.514418 | 0.804421 |
| f9 | 2601 | 26 | 77 | 0 | 2.78699e-20 |
| f10 | 2601 | 26 | 77 | 0 | 3.30368e-18 |
| f11 | 2601 | 26 | 77 | 0 | 3.30368e-18 |
| f12 | 1473 | 48.1176 | 54.8824 | 0.433679 | 0.246155 |

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

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 12 | MSC-CMA-ES | 1.54167 | 2.58333 | 1.875 | 0.0335126 | MSC-CMA-ES | — | 0.0107244 | **★** |
| Composition | 4 | MSC-CMA-ES | 1.125 | 2.75 | 2.125 | 0.0680509 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
