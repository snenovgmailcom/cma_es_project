# CEC2014, D=10, B=10^5 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=10^5 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=10^5 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=16) | Mean | **98.8751** | 188.735 |
|  | Median | **69.0309** | 123.663 |
|  | Minimum | **27.802** | 29.093 |
|  | Maximum | **430.403** | 685.481 |
|  | Std. | **93.8558** | 176.316 |
|  | FBTC(B) | 6.75394 | **7.65744** |
| **Hybrid** (n=6) | Mean | **40.737** | 65.1757 |
|  | Median | **31.2226** | 35.9834 |
|  | Minimum | 2.45206 | **1.50134** |
|  | Maximum | **182.815** | 488.717 |
|  | Std. | **37.4314** | 99.2188 |
|  | FBTC(B) | 1.03768 | **1.15263** |
| **Composition** (n=8) | Mean | 1592.1 | **1370.4** |
|  | Median | 1694.58 | **1404.33** |
|  | Minimum | **895.916** | 1101.38 |
|  | Maximum | 1856.38 | **1500.04** |
|  | Std. | 278.959 | **96.3686** |
|  | FBTC(B) | **0.209919** | 0.00730488 |
| **All** (n=30) | Mean | 1731.72 | **1624.31** |
|  | Median | 1794.84 | **1563.97** |
|  | Minimum | **926.17** | 1131.98 |
|  | Maximum | **2469.6** | 2674.24 |
|  | Std. | 410.246 | **371.904** |
|  | FBTC(B) | 8.00154 | **8.81738** |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and CMAES-NBC samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; stored zeros are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 30 functions** and to the **8 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and CMAES-NBC samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 30 | 10 | 17 | 3 |
| Composition | 8 | 3 | 5 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **4.03271e-19** | **`>`** |
| f2 | Unimodal and simple multimodal | **6.48729e-17** | **`>`** |
| f3 | Unimodal and simple multimodal | **4.22636e-07** | **`>`** |
| f4 | Unimodal and simple multimodal | **2.20399e-19** | **`<`** |
| f5 | Unimodal and simple multimodal | **0.0262842** | **`<`** |
| f6 | Unimodal and simple multimodal | **2.96342e-18** | **`>`** |
| f7 | Unimodal and simple multimodal | **1.79386e-14** | **`>`** |
| f8 | Unimodal and simple multimodal | **1.1985e-06** | **`<`** |
| f9 | Unimodal and simple multimodal | **1.38409e-06** | **`>`** |
| f10 | Unimodal and simple multimodal | **0.00866313** | **`<`** |
| f11 | Unimodal and simple multimodal | 0.898968 | `=` |
| f12 | Unimodal and simple multimodal | **8.2592e-17** | **`<`** |
| f13 | Unimodal and simple multimodal | **8.2592e-17** | **`>`** |
| f14 | Unimodal and simple multimodal | **4.22712e-16** | **`<`** |
| f15 | Unimodal and simple multimodal | 0.0788542 | `=` |
| f16 | Unimodal and simple multimodal | **8.2592e-17** | **`>`** |
| f17 | Hybrid | 0.898968 | `=` |
| f18 | Hybrid | **0.000785085** | **`>`** |
| f19 | Hybrid | **4.76771e-11** | **`>`** |
| f20 | Hybrid | **1.31389e-08** | **`>`** |
| f21 | Hybrid | **1.72221e-07** | **`>`** |
| f22 | Hybrid | **0.0262842** | **`<`** |
| f23 | Composition | **8.04997e-06** | **`>`** |
| f24 | Composition | **0.00514426** | **`<`** |
| f25 | Composition | **1.60761e-09** | **`<`** |
| f26 | Composition | **1.26299e-15** | **`>`** |
| f27 | Composition | **1.25248e-16** | **`<`** |
| f28 | Composition | **8.04997e-06** | **`>`** |
| f29 | Composition | **1.37268e-12** | **`>`** |
| f30 | Composition | **4.03271e-19** | **`>`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f23 | Composition | **2.41499e-06** | **`>`** |
| f24 | Composition | **0.000734895** | **`<`** |
| f25 | Composition | **4.01902e-10** | **`<`** |
| f26 | Composition | **3.78897e-16** | **`>`** |
| f27 | Composition | **3.98516e-17** | **`<`** |
| f28 | Composition | **2.41499e-06** | **`>`** |
| f29 | Composition | **3.813e-13** | **`>`** |
| f30 | Composition | **1.11247e-19** | **`>`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f2 | 102 | 75 | 28 | 0.960784 | 2.49511e-18 |
| f3 | 688.5 | 63.5 | 39.5 | 0.735294 | 3.25104e-08 |
| f4 | 2601 | 26 | 77 | 0 | 7.34663e-21 |
| f5 | 1709 | 43.4902 | 59.5098 | 0.342945 | 0.00631626 |
| f6 | 3 | 76.9412 | 26.0588 | 0.998847 | 1.09756e-19 |
| f7 | 229.5 | 72.5 | 30.5 | 0.911765 | 9.44135e-16 |
| f8 | 2089 | 36.0392 | 66.9608 | 0.196847 | 9.98754e-08 |
| f9 | 584 | 65.549 | 37.451 | 0.775471 | 1.25826e-07 |
| f10 | 1777 | 42.1569 | 60.8431 | 0.316801 | 0.00144385 |
| f11 | 1321 | 51.098 | 51.902 | 0.492118 | 0.893515 |
| f12 | 2601 | 26 | 77 | 0 | 3.30368e-18 |
| f13 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f14 | 2570 | 26.6078 | 76.3922 | 0.0119185 | 2.01291e-17 |
| f15 | 968 | 58.0196 | 44.9804 | 0.627835 | 0.0262847 |
| f16 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f17 | 1414 | 49.2745 | 53.7255 | 0.456363 | 0.449484 |
| f18 | 718 | 62.9216 | 40.0784 | 0.723952 | 9.81357e-05 |
| f19 | 256 | 71.9804 | 31.0196 | 0.901576 | 2.80453e-12 |
| f20 | 384 | 69.4706 | 33.5294 | 0.852364 | 8.75923e-10 |
| f21 | 449 | 68.1961 | 34.8039 | 0.827374 | 1.23015e-08 |
| f22 | 1718 | 43.3137 | 59.6863 | 0.339485 | 0.00525684 |
| f23 | 612 | 65 | 38 | 0.764706 | 8.04997e-07 |
| f24 | 1805 | 41.6078 | 61.3922 | 0.306036 | 0.000734895 |
| f25 | 2267 | 32.549 | 70.451 | 0.128412 | 1.00475e-10 |
| f26 | 51 | 76 | 27 | 0.980392 | 6.31495e-17 |
| f27 | 2527 | 27.451 | 75.549 | 0.0284506 | 5.69309e-18 |
| f28 | 612 | 65 | 38 | 0.764706 | 8.54873e-07 |
| f29 | 255 | 72 | 31 | 0.901961 | 7.62601e-14 |
| f30 | 0 | 77 | 26 | 1 | 1.39059e-20 |

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
| f2 | 3 | 1.5 | 1.5 |
| f3 | 3 | 1.5 | 1.5 |
| f4 | 1 | 3 | 2 |
| f5 | 3 | 1 | 2 |
| f6 | 3 | 1.5 | 1.5 |
| f7 | 3 | 1.5 | 1.5 |
| f8 | 1.5 | 3 | 1.5 |
| f9 | 2 | 1 | 3 |
| f10 | 1.5 | 3 | 1.5 |
| f11 | 1.5 | 1.5 | 3 |
| f12 | 2 | 3 | 1 |
| f13 | 3 | 2 | 1 |
| f14 | 1 | 3 | 2 |
| f15 | 3 | 2 | 1 |
| f16 | 3 | 1 | 2 |
| f17 | 2 | 2 | 2 |
| f18 | 2 | 1 | 3 |
| f19 | 3 | 1.5 | 1.5 |
| f20 | 2 | 1 | 3 |
| f21 | 1 | 2 | 3 |
| f22 | 1.5 | 3 | 1.5 |
| f23 | 2 | 1 | 3 |
| f24 | 1 | 2.5 | 2.5 |
| f25 | 1 | 3 | 2 |
| f26 | 1 | 2.5 | 2.5 |
| f27 | 1 | 2 | 3 |
| f28 | 2 | 1 | 3 |
| f29 | 2.5 | 1 | 2.5 |
| f30 | 2 | 1 | 3 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 30 | CMAES-NBC | 2.05 | 1.85 | 2.1 | 0.591555 | — | — | — | **O** |
| Composition | 8 | MSC-CMA-ES | 1.5625 | 1.75 | 2.6875 | 0.0546804 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
