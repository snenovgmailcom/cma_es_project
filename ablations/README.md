# MSC-CMA-ES ablation studies

The ablation study is performed on **CEC2017, D=10, B=10^5 NFE**, using 51 runs per function and excluding the deprecated CEC2017 `f2`.

The two MSC-CMA-ES configurations were tuned with Optuna only once, on CEC2017 at D=10 under the official 10^5 evaluation budget. The resulting parameterization is reused across suites, dimensions, and budgets; only the predefined dimension scaling of the CMA initial step-size parameter is applied. For this reason, the ablation study is performed on the same CEC2017 D=10 tuning cell.

The following ablations are considered:

| Ablation | Component tested | Results | MWU direction (variant ↓ / ↑ / —) |
|:--|:--|:--|--:|
| NO-NBC | Removal of nearest-better clustering and the basin-based structure layer | [Data + MWU](cec2017/d10/budget_100000/NO-NBC/README.md) | 5 / 17 / 7 |
| FIXED-PHI | Fixed NBC threshold `phi = 2` instead of automatic staircase selection | [Data + MWU](cec2017/d10/budget_100000/FIXED-PHI/README.md) | 4 / 2 / 23 |
| NO-EXCLUSION | Removal of suppression of repeatedly resolved basins | [Data + MWU](cec2017/d10/budget_100000/NO-EXCLUSION/README.md) | 1 / 0 / 28 |
| C-ONLY | C configuration only, without C/B alternation and cross-cycle Phase-0 reuse | [Data + MWU](cec2017/d10/budget_100000/C-ONLY/README.md) | 5 / 13 / 11 |
| Final refinement | Incumbent immediately before vs after the final refinement stage | [Contribution analysis](cec2017/d10/budget_100000/REFINEMENT/README.md) | — |

For the four algorithmic ablations, statistical comparisons against full MSC-CMA-ES use independent two-sided Mann–Whitney U tests on the 51 raw terminal errors per function, with Bonferroni correction across the 29 CEC2017 functions.

Deep Statistical Comparison is not used for the ablation study: each ablation addresses a direct component-wise comparison against the full algorithm rather than a multi-algorithm ranking question.

