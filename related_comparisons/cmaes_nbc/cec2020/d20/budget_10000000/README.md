# CEC2020, D=20, B=10^7 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=10^7 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=10^7 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | **13.8184** | 179.518 |
|  | Median | **13.1051** | 161.387 |
|  | Minimum | **3.36513** | 24.7305 |
|  | Maximum | **22.0397** | 1145.58 |
|  | Std. | **3.50593** | 139.517 |
|  | FBTC(B) | **1.47443** | 1.28643 |
| **Hybrid** (n=3) | Mean | **9.8242** | 11.1245 |
|  | Median | 11.5504 | **6.95703** |
|  | Minimum | 2.77257 | **0.800046** |
|  | Maximum | **17.6168** | 27.3553 |
|  | Std. | **4.76656** | 8.78333 |
|  | FBTC(B) | 0.504037 | **0.649366** |
| **Composition** (n=3) | Mean | **533.247** | 911.458 |
|  | Median | **539.674** | 912.362 |
|  | Minimum | **399.062** | 908.713 |
|  | Maximum | **578.108** | 913.334 |
|  | Std. | 42.2123 | **1.3969** |
|  | FBTC(B) | **0.364091** | 0 |
| **All** (n=10) | Mean | **556.889** | 1102.1 |
|  | Median | **564.329** | 1080.71 |
|  | Minimum | **405.199** | 934.244 |
|  | Maximum | **617.764** | 2086.27 |
|  | Std. | **50.4848** | 149.698 |
|  | FBTC(B) | **2.34256** | 1.93579 |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and CMAES-NBC samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; stored zeros are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 10 functions** and to the **3 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and CMAES-NBC samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 10 | 5 | 4 | 1 |
| Composition | 3 | 3 | 0 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **5.09147e-08** | **`>`** |
| f2 | Unimodal and simple multimodal | **3.48492e-16** | **`<`** |
| f3 | Unimodal and simple multimodal | **1.39059e-19** | **`<`** |
| f4 | Unimodal and simple multimodal | **1.5852e-14** | **`>`** |
| f5 | Hybrid | **1.78071e-14** | **`>`** |
| f6 | Hybrid | 0.241489 | `=` |
| f7 | Hybrid | **8.35196e-17** | **`>`** |
| f8 | Composition | **1.99011e-17** | **`<`** |
| f9 | Composition | **2.60878e-17** | **`<`** |
| f10 | Composition | **1.78071e-14** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **6.6337e-18** | **`<`** |
| f9 | Composition | **6.6337e-18** | **`<`** |
| f10 | Composition | **4.45179e-15** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 688.5 | 63.5 | 39.5 | 0.735294 | 2.54573e-08 |
| f2 | 2551 | 26.9804 | 76.0196 | 0.0192234 | 5.80819e-17 |
| f3 | 2601 | 26 | 77 | 0 | 1.39059e-20 |
| f4 | 122 | 74.6078 | 28.3922 | 0.953095 | 3.17041e-15 |
| f5 | 147 | 74.1176 | 28.8824 | 0.943483 | 5.75951e-15 |
| f6 | 1476 | 48.0588 | 54.9412 | 0.432526 | 0.241489 |
| f7 | 22 | 76.5686 | 26.4314 | 0.991542 | 1.19314e-17 |
| f8 | 2601 | 26 | 77 | 0 | 2.21123e-18 |
| f9 | 2601 | 26 | 77 | 0 | 3.26098e-18 |
| f10 | 2397 | 30 | 73 | 0.0784314 | 4.45179e-15 |

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
| f2 | 1 | 3 | 2 |
| f3 | 2 | 3 | 1 |
| f4 | 3 | 2 | 1 |
| f5 | 2 | 1 | 3 |
| f6 | 1.5 | 3 | 1.5 |
| f7 | 2 | 1 | 3 |
| f8 | 1 | 3 | 2 |
| f9 | 1 | 3 | 2 |
| f10 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | MSC-CMA-ES | 1.75 | 2.35 | 1.9 | 0.377192 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1 | 3 | 2 | 0.0497871 | MSC-CMA-ES | — | 0.0143059 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
