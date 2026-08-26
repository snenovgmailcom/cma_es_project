# C-only positioning - CEC2017, D = 10, budget 10^5

Composition class (10 functions: f21-f30), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 1568 | 1365 | 929.8 | 2354 | 2.782 |
| MSC-CMA-ES | 1891 | 2152 | 929.9 | 2697 | 1.714 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f21 | 0.1176 | 0.05882 |
| f22 | 0.4275 | 0.4983 |
| f23 | 0.1961 | 0.09804 |
| f24 | 0.5898 | 0.2745 |
| f25 | 0.01961 | 0.01961 |
| f26 | 0.7451 | 0.3922 |
| f27 | 0 | 0 |
| f28 | 0.6863 | 0.3725 |
| f29 | 0 | 0 |
| f30 | 0 | 0 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 10 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES |
|:--|--:|
| f21 | 0.0006776 &#8593; |
| f22 | 1 |
| f23 | 0.07206 |
| f24 | 0.09407 |
| f25 | 1 |
| f26 | 0.02995 &#8593; |
| f27 | 2.805e-11 &#8595; |
| f28 | 0.01601 &#8593; |
| f29 | 7.922e-11 &#8595; |
| f30 | 1 |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 3 | 2 | 5 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
