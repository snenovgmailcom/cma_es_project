# CEC2022, D=20, B=10^6 — MSC-CMA-ES vs CMAES-NBC

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
| **Unimodal and simple multimodal** (n=5) | Mean | **2.42056** | 46.9489 |
|  | Median | **1.11164** | 44.8955 |
|  | Minimum | **0.000339707** | 44.8955 |
|  | Maximum | **33.1114** | 49.0845 |
|  | Std. | 5.43605 | **2.11494** |
|  | FBTC(B) | 3.26413 | **4.03922** |
| **Hybrid** (n=3) | Mean | **29.3505** | 33.3572 |
|  | Median | 41.3614 | **41.147** |
|  | Minimum | **0.841482** | 0.946112 |
|  | Maximum | 72.7505 | **71.9127** |
|  | Std. | 22.1657 | **20.0491** |
|  | FBTC(B) | 0.461361 | **0.551711** |
| **Composition** (n=4) | Mean | **434.705** | 898.797 |
|  | Median | **435.034** | 812.966 |
|  | Minimum | **422.005** | 726.522 |
|  | Maximum | **451.984** | 1856.25 |
|  | Std. | **6.89616** | 206.665 |
|  | FBTC(B) | **1.08228** | 0.00192234 |
| **All** (n=12) | Mean | **466.476** | 979.103 |
|  | Median | **477.507** | 899.009 |
|  | Minimum | **422.847** | 772.363 |
|  | Maximum | **557.846** | 1977.25 |
|  | Std. | **34.4979** | 228.829 |
|  | FBTC(B) | **4.80777** | 4.59285 |

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
| All | 12 | 4 | 5 | 3 |
| Composition | 4 | 3 | 1 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **2.60338e-09** | **`>`** |
| f2 | Unimodal and simple multimodal | **5.08749e-18** | **`<`** |
| f3 | Unimodal and simple multimodal | **1.66871e-19** | **`>`** |
| f4 | Unimodal and simple multimodal | **1.99612e-16** | **`>`** |
| f5 | Unimodal and simple multimodal | **1.60045e-10** | **`>`** |
| f6 | Hybrid | 0.734762 | `=` |
| f7 | Hybrid | 0.734762 | `=` |
| f8 | Hybrid | 0.333572 | `=` |
| f9 | Composition | **8.80201e-11** | **`<`** |
| f10 | Composition | **2.10663e-16** | **`<`** |
| f11 | Composition | **2.9643e-17** | **`<`** |
| f12 | Composition | **1.01464e-17** | **`>`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f9 | Composition | **1.467e-11** | **`<`** |
| f10 | Composition | **6.01893e-17** | **`<`** |
| f11 | Composition | **9.88101e-18** | **`<`** |
| f12 | Composition | **4.05856e-18** | **`>`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 586.5 | 65.5 | 37.5 | 0.77451 | 6.50844e-10 |
| f2 | 2601 | 26 | 77 | 0 | 4.62499e-19 |
| f3 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f4 | 153 | 74 | 29 | 0.941176 | 2.49515e-17 |
| f5 | 484.5 | 67.5 | 35.5 | 0.813725 | 3.20091e-11 |
| f6 | 1173 | 54 | 49 | 0.54902 | 0.367381 |
| f7 | 1239 | 52.7059 | 50.2941 | 0.523645 | 0.683086 |
| f8 | 1062 | 56.1765 | 46.8235 | 0.591696 | 0.111191 |
| f9 | 2205 | 33.7647 | 69.2353 | 0.152249 | 1.467e-11 |
| f10 | 2563 | 26.7451 | 76.2549 | 0.0146098 | 3.00947e-17 |
| f11 | 2601 | 26 | 77 | 0 | 3.29367e-18 |
| f12 | 0 | 77 | 26 | 1 | 1.01464e-18 |

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
| f3 | 3 | 1 | 2 |
| f4 | 2 | 1 | 3 |
| f5 | 3 | 1.5 | 1.5 |
| f6 | 2 | 1 | 3 |
| f7 | 1 | 2 | 3 |
| f8 | 1 | 2.5 | 2.5 |
| f9 | 1 | 3 | 2 |
| f10 | 1 | 3 | 2 |
| f11 | 1 | 3 | 2 |
| f12 | 2.5 | 1 | 2.5 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 12 | MSC-CMA-ES | 1.79167 | 1.95833 | 2.25 | 0.524226 | — | — | — | **O** |
| Composition | 4 | MSC-CMA-ES | 1.375 | 2.5 | 2.125 | 0.269146 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
