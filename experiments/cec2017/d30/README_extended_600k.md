# CEC2017 / D=30 — extended-budget summary (2× CEC budget)

Supplementary view at **600,000 evaluations** (2× the standard CEC budget of D × 10⁴ = 300k). The canonical CEC2017/D=30 ranking is in [README.md](README.md) — that is the budget suitable for direct comparison with published literature. This extended view shows how the relative ordering evolves once budget-constrained algorithms have time to converge.

**Methodological note.** Columns 1–2 are the CMA-ES family: MSC-CMA and its parent BIPOP-CMA-pycma. The primary comparison is MSC-CMA vs its parent — i.e., does the proposed modification improve the underlying CMA-ES design. Columns 3–7 are state-of-the-art DE-family algorithms, included as reference baselines representing the current frontier of evolutionary numerical optimization, not as direct methodological competitors.

F2 excluded per CEC2017 convention (29 functions: F1, F3–F30). Each metric is summed over the functions of the category; the SUM block sums across all 29 functions. **Bold** = best in row across all 7 algorithms. All metrics: lower is better, except FBTC (higher is better).

| Category | Metric | MSC-CMA | BIPOP-CMA | ‖ | ARRDE | LSRTDE | NLSHADE | j2020 | jSO |
|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| **Basic** (n=9) | mean | 227 | 511 | ‖ | 1488 | **221** | 1966 | 3192 | 1553 |
| | median | **218.7** | 552 | ‖ | 1516 | 218.8 | 1888 | 3181 | 1582 |
| | best | **19.7** | 24.6 | ‖ | 703 | 94.1 | 1389 | 2260 | 885 |
| | worst | 813 | 1368 | ‖ | 2107 | **714** | 5543 | 4219 | 1982 |
| | std | 181 | 294 | ‖ | 334 | **119** | 652 | 394 | 240 |
| | FBTC | 3.326 | **4.808** | ‖ | 4.691 | 4.763 | 3.317 | 3.570 | 4.332 |
| **Hybrid** (n=10) | mean | 1531 | 1129 | ‖ | 434 | **51.6** | 1.88e+04 | 3626 | 305 |
| | median | 1532 | 1008 | ‖ | 395 | **59.3** | 1.56e+04 | 3293 | 371 |
| | best | 400 | 360 | ‖ | 26.5 | **2.35** | 4136 | 1340 | 40.7 |
| | worst | 3227 | 2929 | ‖ | 1125 | **211** | 8.37e+04 | 9256 | 774 |
| | std | 694 | 563 | ‖ | 240 | **48.5** | 1.42e+04 | 1686 | 200 |
| | FBTC | 0.682 | 0.676 | ‖ | 1.417 | **3.475** | 0.464 | 0.362 | 1.225 |
| **Composition** (n=10) | mean | 5129 | 5369 | ‖ | **4962** | 5124 | 6085 | 6692 | 5514 |
| | median | 5123 | 5175 | ‖ | **4860** | 5166 | 5944 | 6718 | 5533 |
| | best | 4410 | **4165** | ‖ | 4777 | 4825 | 4457 | 5079 | 4740 |
| | worst | 5846 | 9489 | ‖ | 5831 | **5436** | 1.67e+04 | 7944 | 5773 |
| | std | 309 | 1014 | ‖ | 262 | 173 | 1856 | 614 | **154** |
| | FBTC | 0.000 | 0.000 | ‖ | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| **SUM** (n=29) | mean | 6886 | 7009 | ‖ | 6884 | **5396** | 2.68e+04 | 1.35e+04 | 7372 |
| | median | 6874 | 6736 | ‖ | 6770 | **5444** | 2.34e+04 | 1.32e+04 | 7486 |
| | best | 4830 | **4549** | ‖ | 5506 | 4922 | 9982 | 8679 | 5666 |
| | worst | 9886 | 1.38e+04 | ‖ | 9064 | **6361** | 1.06e+05 | 2.14e+04 | 8529 |
| | std | 1185 | 1871 | ‖ | 836 | **341** | 1.68e+04 | 2694 | 593 |
| | FBTC | 4.008 | 5.484 | ‖ | 6.107 | **8.238** | 3.781 | 3.932 | 5.556 |

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF.*
