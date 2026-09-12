# CEC2020, D=5, B=5×10^4 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=5×10^4 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=5×10^4 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | **25.0693** | 35.4187 |
|  | Median | **4.13392** | 12.5885 |
|  | Minimum | **0.124899** | 5.27313 |
|  | Maximum | **165.056** | 244.676 |
|  | Std. | **43.1211** | 57.7351 |
|  | FBTC(B) | **1.69319** | 1.599 |
| **Hybrid** (n=3) | Mean | **1.03224** | 3.50304 |
|  | Median | 0.542041 | **0.0549971** |
|  | Minimum | **5.49722e-07** | 3.5819e-06 |
|  | Maximum | **7.38436** | 121.082 |
|  | Std. | **1.40582** | 17.5512 |
|  | FBTC(B) | 1.4283 | **1.68128** |
| **Composition** (n=3) | Mean | **48.2654** | 481.876 |
|  | Median | **0** | 447.367 |
|  | Minimum | **0** | 445.225 |
|  | Maximum | **115.655** | 673.258 |
|  | Std. | **53.6787** | 64.2629 |
|  | FBTC(B) | **2.40792** | 0.86313 |
| **All** (n=10) | Mean | **74.367** | 520.798 |
|  | Median | **4.67597** | 460.01 |
|  | Minimum | **0.1249** | 450.499 |
|  | Maximum | **288.095** | 1039.02 |
|  | Std. | **98.2057** | 139.549 |
|  | FBTC(B) | **5.52941** | 4.14341 |

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
| All | 10 | 3 | 3 | 4 |
| Composition | 3 | 2 | 1 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **2.20879e-13** | **`>`** |
| f2 | Unimodal and simple multimodal | 0.907306 | `=` |
| f3 | Unimodal and simple multimodal | **2.16819e-06** | **`<`** |
| f4 | Unimodal and simple multimodal | 0.106924 | `=` |
| f5 | Hybrid | 1 | `=` |
| f6 | Hybrid | **5.83306e-05** | **`>`** |
| f7 | Hybrid | 1 | `=` |
| f8 | Composition | **1.78352e-09** | **`>`** |
| f9 | Composition | **2.97202e-17** | **`<`** |
| f10 | Composition | **3.83762e-19** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **2.54789e-10** | **`>`** |
| f9 | Composition | **6.6045e-18** | **`<`** |
| f10 | Composition | **1.15129e-19** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 306 | 71 | 32 | 0.882353 | 2.76099e-14 |
| f2 | 1455 | 48.4706 | 54.5294 | 0.4406 | 0.302435 |
| f3 | 2060 | 36.6078 | 66.3922 | 0.207997 | 3.61365e-07 |
| f4 | 969 | 58 | 45 | 0.627451 | 0.026731 |
| f5 | 1276 | 51.9804 | 51.0196 | 0.509419 | 0.868539 |
| f6 | 645 | 64.3529 | 38.6471 | 0.752018 | 1.16661e-05 |
| f7 | 1241 | 52.6667 | 50.3333 | 0.522876 | 0.692938 |
| f8 | 391.5 | 69.3235 | 33.6765 | 0.849481 | 2.54789e-10 |
| f9 | 2601 | 26 | 77 | 0 | 3.30225e-18 |
| f10 | 2601 | 26 | 77 | 0 | 3.83762e-20 |

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
| f2 | 2 | 2 | 2 |
| f3 | 1 | 2.5 | 2.5 |
| f4 | 2.5 | 2.5 | 1 |
| f5 | 2 | 2 | 2 |
| f6 | 3 | 2 | 1 |
| f7 | 2.5 | 2.5 | 1 |
| f8 | 1 | 3 | 2 |
| f9 | 1 | 3 | 2 |
| f10 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | BIPOP-CMA-ES | 1.9 | 2.4 | 1.7 | 0.272532 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1 | 3 | 2 | 0.0497871 | MSC-CMA-ES | — | 0.0143059 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
