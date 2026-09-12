# CMAES-NBC related-method comparison

This supplementary comparison evaluates MSC-CMA-ES against **CMAES-NBC** on the ten suite–dimension–budget settings for which complete 51-run CMAES-NBC data are available.

CMAES-NBC reference: [Adapting the population size in CMA-ES using nearest-better clustering method for multimodal optimization](https://doi.org/10.1016/j.asoc.2024.112361). This comparison uses the locally executed non-qN algorithm, with the author-provided corrections: restart means in [-80, 80] and a 20-iteration maximum-population window.

Here B is the configured evaluation budget. The CMAES-NBC CSV bridge stores the author's best-ever objective error at algorithm termination (`params.errors_at_exact_budget=False`). Its target coverage is computed from these stored terminal errors; exact-budget trajectories are unavailable. Thus the CMAES-NBC coverage column summarizes termination results for runs configured with B, and does not establish first-hitting-time performance.

Each setting page combines three views:

1. **Benchmark results** — terminal descriptive metrics at each configured budget for MSC-CMA-ES and CMAES-NBC.
2. **Mann–Whitney U** — independent, two-sided tests on 51 stored terminal errors per sample, with Holm–Bonferroni adjustment applied separately to all functions and to composition functions within each setting.
3. **Deep Statistical Comparison** — MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES, analyzed for all functions and for composition functions.

## MWU symbols

Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES and CMAES-NBC samples in their pooled sample, with ranks increasing with terminal error and average ranks assigned to ties.

- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis $H_0:F_M=F_A$ is not rejected.

The `=` symbol denotes non-rejection; it does not assert equality of the sample mean ranks or distributions. Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.

## Settings

The two MWU count columns use independently adjusted families. The composition column is not a subset of decisions adjusted over all functions.

| Suite | D | Budget | Benchmark results | MWU | DSC | All: $n_{<}/n_{>}/n_{=}$ | Composition: $n_{<}/n_{>}/n_{=}$ |
|:--|--:|--:|:--|:--|:--|:--:|:--:|
| CEC2014 | 10 | 10^5 | [Benchmark](cec2014/d10/budget_100000/README.md#benchmark-results) | [MWU](cec2014/d10/budget_100000/README.md#mannwhitney-u) | [DSC](cec2014/d10/budget_100000/README.md#deep-statistical-comparison) | 10 / 17 / 3 | 3 / 5 / 0 |
| CEC2014 | 30 | 3×10^5 | [Benchmark](cec2014/d30/budget_300000/README.md#benchmark-results) | [MWU](cec2014/d30/budget_300000/README.md#mannwhitney-u) | [DSC](cec2014/d30/budget_300000/README.md#deep-statistical-comparison) | 4 / 25 / 1 | 0 / 8 / 0 |
| CEC2017 | 10 | 10^5 | [Benchmark](cec2017/d10/budget_100000/README.md#benchmark-results) | [MWU](cec2017/d10/budget_100000/README.md#mannwhitney-u) | [DSC](cec2017/d10/budget_100000/README.md#deep-statistical-comparison) | 8 / 17 / 4 | 8 / 2 / 0 |
| CEC2017 | 30 | 3×10^5 | [Benchmark](cec2017/d30/budget_300000/README.md#benchmark-results) | [MWU](cec2017/d30/budget_300000/README.md#mannwhitney-u) | [DSC](cec2017/d30/budget_300000/README.md#deep-statistical-comparison) | 5 / 23 / 1 | 3 / 7 / 0 |
| CEC2020 | 5 | 5×10^4 | [Benchmark](cec2020/d5/budget_50000/README.md#benchmark-results) | [MWU](cec2020/d5/budget_50000/README.md#mannwhitney-u) | [DSC](cec2020/d5/budget_50000/README.md#deep-statistical-comparison) | 3 / 3 / 4 | 2 / 1 / 0 |
| CEC2020 | 10 | 10^6 | [Benchmark](cec2020/d10/budget_1000000/README.md#benchmark-results) | [MWU](cec2020/d10/budget_1000000/README.md#mannwhitney-u) | [DSC](cec2020/d10/budget_1000000/README.md#deep-statistical-comparison) | 4 / 4 / 2 | 3 / 0 / 0 |
| CEC2020 | 15 | 3×10^6 | [Benchmark](cec2020/d15/budget_3000000/README.md#benchmark-results) | [MWU](cec2020/d15/budget_3000000/README.md#mannwhitney-u) | [DSC](cec2020/d15/budget_3000000/README.md#deep-statistical-comparison) | 5 / 5 / 0 | 3 / 0 / 0 |
| CEC2020 | 20 | 10^7 | [Benchmark](cec2020/d20/budget_10000000/README.md#benchmark-results) | [MWU](cec2020/d20/budget_10000000/README.md#mannwhitney-u) | [DSC](cec2020/d20/budget_10000000/README.md#deep-statistical-comparison) | 5 / 4 / 1 | 3 / 0 / 0 |
| CEC2022 | 10 | 2×10^5 | [Benchmark](cec2022/d10/budget_200000/README.md#benchmark-results) | [MWU](cec2022/d10/budget_200000/README.md#mannwhitney-u) | [DSC](cec2022/d10/budget_200000/README.md#deep-statistical-comparison) | 3 / 7 / 2 | 2 / 2 / 0 |
| CEC2022 | 20 | 10^6 | [Benchmark](cec2022/d20/budget_1000000/README.md#benchmark-results) | [MWU](cec2022/d20/budget_1000000/README.md#mannwhitney-u) | [DSC](cec2022/d20/budget_1000000/README.md#deep-statistical-comparison) | 4 / 5 / 3 | 3 / 1 / 0 |
| **Total** | | | | | | **51 / 110 / 21** | **30 / 26 / 0** |

Across the ten complete settings there are **182 function–setting comparisons**, including **56 composition-function comparisons**. They use **9282 runs per algorithm**; the composition analysis reuses the corresponding samples.

MWU and DSC use the stored run-wise terminal errors without additional rounding or zero flooring; stored zeros are retained. Descriptive benchmark metrics use the same display/aggregation convention as the main benchmark reports, including the `1e-8` zero rule.

Full-precision results: [MWU details](mwu/details.csv) and [MWU summaries](mwu/summary.csv).

## Reproduction

Run from the repository root:

```bash
python analysis/build_cmaes_nbc_comparison_readmes.py
```

This computes MWU, obtains DSC through DSCTool and regenerates all pages. Use `--reuse-dsc` to regenerate locally from saved DSC responses after checking that their requests and source hashes match the current PKLs. The scripts read terminal errors and do not rerun optimization experiments.
