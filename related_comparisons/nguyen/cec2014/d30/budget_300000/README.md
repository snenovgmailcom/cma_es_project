# CEC2014, D=30, B=3×10^5 — MSC-CMA-ES vs CMAES-NBC-qN

This page compares MSC-CMA-ES with the numerical values reported by Nguyen for CMAES-NBC-qN:

> D. M. Nguyen, *Adapting the population size in CMA-ES using nearest-better clustering method for multimodal optimization*, *Applied Soft Computing* 167 (2024), 112361. DOI [10.1016/j.asoc.2024.112361](https://doi.org/10.1016/j.asoc.2024.112361).

Nguyen reports 51 runs per function and `maxFEs = 10,000 × D`; therefore D=30 corresponds to **3×10^5 NFE**. CMAES-NBC-qN mean/std values below are taken from **Table 10**.

MSC-CMA-ES mean/std values are computed from the repository's 51 terminal-error runs at the same suite, dimension and budget. The MSC values are computed from the stored terminal errors without flooring or clipping; std uses `ddof=1`.

**No MWU or DSC is computed for CMAES-NBC-qN**, because its run-wise samples are not available in the paper.

| Function | Class | MSC-CMA-ES Mean | CMAES-NBC-qN Mean | MSC-CMA-ES Std. | CMAES-NBC-qN Std. |
|:--|:--|--:|--:|--:|--:|
| f1 | Unimodal and simple multimodal | 5.60436 | **0** | 6.82557 | 0 |
| f2 | Unimodal and simple multimodal | 6.6286e-08 | **0** | 3.48538e-07 | 0 |
| f3 | Unimodal and simple multimodal | 5.94787e-05 | **0** | 8.21351e-05 | 0 |
| f4 | Unimodal and simple multimodal | 11.2067 | **0** | 24.4016 | 0 |
| f5 | Unimodal and simple multimodal | **20.6011** | 21.7 | 0.452481 | 0.0245 |
| f6 | Unimodal and simple multimodal | 4.2855 | **3.06** | 2.10546 | 7.62 |
| f7 | Unimodal and simple multimodal | 0.00149678 | **0** | 0.00437577 | 0 |
| f8 | Unimodal and simple multimodal | **7.94016** | 233 | 2.44922 | 73.7 |
| f9 | Unimodal and simple multimodal | **4.83945** | 7.63 | 2.08821 | 42 |
| f10 | Unimodal and simple multimodal | **126.111** | 788 | 113.043 | 415 |
| f11 | Unimodal and simple multimodal | 315.339 | **188** | 192.527 | 199 |
| f12 | Unimodal and simple multimodal | **0.0335849** | 5.13 | 0.017814 | 4.61 |
| f13 | Unimodal and simple multimodal | **0.285326** | 0.775 | 0.0592207 | 0.0826 |
| f14 | Unimodal and simple multimodal | 0.809769 | **0.679** | 0.132979 | 0.137 |
| f15 | Unimodal and simple multimodal | **3.1239** | 1.23e+06 | 0.640533 | 8.78e+06 |
| f16 | Unimodal and simple multimodal | 12.4327 | **9.66** | 0.469295 | 2.45 |
| f17 | Hybrid | 1003.58 | **146** | 204.012 | 641 |
| f18 | Hybrid | 78.9645 | **0.528** | 98.9102 | 0.143 |
| f19 | Hybrid | 7.029 | **3.14** | 0.883523 | 1.08 |
| f20 | Hybrid | 100.595 | **1.7** | 51.2621 | 0.647 |
| f21 | Hybrid | **648.563** | 40600 | 134.485 | 228000 |
| f22 | Hybrid | **27.7286** | 134 | 6.45616 | 51.8 |
| f23 | Composition | **315.244** | 1020 | 7.99858e-14 | 2250 |
| f24 | Composition | **186.792** | 227 | 20.5717 | 32.9 |
| f25 | Composition | **203.085** | 252 | 0.484529 | 183 |
| f26 | Composition | **100.338** | 101 | 0.116656 | 0.151 |
| f27 | Composition | **343.363** | 571 | 27.8387 | 1170 |
| f28 | Composition | **779.272** | 862 | 40.5849 | 94.7 |
| f29 | Composition | 1128.54 | **712** | 107.026 | 92.1 |
| f30 | Composition | 1299.05 | **787** | 233.531 | 495 |

*Bold marks the minimum of the two mean values. This is descriptive and is not a significance test.*

Source for CMAES-NBC-qN: Nguyen (2024), Table 10.
