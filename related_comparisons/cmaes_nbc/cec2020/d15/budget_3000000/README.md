# CEC2020, D=15, B=3×10^6 — MSC-CMA-ES vs CMAES-NBC

This page combines the terminal benchmark results and the two statistical analyses used for the related-method comparison with CMAES-NBC.

- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B=3×10^6 NFE.
- **MWU:** independent two-sided Mann–Whitney U tests with Holm–Bonferroni adjustment, separately for all functions and for composition functions; symbols are stated from the MSC-CMA-ES perspective.
- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and composition functions are analyzed separately.

Contents: [Benchmark results](#benchmark-results) · [Mann–Whitney U](#mannwhitney-u) · [Deep Statistical Comparison](#deep-statistical-comparison)
## Benchmark results

Terminal results for configured budget **B=3×10^6 NFE**, using 51 runs per function for MSC-CMA-ES and CMAES-NBC.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

The descriptive metrics use the same definitions as the main benchmark reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; the standard deviation is the sample standard deviation (`ddof=1`). The FBTC(B) column uses the same 51 log-uniform targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. Class and All values are sums over functions.

| Category | Metric | MSC-CMA-ES | CMAES-NBC |
|:--|:--|--:|--:|
| **Unimodal and simple multimodal** (n=4) | Mean | **11.1224** | 93.7752 |
|  | Median | **11.7104** | 60.2539 |
|  | Minimum | **1.2221** | 15.7335 |
|  | Maximum | **28.2452** | 217.718 |
|  | Std. | **6.36379** | 67.043 |
|  | FBTC(B) | **1.53018** | 1.39293 |
| **Hybrid** (n=3) | Mean | 3.61562 | **1.55573** |
|  | Median | 3.34178 | **1.68992** |
|  | Minimum | 0.868499 | **0.775752** |
|  | Maximum | 8.19824 | **2.38214** |
|  | Std. | 1.53154 | **0.335465** |
|  | FBTC(B) | 0.641676 | **0.724337** |
| **Composition** (n=3) | Mean | **266.142** | 882.5 |
|  | Median | **200.007** | 890.395 |
|  | Minimum | **100.002** | 789.678 |
|  | Maximum | **525.082** | 891.197 |
|  | Std. | 145.79 | **27.7187** |
|  | FBTC(B) | **0.914648** | 0.0784314 |
| **All** (n=10) | Mean | **280.88** | 977.831 |
|  | Median | **215.06** | 952.339 |
|  | Minimum | **102.092** | 806.187 |
|  | Maximum | **561.526** | 1111.3 |
|  | Std. | 153.685 | **95.0971** |
|  | FBTC(B) | **3.08651** | 2.19569 |

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
| All | 10 | 5 | 5 | 0 |
| Composition | 3 | 3 | 0 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **0.0433389** | **`>`** |
| f2 | Unimodal and simple multimodal | **4.01836e-09** | **`<`** |
| f3 | Unimodal and simple multimodal | **1.98815e-19** | **`<`** |
| f4 | Unimodal and simple multimodal | **1.5428e-12** | **`>`** |
| f5 | Hybrid | **4.93084e-05** | **`>`** |
| f6 | Hybrid | **1.11346e-16** | **`>`** |
| f7 | Hybrid | **1.69091e-08** | **`>`** |
| f8 | Composition | **5.27483e-13** | **`<`** |
| f9 | Composition | **2.10502e-17** | **`<`** |
| f10 | Composition | **8.84882e-09** | **`<`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f8 | Composition | **1.50709e-13** | **`<`** |
| f9 | Composition | **7.01672e-18** | **`<`** |
| f10 | Composition | **2.21221e-09** | **`<`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 1198.5 | 53.5 | 49.5 | 0.539216 | 0.0433389 |
| f2 | 2219 | 33.4902 | 69.5098 | 0.146867 | 8.03672e-10 |
| f3 | 2601 | 26 | 77 | 0 | 1.98815e-20 |
| f4 | 207 | 72.9412 | 30.0588 | 0.920415 | 2.57134e-13 |
| f5 | 675.5 | 63.7549 | 39.2451 | 0.740292 | 2.46542e-05 |
| f6 | 26 | 76.4902 | 26.5098 | 0.990004 | 1.39183e-17 |
| f7 | 430 | 68.5686 | 34.4314 | 0.834679 | 5.63636e-09 |
| f8 | 2397 | 30 | 73 | 0.0784314 | 7.53547e-14 |
| f9 | 2601 | 26 | 77 | 0 | 2.33891e-18 |
| f10 | 2193 | 34 | 69 | 0.156863 | 2.21221e-09 |

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
| f5 | 3 | 1.5 | 1.5 |
| f6 | 3 | 1 | 2 |
| f7 | 1 | 2.5 | 2.5 |
| f8 | 1 | 3 | 2 |
| f9 | 1 | 3 | 2 |
| f10 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 10 | BIPOP-CMA-ES | 1.9 | 2.35 | 1.75 | 0.377192 | — | — | — | **O** |
| Composition | 3 | MSC-CMA-ES | 1 | 3 | 2 | 0.0497871 | MSC-CMA-ES | — | 0.0143059 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
