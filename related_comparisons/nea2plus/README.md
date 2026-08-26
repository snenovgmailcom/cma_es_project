# NEA2+ related-method comparison

This supplementary comparison evaluates MSC-CMA-ES against **NEA2+** on the six suite–dimension–budget settings for which complete 51-run NEA2+ data are available.

NEA2+ reference: [Experimental Assessment of Multimodal Optimization Algorithms](https://titan.csit.rmit.edu.au/~e46507/publications/Experimental_Assessment_of_Multimodal_Optimization_Algorithms.pdf).

Each setting page combines three views:

1. **Benchmark results** — fixed-budget descriptive metrics for MSC-CMA-ES and NEA2+.
2. **Mann–Whitney U** — function-wise NEA2+ vs MSC-CMA-ES tests on 51 unmodified terminal errors with Bonferroni adjustment.
3. **Deep Statistical Comparison** — MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES, analyzed for all functions and for composition functions.

CEC2020 D=20 is not included because a complete 51-run NEA2+ result set was not available.

| Suite | D | Budget | Benchmark results | MWU | DSC | MWU summary (↓ / ↑ / —) |
|:--|--:|--:|:--|:--|:--|:--:|
| CEC2017 | 10 | 10^5 | [Benchmark](cec2017/d10/budget_100000/README.md#benchmark-results) | [MWU](cec2017/d10/budget_100000/README.md#mannwhitney-u) | [DSC](cec2017/d10/budget_100000/README.md#deep-statistical-comparison) | 2 / 21 / 6 |
| CEC2020 | 5 | 5×10^4 | [Benchmark](cec2020/d5/budget_50000/README.md#benchmark-results) | [MWU](cec2020/d5/budget_50000/README.md#mannwhitney-u) | [DSC](cec2020/d5/budget_50000/README.md#deep-statistical-comparison) | 2 / 4 / 4 |
| CEC2020 | 10 | 10^6 | [Benchmark](cec2020/d10/budget_1000000/README.md#benchmark-results) | [MWU](cec2020/d10/budget_1000000/README.md#mannwhitney-u) | [DSC](cec2020/d10/budget_1000000/README.md#deep-statistical-comparison) | 1 / 6 / 3 |
| CEC2020 | 15 | 3×10^6 | [Benchmark](cec2020/d15/budget_3000000/README.md#benchmark-results) | [MWU](cec2020/d15/budget_3000000/README.md#mannwhitney-u) | [DSC](cec2020/d15/budget_3000000/README.md#deep-statistical-comparison) | 2 / 8 / 0 |
| CEC2022 | 10 | 2×10^5 | [Benchmark](cec2022/d10/budget_200000/README.md#benchmark-results) | [MWU](cec2022/d10/budget_200000/README.md#mannwhitney-u) | [DSC](cec2022/d10/budget_200000/README.md#deep-statistical-comparison) | 1 / 9 / 2 |
| CEC2022 | 20 | 10^6 | [Benchmark](cec2022/d20/budget_1000000/README.md#benchmark-results) | [MWU](cec2022/d20/budget_1000000/README.md#mannwhitney-u) | [DSC](cec2022/d20/budget_1000000/README.md#deep-statistical-comparison) | 1 / 8 / 3 |

Across the six complete settings there are **83 functions**, i.e. **4233 NEA2+ runs** and the corresponding MSC-CMA-ES runs.

MWU and DSC use the stored run-wise terminal errors without clipping, rounding, sorting, or COCO-zero flooring. Descriptive benchmark metrics use the same display/aggregation convention as the main benchmark reports, including the `1e-8` zero rule.
