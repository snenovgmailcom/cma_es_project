# C-only comparison — CEC2020, D=5, B=5×10^4

Composition class (3 functions: f8-f10), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(minimum) | SUM(maximum) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 41.8286 | 6.60599 | 2.41016e-11 | 117.561 | 2.12072 |
| MSC-CMA-ES | 48.2654 | 6.16183e-10 | 4.00178e-11 | 115.655 | 2.40792 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f8 | 0.473664 | 0.878508 |
| f9 | 1 | 1 |
| f10 | 0.647059 | 0.529412 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 3 composition functions. Direction is stated from the C-only perspective: ↓ denotes a statistically significant shift toward lower terminal errors, ↑ a statistically significant shift toward higher terminal errors, and — no statistically significant difference after correction.

| Function | MSC-CMA-ES |
|:--|--:|
| f8 | 0.0256772 ↑ |
| f9 | 2.88662e-06 ↓ |
| f10 | 0.0241226 ↓ |

| Compared with | C-only ↓ | C-only ↑ | — |
|:--|--:|--:|--:|
| MSC-CMA-ES | 2 | 1 | 0 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. Each budget is evaluated separately; FBTC(B) is not an anytime measure.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
