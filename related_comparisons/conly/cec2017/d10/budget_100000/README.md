# C-only positioning - CEC2017, D = 10, budget 10^5

Composition class (10 functions: f21-f30), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 1568 | 1365 | 929.8 | 2354 | 2.782 |
| MSC-CMA-ES | 1891 | 2152 | 929.9 | 2697 | 1.714 |
| ARRDE | 2183 | 2317 | 1309 | 2783 | 0.6348 |
| NL-SHADE-RSP | 2292 | 2193 | 1170 | 3446 | 1.785 |
| NEA2+ | 2393 | 2479 | 1416 | 3031 | 0.3583 |
| j2020 | 2637 | 2733 | 1480 | 4231 | 0.4998 |
| BIPOP-CMA-ES | 2754 | 2745 | 1812 | 3472 | 0.1434 |
| jSO | 2799 | 2844 | 2610 | 3297 | 0.01115 |
| L-SRTDE | 3.496e+04 | 2909 | 2508 | 8.205e+05 | 0.06997 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| f21 | 0.1176 | 0.05882 | 0 | 0.0007689 | 0.006151 | 0.04114 | 0.01961 | 0.004614 | 0.01884 |
| f22 | 0.4275 | 0.4983 | 0.04806 | 0.123 | 0.06382 | 0.1384 | 0.05075 | 0.006151 | 0.1223 |
| f23 | 0.1961 | 0.09804 | 0.0223 | 0 | 0 | 0.1569 | 0 | 0 | 0 |
| f24 | 0.5898 | 0.2745 | 0 | 0.01961 | 0 | 0.06767 | 0.001538 | 0.0003845 | 0.05498 |
| f25 | 0.01961 | 0.01961 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| f26 | 0.7451 | 0.3922 | 0.4121 | 0 | 0 | 0.8574 | 0.2741 | 0 | 0.1088 |
| f27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| f28 | 0.6863 | 0.3725 | 0.1522 | 0 | 0 | 0.5233 | 0.1538 | 0 | 0.05344 |
| f29 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| f30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 10 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f21 | 0.0006776 &#8593; | 0.009013 &#8593; | 0.02492 &#8593; | 1 | 0.0002191 &#8595; | 1.328e-05 &#8593; | 0.003112 &#8595; | 6.629e-13 &#8593; |
| f22 | 1 | 5.573e-14 &#8593; | 1.503e-09 &#8593; | 5.303e-14 &#8593; | 6.028e-09 &#8593; | 9.544e-15 &#8593; | 5.532e-18 &#8593; | 5.146e-10 &#8593; |
| f23 | 0.07206 | 0.1525 | 0.001419 &#8593; | 0.1868 | 0.001255 &#8593; | 1.449e-10 &#8593; | 0.2198 | 1.288e-06 &#8593; |
| f24 | 0.09407 | 3.907e-07 &#8593; | 5.686e-11 &#8593; | 3.251e-16 &#8593; | 0.6988 | 0.01004 &#8593; | 1.23e-09 &#8593; | 1.242e-15 &#8593; |
| f25 | 1 | 4.424e-17 &#8593; | 7.026e-16 &#8593; | 2.929e-17 &#8593; | 1.937e-18 &#8593; | 3.299e-17 &#8593; | 1.076e-17 &#8593; | 2.208e-11 &#8593; |
| f26 | 0.02995 &#8593; | 1 | 3.675e-13 &#8593; | 1.987e-19 &#8593; | 6.789e-08 &#8595; | 0.001945 &#8593; | 6.868e-19 &#8593; | 2.873e-15 &#8593; |
| f27 | 2.805e-11 &#8595; | 1.056e-15 &#8595; | 3.063e-12 &#8595; | 1 | 2.617e-05 &#8595; | 8.916e-08 &#8595; | 1 | 1.033e-08 &#8595; |
| f28 | 0.01601 &#8593; | 7.752e-06 &#8593; | 2.187e-09 &#8593; | 1.436e-09 &#8593; | 1 | 0.0007289 &#8593; | 6.89e-09 &#8593; | 5.326e-16 &#8593; |
| f29 | 7.922e-11 &#8595; | 4.897e-12 &#8595; | 1 | 1.471e-13 &#8595; | 0.3739 | 1 | 1.792e-09 &#8595; | 0.7952 |
| f30 | 1 | 7.295e-13 &#8595; | 1 | 2.304e-13 &#8595; | 5.326e-16 &#8593; | 1.9e-16 &#8593; | 2.646e-17 &#8595; | 1 |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 3 | 2 | 5 |
| ARRDE | 5 | 3 | 2 |
| BIPOP-CMA-ES | 7 | 1 | 2 |
| L-SRTDE | 5 | 2 | 3 |
| NL-SHADE-RSP | 4 | 3 | 3 |
| j2020 | 8 | 1 | 1 |
| jSO | 5 | 3 | 2 |
| NEA2+ | 7 | 1 | 2 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
