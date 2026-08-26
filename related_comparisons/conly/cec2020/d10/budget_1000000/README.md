# C-only comparison — CEC2020, D=10, B=10^6

Composition class (3 functions: f8-f10), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(minimum) | SUM(maximum) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 62.7494 | 100.002 | 2.00544e-10 | 100.019 | 2.37255 |
| MSC-CMA-ES | 106.147 | 100.004 | 4.12456e-10 | 200.02 | 1.92349 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f8 | 1 | 1 |
| f9 | 1 | 0.805844 |
| f10 | 0.372549 | 0.117647 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 3 composition functions. Direction is stated from the C-only perspective: ↓ denotes a statistically significant shift toward lower terminal errors, ↑ a statistically significant shift toward higher terminal errors, and — no statistically significant difference after correction.

| Function | MSC-CMA-ES |
|:--|--:|
| f8 | 1 — |
| f9 | 1 — |
| f10 | 0.188414 — |

| Compared with | C-only ↓ | C-only ↑ | — |
|:--|--:|--:|--:|
| MSC-CMA-ES | 0 | 0 | 3 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. Each budget is evaluated separately; FBTC(B) is not an anytime measure.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
