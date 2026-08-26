# C-only positioning campaign

MSC-CMA-ES (C-only) - the C configuration run alone - against the full benchmark portfolio on the composition class of the eight design-envelope cells. The component ablations (NO-NBC, FIXED-PHI, NO-EXCLUSION, B-only) are documented in `ablations/`; NEA2+ has its own comparison in `related_comparisons/nea2plus/`.

Statistics: two-sided Mann-Whitney U on 51 raw terminal errors per function, Bonferroni within each (cell, opponent) family over the composition functions; DSC with the k = 8 portfolio on the composition scope where available.

| Cell | Budget | Functions | C-only vs MSC-CMA-ES (MW-U) | C-only vs ARRDE (MW-U) | Page |
|:--|:--|:--|:--|:--|:--|
| CEC2014 D=10 | 10^5 | 8 | 2 / 5 / 1 | 1 / 6 / 1 | [page](cec2014/d10/budget_100000/README.md) |
| CEC2017 D=10 | 10^5 | 10 | 3 / 2 / 5 | 5 / 3 / 2 | [page](cec2017/d10/budget_100000/README.md) |
| CEC2020 D=5 | 5x10^4 | 3 | 2 / 1 / 0 | 1 / 1 / 1 | [page](cec2020/d5/budget_50000/README.md) |
| CEC2020 D=10 | 10^6 | 3 | 0 / 0 / 3 | 2 / 0 / 1 | [page](cec2020/d10/budget_1000000/README.md) |
| CEC2020 D=15 | 3x10^6 | 3 | 0 / 1 / 2 | 2 / 1 / 0 | [page](cec2020/d15/budget_3000000/README.md) |
| CEC2020 D=20 | 10^7 | 3 | 1 / 0 / 2 | 1 / 2 / 0 | [page](cec2020/d20/budget_10000000/README.md) |
| CEC2022 D=10 | 2x10^5 | 4 | 1 / 2 / 1 | 1 / 3 / 0 | [page](cec2022/d10/budget_200000/README.md) |
| CEC2022 D=20 | 10^6 | 4 | 0 / 2 / 2 | 0 / 3 / 1 | [page](cec2022/d20/budget_1000000/README.md) |

Triples read: C-only better / opponent better / not significant, per composition function of the cell.
