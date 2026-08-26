# C-only comparison — CEC2017, D=10, B=10^5

Composition class (10 functions: f21-f30), 51 runs per function, seeds 0-50, raw terminal errors.

## Benchmark summary (sums over the composition functions)

| Algorithm | SUM(mean) | SUM(median) | SUM(minimum) | SUM(maximum) | SUM(FBTC(B)) |
|:--|--:|--:|--:|--:|--:|
| MSC-CMA-ES (C-only) | 1567.88 | 1365.44 | 929.844 | 2354.48 | 2.78201 |
| MSC-CMA-ES | 1891.37 | 2152.01 | 929.859 | 2696.97 | 1.71396 |

## FBTC(B) per function

| Function | MSC-CMA-ES (C-only) | MSC-CMA-ES |
|:--|--:|--:|
| f21 | 0.117647 | 0.0588235 |
| f22 | 0.427528 | 0.49827 |
| f23 | 0.196078 | 0.0980392 |
| f24 | 0.589773 | 0.27451 |
| f25 | 0.0196078 | 0.0196078 |
| f26 | 0.745098 | 0.392157 |
| f27 | 0 | 0 |
| f28 | 0.686275 | 0.372549 |
| f29 | 0 | 0 |
| f30 | 0 | 0 |

## Mann-Whitney U: C-only vs full MSC-CMA-ES

Two-sided Mann-Whitney U on the 51 raw terminal errors per function; p_Bonferroni corrects within this cell over the 10 composition functions. Direction is stated from the C-only perspective: ↓ denotes a statistically significant shift toward lower terminal errors, ↑ a statistically significant shift toward higher terminal errors, and — no statistically significant difference after correction.

| Function | MSC-CMA-ES |
|:--|--:|
| f21 | 0.000677587 ↓ |
| f22 | 1 — |
| f23 | 0.0720608 — |
| f24 | 0.0940686 — |
| f25 | 1 — |
| f26 | 0.0299485 ↓ |
| f27 | 2.80547e-11 ↑ |
| f28 | 0.0160138 ↓ |
| f29 | 7.92225e-11 ↑ |
| f30 | 1 — |

| Compared with | C-only ↓ | C-only ↑ | — |
|:--|--:|--:|--:|
| MSC-CMA-ES | 3 | 2 | 5 |

## Protocol notes

- The C-only variant runs `benchmark/msc.py --conly`: the C configuration alone, without C/B alternation and without cross-cycle Phase-0 reuse; clustering, staircase, adaptive basin parameters, exclusion and refinement are unchanged.
- FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. Each budget is evaluated separately; FBTC(B) is not an anytime measure.
- This page is a positioning comparison of the C-only schedule directly against the full MSC-CMA-ES method; the component ablations of MSC-CMA-ES are documented in `ablations/`.
