# CEC2017, D=10, B=10^5 — MSC-CMA-ES vs NEA2+

This page combines the fixed-budget benchmark results and the two statistical analyses used for the related-method comparison with NEA2+.

- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B=10^5 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Fixed-budget terminal results at **B=10^5 NFE**, using 51 runs per function for MSC-CMA-ES and NEA2+.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | NEA2+ |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=9) | Mean | **60.6899** | 253.871 |
|  | Median | **32.7803** | 255.547 |
|  | Minimum | **3.17225** | 13.5536 |
|  | Maximum | **264.107** | 517.27 |
|  | Std. | **67.4759** | 137.663 |
|  | FBTC(B) | **5.14802** | 5.00654 |
| **Hybrid** (n=10) | Mean | **170.851** | 323.305 |
|  | Median | **202.261** | 292.218 |
|  | Minimum | **4.37748** | 39.8943 |
|  | Maximum | **423.371** | 739.73 |
|  | Std. | **123.599** | 167.318 |
|  | FBTC(B) | **2.34679** | 1.04921 |
| **Composition** (n=10) | Mean | **1891.37** | 2393.13 |
|  | Median | **2152.01** | 2479.15 |
|  | Minimum | **929.859** | 1415.54 |
|  | Maximum | **2696.97** | 3030.94 |
|  | Std. | 569.04 | **422.432** |
|  | FBTC(B) | **1.71396** | 0.358324 |
| **All** (n=29) | Mean | **2122.91** | 2970.31 |
|  | Median | **2387.06** | 3026.91 |
|  | Minimum | **937.409** | 1468.99 |
|  | Maximum | **3384.44** | 4287.94 |
|  | Std. | 760.115 | **727.413** |
|  | FBTC(B) | **9.20877** | 6.41407 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and NEA2+ samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; zeros returned by the algorithms are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 29 functions** and to the **10 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and NEA2+ samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 29 | 21 | 2 | 6 |
| Composition | 10 | 8 | 0 | 2 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **2.93411e-13** | **`>`** |
| f3 | Unimodal and simple multimodal | **1.81338e-17** | **`<`** |
| f4 | Unimodal and simple multimodal | **6.81456e-10** | **`<`** |
| f5 | Unimodal and simple multimodal | **9.68218e-16** | **`<`** |
| f6 | Unimodal and simple multimodal | **1.07845e-11** | **`>`** |
| f7 | Unimodal and simple multimodal | 1 | `=` |
| f8 | Unimodal and simple multimodal | **1.0482e-16** | **`<`** |
| f9 | Unimodal and simple multimodal | 0.0598547 | `=` |
| f10 | Unimodal and simple multimodal | **8.10911e-11** | **`<`** |
| f11 | Hybrid | **8.36841e-17** | **`<`** |
| f12 | Hybrid | **0.00178489** | **`<`** |
| f13 | Hybrid | **0.0017831** | **`<`** |
| f14 | Hybrid | **3.89061e-15** | **`<`** |
| f15 | Hybrid | **4.86624e-09** | **`<`** |
| f16 | Hybrid | 1 | `=` |
| f17 | Hybrid | **7.93948e-10** | **`<`** |
| f18 | Hybrid | 1 | `=` |
| f19 | Hybrid | **0.00211822** | **`<`** |
| f20 | Hybrid | **8.14711e-15** | **`<`** |
| f21 | Composition | **2.15734e-07** | **`<`** |
| f22 | Composition | **4.80424e-10** | **`<`** |
| f23 | Composition | **0.00317246** | **`<`** |
| f24 | Composition | **3.85457e-14** | **`<`** |
| f25 | Composition | **1.5322e-08** | **`<`** |
| f26 | Composition | **8.10911e-11** | **`<`** |
| f27 | Composition | 1 | `=` |
| f28 | Composition | **1.7831e-14** | **`<`** |
| f29 | Composition | **4.21166e-12** | **`<`** |
| f30 | Composition | 1 | `=` |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f21 | Composition | **7.84487e-08** | **`<`** |
| f22 | Composition | **1.80159e-10** | **`<`** |
| f23 | Composition | **0.00135963** | **`<`** |
| f24 | Composition | **1.57687e-14** | **`<`** |
| f25 | Composition | **6.38415e-09** | **`<`** |
| f26 | Composition | **3.15572e-11** | **`<`** |
| f27 | Composition | 0.898729 | `=` |
| f28 | Composition | **7.75259e-15** | **`<`** |
| f29 | Composition | **1.68466e-12** | **`<`** |
| f30 | Composition | 0.898729 | `=` |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_nea2plus_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (NEA2+) | $\bar R_M$ | $\bar R_A$ | P(NEA2+ lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 150 | 74.0588 | 28.9412 | 0.94233 | 1.3972e-14 |
| f3 | 2601 | 26 | 77 | 0 | 6.25304e-19 |
| f4 | 2277 | 32.3529 | 70.6471 | 0.124567 | 4.54304e-11 |
| f5 | 2556 | 26.8824 | 76.1176 | 0.017301 | 3.72391e-17 |
| f6 | 223 | 72.6275 | 30.3725 | 0.914264 | 5.67605e-13 |
| f7 | 1470 | 48.1765 | 54.8235 | 0.434833 | 0.258027 |
| f8 | 2592 | 26.1765 | 76.8235 | 0.00346021 | 3.88223e-18 |
| f9 | 1683 | 44 | 59 | 0.352941 | 0.00997579 |
| f10 | 2335 | 31.2157 | 71.7843 | 0.102268 | 4.50506e-12 |
| f11 | 2601 | 26 | 77 | 0 | 2.98872e-18 |
| f12 | 1857 | 40.5882 | 62.4118 | 0.286044 | 0.000198321 |
| f13 | 1861 | 40.5098 | 62.4902 | 0.284506 | 0.00017831 |
| f14 | 2534 | 27.3137 | 75.6863 | 0.0257593 | 1.55624e-16 |
| f15 | 2237 | 33.1373 | 69.8627 | 0.139946 | 3.74326e-10 |
| f16 | 1440 | 48.7647 | 54.2353 | 0.446367 | 0.352223 |
| f17 | 2280 | 32.2941 | 70.7059 | 0.123414 | 5.67105e-11 |
| f18 | 1308 | 51.3529 | 51.6471 | 0.497116 | 0.962634 |
| f19 | 1846 | 40.8039 | 62.1961 | 0.290273 | 0.000264778 |
| f20 | 2520 | 27.5882 | 75.4118 | 0.0311419 | 3.39463e-16 |
| f21 | 2140 | 35.0392 | 67.9608 | 0.17724 | 1.96122e-08 |
| f22 | 2294 | 32.0196 | 70.9804 | 0.118032 | 3.00265e-11 |
| f23 | 1825 | 41.2157 | 61.7843 | 0.298347 | 0.000453209 |
| f24 | 2490 | 28.1765 | 74.8235 | 0.0426759 | 1.75208e-15 |
| f25 | 2208 | 33.7059 | 69.2941 | 0.151096 | 1.27683e-09 |
| f26 | 2335 | 31.2157 | 71.7843 | 0.102268 | 4.50817e-12 |
| f27 | 1414 | 49.2745 | 53.7255 | 0.456363 | 0.449365 |
| f28 | 2505 | 27.8824 | 75.1176 | 0.0369089 | 7.75259e-16 |
| f29 | 2398 | 29.9804 | 73.0196 | 0.0780469 | 2.10583e-13 |
| f30 | 1225 | 52.9804 | 50.0196 | 0.529027 | 0.615701 |

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
| f3 | 2 | 3 | 1 |
| f4 | 3 | 2 | 1 |
| f5 | 1 | 3 | 2 |
| f6 | 3 | 2 | 1 |
| f7 | 1.5 | 3 | 1.5 |
| f8 | 1.5 | 3 | 1.5 |
| f9 | 3 | 2 | 1 |
| f10 | 1.5 | 3 | 1.5 |
| f11 | 1 | 3 | 2 |
| f12 | 1.5 | 3 | 1.5 |
| f13 | 2 | 3 | 1 |
| f14 | 1.5 | 3 | 1.5 |
| f15 | 2 | 3 | 1 |
| f16 | 2.5 | 2.5 | 1 |
| f17 | 1.5 | 3 | 1.5 |
| f18 | 2 | 2 | 2 |
| f19 | 2 | 3 | 1 |
| f20 | 1 | 3 | 2 |
| f21 | 1 | 2 | 3 |
| f22 | 1 | 2 | 3 |
| f23 | 1.5 | 3 | 1.5 |
| f24 | 1 | 2 | 3 |
| f25 | 1 | 2 | 3 |
| f26 | 1 | 2 | 3 |
| f27 | 2 | 3 | 1 |
| f28 | 1 | 2 | 3 |
| f29 | 1 | 2.5 | 2.5 |
| f30 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(NEA2+) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 29 | MSC-CMA-ES | 1.65517 | 2.58621 | 1.75862 | 0.000525204 | MSC-CMA-ES | — | 0.000392206 | **★** |
| Composition | 10 | MSC-CMA-ES | 1.15 | 2.35 | 2.5 | 0.00419023 | MSC-CMA-ES | — | 0.00364518 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/nea2plus/dsc/`.
