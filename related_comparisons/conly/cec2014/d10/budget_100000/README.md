# C-only positioning - CEC2014, D = 10, budget 10^5

Composition class (8 functions: f23-f30), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 1499 | 1477 | 860 | 2018 | 0.2138 |
| MSC-CMA-ES | 1592 | 1695 | 895.9 | 1856 | 0.2099 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f23 | 0.05882 | 0.03922 |
| f24 | 0 | 0 |
| f25 | 0 | 0 |
| f26 | 0.003076 | 0.0007689 |
| f27 | 0.1519 | 0.1699 |
| f28 | 0 | 0 |
| f29 | 0 | 0 |
| f30 | 0 | 0 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 8 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES |
|:--|--:|
| f23 | 0.02658 &#8593; |
| f24 | 4.606e-14 &#8595; |
| f25 | 1.832e-07 &#8595; |
| f26 | 0.004539 &#8595; |
| f27 | 1.905e-07 &#8595; |
| f28 | 0.0005944 &#8593; |
| f29 | 1 |
| f30 | 3.865e-06 &#8595; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 2 | 5 | 1 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
