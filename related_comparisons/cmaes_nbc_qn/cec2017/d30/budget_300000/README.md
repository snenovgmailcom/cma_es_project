# CEC2017, D=30, B=3×10^5 — MSC-CMA-ES vs CMAES-NBC-qN

This page compares MSC-CMA-ES with the numerical values reported by Nguyen for CMAES-NBC-qN:

> D. M. Nguyen, *Adapting the population size in CMA-ES using nearest-better clustering method for multimodal optimization*, *Applied Soft Computing* 167 (2024), 112361. DOI [10.1016/j.asoc.2024.112361](https://doi.org/10.1016/j.asoc.2024.112361).

Nguyen reports 51 runs per function and `maxFEs = 10,000 × D`; therefore D=30 corresponds to **3×10^5 NFE**. CMAES-NBC-qN mean/std values below are taken from **Table 12**.

MSC-CMA-ES mean/std values are computed from the repository's 51 terminal-error runs at the same suite, dimension and budget. The MSC values are computed from the stored terminal errors without flooring or clipping; std uses `ddof=1`.

**No MWU or DSC is computed for CMAES-NBC-qN**, because its run-wise samples are not available in the paper.

CEC2017 `f2` is omitted here to remain consistent with the project's 29-function CEC2017 evaluation set.

| Function | Class | MSC-CMA-ES Mean | CMAES-NBC-qN Mean | MSC-CMA-ES Std. | CMAES-NBC-qN Std. |
|:--|:--|--:|--:|--:|--:|
| f1 | Unimodal and simple multimodal | 1.41115e-07 | **0** | 4.06226e-07 | 0 |
| f3 | Unimodal and simple multimodal | 9.80828e-14 | **0** | 2.95165e-13 | 0 |
| f4 | Unimodal and simple multimodal | **56.6341** | 64.7 | 10.6787 | 12.5 |
| f5 | Unimodal and simple multimodal | **4.67532** | 25.5 | 2.28445 | 71.7 |
| f6 | Unimodal and simple multimodal | 0.131362 | **0** | 0.145889 | 0 |
| f7 | Unimodal and simple multimodal | **12.6445** | 361 | 12.4026 | 804 |
| f8 | Unimodal and simple multimodal | **4.51964** | 25.4 | 2.28247 | 81.3 |
| f9 | Unimodal and simple multimodal | 0.70592 | **0** | 0.741704 | 0 |
| f10 | Unimodal and simple multimodal | **356.103** | 477 | 256.785 | 363 |
| f11 | Hybrid | **35.6118** | 45600 | 25.4848 | 305000 |
| f12 | Hybrid | **1091.72** | 38000 | 309.551 | 249000 |
| f13 | Hybrid | **869.591** | 70900 | 320.075 | 383000 |
| f14 | Hybrid | 96.9617 | **19.6** | 35.0853 | 6.45 |
| f15 | Hybrid | **288.601** | 1.33e+09 | 73.9833 | 8.08e+09 |
| f16 | Hybrid | 33.4222 | **19.4** | 32.8711 | 23.8 |
| f17 | Hybrid | 36.6642 | **30.3** | 16.2004 | 6.56 |
| f18 | Hybrid | 207.884 | **22.2** | 58.2054 | 0.0115 |
| f19 | Hybrid | 88.0177 | **4.52** | 27.2486 | 0.956 |
| f20 | Hybrid | **30.4844** | 48.2 | 9.95161 | 33.2 |
| f21 | Composition | **203.097** | 428 | 21.1668 | 82.7 |
| f22 | Composition | **109.781** | 3190 | 69.8519 | 2540 |
| f23 | Composition | **355.268** | 525 | 36.5835 | 115 |
| f24 | Composition | **430.229** | 522 | 2.64934 | 110 |
| f25 | Composition | **386.938** | 387 | 0.0927667 | 2.92 |
| f26 | Composition | **227.451** | 1850 | 45.0708 | 2320 |
| f27 | Composition | **501.54** | 531 | 5.21826 | 91.5 |
| f28 | Composition | **310.565** | 4000 | 32.3395 | 10800 |
| f29 | Composition | 460.026 | **424** | 47.7271 | 38.7 |
| f30 | Composition | 2338.51 | **2030** | 117.974 | 166 |

*Bold marks the minimum of the two mean values. This is descriptive and is not a significance test.*

Source for CMAES-NBC-qN: Nguyen (2024), Table 12.
