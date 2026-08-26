# C-only positioning - CEC2014, D = 10, budget 10^5

Composition class (8 functions: f23-f30), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 1499 | 1477 | 860 | 2018 | 0.2138 |
| ARRDE | 1581 | 1695 | 895.8 | 1769 | 0.2726 |
| MSC-CMA-ES | 1592 | 1695 | 895.9 | 1856 | 0.2099 |
| NL-SHADE-RSP | 1604 | 1752 | 951.9 | 1883 | 0.539 |
| jSO | 1728 | 1693 | 1573 | 2166 | 0.1992 |
| j2020 | 1798 | 1762 | 1559 | 2283 | 0.1342 |
| L-SRTDE | 2000 | 2054 | 1573 | 2437 | 0.1123 |
| BIPOP-CMA-ES | 2008 | 2054 | 1132 | 2574 | 0.03537 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f23 | 0.05882 | 0.03922 | 0.08035 | 0 | 0 | 0.3318 | 0 | 0 |
| f24 | 0 | 0 | 0 | 0 | 0.003845 | 0 | 0 | 0.0003845 |
| f25 | 0 | 0 | 0 | 0 | 0.0007689 | 0 | 0 | 0 |
| f26 | 0.003076 | 0.0007689 | 0 | 0 | 0 | 0 | 0 | 0 |
| f27 | 0.1519 | 0.1699 | 0.1922 | 0.03537 | 0.1077 | 0.168 | 0.1342 | 0.1988 |
| f28 | 0 | 0 | 0 | 0 | 0 | 0.03922 | 0 | 0 |
| f29 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| f30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 8 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| f23 | 0.02658 &#8593; | 0.01547 &#8593; | 1.527e-13 &#8593; | 2.457e-14 &#8593; | 0.9593 | 5.584e-17 &#8593; | 2.457e-14 &#8593; |
| f24 | 4.606e-14 &#8595; | 5.963e-13 &#8595; | 2.14e-08 &#8595; | 9.587e-16 &#8595; | 0.831 | 1 | 9.246e-14 &#8595; |
| f25 | 1.832e-07 &#8595; | 3.242e-06 &#8595; | 1 | 0.0005584 &#8593; | 0.01103 &#8595; | 1 | 2.479e-07 &#8595; |
| f26 | 0.004539 &#8595; | 2.638e-12 &#8595; | 2.51e-12 &#8595; | 1.203e-11 &#8595; | 1.684e-11 &#8595; | 3.358e-08 &#8595; | 1.684e-11 &#8595; |
| f27 | 1.905e-07 &#8595; | 1.007e-13 &#8595; | 5.59e-11 &#8593; | 1 | 1.192e-06 &#8595; | 0.9261 | 1.741e-15 &#8595; |
| f28 | 0.0005944 &#8593; | 1 | 2.846e-11 &#8593; | 4.091e-05 &#8593; | 0.07381 | 0.0002589 &#8593; | 0.07983 |
| f29 | 1 | 0.007387 &#8595; | 1 | 0.007947 &#8595; | 0.04474 &#8595; | 1 | 0.02041 &#8595; |
| f30 | 3.865e-06 &#8595; | 5.92e-09 &#8595; | 1 | 0.0004069 &#8595; | 1 | 0.0724 | 2.633e-08 &#8595; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 2 | 5 | 1 |
| ARRDE | 1 | 6 | 1 |
| BIPOP-CMA-ES | 3 | 2 | 3 |
| L-SRTDE | 3 | 4 | 1 |
| NL-SHADE-RSP | 0 | 4 | 4 |
| j2020 | 2 | 1 | 5 |
| jSO | 1 | 6 | 1 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
