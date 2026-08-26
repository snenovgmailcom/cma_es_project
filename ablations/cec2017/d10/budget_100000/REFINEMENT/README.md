# Final-refinement contribution — CEC2017, D=10, B=10^5

## Analysis

This analysis uses the full MSC-CMA-ES runs and compares the incumbent recorded immediately before the final refinement stage with the terminal incumbent after refinement.

This is **not** treated as a separate fixed-budget algorithmic ablation. The two values come from the same run and correspond to different evaluation counts: the pre-refinement incumbent is recorded before the reserved refinement budget is spent, while the final incumbent is recorded at the end of the run.

Raw data: `experiments/cec2017/d10/MSC-CMA/maxevals_100000/`

For descriptive display, errors with absolute value at most `1e-8` are treated as zero, consistently with the main benchmark tables.

## Class summary

| Category | SUM(median before) | SUM(median after) | Improved run-function pairs |
|:--|--:|--:|--:|
| **Unimodal and simple multimodal** (n=9) | 41.7707 | 32.7803 | 428/459 |
| **Hybrid** (n=10) | 220.112 | 202.261 | 397/510 |
| **Composition** (n=10) | 2212.25 | 2152.01 | 506/510 |
| **All** (n=29) | 2474.13 | 2387.06 | 1331/1479 |

## Per-function refinement contribution

| Function | Class | Median before | Median after | Runs improved |
|:--|:--|--:|--:|--:|
| f1 | Unimodal and simple multimodal | 0.812146 | 2.37419e-08 | 51/51 |
| f3 | Unimodal and simple multimodal | 0.571886 | 0 | 51/51 |
| f4 | Unimodal and simple multimodal | 3.78345 | 0 | 51/51 |
| f5 | Unimodal and simple multimodal | 2.3297 | 1.98992 | 51/51 |
| f6 | Unimodal and simple multimodal | 1.77329 | 0.00545266 | 51/51 |
| f7 | Unimodal and simple multimodal | 11.3166 | 11.2554 | 27/51 |
| f8 | Unimodal and simple multimodal | 1.39644 | 0.994959 | 51/51 |
| f9 | Unimodal and simple multimodal | 0.408774 | 0 | 44/51 |
| f10 | Unimodal and simple multimodal | 19.3785 | 18.5345 | 51/51 |
| f11 | Hybrid | 2.17374 | 0 | 51/51 |
| f12 | Hybrid | 132.792 | 129.611 | 51/51 |
| f13 | Hybrid | 6.85605 | 6.52556 | 23/51 |
| f14 | Hybrid | 2.50652 | 0.995724 | 32/51 |
| f15 | Hybrid | 1.97585 | 1.63898 | 27/51 |
| f16 | Hybrid | 4.99671 | 1.85165 | 51/51 |
| f17 | Hybrid | 23.6266 | 21.3695 | 50/51 |
| f18 | Hybrid | 21.5048 | 20.5907 | 45/51 |
| f19 | Hybrid | 2.78741 | 2.44898 | 20/51 |
| f20 | Hybrid | 20.8923 | 17.2287 | 47/51 |
| f21 | Composition | 102.806 | 100 | 51/51 |
| f22 | Composition | 13.0739 | 11.3965 | 51/51 |
| f23 | Composition | 305.895 | 305.32 | 51/51 |
| f24 | Composition | 105.199 | 100 | 51/51 |
| f25 | Composition | 115.698 | 100.007 | 51/51 |
| f26 | Composition | 202.515 | 200 | 51/51 |
| f27 | Composition | 391.392 | 389.706 | 51/51 |
| f28 | Composition | 301.645 | 300 | 51/51 |
| f29 | Composition | 234.217 | 232.245 | 48/51 |
| f30 | Composition | 439.81 | 413.34 | 50/51 |

No independent-sample MWU test is attached to this table because pre- and post-refinement values are stages of the same optimization run rather than results from two independently executed algorithms.

