# CEC2022, D=10, B=2×10^5 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=2×10^5 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=2×10^5 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=5) | Mean | **0.434976** | 0.781682 |
|  | Median | 0.00371688 | **0** |
|  | Minimum | 7.67819e-05 | **0** |
|  | Maximum | 7.10815 | **3.98658** |
|  | Std. | **1.27179** | 1.59854 |
|  | FBTC(B) | 4.04344 | **4.82468** |
| **Hybrid** (n=3) | Mean | **7.5793** | 16.9659 |
|  | Median | 2.04258 | **1.9337** |
|  | Minimum | **0.143136** | 0.262509 |
|  | Maximum | **42.7587** | 45.0879 |
|  | Std. | **13.8006** | 19.4221 |
|  | FBTC(B) | **0.864283** | 0.758554 |
| **Composition** (n=4) | Mean | **420.504** | 512.902 |
|  | Median | **422.65** | 494.515 |
|  | Minimum | **261.717** | 399.797 |
|  | Maximum | **493.958** | 599.884 |
|  | Std. | 88.9606 | **41.8485** |
|  | FBTC(B) | **1.07113** | 1.00231 |
| **All** (n=12) | Mean | **428.518** | 530.649 |
|  | Median | **424.697** | 496.449 |
|  | Minimum | **261.86** | 400.059 |
|  | Maximum | **543.824** | 648.958 |
|  | Std. | 104.033 | **62.8692** |
|  | FBTC(B) | 5.97885 | **6.58554** |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and CMAES-NBC samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; stored zeros are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 12 functions** and to the **4 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and CMAES-NBC samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 12 | 3 | 7 | 2 |
| Composition | 4 | 2 | 2 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **4.28832e-05** | **`>`** |
| f2 | Unimodal and simple multimodal | 0.890964 | `=` |
| f3 | Unimodal and simple multimodal | **1.66729e-19** | **`>`** |
| f4 | Unimodal and simple multimodal | **2.39504e-08** | **`>`** |
| f5 | Unimodal and simple multimodal | **1.23041e-07** | **`>`** |
| f6 | Hybrid | **0.0279734** | **`>`** |
| f7 | Hybrid | **0.0398254** | **`<`** |
| f8 | Hybrid | 0.890964 | `=` |
| f9 | Composition | **3.24745e-07** | **`>`** |
| f10 | Composition | **0.00116165** | **`<`** |
| f11 | Composition | **1.66729e-19** | **`>`** |
| f12 | Composition | **1.35148e-15** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f9 | Composition | **9.27843e-08** | **`>`** |
| f10 | Composition | **0.000232331** | **`<`** |
| f11 | Composition | **5.55764e-20** | **`>`** |
| f12 | Composition | **4.05443e-16** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 867 | 60 | 43 | 0.666667 | 7.1472e-06 |
| f2 | 1220 | 53.0784 | 49.9216 | 0.53095 | 0.499241 |
| f3 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f4 | 612 | 65 | 38 | 0.764706 | 2.66116e-09 |
| f5 | 663 | 64 | 39 | 0.745098 | 1.53801e-08 |
| f6 | 897 | 59.4118 | 43.5882 | 0.655133 | 0.00699334 |
| f7 | 1671 | 44.2353 | 58.7647 | 0.357555 | 0.0132751 |
| f8 | 1415 | 49.2549 | 53.7451 | 0.455978 | 0.445482 |
| f9 | 561 | 66 | 37 | 0.784314 | 4.63921e-08 |
| f10 | 1851 | 40.7059 | 62.2941 | 0.288351 | 0.000232331 |
| f11 | 0 | 77 | 26 | 1 | 1.38941e-20 |
| f12 | 2518 | 27.6275 | 75.3725 | 0.0319108 | 1.35148e-16 |

</details>

Full-precision MWU statistics for both scopes are available in [`mwu/details.csv`](../../../mwu/details.csv).

<a id="deep-statistical-comparison"></a>

## Deep Statistical Comparison

DSC compares **MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES** using the 51 unmodified terminal errors per function. Per-function rankings use Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`, `monte_carlo_iterations=0`). The rank matrices are analyzed with the Friedman omnibus test separately for all functions and for the composition-function subset. When the omnibus null hypothesis is rejected, Holm-adjusted post-hoc comparisons are performed against the algorithm with the lowest mean DSC rank.

`★` means MSC-CMA-ES has the lowest mean DSC rank and the Friedman test rejects the null hypothesis; `≈` means the Friedman test rejects the null hypothesis but the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant; `↓` means the lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means the Friedman test does not reject the null hypothesis and no post-hoc interpretation is made.

### DSC ranks by function

DSC ranks are ordered from 1 upward; tied distributions receive fractional ranks. Smaller numerical ranks are lower in this ordering.

| Function | MSC-CMA-ES | CMAES-NBC | BIPOP-CMA-ES |
|:--|--:|--:|--:|
| f1 | 3 | 1.5 | 1.5 |
| f2 | 1.5 | 1.5 | 3 |
| f3 | 3 | 1 | 2 |
| f4 | 2.5 | 1 | 2.5 |
| f5 | 3 | 1.5 | 1.5 |
| f6 | 2 | 1 | 3 |
| f7 | 1 | 2 | 3 |
| f8 | 1.5 | 3 | 1.5 |
| f9 | 1 | 2 | 3 |
| f10 | 1 | 2.5 | 2.5 |
| f11 | 3 | 1 | 2 |
| f12 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 12 | CMAES-NBC | 1.95833 | 1.75 | 2.29167 | 0.408267 | — | — | — | **O** |
| Composition | 4 | MSC-CMA-ES | 1.5 | 2.125 | 2.375 | 0.443747 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
