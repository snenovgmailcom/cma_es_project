# Deep Statistical Comparison — summary

This page summarizes the Deep Statistical Comparison (DSC) results for
the 17 suite–dimension–budget settings used in the study. Detailed
per-function DSC ranks and statistical comparisons are linked from the
table below.

DSC is applied to the 51 run-wise terminal errors for each function using
Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`,
`monte_carlo_iterations=0`). The resulting per-function ranks are
analyzed with the Friedman omnibus test. When the omnibus null
hypothesis is rejected, Holm-adjusted post-hoc comparisons are
performed against the algorithm with the lowest mean DSC rank.

## Overall summary

**All functions.** MSC-CMA-ES has the lowest mean DSC rank in **0/17** settings. The Friedman test rejects the null hypothesis in **11/17** settings. Among these, the Holm-adjusted comparison with MSC-CMA-ES is significant in **7** settings and not significant in **4** settings. In the remaining **6/17** settings, the Friedman test does not reject the null hypothesis.

**Composition functions.** MSC-CMA-ES has the lowest mean DSC rank in **8/17** settings. The Friedman test rejects the null hypothesis in **12/17** settings. MSC-CMA-ES has the lowest mean DSC rank in **5** of these rejected settings. In **6** other rejected settings, the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant. The only significant Holm-adjusted comparison occurs for **CEC2017, D=30, B=3×10^5**, where the lowest-mean-rank algorithm is **L-SRTDE** (`p_Holm = 0.0345571`). In the remaining **5/17** settings, the Friedman test does not reject the null hypothesis.

### Symbols

- **★** — MSC-CMA-ES has the lowest mean DSC rank and the Friedman test rejects the null hypothesis.
- **≈** — the Friedman test rejects the null hypothesis, but the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant.
- **↓** — the lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES and the Holm-adjusted comparison is significant.
- **O** — the Friedman test does not reject the null hypothesis; no post-hoc interpretation is made.

`p_Holm` is shown only when the lowest-mean-rank algorithm is not MSC-CMA-ES and the Friedman test rejects the null hypothesis.

## All 17 settings

| Suite | D | Budget | All: lowest-mean-rank algorithm | MSC position | Friedman p | p_Holm | Result | Composition: lowest-mean-rank algorithm | MSC position | Friedman p | p_Holm | Result |
|:--|--:|--:|:--|:--:|--:|--:|:--:|:--|:--:|--:|--:|:--:|
| CEC2014 | 10 | [10^5](../mwu/cec2014/d10/README.md#dsc-budget-100k) | jSO | 5/7 | 0.000182671 | 0.00576245 | **↓** | ARRDE | 2/7 | 0.0412975 | 0.476929 | **≈** |
| CEC2014 | 10 | [10^6](../mwu/cec2014/d10/README.md#dsc-budget-1m) | ARRDE | 5/7 | 0.000132423 | 0.000844015 | **↓** | ARRDE | 2/7 | 0.000302263 | 0.342722 | **≈** |
| CEC2014 | 30 | [3×10^5](../mwu/cec2014/d30/README.md#dsc-budget-300k) | L-SRTDE | 5/7 | 3.69553e-11 | 9.65698e-05 | **↓** | L-SRTDE | 4.5/7 | 0.000257483 | 0.0645547 | **≈** |
| CEC2014 | 30 | [10^6](../mwu/cec2014/d30/README.md#dsc-budget-1m) | L-SRTDE | 5/7 | 7.59038e-11 | 0.00163595 | **↓** | L-SRTDE | 5/7 | 0.00120862 | 0.32983 | **≈** |
| CEC2017 | 10 | [10^5](../mwu/cec2017/d10/README.md#dsc-budget-100k) | ARRDE | 5/7 | 0.430681 | — | **O** | MSC-CMA-ES | 1/7 | 6.1599e-05 | — | **★** |
| CEC2017 | 10 | [10^6](../mwu/cec2017/d10/README.md#dsc-budget-1m) | NL-SHADE-RSP | 4.5/7 | 0.000104547 | 0.023305 | **↓** | MSC-CMA-ES | 1/7 | 0.000130799 | — | **★** |
| CEC2017 | 30 | [3×10^5](../mwu/cec2017/d30/README.md#dsc-budget-300k) | L-SRTDE | 5/7 | 4.32876e-13 | 2.77299e-05 | **↓** | L-SRTDE | 5/7 | 0.000414182 | 0.0345571 | **↓** |
| CEC2017 | 30 | [10^6](../mwu/cec2017/d30/README.md#dsc-budget-1m) | L-SRTDE | 4/7 | 3.252e-11 | 0.00852195 | **↓** | L-SRTDE | 3/7 | 0.0332618 | 0.641363 | **≈** |
| CEC2020 | 5 | [5×10^4](../mwu/cec2020/d5/README.md#dsc-budget-50k) | NL-SHADE-RSP | 5/7 | 0.000710485 | 0.0676836 | **≈** | MSC-CMA-ES | 1/7 | 0.0799374 | — | **O** |
| CEC2020 | 5 | [10^6](../mwu/cec2020/d5/README.md#dsc-budget-1m) | j2020 | 5/7 | 0.0144811 | 0.405746 | **≈** | MSC-CMA-ES | 1/7 | 0.0988332 | — | **O** |
| CEC2020 | 10 | [10^6](../mwu/cec2020/d10/README.md#dsc-budget-1m) | j2020 | 3/7 | 0.00752491 | 0.703075 | **≈** | MSC-CMA-ES | 1/7 | 0.0121289 | — | **★** |
| CEC2020 | 10 | [2×10^7](../mwu/cec2020/d10/README.md#dsc-budget-20m) | ARRDE | 4/7 | 0.000356322 | 0.073829 | **≈** | MSC-CMA-ES | 1/7 | 0.0377023 | — | **★** |
| CEC2020 | 15 | [3×10^6](../mwu/cec2020/d15/README.md#dsc-budget-3m) | ARRDE | 3/7 | 0.082492 | — | **O** | MSC-CMA-ES | 1/7 | 0.0292397 | — | **★** |
| CEC2020 | 20 | [10^7](../mwu/cec2020/d20/README.md#dsc-budget-10m) | ARRDE | 4/7 | 0.109454 | — | **O** | ARRDE | 3/7 | 0.0397565 | 0.508332 | **≈** |
| CEC2022 | 10 | [2×10^5](../mwu/cec2022/d10/README.md#dsc-budget-200k) | ARRDE | 6/7 | 0.0894865 | — | **O** | NL-SHADE-RSP | 4/7 | 0.241392 | — | **O** |
| CEC2022 | 10 | [10^6](../mwu/cec2022/d10/README.md#dsc-budget-1m) | ARRDE | 5/7 | 0.111072 | — | **O** | j2020 | 4/7 | 0.206022 | — | **O** |
| CEC2022 | 20 | [10^6](../mwu/cec2022/d20/README.md#dsc-budget-1m) | L-SRTDE | 4/7 | 0.167155 | — | **O** | MSC-CMA-ES | 1/7 | 0.950107 | — | **O** |

## Function subsets

- **CEC2014:** All: `f1–f30`; Composition: `f23–f30`.
- **CEC2017:** All: `f1, f3–f30`; Composition: `f21–f30`.
- **CEC2020:** All: `f1–f10`; Composition: `f8–f10`.
- **CEC2022:** All: `f1–f12`; Composition: `f9–f12`.

All settings compare the same seven algorithms:
MSC-CMA-ES, BIPOP-CMA-ES, ARRDE, L-SRTDE, NL-SHADE-RSP, j2020, jSO.

The numerical source for this page is [`dsc_results_final_table.csv`](dsc_results_final_table.csv). The detailed per-scope values are stored in [`dsc_results_final_long.csv`](dsc_results_final_long.csv).
