# C-only positioning - CEC2020, D = 20, budget 10^7

Composition class (3 functions: f8-f10), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 513.4 | 534.8 | 100 | 559.5 | 0.1715 |
| MSC-CMA-ES | 533.2 | 539.7 | 399.1 | 578.1 | 0.3641 |
| ARRDE | 566.6 | 581.2 | 130.5 | 601 | 0.05882 |
| NL-SHADE-RSP | 593.2 | 599.1 | 444.8 | 613.7 | 0.03383 |
| BIPOP-CMA-ES | 723.8 | 713.7 | 499.1 | 918.2 | 0.02384 |
| j2020 | 853.2 | 910.9 | 499 | 935 | 0.02076 |
| L-SRTDE | 873.6 | 891 | 813.7 | 910.4 | 0.00692 |
| jSO | 904.6 | 906.7 | 878.7 | 912.6 | 0 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 0.07343 | 0.3445 | 0.01807 | 0.02384 | 0.00692 | 0.01038 | 0.02076 | 0 |
| f9 | 0.09804 | 0.01961 | 0.04037 | 0 | 0 | 0.02345 | 0 | 0 |
| f10 | 0 | 0 | 0.0003845 | 0 | 0 | 0 | 0 | 0 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 3 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|
| f8 | 0.7573 | 2.487e-15 &#8593; | 2.99e-15 &#8593; | 2.065e-18 &#8593; | 4.519e-18 &#8593; | 1.633e-16 &#8593; | 4.172e-20 &#8593; |
| f9 | 1 | 3.817e-13 &#8595; | 0.01056 &#8593; | 9.654e-18 &#8593; | 1.385e-12 &#8595; | 2.394e-12 &#8593; | 9.881e-18 &#8593; |
| f10 | 0.01877 &#8593; | 1.535e-12 &#8595; | 3.663e-16 &#8593; | 2.569e-18 &#8593; | 0.1358 | 9.516e-06 &#8595; | 1.843e-18 &#8593; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 1 | 0 | 2 |
| ARRDE | 1 | 2 | 0 |
| BIPOP-CMA-ES | 3 | 0 | 0 |
| L-SRTDE | 3 | 0 | 0 |
| NL-SHADE-RSP | 1 | 1 | 1 |
| j2020 | 2 | 1 | 0 |
| jSO | 3 | 0 | 0 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
