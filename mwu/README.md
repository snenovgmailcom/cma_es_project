# Mann–Whitney U comparisons with MSC-CMA-ES

Fixed-budget comparisons with BIPOP-CMA-ES, ARRDE, L-SRTDE,
NL-SHADE-RSP, j2020, and jSO.

Contents: [All functions](#all) · [Composition functions](#composition) · [Method and symbols](#method-and-symbols)

**17 suite/dimension/budget settings**. Each table cell contains $n_{<}/n_{>}/n_{=}$: counts of functions for which
the MWU symbol is `<`, `>`, or `=`, respectively. See the definitions below.

Each setting links to the per-function p_Holm table. U and raw p-values
are available in expandable sections on those pages.

<a id="all"></a>

## All functions

| Suite | D | Budget | Functions | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| CEC2014 | 10 | [10^5](cec2014/d10/README.md#budget-100k-all) | 30 | 11/12/7 | 5/22/3 | 4/20/6 | 9/15/6 | 14/11/5 | 5/21/4 |
| CEC2014 | 10 | [10^6](cec2014/d10/README.md#budget-1m-all) | 30 | 11/12/7 | 2/23/5 | 9/12/9 | 4/14/12 | 8/13/9 | 7/16/7 |
| CEC2014 | 30 | [3×10^5](cec2014/d30/README.md#budget-300k-all) | 30 | 8/19/3 | 6/22/2 | 3/23/4 | 16/13/1 | 20/8/2 | 5/22/3 |
| CEC2014 | 30 | [10^6](cec2014/d30/README.md#budget-1m-all) | 30 | 7/17/6 | 5/23/2 | 4/24/2 | 17/10/3 | 20/6/4 | 5/21/4 |
| CEC2017 | 10 | [10^5](cec2017/d10/README.md#budget-100k-all) | 29 | 6/11/12 | 7/16/6 | 8/19/2 | 9/14/6 | 11/9/9 | 8/18/3 |
| CEC2017 | 10 | [10^6](cec2017/d10/README.md#budget-1m-all) | 29 | 8/14/7 | 3/21/5 | 11/13/5 | 6/17/6 | 9/15/5 | 12/14/3 |
| CEC2017 | 30 | [3×10^5](cec2017/d30/README.md#budget-300k-all) | 29 | 9/15/5 | 9/20/0 | 2/25/2 | 16/7/6 | 20/8/1 | 8/20/1 |
| CEC2017 | 30 | [10^6](cec2017/d30/README.md#budget-1m-all) | 29 | 10/11/8 | 6/18/5 | 3/23/3 | 17/7/5 | 24/4/1 | 8/17/4 |
| CEC2020 | 5 | [5×10^4](cec2020/d5/README.md#budget-50k-all) | 10 | 3/5/2 | 2/8/0 | 3/6/1 | 1/8/1 | 3/5/2 | 3/7/0 |
| CEC2020 | 5 | [10^6](cec2020/d5/README.md#budget-1m-all) | 10 | 3/5/2 | 0/9/1 | 4/4/2 | 1/8/1 | 1/8/1 | 3/6/1 |
| CEC2020 | 10 | [10^6](cec2020/d10/README.md#budget-1m-all) | 10 | 4/5/1 | 3/6/1 | 4/4/2 | 2/4/4 | 3/4/3 | 5/4/1 |
| CEC2020 | 10 | [2×10^7](cec2020/d10/README.md#budget-20m-all) | 10 | 5/3/2 | 1/7/2 | 6/2/2 | 2/5/3 | 2/7/1 | 5/4/1 |
| CEC2020 | 15 | [3×10^6](cec2020/d15/README.md#budget-3m-all) | 10 | 3/7/0 | 2/6/2 | 4/3/3 | 3/5/2 | 2/5/3 | 5/3/2 |
| CEC2020 | 20 | [10^7](cec2020/d20/README.md#budget-10m-all) | 10 | 4/5/1 | 2/8/0 | 4/6/0 | 4/6/0 | 4/6/0 | 5/5/0 |
| CEC2022 | 10 | [2×10^5](cec2022/d10/README.md#budget-200k-all) | 12 | 2/4/6 | 2/7/3 | 2/6/4 | 4/8/0 | 5/7/0 | 3/8/1 |
| CEC2022 | 10 | [10^6](cec2022/d10/README.md#budget-1m-all) | 12 | 4/4/4 | 1/8/3 | 5/5/2 | 2/8/2 | 2/7/3 | 4/6/2 |
| CEC2022 | 20 | [10^6](cec2022/d20/README.md#budget-1m-all) | 12 | 5/4/3 | 3/7/2 | 3/6/3 | 5/3/4 | 7/2/3 | 4/7/1 |

<a id="composition"></a>

## Composition functions

| Suite | D | Budget | Functions | BIPOP-CMA-ES | ARRDE | L-SRTDE | NL-SHADE-RSP | j2020 | jSO |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| CEC2014 | 10 | [10^5](cec2014/d10/README.md#budget-100k-composition) | 8 | 6/1/1 | 0/5/3 | 2/3/3 | 3/3/2 | 6/1/1 | 1/4/3 |
| CEC2014 | 10 | [10^6](cec2014/d10/README.md#budget-1m-composition) | 8 | 6/1/1 | 0/8/0 | 5/2/1 | 2/1/5 | 3/1/4 | 4/2/2 |
| CEC2014 | 30 | [3×10^5](cec2014/d30/README.md#budget-300k-composition) | 8 | 3/4/1 | 2/5/1 | 0/6/2 | 6/2/0 | 7/0/1 | 1/5/2 |
| CEC2014 | 30 | [10^6](cec2014/d30/README.md#budget-1m-composition) | 8 | 3/4/1 | 1/5/2 | 2/5/1 | 6/1/1 | 7/0/1 | 2/5/1 |
| CEC2017 | 10 | [10^5](cec2017/d10/README.md#budget-100k-composition) | 10 | 5/1/4 | 3/4/3 | 5/3/2 | 6/4/0 | 5/0/5 | 6/3/1 |
| CEC2017 | 10 | [10^6](cec2017/d10/README.md#budget-1m-composition) | 10 | 7/3/0 | 2/6/2 | 7/1/2 | 4/3/3 | 4/3/3 | 8/1/1 |
| CEC2017 | 30 | [3×10^5](cec2017/d30/README.md#budget-300k-composition) | 10 | 5/4/1 | 2/8/0 | 1/9/0 | 4/1/5 | 9/1/0 | 2/8/0 |
| CEC2017 | 30 | [10^6](cec2017/d30/README.md#budget-1m-composition) | 10 | 4/3/3 | 0/6/4 | 2/7/1 | 4/4/2 | 8/2/0 | 4/6/0 |
| CEC2020 | 5 | [5×10^4](cec2020/d5/README.md#budget-50k-composition) | 3 | 2/1/0 | 1/2/0 | 2/1/0 | 1/2/0 | 2/0/1 | 2/1/0 |
| CEC2020 | 5 | [10^6](cec2020/d5/README.md#budget-1m-composition) | 3 | 1/1/1 | 0/3/0 | 2/1/0 | 1/2/0 | 1/2/0 | 2/1/0 |
| CEC2020 | 10 | [10^6](cec2020/d10/README.md#budget-1m-composition) | 3 | 3/0/0 | 2/1/0 | 3/0/0 | 1/0/2 | 2/0/1 | 3/0/0 |
| CEC2020 | 10 | [2×10^7](cec2020/d10/README.md#budget-20m-composition) | 3 | 2/0/1 | 1/2/0 | 3/0/0 | 2/1/0 | 2/1/0 | 3/0/0 |
| CEC2020 | 15 | [3×10^6](cec2020/d15/README.md#budget-3m-composition) | 3 | 2/1/0 | 2/1/0 | 3/0/0 | 1/1/1 | 1/2/0 | 3/0/0 |
| CEC2020 | 20 | [10^7](cec2020/d20/README.md#budget-10m-composition) | 3 | 3/0/0 | 1/2/0 | 3/0/0 | 1/2/0 | 2/1/0 | 3/0/0 |
| CEC2022 | 10 | [2×10^5](cec2022/d10/README.md#budget-200k-composition) | 4 | 2/1/1 | 0/2/2 | 2/1/1 | 2/2/0 | 1/3/0 | 2/1/1 |
| CEC2022 | 10 | [10^6](cec2022/d10/README.md#budget-1m-composition) | 4 | 3/1/0 | 0/3/1 | 3/1/0 | 1/3/0 | 0/3/1 | 3/1/0 |
| CEC2022 | 20 | [10^6](cec2022/d20/README.md#budget-1m-composition) | 4 | 1/1/2 | 2/2/0 | 2/1/1 | 2/1/1 | 2/1/1 | 2/1/1 |

## Method and symbols

Each competitor is compared with MSC-CMA-ES using independent, two-sided
Mann–Whitney U tests on 51 stored run-wise terminal errors at the stated budget.
The tests use the asymptotic method with tie and continuity corrections.
No zero threshold or rounding is applied to the MWU inputs; zeros already
present in the stored samples are retained.

Holm–Bonferroni correction is applied separately for each competitor, suite,
dimension, budget, and function scope, at `alpha=0.05`.
All-function and composition-function results use independent corrections
of the same raw p-values. For CEC2017 the family sizes are 29 and 10,
respectively; withdrawn function f2 is excluded.

**MWU symbols:**

For each comparison, $\bar R_M$ and $\bar R_A$ are the mean ranks of
the MSC-CMA-ES sample and the compared algorithm's sample in the pooled
sample, using average ranks for ties. These are the observation ranks
used by MWU, distinct from DSC ranks.

- **`<`**: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.
- **`>`**: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.
- **`=`**: $p_{\mathrm{Holm}}>0.05$; the null hypothesis is not rejected.

The symbol `=` denotes non-rejection of $H_0:F_M=F_A$; it does not
assert equality of the sample mean ranks.

Significance uses the full-precision adjusted p-value (`p_Holm <= 0.05`).
The mean-rank relation is obtained from U without rounding the input errors.
Summary cells contain $n_{<}/n_{>}/n_{=}$: counts of functions in the
three categories defined above.

CSV values retain full numerical precision. Only descriptive medians use
a separate copy with `abs(error) <= 1e-8` set to zero.

## Deep Statistical Comparison

Each suite/dimension page also contains the existing DSC ranks,
Friedman results, and Holm-adjusted post-hoc comparisons for both scopes.
They are read from the existing DSC result files; no DSC test is recomputed.

### Symbols

- **★** — MSC-CMA-ES has the lowest mean DSC rank and the Friedman test rejects the null hypothesis.
- **≈** — the Friedman test rejects the null hypothesis, but the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant.
- **↓** — the lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES and the Holm-adjusted comparison is significant.
- **O** — the Friedman test does not reject the null hypothesis; no post-hoc interpretation is made.

`p_Holm` is shown only when the lowest-mean-rank algorithm is not MSC-CMA-ES
and the Friedman test rejects the null hypothesis.

## Data and regeneration

[Download all settings and scopes as CSV](mann_whitney_u_all_settings.csv).
Per-dimension `details.csv` files use the same schema. The `scope` column
identifies the function family used for each correction.
Composition functions occur once in the all-function analysis and again
in the independently corrected composition analysis.

The U statistics and raw p-values are preserved from the
[previous published results](https://github.com/snenovgmailcom/cma_es_project/blob/3f9bac714bc0e4d7b519ed459956dd774abc3442/mwu/mann_whitney_u_all_settings.csv).
Holm corrections are calculated independently for each selected function family.
The DSC tables use the [existing DSC results](https://github.com/snenovgmailcom/cma_es_project/tree/3f9bac714bc0e4d7b519ed459956dd774abc3442/dsc).

Regeneration requires the updated `run_mwu_all_functions.py` generator with
Holm correction and `--func-class both` support. The older Bonferroni generator
under `analysis/` is outside the scope of this directory update. After installing
the updated generator, run from the repository root:

```bash
python analysis/run_mwu_all_functions.py --dsc-results dsc
```
