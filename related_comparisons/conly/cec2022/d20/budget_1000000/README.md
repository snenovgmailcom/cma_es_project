# C-only comparison — CEC2022, D=20, B=10^6

Composition class (4 functions: f9-f12), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(minimum) | SUM(maximum) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES | 434.705 | 435.034 | 422.005 | 451.984 | 1.08228 |
| MSC-CMA-ES (C-only) | 516.764 | 517.973 | 453.099 | 525.594 | 1.00077 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f9 | 0 | 0 |
| f10 | 0.000768935 | 0.082276 |
| f11 | 1 | 1 |
| f12 | 0 | 0 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 4 composition functions. Direction is stated from the C-only perspective: ↓ denotes a statistically significant shift toward lower terminal errors, ↑ a statistically significant shift toward higher terminal errors, and — no statistically significant difference after correction.

| Function | MSC-CMA-ES |
|:--|--:|
| f9 | 1 — |
| f10 | 1.32147e-17 ↑ |
| f11 | 0.21567 — |
| f12 | 0.0199198 ↑ |

| Compared with | C-only ↓ | C-only ↑ | — |
|:--|--:|--:|--:|
| MSC-CMA-ES | 0 | 2 | 2 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. Each budget is evaluated separately; FBTC(B) is not an anytime measure.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
