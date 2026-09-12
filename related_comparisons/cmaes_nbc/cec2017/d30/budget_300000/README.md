# CEC2017, D=30, B=3×10^5 — MSC-CMA-ES vs CMAES-NBC

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
| **Unimodal and simple multimodal** (n=9) | Mean | 435.414 | **359.931** |
|  | Median | 373.256 | **299.4** |
|  | Minimum | **28.9134** | 96.5265 |
|  | Maximum | 1162.17 | **933.648** |
|  | Std. | 285.321 | **215.191** |
|  | FBTC(B) | 3.11534 | **5.86121** |
| **Hybrid** (n=10) | Mean | 2778.96 | **910.676** |
|  | Median | 2770.04 | **961.801** |
|  | Minimum | 1095.53 | **16.6899** |
|  | Maximum | 4934.45 | **2102.5** |
|  | Std. | 908.656 | **598.185** |
|  | FBTC(B) | 0.300269 | **1.79546** |
| **Composition** (n=10) | Mean | 5323.41 | **5235.41** |
|  | Median | 5287.93 | **5061.28** |
|  | Minimum | **4596.19** | 5003.2 |
|  | Maximum | **6451.26** | 9738.97 |
|  | Std. | **378.674** | 754.074 |
|  | FBTC(B) | **0** | **0** |
| **All** (n=29) | Mean | 8537.78 | **6506.02** |
|  | Median | 8431.22 | **6322.48** |
|  | Minimum | 5720.63 | **5116.41** |
|  | Maximum | **12547.9** | 12775.1 |
|  | Std. | 1572.65 | **1567.45** |
|  | FBTC(B) | 3.41561 | **7.65667** |

*Bold marks the minimum value for error-based metrics and standard deviation, and the maximum value for FBTC(B). These values are descriptive and are not significance tests.*

<a id="mannwhitney-u"></a>

## Mann–Whitney U

Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES and CMAES-NBC samples on each function. Each sample contains 51 stored run-wise terminal errors, without additional rounding or zero flooring; stored zeros are retained. SciPy's asymptotic method (`method="asymptotic"`) with continuity correction (`use_continuity=True`) is used.

Holm–Bonferroni adjustment is applied separately within this setting to **all 29 functions** and to the **10 composition functions**. These are two independently adjusted families of hypotheses.

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and CMAES-NBC samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |
|:--|--:|--:|--:|--:|
| All | 29 | 5 | 23 | 1 |
| Composition | 10 | 3 | 7 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **3.89365e-19** | **`>`** |
| f3 | Unimodal and simple multimodal | **2.91426e-20** | **`>`** |
| f4 | Unimodal and simple multimodal | **2.72315e-15** | **`>`** |
| f5 | Unimodal and simple multimodal | **4.52812e-17** | **`>`** |
| f6 | Unimodal and simple multimodal | **3.89365e-19** | **`>`** |
| f7 | Unimodal and simple multimodal | **7.45059e-07** | **`<`** |
| f8 | Unimodal and simple multimodal | **5.73282e-18** | **`>`** |
| f9 | Unimodal and simple multimodal | **1.29955e-18** | **`>`** |
| f10 | Unimodal and simple multimodal | 0.0656957 | `=` |
| f11 | Hybrid | **2.97967e-13** | **`>`** |
| f12 | Hybrid | **0.00745644** | **`>`** |
| f13 | Hybrid | **7.24574e-17** | **`>`** |
| f14 | Hybrid | **7.24574e-17** | **`>`** |
| f15 | Hybrid | **7.24574e-17** | **`>`** |
| f16 | Hybrid | **8.93193e-16** | **`>`** |
| f17 | Hybrid | **2.41538e-06** | **`>`** |
| f18 | Hybrid | **7.24574e-17** | **`>`** |
| f19 | Hybrid | **7.24574e-17** | **`>`** |
| f20 | Hybrid | **0.00745644** | **`<`** |
| f21 | Composition | **2.27453e-08** | **`>`** |
| f22 | Composition | **8.93193e-16** | **`<`** |
| f23 | Composition | **3.43956e-11** | **`>`** |
| f24 | Composition | **7.24574e-17** | **`>`** |
| f25 | Composition | **7.24574e-17** | **`>`** |
| f26 | Composition | **7.24574e-17** | **`<`** |
| f27 | Composition | **0.00564271** | **`<`** |
| f28 | Composition | **1.98932e-12** | **`>`** |
| f29 | Composition | **2.14917e-14** | **`>`** |
| f30 | Composition | **8.93193e-16** | **`>`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f21 | Composition | **6.49866e-09** | **`>`** |
| f22 | Composition | **4.16823e-16** | **`<`** |
| f23 | Composition | **1.28983e-11** | **`>`** |
| f24 | Composition | **3.15032e-17** | **`>`** |
| f25 | Composition | **3.15032e-17** | **`>`** |
| f26 | Composition | **3.15032e-17** | **`<`** |
| f27 | Composition | **0.00141068** | **`<`** |
| f28 | Composition | **8.84144e-13** | **`>`** |
| f29 | Composition | **9.76896e-15** | **`>`** |
| f30 | Composition | **4.16823e-16** | **`>`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f3 | 51 | 76 | 27 | 0.980392 | 1.00492e-21 |
| f4 | 153 | 74 | 29 | 0.941176 | 2.26929e-16 |
| f5 | 42 | 76.1765 | 26.8235 | 0.983852 | 1.88672e-18 |
| f6 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f7 | 2091 | 36 | 67 | 0.196078 | 1.24176e-07 |
| f8 | 4 | 76.9216 | 26.0784 | 0.998462 | 2.29313e-19 |
| f9 | 25.5 | 76.5 | 26.5 | 0.990196 | 4.99828e-20 |
| f10 | 1025 | 56.902 | 46.098 | 0.605921 | 0.0656957 |
| f11 | 192 | 73.2353 | 29.7647 | 0.926182 | 2.97967e-14 |
| f12 | 849 | 60.3529 | 42.6471 | 0.673587 | 0.00254104 |
| f13 | 0 | 77 | 26 | 1 | 3.30297e-18 |
| f14 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f15 | 0 | 77 | 26 | 1 | 3.22159e-18 |
| f16 | 51 | 76 | 27 | 0.980392 | 6.31495e-17 |
| f17 | 548 | 66.2549 | 36.7451 | 0.789312 | 4.83075e-07 |
| f18 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f19 | 0 | 77 | 26 | 1 | 3.30368e-18 |
| f20 | 1753 | 42.6275 | 60.3725 | 0.326028 | 0.00248548 |
| f21 | 416 | 68.8431 | 34.1569 | 0.840062 | 3.24933e-09 |
| f22 | 2551 | 26.9804 | 76.0196 | 0.0192234 | 5.95462e-17 |
| f23 | 265 | 71.8039 | 31.1961 | 0.898116 | 4.29945e-12 |
| f24 | 2 | 76.9608 | 26.0392 | 0.999231 | 3.70574e-18 |
| f25 | 0 | 77 | 26 | 1 | 3.15032e-18 |
| f26 | 2601 | 26 | 77 | 0 | 3.30153e-18 |
| f27 | 1778 | 42.1373 | 60.8627 | 0.316417 | 0.00141068 |
| f28 | 204 | 73 | 30 | 0.921569 | 2.21036e-13 |
| f29 | 113 | 74.7843 | 28.2157 | 0.956555 | 1.95379e-15 |
| f30 | 51 | 76 | 27 | 0.980392 | 6.31495e-17 |

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
| f3 | 3 | 1.5 | 1.5 |
| f4 | 2 | 3 | 1 |
| f5 | 2 | 1 | 3 |
| f6 | 3 | 1 | 2 |
| f7 | 2 | 3 | 1 |
| f8 | 2 | 1 | 3 |
| f9 | 3 | 1.5 | 1.5 |
| f10 | 1.5 | 1.5 | 3 |
| f11 | 2.5 | 1 | 2.5 |
| f12 | 2.5 | 1 | 2.5 |
| f13 | 3 | 1 | 2 |
| f14 | 3 | 1 | 2 |
| f15 | 3 | 1 | 2 |
| f16 | 2 | 1 | 3 |
| f17 | 2 | 1 | 3 |
| f18 | 3 | 1 | 2 |
| f19 | 3 | 1 | 2 |
| f20 | 1 | 2 | 3 |
| f21 | 2 | 3 | 1 |
| f22 | 1 | 2 | 3 |
| f23 | 2 | 1 | 3 |
| f24 | 2.5 | 1 | 2.5 |
| f25 | 3 | 1.5 | 1.5 |
| f26 | 1 | 2 | 3 |
| f27 | 1 | 2 | 3 |
| f28 | 3 | 1 | 2 |
| f29 | 2 | 1 | 3 |
| f30 | 3 | 1 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 29 | CMAES-NBC | 2.31034 | 1.43103 | 2.25862 | 0.000858482 | CMAES-NBC | 0.000813048 | — | **↓** |
| Composition | 10 | CMAES-NBC | 2.05 | 1.55 | 2.4 | 0.161218 | — | — | — | **O** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
