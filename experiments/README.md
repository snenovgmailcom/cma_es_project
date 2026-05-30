# Cross-suite summary — by dimension

Per-function metrics summed across **all CEC suites at each dimension**: a cell is the sum over every function at that dimension (across suites) for one algorithm. CMA family first (MSC-CMA, BIPOP-CMA), then DE family. **Bold** = best in that row (min for best/mean/median, max for FBTC; ties bolded together).

| D · nF | Metric | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **2 · 31** | best | 5.67e-8 | **0** |   | **0** | 0.620 | **0** | 4.54e-5 | **0** |
|  | mean | **1.40** | 178 |   | 1.79 | 511 | 13.9 | 9.01 | 310 |
|  | median | 1.84e-5 | 21.6 |   | **0** | 405 | **0** | 2.60 | 304 |
|  | FBTC | 28.9 | 26.0 |   | 30.7 | 23.5 | **30.7** | 22.1 | 26.4 |
| **5 · 10** | best | 0.120 | 101 |   | 0.610 | 400 | **0** | **0** | 401 |
|  | mean | **74.8** | 391 |   | 159 | 482 | 227 | 189 | 452 |
|  | median | **4.68** | 457 |   | 106 | 453 | 302 | 106 | 453 |
|  | FBTC | 5.49 | 4.72 |   | 6.73 | 5.07 | **7.83** | 6.15 | 5.84 |
| **10 · 81** | best | **2126** | 3454 |   | 2481 | 5092 | 2414 | 3417 | 5300 |
|  | mean | **4403** | 6266 |   | 4700 | 3.84e4 | 5220 | 5409 | 5948 |
|  | median | **4715** | 6322 |   | 4934 | 6389 | 5300 | 5337 | 6064 |
|  | FBTC | 27.4 | 26.1 |   | 32.4 | 29.9 | **33.5** | 28.3 | 32.0 |
| **15 · 10** | best | **102** | 201 |   | 216 | 817 | 516 | 201 | 616 |
|  | mean | **281** | 638 |   | 408 | 938 | 563 | 557 | 907 |
|  | median | **215** | 625 |   | 354 | 908 | 531 | 526 | 884 |
|  | FBTC | 3.09 | 3.33 |   | 2.47 | 2.12 | 3.46 | **3.52** | 2.10 |
| **20 · 12** | best | 423 | 427 |   | **419** | 558 | 745 | 711 | 860 |
|  | mean | **467** | 601 |   | 550 | 910 | 954 | 783 | 891 |
|  | median | **478** | 506 |   | 538 | 881 | 881 | 774 | 888 |
|  | FBTC | 4.79 | 5.02 |   | **5.66** | 4.30 | 4.20 | 3.98 | 3.67 |
| **30 · 59** | best | 1.03e4 | 9124 |   | 9903 | **7256** | 7.69e4 | 1.38e5 | 9316 |
|  | mean | 1.53e4 | 1.68e4 |   | 1.37e4 | **8631** | 4.39e5 | 4.68e5 | 1.18e4 |
|  | median | 1.49e4 | 1.62e4 |   | 1.32e4 | **8395** | 2.78e5 | 3.58e5 | 1.18e4 |
|  | FBTC | 8.46 | 12.2 |   | 14.1 | **15.8** | 8.55 | 9.17 | 14.5 |

**Composition of each dimension** (suite → nF, budget):
- **D=2** (31): cec2017 (15) · cec2020 (7) · cec2022 (9) — all 20 000.
- **D=5** (10): cec2020 — 50 000.
- **D=10** (81): cec2014 (30, 100K) · cec2017 (29, 100K) · cec2020 (10, 1M) · cec2022 (12, 200K).
- **D=15** (10): cec2020 — 3 000 000.
- **D=20** (12): cec2022 — 1 000 000.
- **D=30** (59): cec2014 (30) · cec2017 (29) — both 300 000.

CEC2017 excludes F2 uniformly (numerical instability), so its counts are 15 / 29 / 29 at D=2 / 10 / 30. Per-dimension breakdowns by function class live in each `<suite>/d<dim>/README.md`.

*FBTC = Fixed-Budget Target Coverage (mean per-target success rate over 51 log-uniform targets in [10²…10⁻⁸]); range [0, nF]. Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
