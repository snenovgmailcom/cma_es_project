# NEA2+ related-method comparison

This supplementary comparison evaluates MSC-CMA-ES against **NEA2+** on the six suite–dimension–budget settings for which complete 51-run NEA2+ data are available.

NEA2+ reference: [Experimental Assessment of Multimodal Optimization Algorithms](https://titan.csit.rmit.edu.au/~e46507/publications/Experimental_Assessment_of_Multimodal_Optimization_Algorithms.pdf).

Each setting page combines three views:

1. **Benchmark results** — fixed-budget descriptive metrics for MSC-CMA-ES and NEA2+.
2. **Mann–Whitney U** — independent, two-sided tests on 51 stored terminal errors per sample, with Holm–Bonferroni adjustment applied separately to all functions and to composition functions within each setting.
3. **Deep Statistical Comparison** — MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES, analyzed for all functions and for composition functions.

CEC2020 D=20 is not included because a complete 51-run NEA2+ result set was not available.

## MWU symbols

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and NEA2+ samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

## Settings

The two MWU count columns use independently adjusted families. The composition column is not a subset of decisions adjusted over all functions.

| Suite | D | Budget | Benchmark results | MWU | DSC | All: $n_{<}/n_{>}/n_{=}$ | Composition: $n_{<}/n_{>}/n_{=}$ |
|:--|--:|--:|:--|:--|:--|:--:|:--:|
| CEC2017 | 10 | 10^5 | [Benchmark](cec2017/d10/budget_100000/README.md#benchmark-results) | [MWU](cec2017/d10/budget_100000/README.md#mannwhitney-u) | [DSC](cec2017/d10/budget_100000/README.md#deep-statistical-comparison) | 21 / 2 / 6 | 8 / 0 / 2 |
| CEC2020 | 5 | 5×10^4 | [Benchmark](cec2020/d5/budget_50000/README.md#benchmark-results) | [MWU](cec2020/d5/budget_50000/README.md#mannwhitney-u) | [DSC](cec2020/d5/budget_50000/README.md#deep-statistical-comparison) | 4 / 2 / 4 | 3 / 0 / 0 |
| CEC2020 | 10 | 10^6 | [Benchmark](cec2020/d10/budget_1000000/README.md#benchmark-results) | [MWU](cec2020/d10/budget_1000000/README.md#mannwhitney-u) | [DSC](cec2020/d10/budget_1000000/README.md#deep-statistical-comparison) | 6 / 1 / 3 | 2 / 0 / 1 |
| CEC2020 | 15 | 3×10^6 | [Benchmark](cec2020/d15/budget_3000000/README.md#benchmark-results) | [MWU](cec2020/d15/budget_3000000/README.md#mannwhitney-u) | [DSC](cec2020/d15/budget_3000000/README.md#deep-statistical-comparison) | 8 / 2 / 0 | 3 / 0 / 0 |
| CEC2022 | 10 | 2×10^5 | [Benchmark](cec2022/d10/budget_200000/README.md#benchmark-results) | [MWU](cec2022/d10/budget_200000/README.md#mannwhitney-u) | [DSC](cec2022/d10/budget_200000/README.md#deep-statistical-comparison) | 11 / 1 / 0 | 4 / 0 / 0 |
| CEC2022 | 20 | 10^6 | [Benchmark](cec2022/d20/budget_1000000/README.md#benchmark-results) | [MWU](cec2022/d20/budget_1000000/README.md#mannwhitney-u) | [DSC](cec2022/d20/budget_1000000/README.md#deep-statistical-comparison) | 8 / 1 / 3 | 3 / 0 / 1 |
| **Total** | | | | | | **58 / 9 / 16** | **23 / 0 / 4** |

Across the six complete settings there are **83 function–setting comparisons**, including **27 composition-function comparisons**. They use **4233 runs per algorithm**; the composition analysis reuses the corresponding samples.

MWU and DSC use the stored run-wise terminal errors without additional rounding or zero flooring; zeros returned by the algorithms are retained. Descriptive benchmark metrics use the same display/aggregation convention as the main benchmark reports, including the `1e-8` zero rule.

Full-precision results: [MWU details](mwu/details.csv) and [MWU summaries](mwu/summary.csv).
