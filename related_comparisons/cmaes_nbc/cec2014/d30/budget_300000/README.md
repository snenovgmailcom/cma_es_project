# CEC2014, D=30, B=3×10^5 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=3×10^5 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=3×10^5 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=16) | Mean | **512.614** | 906.042 |
|  | Median | **376.927** | 806.982 |
|  | Minimum | 74.2311 | **51.6292** |
|  | Maximum | **1413.88** | 2160.47 |
|  | Std. | **345.217** | 494.08 |
|  | FBTC(B) | 4.76817 | **7.99962** |
| **Hybrid** (n=6) | Mean | 1866.46 | **179.85** |
|  | Median | 1794.79 | **174.072** |
|  | Minimum | 1167.61 | **29.332** |
|  | Maximum | 3188.42 | **724.092** |
|  | Std. | 496.009 | **149.131** |
|  | FBTC(B) | 0.264129 | **0.85544** |
| **Composition** (n=8) | Mean | 4355.69 | **1500.31** |
|  | Median | 4330.17 | **1500.12** |
|  | Minimum | 3351.26 | **1500.06** |
|  | Maximum | 5287.51 | **1509.35** |
|  | Std. | 430.153 | **1.29213** |
|  | FBTC(B) | **0** | **0** |
| **All** (n=30) | Mean | 6734.76 | **2586.21** |
|  | Median | 6501.88 | **2481.17** |
|  | Minimum | 4593.11 | **1581.02** |
|  | Maximum | 9889.82 | **4393.91** |
|  | Std. | 1271.38 | **644.503** |
|  | FBTC(B) | 5.0323 | **8.85506** |

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
| All | 30 | 4 | 25 | 1 |
| Composition | 8 | 0 | 8 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **3.76369e-19** | **`>`** |
| f2 | Unimodal and simple multimodal | **3.76369e-19** | **`>`** |
| f3 | Unimodal and simple multimodal | **3.76369e-19** | **`>`** |
| f4 | Unimodal and simple multimodal | **3.76369e-19** | **`>`** |
| f5 | Unimodal and simple multimodal | 0.105311 | `=` |
| f6 | Unimodal and simple multimodal | **3.04984e-17** | **`>`** |
| f7 | Unimodal and simple multimodal | **2.78944e-20** | **`>`** |
| f8 | Unimodal and simple multimodal | **2.36655e-13** | **`<`** |
| f9 | Unimodal and simple multimodal | **4.76033e-18** | **`>`** |
| f10 | Unimodal and simple multimodal | **1.11776e-13** | **`<`** |
| f11 | Unimodal and simple multimodal | **5.55079e-09** | **`>`** |
| f12 | Unimodal and simple multimodal | **6.31495e-16** | **`<`** |
| f13 | Unimodal and simple multimodal | **5.61626e-17** | **`>`** |
| f14 | Unimodal and simple multimodal | **7.37111e-15** | **`>`** |
| f15 | Unimodal and simple multimodal | **0.00632502** | **`>`** |
| f16 | Unimodal and simple multimodal | **5.61626e-17** | **`>`** |
| f17 | Hybrid | **5.61626e-17** | **`>`** |
| f18 | Hybrid | **5.61626e-17** | **`>`** |
| f19 | Hybrid | **5.61626e-17** | **`>`** |
| f20 | Hybrid | **5.61626e-17** | **`>`** |
| f21 | Hybrid | **5.61626e-17** | **`>`** |
| f22 | Hybrid | **5.48754e-11** | **`<`** |
| f23 | Composition | **4.66153e-22** | **`>`** |
| f24 | Composition | **0.00160343** | **`>`** |
| f25 | Composition | **3.76369e-19** | **`>`** |
| f26 | Composition | **2.36655e-13** | **`>`** |
| f27 | Composition | **3.76369e-19** | **`>`** |
| f28 | Composition | **3.76369e-19** | **`>`** |
| f29 | Composition | **3.76369e-19** | **`>`** |
| f30 | Composition | **3.76369e-19** | **`>`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f23 | Composition | **1.24307e-22** | **`>`** |
| f24 | Composition | **0.000534478** | **`>`** |
| f25 | Composition | **9.73412e-20** | **`>`** |
| f26 | Composition | **6.76157e-14** | **`>`** |
| f27 | Composition | **9.73412e-20** | **`>`** |
| f28 | Composition | **9.73412e-20** | **`>`** |
| f29 | Composition | **9.73412e-20** | **`>`** |
| f30 | Composition | **9.73412e-20** | **`>`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f2 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f3 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f4 | 0 | 77 | 26 | 1 | 1.34417e-20 |
| f5 | 1543 | 46.7451 | 56.2549 | 0.406767 | 0.105311 |
| f6 | 32 | 76.3725 | 26.6275 | 0.987697 | 1.69436e-18 |
| f7 | 25.5 | 76.5 | 26.5 | 0.990196 | 9.61876e-22 |
| f8 | 2425 | 29.451 | 73.549 | 0.0676663 | 3.38219e-14 |
| f9 | 6 | 76.8824 | 26.1176 | 0.997693 | 2.50543e-19 |
| f10 | 2451 | 28.9412 | 74.0588 | 0.0576701 | 1.3972e-14 |
| f11 | 395 | 69.2549 | 33.7451 | 0.848135 | 1.3877e-09 |
| f12 | 2550 | 27 | 76 | 0.0196078 | 6.31495e-17 |
| f13 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f14 | 97 | 75.098 | 27.902 | 0.962707 | 8.19012e-16 |
| f15 | 859 | 60.1569 | 42.8431 | 0.669742 | 0.00316251 |
| f16 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f17 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f18 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f19 | 4 | 76.9216 | 26.0784 | 0.998462 | 4.18122e-18 |
| f20 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f21 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f22 | 2316 | 31.5882 | 71.4118 | 0.109573 | 1.09751e-11 |
| f23 | 0 | 77 | 26 | 1 | 1.55384e-23 |
| f24 | 816 | 61 | 42 | 0.686275 | 0.000534478 |
| f25 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f26 | 167 | 73.7255 | 29.2745 | 0.935794 | 3.38078e-14 |
| f27 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f28 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f29 | 0 | 77 | 26 | 1 | 1.39059e-20 |
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
| f1 | 3 | 1 | 2 |
| f2 | 3 | 1.5 | 1.5 |
| f3 | 3 | 1.5 | 1.5 |
| f4 | 3 | 1.5 | 1.5 |
| f5 | 2 | 3 | 1 |
| f6 | 3 | 1 | 2 |
| f7 | 3 | 1.5 | 1.5 |
| f8 | 1 | 3 | 2 |
| f9 | 2.5 | 1 | 2.5 |
| f10 | 1 | 3 | 2 |
| f11 | 2 | 1 | 3 |
| f12 | 2 | 3 | 1 |
| f13 | 3 | 1 | 2 |
| f14 | 3 | 2 | 1 |
| f15 | 3 | 2 | 1 |
| f16 | 3 | 1 | 2 |
| f17 | 3 | 1 | 2 |
| f18 | 2 | 1 | 3 |
| f19 | 3 | 1 | 2 |
| f20 | 3 | 1 | 2 |
| f21 | 2 | 1 | 3 |
| f22 | 1 | 3 | 2 |
| f23 | 3 | 1 | 2 |
| f24 | 1 | 2 | 3 |
| f25 | 3 | 1 | 2 |
| f26 | 3 | 2 | 1 |
| f27 | 2.5 | 1 | 2.5 |
| f28 | 2 | 1 | 3 |
| f29 | 3 | 1 | 2 |
| f30 | 2 | 1 | 3 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 30 | CMAES-NBC | 2.46667 | 1.53333 | 2 | 0.00145415 | CMAES-NBC | 0.000300598 | — | **↓** |
| Composition | 8 | CMAES-NBC | 2.4375 | 1.25 | 2.3125 | 0.0331653 | CMAES-NBC | 0.017549 | — | **↓** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
