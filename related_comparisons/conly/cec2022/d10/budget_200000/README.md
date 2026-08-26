# C-only positioning - CEC2022, D = 10, budget 2x10^5

Composition class (4 functions: f9-f12), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| NL-SHADE-RSP | 384.9 | 393.1 | 159.4 | 419.6 | 1.665 |
| j2020 | 387.4 | 390.8 | 258.6 | 392.9 | 1.371 |
| MSC-CMA-ES (C-only) | 397.1 | 465.2 | 161.7 | 496.9 | 1.113 |
| MSC-CMA-ES | 420.5 | 422.7 | 261.7 | 494 | 1.071 |
| ARRDE | 437.7 | 489 | 159.2 | 492.2 | 1.1 |
| NEA2+ | 474.6 | 493.1 | 15.29 | 493.5 | 0.99 |
| BIPOP-CMA-ES | 479.9 | 493.1 | 398.9 | 493.7 | 1.013 |
| jSO | 494.2 | 494.4 | 492.1 | 494.4 | 1 |
| L-SRTDE | 494.3 | 494.4 | 492 | 494.4 | 1 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| f9 | 0.07843 | 0 | 0.05998 | 0 | 0 | 0.03922 | 0 | 0 | 0.01884 |
| f10 | 0.0346 | 0.07113 | 0.03998 | 0.01307 | 0 | 0.6259 | 0.3714 | 0 | 0.008843 |
| f11 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0.9566 |
| f12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.005767 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 4 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f9 | 0.001669 &#8593; | 8.32e-05 &#8593; | 1.196e-08 &#8593; | 1.196e-08 &#8593; | 9.714e-07 &#8593; | 1.088e-07 &#8593; | 1.196e-08 &#8593; | 1.257e-16 &#8593; |
| f10 | 0.005023 &#8595; | 0.001768 &#8595; | 0.1226 | 0.2437 | 3.255e-17 &#8595; | 1.321e-17 &#8595; | 0.2437 | 0.3321 |
| f11 | 0.2493 | 8.868e-19 &#8595; | 1.283e-17 &#8595; | 2.753e-18 &#8595; | 1.114e-19 &#8595; | 3.889e-18 &#8595; | 3.793e-18 &#8595; | 1.321e-17 &#8593; |
| f12 | 1.831e-09 &#8595; | 1.674e-16 &#8595; | 9.224e-09 &#8595; | 1 | 0.0009641 &#8595; | 1.224e-16 &#8595; | 1 | 1.104e-08 &#8595; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 1 | 2 | 1 |
| ARRDE | 1 | 3 | 0 |
| BIPOP-CMA-ES | 1 | 2 | 1 |
| L-SRTDE | 1 | 1 | 2 |
| NL-SHADE-RSP | 1 | 3 | 0 |
| j2020 | 1 | 3 | 0 |
| jSO | 1 | 1 | 2 |
| NEA2+ | 2 | 1 | 1 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
