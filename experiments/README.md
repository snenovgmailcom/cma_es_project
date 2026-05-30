# CEC benchmarks — cross-suite summary by dimension

SUM of per-function metrics, aggregated **across all suites** at each dimension. `nF` = total functions summed at that D (suites present). cec2017 has **F2 excluded** at every dimension. Budgets per suite-cell: cec2014 100K (D10)/300K (D30); cec2017 20K (D2)/100K (D10)/300K (D30); cec2020 50K (D5)/1M (D10)/3M (D15)/10M (D20); cec2022 200K (D10)/1M (D20).

Each cell packs four metrics in a 2×2: best · mean / median · FBTC

**Bold** = best algorithm in that row for that metric (min for best/mean/median; max for FBTC). Ties bolded together.

| D · nF | MSC-CMA | BIPOP-CMA |   | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|:--|:-:|:--|:--|:--|:--|:--|
| **2** · 15 | 3.64e-8 · **0.690**<br>9.28e-6 · 14.0 | **0** · 91.6<br>2.77 · 12.7 |   | **0** · 0.900<br>**0** · 14.8 | **0** · 241<br>202 · 11.4 | **0** · 7.95<br>**0** · **14.8** | 3.58e-5 · 5.64<br>1.29 · 10.6 | **0** · 135<br>102 · 12.9 |
| **5** · 10 | 0.120 · **74.8**<br>**4.68** · 5.49 | 101 · 391<br>457 · 4.72 |   | 0.610 · 159<br>106 · 6.73 | 400 · 482<br>453 · 5.07 | **0** · 227<br>302 · **7.83** | **0** · 189<br>106 · 6.15 | 401 · 452<br>453 · 5.84 |
| **10** · 81 | **2126** · **4403**<br>**4715** · 27.4 | 3454 · 6266<br>6322 · 26.1 |   | 2481 · 4700<br>4934 · 32.4 | 5092 · 3.84e4<br>6389 · 29.9 | 2414 · 5220<br>5300 · **33.5** | 3417 · 5409<br>5337 · 28.3 | 5300 · 5948<br>6064 · 32.0 |
| **15** · 10 | **102** · **281**<br>**215** · 3.09 | 201 · 638<br>625 · 3.33 |   | 216 · 408<br>354 · 2.47 | 817 · 938<br>908 · 2.12 | 516 · 563<br>531 · 3.46 | 201 · 557<br>526 · **3.52** | 616 · 907<br>884 · 2.10 |
| **20** · 12 | 423 · **467**<br>**478** · 4.79 | 427 · 601<br>506 · 5.02 |   | **419** · 550<br>538 · **5.66** | 558 · 910<br>881 · 4.30 | 745 · 954<br>881 · 4.20 | 711 · 783<br>774 · 3.98 | 860 · 891<br>888 · 3.67 |
| **30** · 59 | 1.03e4 · 1.53e4<br>1.49e4 · 8.46 | 9124 · 1.68e4<br>1.62e4 · 12.2 |   | 9903 · 1.37e4<br>1.32e4 · 14.1 | **7256** · **8631**<br>**8395** · **15.8** | 7.69e4 · 4.39e5<br>2.78e5 · 8.55 | 1.38e5 · 4.68e5<br>3.58e5 · 9.17 | 9316 · 1.18e4<br>1.18e4 · 14.5 |

*FBTC = Fixed-Budget Target Coverage (mean per-target success rate over 51 log-uniform targets in [10²…10⁻⁸]; range [0, nF]). Higher is better.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.