# C-only positioning - CEC2020, D = 15, budget 3x10^6

Composition class (3 functions: f8-f10), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 193.8 | 200 | 100 | 326.1 | 0.7278 |
| MSC-CMA-ES | 266.1 | 200 | 100 | 525.1 | 0.9146 |
| ARRDE | 387.7 | 334.9 | 200 | 600 | 0.1157 |
| NEA2+ | 493.4 | 524.2 | 100 | 549.3 | 0.1888 |
| NL-SHADE-RSP | 520.6 | 500 | 500 | 600 | 0.5513 |
| j2020 | 531.3 | 500 | 200.2 | 700 | 0.7382 |
| BIPOP-CMA-ES | 609.3 | 600 | 200 | 892.2 | 0.1576 |
| jSO | 840.4 | 852.8 | 600 | 886.1 | 0.006151 |
| L-SRTDE | 881.8 | 886.1 | 800 | 890.9 | 0.01115 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 0.5513 | 0.8558 | 0.1107 | 0.1576 | 0.01115 | 0.5379 | 0.7382 | 0.006151 | 0.1707 |
| f9 | 0.1765 | 0.05882 | 0.001538 | 0 | 0 | 0.01346 | 0 | 0 | 0.01807 |
| f10 | 0 | 0 | 0.00346 | 0 | 0 | 0 | 0 | 0 | 0 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 3 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 0.000327 &#8595; | 1.103e-11 &#8593; | 9.761e-10 &#8593; | 2.654e-18 &#8593; | 1 | 9.304e-05 &#8595; | 1.665e-18 &#8593; | 2.117e-09 &#8593; |
| f9 | 1 | 9.307e-09 &#8595; | 0.2928 | 8.915e-18 &#8593; | 2.563e-08 &#8595; | 0.002054 &#8595; | 1.011e-16 &#8593; | 1.134e-16 &#8593; |
| f10 | 0.2123 | 9.542e-08 &#8593; | 1.326e-17 &#8593; | 4.172e-20 &#8593; | 4.172e-20 &#8593; | 2.205e-19 &#8593; | 1.15e-19 &#8593; | 6.186e-15 &#8593; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 0 | 1 | 2 |
| ARRDE | 2 | 1 | 0 |
| BIPOP-CMA-ES | 2 | 0 | 1 |
| L-SRTDE | 3 | 0 | 0 |
| NL-SHADE-RSP | 1 | 1 | 1 |
| j2020 | 1 | 2 | 0 |
| jSO | 3 | 0 | 0 |
| NEA2+ | 3 | 0 | 0 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
