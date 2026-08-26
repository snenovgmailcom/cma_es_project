# C-only positioning - CEC2020, D = 10, budget 10^6

Composition class (3 functions: f8-f10), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 62.75 | 100 | 2.005e-10 | 100 | 2.373 |
| MSC-CMA-ES | 106.1 | 100 | 4.125e-10 | 200 | 1.923 |
| NEA2+ | 182.3 | 211.4 | 1.736e-07 | 424.3 | 0.7643 |
| ARRDE | 205.3 | 219.8 | 100 | 367 | 0.5113 |
| j2020 | 243.8 | 200.1 | 100 | 598.1 | 0.6855 |
| NL-SHADE-RSP | 461.5 | 497.7 | 100 | 597.7 | 0.8328 |
| BIPOP-CMA-ES | 512 | 598 | 100 | 781.6 | 0.4356 |
| jSO | 719.1 | 797.7 | 597.7 | 872.1 | 0.02384 |
| L-SRTDE | 814.1 | 825.2 | 497.7 | 875.8 | 0.09535 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 1 | 1 | 0.3291 | 0.3572 | 0.09419 | 0.5617 | 0.6052 | 0.01961 | 0.4752 |
| f9 | 1 | 0.8058 | 0.1822 | 0.07843 | 0.001153 | 0.271 | 0.08035 | 0.004229 | 0.2718 |
| f10 | 0.3725 | 0.1176 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0173 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 3 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 1 | 0.0002591 &#8593; | 0.01037 &#8593; | 9.835e-14 &#8593; | 1 | 0.6932 | 4.123e-20 &#8593; | 9.821e-18 &#8593; |
| f9 | 1 | 3.624e-08 &#8593; | 1.116e-13 &#8593; | 9.55e-18 &#8593; | 3.817e-05 &#8593; | 1.301e-13 &#8593; | 8.578e-18 &#8593; | 9.909e-18 &#8593; |
| f10 | 0.1884 | 0.3473 | 7.67e-16 &#8593; | 8.058e-18 &#8593; | 1.254e-17 &#8593; | 2.972e-16 &#8593; | 2.14e-18 &#8593; | 0.02228 &#8593; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 0 | 0 | 3 |
| ARRDE | 2 | 0 | 1 |
| BIPOP-CMA-ES | 3 | 0 | 0 |
| L-SRTDE | 3 | 0 | 0 |
| NL-SHADE-RSP | 2 | 0 | 1 |
| j2020 | 2 | 0 | 1 |
| jSO | 3 | 0 | 0 |
| NEA2+ | 3 | 0 | 0 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
