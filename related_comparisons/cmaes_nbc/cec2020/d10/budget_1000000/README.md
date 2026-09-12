# CEC2020, D=10, B=10^6 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=10^6 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=10^6 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | **8.66991** | 46.6986 |
|  | Median | **6.91823** | 14.5486 |
|  | Minimum | **1.02758** | 10.4294 |
|  | Maximum | **20.6261** | 384.027 |
|  | Std. | **5.19961** | 84.5037 |
|  | FBTC(B) | 1.55556 | **1.65129** |
| **Hybrid** (n=3) | Mean | 2.12353 | **1.82931** |
|  | Median | 2.03107 | **0.885154** |
|  | Minimum | 0.63611 | **0.0208786** |
|  | Maximum | **4.4467** | 41.5297 |
|  | Std. | **0.835994** | 5.94723 |
|  | FBTC(B) | 0.730488 | **0.934256** |
| **Composition** (n=3) | Mean | **106.147** | 702.722 |
|  | Median | **100.004** | 728.612 |
|  | Minimum | **0** | 497.743 |
|  | Maximum | **200.02** | 842.054 |
|  | Std. | **70.9661** | 96.5857 |
|  | FBTC(B) | **1.92349** | 0.165705 |
| **All** (n=10) | Mean | **116.94** | 751.25 |
|  | Median | **108.953** | 744.046 |
|  | Minimum | **1.66369** | 508.193 |
|  | Maximum | **225.093** | 1267.61 |
|  | Std. | **77.0017** | 187.037 |
|  | FBTC(B) | **4.20953** | 2.75125 |

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
| All | 10 | 4 | 4 | 2 |
| Composition | 3 | 3 | 0 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **1.0098e-05** | **`>`** |
| f2 | Unimodal and simple multimodal | 0.106026 | `=` |
| f3 | Unimodal and simple multimodal | **4.20091e-12** | **`<`** |
| f4 | Unimodal and simple multimodal | **3.48323e-14** | **`>`** |
| f5 | Hybrid | 0.506323 | `=` |
| f6 | Hybrid | **5.80472e-14** | **`>`** |
| f7 | Hybrid | **2.67589e-14** | **`>`** |
| f8 | Composition | **9.30834e-09** | **`<`** |
| f9 | Composition | **2.97074e-17** | **`<`** |
| f10 | Composition | **1.32894e-17** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **2.32708e-09** | **`<`** |
| f9 | Composition | **6.60164e-18** | **`<`** |
| f10 | Composition | **3.98683e-18** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 841.5 | 60.5 | 42.5 | 0.676471 | 3.366e-06 |
| f2 | 1590 | 45.8235 | 57.1765 | 0.388697 | 0.0530129 |
| f3 | 2348 | 30.9608 | 72.0392 | 0.0972703 | 8.40182e-13 |
| f4 | 131 | 74.4314 | 28.5686 | 0.949635 | 4.97604e-15 |
| f5 | 1202 | 53.4314 | 49.5686 | 0.53787 | 0.506323 |
| f6 | 143 | 74.1961 | 28.8039 | 0.945021 | 9.67454e-15 |
| f7 | 123 | 74.5882 | 28.4118 | 0.95271 | 3.34487e-15 |
| f8 | 2193 | 34 | 69 | 0.156863 | 2.32708e-09 |
| f9 | 2601 | 26 | 77 | 0 | 3.30082e-18 |
| f10 | 2601 | 26 | 77 | 0 | 1.32894e-18 |

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
| f3 | 1 | 3 | 2 |
| f4 | 3 | 2 | 1 |
| f5 | 1 | 2 | 3 |
| f6 | 3 | 1 | 2 |
| f7 | 3 | 1.5 | 1.5 |
| f8 | 1 | 3 | 2 |
| f9 | 1 | 3 | 2 |
| f10 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | MSC-CMA-ES | 1.8 | 2.3 | 1.9 | 0.496585 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1 | 3 | 2 | 0.0497871 | MSC-CMA-ES | — | 0.0143059 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
