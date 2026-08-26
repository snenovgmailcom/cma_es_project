# C-only positioning - CEC2020, D = 5, budget 5x10^4

Composition class (3 functions: f8-f10), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 41.83 | 6.606 | 2.41e-11 | 117.6 | 2.121 |
| MSC-CMA-ES | 48.27 | 6.162e-10 | 4.002e-11 | 115.7 | 2.408 |
| NEA2+ | 137.6 | 106.6 | 5.324e-08 | 319.2 | 1.215 |
| ARRDE | 144.7 | 100 | 1.819e-12 | 418.4 | 1.898 |
| j2020 | 179.9 | 100.1 | 9.095e-13 | 414.2 | 1.296 |
| NL-SHADE-RSP | 224.2 | 300 | 0 | 400.9 | 2.102 |
| BIPOP-CMA-ES | 371.8 | 447.4 | 100 | 690.9 | 0.9193 |
| jSO | 446.4 | 447.4 | 400 | 447.4 | 1.019 |
| L-SRTDE | 461.8 | 447.4 | 400 | 647.9 | 0.8312 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 0.4737 | 0.8785 | 0.9473 | 0.7297 | 0.812 | 1 | 0.7247 | 1 | 0.4906 |
| f9 | 1 | 1 | 0.7547 | 0.1895 | 0.01922 | 0.945 | 0.4375 | 0.01884 | 0.6513 |
| f10 | 0.6471 | 0.5294 | 0.1961 | 0 | 0 | 0.1569 | 0.1338 | 0 | 0.07305 |

## Mann-Whitney U: C-only vs each opponent

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 3 composition functions per opponent. Arrows mark significant results at alpha = 0.05 from the C-only perspective: up = C-only better, down = opponent better.

| Function | MSC-CMA-ES | ARRDE | BIPOP-CMA-ES | L-SRTDE | NL-SHADE-RSP | j2020 | jSO | NEA2+ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| f8 | 0.02568 &#8595; | 5.268e-10 &#8595; | 3.395e-07 &#8595; | 1.493e-08 &#8595; | 4.005e-20 &#8595; | 0.0017 &#8595; | 1.342e-19 &#8595; | 0.5287 |
| f9 | 2.887e-06 &#8593; | 0.3426 | 6.093e-09 &#8593; | 5.958e-20 &#8593; | 1.509e-15 &#8595; | 1.499e-06 &#8593; | 8.352e-20 &#8593; | 9.902e-18 &#8593; |
| f10 | 0.02412 &#8593; | 1.351e-06 &#8593; | 1.744e-15 &#8593; | 1.686e-18 &#8593; | 1.528e-07 &#8593; | 4.338e-11 &#8593; | 5.963e-20 &#8593; | 8.256e-11 &#8593; |

| Opponent | C-only better | Opponent better | Not significant |
|:--|--:|--:|--:|
| MSC-CMA-ES | 2 | 1 | 0 |
| ARRDE | 1 | 1 | 1 |
| BIPOP-CMA-ES | 2 | 1 | 0 |
| L-SRTDE | 2 | 1 | 0 |
| NL-SHADE-RSP | 1 | 2 | 0 |
| j2020 | 2 | 1 | 0 |
| jSO | 2 | 1 | 0 |
| NEA2+ | 2 | 0 | 1 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) is the raw fixed-budget target coverage at this cell's budget, on the target grid of the main benchmark pages.
- This page is a positioning comparison of the C-only schedule against the full portfolio; the component ablations of MSC-CMA-ES are documented in `ablations/`.
