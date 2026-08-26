# C-only cross-suite comparison

Direct comparison of MSC-CMA-ES (C-only) with the full MSC-CMA-ES method on the composition-function subsets of eight suite-dimension-budget cells.

Statistics: independent two-sided Mann-Whitney U tests on 51 raw terminal errors per function, with Bonferroni correction within each cell over its composition functions.

| Cell | Budget | Composition functions | C-only ↓ / ↑ / — | Page |
|:--|:--|:--|:--|:--|
| CEC2014 D=10 | 10^5 | 8 | 2 / 5 / 1 | [results](cec2014/d10/budget_100000/README.md) |
| CEC2017 D=10 | 10^5 | 10 | 3 / 2 / 5 | [results](cec2017/d10/budget_100000/README.md) |
| CEC2020 D=5 | 5×10^4 | 3 | 2 / 1 / 0 | [results](cec2020/d5/budget_50000/README.md) |
| CEC2020 D=10 | 10^6 | 3 | 0 / 0 / 3 | [results](cec2020/d10/budget_1000000/README.md) |
| CEC2020 D=15 | 3×10^6 | 3 | 0 / 1 / 2 | [results](cec2020/d15/budget_3000000/README.md) |
| CEC2020 D=20 | 10^7 | 3 | 1 / 0 / 2 | [results](cec2020/d20/budget_10000000/README.md) |
| CEC2022 D=10 | 2×10^5 | 4 | 1 / 2 / 1 | [results](cec2022/d10/budget_200000/README.md) |
| CEC2022 D=20 | 10^6 | 4 | 0 / 2 / 2 | [results](cec2022/d20/budget_1000000/README.md) |

From the C-only perspective, ↓ counts statistically significant shifts toward lower terminal errors, ↑ counts statistically significant shifts toward higher terminal errors, and — counts comparisons that are not statistically significant after Bonferroni correction.
