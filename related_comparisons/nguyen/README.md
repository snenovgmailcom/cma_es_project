# CMAES-NBC-qN (Nguyen 2024) — published-value comparison

Nguyen reports CEC2014 and CEC2017 results for CMAES-NBC-qN in D=30 and D=50.
The two D=30 cells correspond directly to MSC-CMA-ES experiments at the same
budget, **300,000 NFE**.

Reference:

> D. M. Nguyen, *Adapting the population size in CMA-ES using nearest-better
> clustering method for multimodal optimization*, *Applied Soft Computing*
> 167 (2024), 112361. DOI [10.1016/j.asoc.2024.112361](https://doi.org/10.1016/j.asoc.2024.112361).

| Suite | D | Budget | Published source | Comparison |
|:--|--:|--:|:--|:--|
| CEC2014 | 30 | 300K | Nguyen Table 10 | [MSC-CMA-ES vs CMAES-NBC-qN](cec2014/d30/budget_300000/README.md) |
| CEC2017 | 30 | 300K | Nguyen Table 12 | [MSC-CMA-ES vs CMAES-NBC-qN](cec2017/d30/budget_300000/README.md) |

Only published **mean and standard deviation** values are used for
CMAES-NBC-qN. No MWU or DSC is reported because the run-wise CMAES-NBC-qN
samples are not available.
