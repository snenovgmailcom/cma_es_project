# C-only comparison — CEC2014, D=10, B=10^5

Composition class (8 functions: f23-f30), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(minimum) | SUM(maximum) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 1498.82 | 1476.63 | 859.963 | 2017.88 | 0.213764 |
| MSC-CMA-ES | 1592.1 | 1694.58 | 895.916 | 1856.38 | 0.209919 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f23 | 0.0588235 | 0.0392157 |
| f24 | 0 | 0 |
| f25 | 0 | 0 |
| f26 | 0.00307574 | 0.000768935 |
| f27 | 0.151865 | 0.169935 |
| f28 | 0 | 0 |
| f29 | 0 | 0 |
| f30 | 0 | 0 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 8 composition functions. Direction is stated from the C-only perspective: ↓ denotes a statistically significant shift toward lower terminal errors, ↑ a statistically significant shift toward higher terminal errors, and — no statistically significant difference after correction.

| Function | MSC-CMA-ES |
|:--|--:|
| f23 | 0.0265826 ↓ |
| f24 | 4.60552e-14 ↑ |
| f25 | 1.83176e-07 ↑ |
| f26 | 0.00453908 ↑ |
| f27 | 1.90524e-07 ↑ |
| f28 | 0.00059439 ↓ |
| f29 | 1 — |
| f30 | 3.8646e-06 ↑ |

| Compared with | C-only ↓ | C-only ↑ | — |
|:--|--:|--:|--:|
| MSC-CMA-ES | 2 | 5 | 1 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. Each budget is evaluated separately; FBTC(B) is not an anytime measure.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
