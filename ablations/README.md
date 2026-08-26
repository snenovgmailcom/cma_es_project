# MSC-CMA-ES ablation studies

The component ablations are performed on **CEC2017, D=10, B=100,000 NFE**, using 51 runs per function and excluding the deprecated CEC2017 `f2`.

The two MSC-CMA-ES configurations were tuned with Optuna only once, on CEC2017 at D=10 under the official 100K evaluation budget. The resulting parameterization is reused across suites, dimensions, and budgets; only the predefined dimension scaling of the CMA initial step-size parameter is applied. On the tuning cell a component ablation therefore acts on parameters in their native environment; on any other cell the component effect would be confounded with the parameter-transfer effect. For this reason the component ablations are evaluated on the CEC2017 D=10 tuning cell, and the cross-suite runs listed below serve as supporting evidence for transferability.

The following ablations are considered:

| Ablation | Component tested | Results | MW-U summary (variant / MSC-CMA-ES / n.s.) |
|:--|:--|:--|--:|
| NO-NBC | Removal of nearest-better clustering and the basin-based structure layer | [Data + MW-U](cec2017/d10/budget_100000/NO-NBC/README.md) | 5 / 17 / 7 |
| FIXED-PHI | Fixed NBC threshold `phi = 2` instead of automatic staircase selection | [Data + MW-U](cec2017/d10/budget_100000/FIXED-PHI/README.md) | 4 / 2 / 23 |
| NO-EXCLUSION | Removal of suppression of repeatedly resolved basins | [Data + MW-U](cec2017/d10/budget_100000/NO-EXCLUSION/README.md) | 1 / 0 / 28 |
| C-ONLY | C configuration only, without C/B alternation and cross-cycle Phase-0 reuse | [Data + MW-U](cec2017/d10/budget_100000/C-ONLY/README.md) | 5 / 13 / 11 |
| B-ONLY (STAIR / PHI2 / PHI13) | B configuration only, with staircase, fixed `phi = 2`, or fixed `phi = 1.3`; hybrid-class diagnostic | [Data](experiments/cec2017/d10/) | - |
| Final refinement | Incumbent immediately before vs after the final refinement stage | [Contribution analysis](cec2017/d10/budget_100000/REFINEMENT/README.md) | - |

For the four algorithmic ablations, statistical comparisons against full MSC-CMA-ES use independent two-sided Mann-Whitney U tests on the 51 raw terminal errors per function, with Bonferroni correction across the 29 CEC2017 functions. In the manuscript the ablation tables are reported descriptively (mean, median, best, worst, FBTC(B)); the significance tables on these pages serve as the public supplement.

## Cross-suite supporting runs

- **FIXED-PHI**: full cells on CEC2014 D=10 at 10^5 ([data](experiments/cec2014/d10/FIXED-PHI/)) and CEC2020 D=15 at 3x10^6 ([data](experiments/cec2020/d15/FIXED-PHI/)); a partial composition-only run on CEC2020 D=20 at the extended 4x10^7 budget ([data](experiments/cec2020/d20/FIXED-PHI/)) is exploratory and excluded from the conclusions.
- **B-ONLY**: the three variants on the hybrid classes of CEC2014 D=10, CEC2017 D=10, CEC2020 D=15, and CEC2022 D=10 ([data](experiments/)), plus one extended-budget run of B-ONLY-STAIR on CEC2017 D=10 at 10^6.
- **C-only**: the composition classes of all eight design-envelope cells and the CEC2014/CEC2017 D=30 boundary cells. The C-only-versus-portfolio positioning comparison, with per-cell Mann-Whitney U and DSC analyses, is documented separately in [`related_comparisons/conly/`](../related_comparisons/conly/README.md); the component comparison C-only versus full MSC-CMA-ES on the tuning cell remains on the page linked above.

Deep Statistical Comparison is not used for the component ablations: each ablation addresses a direct component-wise comparison against the full algorithm rather than a multi-algorithm ranking question. The C-only positioning comparison against the full portfolio is a ranking question and is therefore reported separately in `related_comparisons/conly/` with per-cell Friedman and Holm post-hoc analyses (k = 8).
