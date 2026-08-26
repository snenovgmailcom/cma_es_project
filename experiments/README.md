# Cross-suite summary

MSC-CMA-ES and BIPOP-CMA-ES are reported together with ARRDE, L-SRTDE, NL-SHADE-RSP, j2020, and jSO. All four tables use the same algorithm ordering and descriptive bolding.

## Budget

All results use each competition's **standard budget** (MaxFES) — no extended-budget runs are mixed in:

- **CEC2014 / CEC2017:** MaxFES = D·10⁴ — so 2×10^4 at D=2, 10^5 at D=10, 3·10^5 at D=30.
- **CEC2020:** the official per-dimension budgets — 5×10^4 (D=5), 10^6 (D=10), 3·10^6 (D=15), 10^7 (D=20); 2×10^4 at D=2 (project low-dim setting).
- **CEC2022:** 2·10^5 (D=10), 10^6 (D=20); 2×10^4 at D=2.

Which suites contribute at each dimension (with nF and budget) is listed under the by-dimension table.

## By dimension — all functions

Per-function metrics summed across **all CEC suites at each dimension**, using the standard competition budget only (see *Budget* below). Bold marks the minimum value for error-based metrics and the maximum value for FBTC(B); ties are also bolded. These values are descriptive and are not significance tests.

| D · nF | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **2 · 31** | Minimum | 5.67e-8 | **0** | **0** | 0.620 | **0** | 4.54e-5 | **0** |
|  | Mean | **1.40** | 178 | 1.79 | 511 | 13.9 | 9.01 | 310 |
|  | Median | 1.84e-5 | 21.6 | **0** | 405 | **0** | 2.60 | 304 |
|  | FBTC(B) | 28.9 | 26.0 | 30.7 | 23.5 | **30.7** | 22.1 | 26.4 |
| **5 · 10** | Minimum | 0.120 | 101 | 0.610 | 400 | **0** | **0** | 401 |
|  | Mean | **74.8** | 391 | 159 | 482 | 227 | 189 | 452 |
|  | Median | **4.68** | 457 | 106 | 453 | 302 | 106 | 453 |
|  | FBTC(B) | 5.49 | 4.72 | 6.73 | 5.07 | **7.83** | 6.15 | 5.84 |
| **10 · 81** | Minimum | **2126** | 3454 | 2481 | 5092 | 2414 | 3417 | 5300 |
|  | Mean | **4403** | 6266 | 4700 | 3.84e4 | 5220 | 5409 | 5948 |
|  | Median | **4715** | 6322 | 4934 | 6389 | 5300 | 5337 | 6064 |
|  | FBTC(B) | 27.4 | 26.1 | 32.4 | 29.9 | **33.5** | 28.3 | 32.0 |
| **15 · 10** | Minimum | **102** | 201 | 216 | 817 | 516 | 201 | 616 |
|  | Mean | **281** | 638 | 408 | 938 | 563 | 557 | 907 |
|  | Median | **215** | 625 | 354 | 908 | 531 | 526 | 884 |
|  | FBTC(B) | 3.09 | 3.33 | 2.47 | 2.12 | 3.46 | **3.52** | 2.10 |
| **20 · 12** | Minimum | 423 | 427 | **419** | 558 | 745 | 711 | 860 |
|  | Mean | **467** | 601 | 550 | 910 | 954 | 783 | 891 |
|  | Median | **478** | 506 | 538 | 881 | 881 | 774 | 888 |
|  | FBTC(B) | 4.79 | 5.02 | **5.66** | 4.30 | 4.20 | 3.98 | 3.67 |
| **30 · 59** | Minimum | 1.03e4 | 9124 | 9903 | **7256** | 7.69e4 | 1.38e5 | 9316 |
|  | Mean | 1.53e4 | 1.68e4 | 1.37e4 | **8631** | 4.39e5 | 4.68e5 | 1.18e4 |
|  | Median | 1.49e4 | 1.62e4 | 1.32e4 | **8395** | 2.78e5 | 3.58e5 | 1.18e4 |
|  | FBTC(B) | 8.46 | 12.2 | 14.1 | **15.8** | 8.55 | 9.17 | 14.5 |

**Composition of each dimension** (suite → nF, budget):
- **D=2** (31): cec2017 (15) · cec2020 (7) · cec2022 (9) — all 2×10^4.
- **D=5** (10): cec2020 — 5×10^4.
- **D=10** (81): cec2014 (30, 10^5) · cec2017 (29, 10^5) · cec2020 (10, 10^6) · cec2022 (12, 2×10^5).
- **D=15** (10): cec2020 — 3×10^6.
- **D=20** (12): cec2022 — 10^6.
- **D=30** (59): cec2014 (30) · cec2017 (29) — both 3×10^5.

CEC2017 excludes F2 uniformly (numerical instability), so its counts are 15 / 29 / 29 at D=2 / 10 / 30.

*FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. For each function it is the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, and the table values sum the per-function FBTC(B) values. Each budget is evaluated separately; FBTC(B) is not an anytime measure. Larger FBTC(B) values indicate greater fixed-budget target coverage.*

## By dimension — Unimodal and simple multimodal functions

Sum over all **Unimodal and simple multimodal** functions at each dimension; same suites, budgets, algorithm ordering, and descriptive bolding as the by-dimension table.

| D · nF | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **2 · 9** | Minimum | **0** | **0** | **0** | **0** | **0** | 3.58e-05 | **0** |
|  | Mean | 0.687 | 1.7 | 0.162 | 5.2 | **0.111** | 0.449 | 1.4 |
|  | Median | 8.51e-06 | 2.3 | **0** | 2.3 | **0** | 0.111 | 2.0 |
|  | FBTC(B) | 8.2 | 7.9 | 8.9 | 7.6 | **8.9** | 7.0 | 8.2 |
| **5 · 4** | Minimum | 0.125 | 1.1 | 0.613 | **0** | **0** | **0** | 0.613 |
|  | Mean | 25.1 | 18.7 | 14.3 | 14.9 | **3.0** | 9.2 | 5.6 |
|  | Median | 4.1 | 8.7 | 5.8 | 5.9 | **1.8** | 5.8 | 5.5 |
|  | FBTC(B) | 1.7 | 1.7 | 1.8 | 1.9 | **2.7** | 1.9 | 1.9 |
| **10 · 34** | Minimum | 31.0 | **7.7** | 17.6 | 21.5 | 28.2 | 18.6 | 26.9 |
|  | Mean | 168 | 235 | 255 | **85.4** | 274 | 238 | 202 |
|  | Median | 108 | 180 | 202 | **98.5** | 305 | 186 | 230 |
|  | FBTC(B) | 17.5 | 19.6 | 20.5 | **20.6** | 20.2 | 17.7 | 20.3 |
| **15 · 4** | Minimum | 1.2 | 0.125 | 15.9 | 16.3 | 15.6 | **0** | 15.8 |
|  | Mean | 11.2 | 24.8 | 18.8 | 50.8 | 19.2 | **8.8** | 62.0 |
|  | Median | **11.7** | 23.1 | 18.3 | 19.7 | 15.7 | 15.8 | 26.8 |
|  | FBTC(B) | 1.5 | **2.4** | 1.6 | 1.4 | 2.3 | 2.2 | 1.4 |
| **20 · 9** | Minimum | **3.4** | 6.2 | 21.7 | 66.2 | 50.2 | 7.3 | 67.6 |
|  | Mean | **16.2** | 34.9 | 24.4 | 69.9 | 110 | 44.9 | 76.0 |
|  | Median | **14.2** | 19.8 | 23.9 | 70.0 | 115 | 43.5 | 75.5 |
|  | FBTC(B) | 4.7 | **6.2** | 5.7 | 5.0 | 5.4 | 5.2 | 4.7 |
| **30 · 25** | Minimum | **103** | 489 | 2015 | 130 | 61308 | 1.14e+05 | 2019 |
|  | Mean | 942 | 2431 | 4038 | **878** | 3.73e+05 | 4.01e+05 | 3119 |
|  | Median | 748 | 2280 | 3912 | **704** | 2.3e+05 | 3.07e+05 | 3153 |
|  | FBTC(B) | 7.9 | 11.6 | 12.3 | 12.3 | 7.9 | 8.7 | **12.8** |

## By dimension — Hybrid functions

Sum over all **Hybrid** functions at each dimension; same suites, budgets, algorithm ordering, and descriptive bolding as the by-dimension table.

| D · nF | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **5 · 3** | Minimum | 5.5e-07 | **0** | **0** | **0** | **0** | **0** | **0** |
|  | Mean | 1.0 | 0.754 | 0.0122 | 5.6 | **0** | 0.0131 | 0.0489 |
|  | Median | 0.542 | 0.624 | **0** | **0** | **0** | **0** | **0** |
|  | FBTC(B) | 1.4 | 2.1 | 3.0 | 2.3 | **3.0** | 3.0 | 2.9 |
| **10 · 22** | Minimum | 7.6 | 2.9 | **0.0933** | 0.131 | 4.8 | 0.603 | 0.136 |
|  | Mean | 225 | 278 | 37.7 | 23.3 | 203 | 104 | **5.7** |
|  | Median | 238 | 252 | 11.0 | 7.5 | 159 | 64.9 | **4.8** |
|  | FBTC(B) | 5.0 | 4.9 | 9.4 | 8.0 | 8.5 | 7.9 | **10.5** |
| **15 · 3** | Minimum | 0.915 | 0.743 | **0.127** | 0.878 | 0.531 | 0.927 | 0.436 |
|  | Mean | 3.6 | 4.3 | **1.3** | 5.4 | 23.4 | 17.0 | 4.4 |
|  | Median | 3.3 | 1.8 | **1.2** | 2.0 | 15.7 | 10.5 | 4.2 |
|  | FBTC(B) | 0.642 | 0.737 | **0.798** | 0.668 | 0.632 | 0.562 | 0.646 |
| **20 · 6** | Minimum | 3.6 | 2.9 | **1.1** | 1.8 | 3.9 | 26.2 | 2.6 |
|  | Mean | 39.2 | 75.0 | 24.7 | **23.8** | 298 | 133 | 29.7 |
|  | Median | 52.9 | 61.3 | **23.8** | 23.8 | 202 | 106 | 30.5 |
|  | FBTC(B) | 0.965 | 0.868 | 1.3 | **1.4** | 0.741 | 0.853 | 1.2 |
| **30 · 16** | Minimum | 2263 | 1039 | 128 | **30.7** | 7621 | 14149 | 144 |
|  | Mean | 4642 | 3699 | 861 | **165** | 54096 | 52340 | 590 |
|  | Median | 4572 | 3484 | 771 | **108** | 36972 | 37130 | 532 |
|  | FBTC(B) | 0.563 | 0.579 | 1.8 | **3.5** | 0.671 | 0.435 | 1.7 |

## By dimension — Composition functions

Sum over all **Composition** functions at each dimension; same suites, budgets, algorithm ordering, and descriptive bolding as the by-dimension table.

| D · nF | Metric | MSC-CMA-ES | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **2 · 6** | Minimum | 3.64e-08 | **0** | **0** | **0** | **0** | **0** | **0** |
|  | Mean | **1.87e-06** | 89.9 | 0.734 | 236 | 7.8 | 5.2 | 134 |
|  | Median | 7.64e-07 | 0.444 | **0** | 200 | **0** | 1.2 | 100 |
|  | FBTC(B) | 5.8 | 4.9 | **6.0** | 3.9 | 5.9 | 3.6 | 4.7 |
| **5 · 3** | Minimum | **0** | 100 | **0** | 400 | **0** | **0** | 400 |
|  | Mean | **48.6** | 372 | 145 | 462 | 224 | 180 | 446 |
|  | Median | **0** | 447 | 100 | 447 | 300 | 100 | 447 |
|  | FBTC(B) | **2.4** | 0.919 | 1.9 | 0.831 | 2.1 | 1.3 | 1.0 |
| **10 · 25** | Minimum | **2088** | 3443 | 2464 | 5070 | 2381 | 3398 | 5272 |
|  | Mean | **4010** | 5754 | 4407 | 38264 | 4742 | 5066 | 5741 |
|  | Median | **4369** | 5890 | 4721 | 6283 | 4836 | 5086 | 5829 |
|  | FBTC(B) | **4.9** | 1.6 | 2.5 | 1.3 | 4.8 | 2.7 | 1.2 |
| **15 · 3** | Minimum | **100** | 200 | 200 | 800 | 500 | 200 | 600 |
|  | Mean | **266** | 609 | 388 | 882 | 521 | 531 | 840 |
|  | Median | **200** | 600 | 335 | 886 | 500 | 500 | 853 |
|  | FBTC(B) | **0.915** | 0.158 | 0.116 | 0.0111 | 0.551 | 0.738 | 0.00615 |
| **20 · 7** | Minimum | 821 | 926 | **548** | 1326 | 1157 | 1197 | 1690 |
|  | Mean | **968** | 1256 | 1090 | 1718 | 1312 | 1569 | 1722 |
|  | Median | **975** | 1165 | 1094 | 1705 | 1318 | 1626 | 1719 |
|  | FBTC(B) | **1.4** | 0.854 | 0.991 | 0.0265 | 0.973 | 0.448 | 0 |
| **30 · 18** | Minimum | 7947 | 7596 | 7759 | **7095** | 7983 | 10252 | 7153 |
|  | Mean | 9676 | 10701 | 8804 | **7588** | 10943 | 14786 | 8070 |
|  | Median | 9618 | 10398 | 8543 | **7583** | 10810 | 14147 | 8076 |
|  | FBTC(B) | 0 | 0 | 0 | 0 | **0.0073** | 0 | 0 |

Per-dimension breakdowns by function class also live in each `<suite>/d<dim>/README.md`.

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
