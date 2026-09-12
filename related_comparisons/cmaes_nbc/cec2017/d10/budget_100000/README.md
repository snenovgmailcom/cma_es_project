# CEC2017, D=10, B=10^5 — MSC-CMA-ES vs CMAES-NBC

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
| **Unimodal and simple multimodal** (n=9) | Mean | **60.6899** | 72.8323 |
|  | Median | 32.7803 | **21.3528** |
|  | Minimum | **3.17225** | 10.4919 |
|  | Maximum | **264.107** | 515.705 |
|  | Std. | **67.4759** | 120.037 |
|  | FBTC(B) | 5.14802 | **7.00308** |
| **Hybrid** (n=10) | Mean | 170.851 | **106.552** |
|  | Median | 202.261 | **33.5519** |
|  | Minimum | 4.37748 | **2.45767** |
|  | Maximum | **423.371** | 943.263 |
|  | Std. | **123.599** | 176.859 |
|  | FBTC(B) | 2.34679 | **3.59862** |
| **Composition** (n=10) | Mean | **1891.37** | 131323 |
|  | Median | **2152.01** | 3273.97 |
|  | Minimum | **929.859** | 2510.41 |
|  | Maximum | **2696.97** | 820606 |
|  | Std. | **569.04** | 300403 |
|  | FBTC(B) | **1.71396** | 0.0430604 |
| **All** (n=29) | Mean | **2122.91** | 131503 |
|  | Median | **2387.06** | 3328.88 |
|  | Minimum | **937.409** | 2523.36 |
|  | Maximum | **3384.44** | 822065 |
|  | Std. | **760.115** | 300699 |
|  | FBTC(B) | 9.20877 | **10.6448** |

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
| All | 29 | 8 | 17 | 4 |
| Composition | 10 | 8 | 2 | 0 |

### All functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f1 | Unimodal and simple multimodal | **1.48125e-18** | **`>`** |
| f3 | Unimodal and simple multimodal | **5.71776e-05** | **`>`** |
| f4 | Unimodal and simple multimodal | **1.41137e-08** | **`>`** |
| f5 | Unimodal and simple multimodal | **1.55909e-11** | **`>`** |
| f6 | Unimodal and simple multimodal | **4.03271e-19** | **`>`** |
| f7 | Unimodal and simple multimodal | 0.538066 | `=` |
| f8 | Unimodal and simple multimodal | **1.6705e-06** | **`>`** |
| f9 | Unimodal and simple multimodal | **7.54879e-08** | **`>`** |
| f10 | Unimodal and simple multimodal | 0.289111 | `=` |
| f11 | Hybrid | **5.45463e-14** | **`>`** |
| f12 | Hybrid | **7.90222e-05** | **`>`** |
| f13 | Hybrid | **1.0294e-08** | **`>`** |
| f14 | Hybrid | **1.91021e-13** | **`>`** |
| f15 | Hybrid | **2.10059e-15** | **`>`** |
| f16 | Hybrid | **3.22131e-08** | **`>`** |
| f17 | Hybrid | **0.00116165** | **`<`** |
| f18 | Hybrid | **1.65205e-13** | **`>`** |
| f19 | Hybrid | **8.76079e-17** | **`>`** |
| f20 | Hybrid | 0.145026 | `=` |
| f21 | Composition | **8.82676e-16** | **`<`** |
| f22 | Composition | **1.71164e-13** | **`<`** |
| f23 | Composition | **0.000603042** | **`>`** |
| f24 | Composition | **6.6288e-17** | **`<`** |
| f25 | Composition | **3.41429e-16** | **`<`** |
| f26 | Composition | **8.91688e-17** | **`<`** |
| f27 | Composition | **4.27269e-16** | **`<`** |
| f28 | Composition | **7.96598e-17** | **`<`** |
| f29 | Composition | 0.0914989 | `=` |
| f30 | Composition | **1.23015e-07** | **`>`** |

### Composition functions: Holm-adjusted comparisons

| Function | Class | $p_{\mathrm{Holm}}$ | Symbol |
|:--|:--|--:|:--:|
| f21 | Composition | **2.10161e-16** | **`<`** |
| f22 | Composition | **4.02738e-14** | **`<`** |
| f23 | Composition | **0.000201014** | **`>`** |
| f24 | Composition | **2.45511e-17** | **`<`** |
| f25 | Composition | **1.03913e-16** | **`<`** |
| f26 | Composition | **2.97229e-17** | **`<`** |
| f27 | Composition | **1.16528e-16** | **`<`** |
| f28 | Composition | **2.75746e-17** | **`<`** |
| f29 | Composition | **0.0228747** | **`<`** |
| f30 | Composition | **3.69046e-08** | **`>`** |

Bold entries indicate rejection of the null hypothesis at the specified Holm-adjusted threshold.

<details>
<summary>Unadjusted statistics and pooled-sample mean ranks</summary>

These statistics are shared by both scopes for a given function. The `probability_competitor_lower` column is the empirical estimate of $P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as $1-U_A/(n_A n_M)$.

| Function | $U_A$ (CMAES-NBC) | $\bar R_M$ | $\bar R_A$ | P(CMAES-NBC lower) | $p_{\mathrm{raw}}$ |
|:--|--:|--:|--:|--:|--:|
| f1 | 25.5 | 76.5 | 26.5 | 0.990196 | 5.29018e-20 |
| f3 | 867 | 60 | 43 | 0.666667 | 7.1472e-06 |
| f4 | 586.5 | 65.5 | 37.5 | 0.77451 | 1.08567e-09 |
| f5 | 279 | 71.5294 | 31.4706 | 0.892734 | 1.03939e-12 |
| f6 | 0 | 77 | 26 | 1 | 1.39059e-20 |
| f7 | 1208 | 53.3137 | 49.6863 | 0.535563 | 0.538066 |
| f8 | 625.5 | 64.7353 | 38.2647 | 0.759516 | 1.85611e-07 |
| f9 | 637.5 | 64.5 | 38.5 | 0.754902 | 6.86254e-09 |
| f10 | 1082 | 55.7843 | 47.2157 | 0.584006 | 0.144555 |
| f11 | 255 | 72 | 31 | 0.901961 | 2.87086e-15 |
| f12 | 644 | 64.3725 | 38.6275 | 0.752403 | 1.12889e-05 |
| f13 | 382 | 69.5098 | 33.4902 | 0.853133 | 7.35283e-10 |
| f14 | 147 | 74.1176 | 28.8824 | 0.943483 | 1.19388e-14 |
| f15 | 60 | 75.8235 | 27.1765 | 0.976932 | 1.05029e-16 |
| f16 | 411 | 68.9412 | 34.0588 | 0.841984 | 2.68443e-09 |
| f17 | 1851 | 40.7059 | 62.2941 | 0.288351 | 0.000232331 |
| f18 | 142 | 74.2157 | 28.7843 | 0.945406 | 9.17804e-15 |
| f19 | 1 | 76.9804 | 26.0196 | 0.999616 | 3.50432e-18 |
| f20 | 1005 | 57.2941 | 45.7059 | 0.61361 | 0.0483421 |
| f21 | 2557 | 26.8627 | 76.1373 | 0.0169166 | 4.20322e-17 |
| f22 | 2457 | 28.8235 | 74.1765 | 0.0553633 | 1.00685e-14 |
| f23 | 719 | 62.902 | 40.098 | 0.723568 | 0.000100507 |
| f24 | 2601 | 26 | 77 | 0 | 2.45511e-18 |
| f25 | 2573 | 26.549 | 76.451 | 0.0107651 | 1.48448e-17 |
| f26 | 2599 | 26.0392 | 76.9608 | 0.000768935 | 3.71537e-18 |
| f27 | 2553 | 26.9412 | 76.0588 | 0.0184544 | 1.94213e-17 |
| f28 | 2601 | 26 | 77 | 0 | 3.06384e-18 |
| f29 | 1641 | 44.8235 | 58.1765 | 0.369089 | 0.0228747 |
| f30 | 449 | 68.1961 | 34.8039 | 0.827374 | 1.23015e-08 |

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
| f4 | 3 | 1.5 | 1.5 |
| f5 | 2 | 1 | 3 |
| f6 | 3 | 1 | 2 |
| f7 | 1.5 | 3 | 1.5 |
| f8 | 2.5 | 1 | 2.5 |
| f9 | 3 | 1.5 | 1.5 |
| f10 | 1 | 2 | 3 |
| f11 | 2 | 1 | 3 |
| f12 | 3 | 1 | 2 |
| f13 | 3 | 1 | 2 |
| f14 | 2.5 | 1 | 2.5 |
| f15 | 3 | 1 | 2 |
| f16 | 1 | 2.5 | 2.5 |
| f17 | 1.5 | 3 | 1.5 |
| f18 | 2.5 | 1 | 2.5 |
| f19 | 3 | 1 | 2 |
| f20 | 1 | 2 | 3 |
| f21 | 1 | 3 | 2 |
| f22 | 1 | 3 | 2 |
| f23 | 1.5 | 3 | 1.5 |
| f24 | 1 | 3 | 2 |
| f25 | 1 | 3 | 2 |
| f26 | 1 | 3 | 2 |
| f27 | 2 | 3 | 1 |
| f28 | 1 | 3 | 2 |
| f29 | 1.5 | 1.5 | 3 |
| f30 | 1 | 3 | 2 |

### Statistical comparison

| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | p_Holm(CMAES-NBC) | Result |
|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|
| All | 29 | MSC-CMA-ES | 1.94828 | 1.96552 | 2.08621 | 0.848918 | — | — | — | **O** |
| Composition | 10 | MSC-CMA-ES | 1.2 | 2.85 | 1.95 | 0.00108628 | MSC-CMA-ES | — | 0.000224684 | **★** |

Complete DSCTool request/response files and exact orderings are stored under `related_comparisons/cmaes_nbc/dsc/`.
