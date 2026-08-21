# Deep Statistical Comparison — summary

This page summarizes the Deep Statistical Comparison (DSC) results for the 17
suite–dimension–budget settings used in the study. The detailed per-function
DSC ranks and the corresponding statistical comparisons are available through
the budget links in the table.

DSC is applied to the 51 run-wise terminal errors for each function using
Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`,
`monte_carlo_iterations=0`). The resulting per-function ranks are analyzed with
the Friedman omnibus test. When the omnibus null hypothesis is rejected,
Holm-adjusted post-hoc comparisons are performed against the algorithm with the
best mean DSC rank.

## Overall summary

**All functions.** MSC-CMA-ES has the best mean DSC rank in **0/17** settings.
The Friedman test rejects the null hypothesis in **11/17** settings. Among
these 11 settings, the Holm-adjusted post-hoc comparison between the
best-ranked algorithm and MSC-CMA-ES is significant in **7** settings and is
not significant in **4** settings. In the remaining **6/17** settings, the
Friedman test does not reject the null hypothesis.

**Composition functions.** MSC-CMA-ES has the best mean DSC rank in **8/17**
settings. The Friedman test rejects the null hypothesis in **12/17** settings.
MSC-CMA-ES is the best-ranked algorithm in **5** of these 12 settings. In **6**
other settings, the Holm-adjusted post-hoc comparison between the best-ranked
algorithm and MSC-CMA-ES is not significant. The only significant
Holm-adjusted comparison with MSC-CMA-ES occurs for **CEC2017, D=30,
B=300,000**, where the best-ranked algorithm is **LSRTDE**
(`p_Holm = 0.034557`). In the remaining **5/17** settings, the Friedman test
does not reject the null hypothesis.

### Symbols

- **★** — MSC-CMA-ES has the best mean DSC rank and the Friedman test rejects the null hypothesis.
- **≈** — the Friedman test rejects the null hypothesis, but the Holm-adjusted comparison between MSC-CMA-ES and the best-ranked algorithm is not significant.
- **↓** — the Friedman test rejects the null hypothesis and the Holm-adjusted comparison between MSC-CMA-ES and the best-ranked algorithm is significant.
- **O** — the Friedman test does not reject the null hypothesis; no post-hoc interpretation is made.

`p_Holm` is shown only when the best-ranked algorithm is not MSC-CMA-ES and
the Friedman test rejects the null hypothesis.

## All 17 settings

| Suite | D | Budget | All: best rank | MSC pos. | Friedman p | p_Holm | Result | Composition: best rank | MSC pos. | Friedman p | p_Holm | Result |
|:--|--:|--:|:--|:--:|--:|--:|:--:|:--|:--:|--:|--:|:--:|
| CEC2014 | 10 | [100K](../mwu/cec2014/d10/README.md#dsc-budget-100k) | jSO | 5/7 | 0.000183 | 0.005762 | **↓** | ARRDE | 2/7 | 0.041297 | 0.476929 | **≈** |
| CEC2014 | 10 | [1M](../mwu/cec2014/d10/README.md#dsc-budget-1m) | ARRDE | 5/7 | 0.000132 | 0.000844 | **↓** | ARRDE | 2/7 | 0.000302 | 0.342722 | **≈** |
| CEC2014 | 30 | [300K](../mwu/cec2014/d30/README.md#dsc-budget-300k) | LSRTDE | 5/7 | 3.696e-11 | 9.657e-05 | **↓** | LSRTDE | 4.5/7 | 0.000257 | 0.064555 | **≈** |
| CEC2014 | 30 | [1M](../mwu/cec2014/d30/README.md#dsc-budget-1m) | LSRTDE | 5/7 | 7.590e-11 | 0.001636 | **↓** | LSRTDE | 5/7 | 0.001209 | 0.32983 | **≈** |
| CEC2017 | 10 | [100K](../mwu/cec2017/d10/README.md#dsc-budget-100k) | ARRDE | 5/7 | 0.430681 | — | **O** | MSC-CMA | 1/7 | 6.160e-05 | — | **★** |
| CEC2017 | 10 | [1M](../mwu/cec2017/d10/README.md#dsc-budget-1m) | NLSHADE-RSP | 4.5/7 | 0.000105 | 0.023305 | **↓** | MSC-CMA | 1/7 | 0.000131 | — | **★** |
| CEC2017 | 30 | [300K](../mwu/cec2017/d30/README.md#dsc-budget-300k) | LSRTDE | 5/7 | 4.329e-13 | 2.773e-05 | **↓** | LSRTDE | 5/7 | 0.000414 | 0.034557 | **↓** |
| CEC2017 | 30 | [1M](../mwu/cec2017/d30/README.md#dsc-budget-1m) | LSRTDE | 4/7 | 3.252e-11 | 0.008522 | **↓** | LSRTDE | 3/7 | 0.033262 | 0.641363 | **≈** |
| CEC2020 | 5 | [50K](../mwu/cec2020/d5/README.md#dsc-budget-50k) | NLSHADE-RSP | 5/7 | 0.00071 | 0.067684 | **≈** | MSC-CMA | 1/7 | 0.079937 | — | **O** |
| CEC2020 | 5 | [1M](../mwu/cec2020/d5/README.md#dsc-budget-1m) | j2020 | 5/7 | 0.014481 | 0.405746 | **≈** | MSC-CMA | 1/7 | 0.098833 | — | **O** |
| CEC2020 | 10 | [1M](../mwu/cec2020/d10/README.md#dsc-budget-1m) | j2020 | 3/7 | 0.007525 | 0.703075 | **≈** | MSC-CMA | 1/7 | 0.012129 | — | **★** |
| CEC2020 | 10 | [20M](../mwu/cec2020/d10/README.md#dsc-budget-20m) | ARRDE | 4/7 | 0.000356 | 0.073829 | **≈** | MSC-CMA | 1/7 | 0.037702 | — | **★** |
| CEC2020 | 15 | [3M](../mwu/cec2020/d15/README.md#dsc-budget-3m) | ARRDE | 3/7 | 0.082492 | — | **O** | MSC-CMA | 1/7 | 0.02924 | — | **★** |
| CEC2020 | 20 | [10M](../mwu/cec2020/d20/README.md#dsc-budget-10m) | ARRDE | 4/7 | 0.109454 | — | **O** | ARRDE | 3/7 | 0.039757 | 0.508332 | **≈** |
| CEC2022 | 10 | [200K](../mwu/cec2022/d10/README.md#dsc-budget-200k) | ARRDE | 6/7 | 0.089487 | — | **O** | NLSHADE-RSP | 4/7 | 0.241392 | — | **O** |
| CEC2022 | 10 | [1M](../mwu/cec2022/d10/README.md#dsc-budget-1m) | ARRDE | 5/7 | 0.111072 | — | **O** | j2020 | 4/7 | 0.206022 | — | **O** |
| CEC2022 | 20 | [1M](../mwu/cec2022/d20/README.md#dsc-budget-1m) | LSRTDE | 4/7 | 0.167155 | — | **O** | MSC-CMA | 1/7 | 0.950107 | — | **O** |

## Function subsets

- **CEC2014:** all functions `f1–f30`; composition functions `f23–f30`.
- **CEC2017:** all functions `f1, f3–f30`; composition functions `f21–f30`.
- **CEC2020:** all functions `f1–f10`; composition functions `f8–f10`.
- **CEC2022:** all functions `f1–f12`; composition functions `f9–f12`.

All settings compare the same seven algorithms:
`MSC-CMA`, `BIPOP-CMA`, `ARRDE`, `LSRTDE`, `NLSHADE-RSP`, `j2020`, and `jSO`.
