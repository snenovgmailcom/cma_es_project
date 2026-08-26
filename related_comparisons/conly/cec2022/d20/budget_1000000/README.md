# C-only positioning - CEC2022, D = 20, budget 10^6

Composition class (4 functions: f9-f12), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES | 434.7 | 435 | 422 | 452 | 1.082 |
| NEA2+ | 516.8 | 516.7 | 512.7 | 523.5 | 0.8816 |
| MSC-CMA-ES (C-only) | 516.8 | 518 | 453.1 | 525.6 | 1.001 |
| ARRDE | 523.5 | 512.7 | 417.4 | 813.2 | 0.9319 |
| BIPOP-CMA-ES | 532.3 | 451.5 | 426.6 | 827.2 | 0.8297 |
| j2020 | 716.1 | 715.5 | 698.4 | 726.1 | 0.4271 |
| NL-SHADE-RSP | 719.1 | 719.2 | 712.1 | 734.1 | 0.9393 |
| jSO | 817.1 | 812.8 | 811.8 | 915.6 | 0 |
| L-SRTDE | 844.7 | 813.6 | 512.1 | 927.7 | 0.01961 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| f9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| f10 | 0.0007689 | 0.08228 | 0.00692 | 0.04537 | 0 | 0.9393 | 0.4271 | 0 | 0 |
| f11 | 1 | 1 | 0.925 | 0.7843 | 0.01961 | 0 | 0 | 0 | 0.8816 |
| f12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 4 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f9 | 1 | 0.08926 | 0.06052 | 0.3288 | 1 | 3.097e-18 &#8593; | 1 | 1.533e-19 &#8593; |
| f10 | 1.321e-17 &#8595; | 2.012e-16 &#8595; | 9.569e-17 &#8595; | 2.526e-16 &#8595; | 2.077e-19 &#8595; | 1.321e-17 &#8595; | 2.526e-16 &#8595; | 7.257e-14 &#8595; |
| f11 | 0.2157 | 1.745e-13 &#8595; | 5.051e-06 &#8595; | 6.869e-17 &#8593; | 3.215e-18 &#8593; | 1.031e-17 &#8593; | 2.366e-18 &#8593; | 1.321e-17 &#8593; |
| f12 | 0.01992 &#8595; | 1.364e-17 &#8595; | 1 | 2.152e-05 &#8595; | 0.01016 &#8593; | 0.1225 | 1.049e-15 &#8595; | 0.2365 |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 0 | 2 | 2 |
| ARRDE | 0 | 3 | 1 |
| BIPOP-CMA-ES | 0 | 2 | 2 |
| L-SRTDE | 1 | 2 | 1 |
| NL-SHADE-RSP | 2 | 1 | 1 |
| j2020 | 2 | 1 | 1 |
| jSO | 1 | 2 | 1 |
| NEA2+ | 2 | 1 | 1 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
