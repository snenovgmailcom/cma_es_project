# MSC-CMA-ES

<table>
<tr>
<td width="67%" valign="top">

<strong>Multi-Start Clustering CMA-ES</strong> — structure-aware restarts for CMA-ES via cyclic nearest-better basin discovery.

<p>Reference implementation, baselines, and experimental results for the paper:</p>

<blockquote>
D. Nedanovski, S. Nenov, D. Pilev.<br>
<em>MSC-CMA-ES: Structure-Aware Restarts for CMA-ES via Cyclic Nearest-Better Basin Discovery.</em><br>
arXiv:2606.15830, 2026.<br>
<a href="https://doi.org/10.48550/arXiv.2606.15830">https://doi.org/10.48550/arXiv.2606.15830</a>
</blockquote>

</td>

<td width="33%" valign="top">

<table>
<tr><th colspan="2" align="left">Benchmark results</th></tr>
<tr><td><a href="experiments/cec2014">CEC2014</a></td><td>
  <a href="experiments/cec2014/d10">D=10</a> ·
  <a href="experiments/cec2014/d30">D=30</a></td></tr>
<tr><td><a href="experiments/cec2017">CEC2017</a></td><td>
  <a href="experiments/cec2017/d10">D=10</a> ·
  <a href="experiments/cec2017/d30">D=30</a></td></tr>
<tr><td><a href="experiments/cec2020">CEC2020</a></td><td>
  <a href="experiments/cec2020/d5">D=5</a> ·
  <a href="experiments/cec2020/d10">D=10</a> ·
  <a href="experiments/cec2020/d15">D=15</a> ·
  <a href="experiments/cec2020/d20">D=20</a></td></tr>
<tr><td><a href="experiments/cec2022">CEC2022</a></td><td>
  <a href="experiments/cec2022/d10">D=10</a> ·
  <a href="experiments/cec2022/d20">D=20</a></td></tr>
</table>

</td>
</tr>

<tr>
<td width="67%" valign="top">

<strong>Statistical analysis</strong>

<p>
Individual-function comparisons use independent two-sided
<strong>Mann–Whitney U (MWU) tests</strong> on the 51 run-wise terminal errors,
with Bonferroni adjustment over the functions of each
suite–dimension–budget setting.
</p>

<p>
<strong>Deep Statistical Comparison (DSC)</strong> is performed through
<a href="https://ws.ijs.si/dsc/">DSCTool</a> following the fixed-budget
analysis perspective implemented in
<a href="https://iohanalyzer.liacs.nl/">IOHanalyzer</a>.
Per-function rankings use Anderson–Darling comparisons
(<code>alpha=0.05</code>, <code>epsilon=0</code>,
<code>monte_carlo_iterations=0</code>), followed by Friedman omnibus tests
and Holm-adjusted post-hoc comparisons when the omnibus null hypothesis
is rejected.
</p>

<p>
References:
<a href="https://doi.org/10.1145/3510426">Wang et al. (2022), IOHanalyzer</a> ·
<a href="https://doi.org/10.1016/j.ins.2017.07.015">Eftimov et al. (2017), Deep Statistics</a> ·
<a href="https://doi.org/10.1016/j.asoc.2019.105977">Eftimov et al. (2020), DSCTool</a>
</p>

</td>

<td width="33%" valign="top">

<table>
<tr><th colspan="2" align="left">Statistical results: MWU and DSC</th></tr>
<tr><td>CEC2014</td><td>
  <a href="mwu/cec2014/d10">D=10</a> ·
  <a href="mwu/cec2014/d30">D=30</a></td></tr>
<tr><td>CEC2017</td><td>
  <a href="mwu/cec2017/d10">D=10</a> ·
  <a href="mwu/cec2017/d30">D=30</a></td></tr>
<tr><td>CEC2020</td><td>
  <a href="mwu/cec2020/d5">D=5</a> ·
  <a href="mwu/cec2020/d10">D=10</a> ·
  <a href="mwu/cec2020/d15">D=15</a> ·
  <a href="mwu/cec2020/d20">D=20</a></td></tr>
<tr><td>CEC2022</td><td>
  <a href="mwu/cec2022/d10">D=10</a> ·
  <a href="mwu/cec2022/d20">D=20</a></td></tr>
  <tr>
<td colspan="2" align="center">
<a href="dsc/README.md"><strong>DSC summary — all 17 settings</strong></a>
</td>
</tr>
</table>

</td>
</tr>
<tr>
<td width="67%" valign="top">

<strong>Comparison with NEA2+ and CMAES-NBC-qN</strong>

<p>
<b>NEA2+</b> is a nearest-better-clustering CMA-ES niching method developed
by Mike Preuss. Our <code>benchmark/nea2plus_preuss.py</code> wrapper
uses the public Python implementation distributed/recommended by Preuss
and runs it on the CEC suites under the same fixed-budget, 51-run
experimental protocol used for MSC-CMA-ES.
</p>

<p>
The algorithmic lineage is documented in:
Preuss (2010), <em>Niching the CMA-ES via Nearest-Better Clustering</em>,
DOI: 10.1145/1830761.1830793;
Preuss (2012), <em>Improved Topological Niching for Real-Valued Global Optimization</em>,
DOI: 10.1007/978-3-642-29178-4_39; and
Preuss, Epitropakis, Li and Fieldsend (2021),
<em>Multimodal Optimization: Formulation, Heuristics, and a Decade of Advances</em>,
DOI: 10.1007/978-3-030-79553-5_1.
</p>

<p>
<b>CMAES-NBC-qN</b> is the nearest-better-clustering CMA-ES variant proposed
by Nguyen, combining NBC-based population adaptation with a quasi-Newton
local-search mechanism. This comparison uses the numerical results reported
in Nguyen (2024),
<em>Adapting the population size in CMA-ES using nearest-better clustering
method for multimodal optimization</em>,
DOI: 10.1016/j.asoc.2024.112361. Since the individual run-wise
CMAES-NBC-qN values are not available, no Mann–Whitney U or DSC analysis
is performed against MSC-CMA-ES.
</p>

</td>

<td width="33%" valign="top">

<table>
<tr><th colspan="2" align="left">MSC-CMA-ES vs NEA2+</th></tr>

<tr><td>CEC2017</td><td>
<a href="related_comparisons/nea2plus/cec2017/d10/budget_100000/README.md">
D=10 · 100K</a>
</td></tr>

<tr><td>CEC2020</td><td>
<a href="related_comparisons/nea2plus/cec2020/d5/budget_50000/README.md">D=5 · 50K</a><br>
<a href="related_comparisons/nea2plus/cec2020/d10/budget_1000000/README.md">D=10 · 1M</a><br>
<a href="related_comparisons/nea2plus/cec2020/d15/budget_3000000/README.md">D=15 · 3M</a>
</td></tr>

<tr><td>CEC2022</td><td>
<a href="related_comparisons/nea2plus/cec2022/d10/budget_200000/README.md">D=10 · 200K</a><br>
<a href="related_comparisons/nea2plus/cec2022/d20/budget_1000000/README.md">D=20 · 1M</a>
</td></tr>

<tr>
<td colspan="2" align="center">
<a href="related_comparisons/nea2plus/README.md">
<strong>Overview — 6 settings</strong></a>
</td>
</tr>

<tr><th colspan="2" align="left">MSC-CMA-ES vs CMAES-NBC-qN</th></tr>

<tr><td>CEC2014</td><td>
<a href="related_comparisons/nguyen/cec2014/d30/budget_300000/README.md">
D=30 · 300K</a>
</td></tr>

<tr><td>CEC2017</td><td>
<a href="related_comparisons/nguyen/cec2017/d30/budget_300000/README.md">
D=30 · 300K</a>
</td></tr>

<tr>
<td colspan="2" align="center">
<a href="related_comparisons/nguyen/README.md">
<strong>CMAES-NBC-qN overview</strong></a>
</td>
</tr>

</table>

</td>
</tr>


<tr>
<td width="67%" valign="top">

<strong>Ablation studies</strong>

<p>
We evaluate the following MSC-CMA-ES ablations:
<b>NO-NBC</b>, removing nearest-better clustering and the basin-based
structure layer;
<b>FIXED-PHI</b>, replacing the automatic staircase threshold selection
with a fixed <code>phi = 2</code>;
<b>NO-EXCLUSION</b>, disabling the suppression of repeatedly resolved basins;
<b>C-ONLY</b>, using only the C configuration without C/B alternation and
cross-cycle Phase-0 reuse; and a
<b>final-refinement contribution</b> analysis comparing the incumbent
immediately before and after the final refinement stage.
</p>

<p>
The two MSC-CMA-ES configurations were tuned with Optuna only once, on
CEC2017 at D=10 under the official 100K evaluation budget. The resulting
parameterization is reused across suites, dimensions, and budgets; only the
predefined dimension scaling of the CMA initial step-size parameter is applied.
For this reason, the ablation study is performed on the same CEC2017 D=10
tuning cell.
</p>

<p>
For the algorithmic ablations, the linked pages report fixed-budget
descriptive results and independent two-sided Mann–Whitney U comparisons
against the full MSC-CMA-ES, with Bonferroni correction across the 29
CEC2017 functions. DSC is not used for the ablation study.
</p>

</td>

<td width="33%" valign="top">

<table>
<tr>
<th colspan="2" align="left">Ablations — CEC2017, D=10, 100K</th>
</tr>

<tr><td>NO-NBC</td><td>
<a href="ablations/cec2017/d10/budget_100000/NO-NBC/README.md">Data + MWU</a>
</td></tr>

<tr><td>FIXED-PHI</td><td>
<a href="ablations/cec2017/d10/budget_100000/FIXED-PHI/README.md">Data + MWU</a>
</td></tr>

<tr><td>NO-EXCLUSION</td><td>
<a href="ablations/cec2017/d10/budget_100000/NO-EXCLUSION/README.md">Data + MWU</a>
</td></tr>

<tr><td>C-ONLY</td><td>
<a href="ablations/cec2017/d10/budget_100000/C-ONLY/README.md">Data + MWU</a>
</td></tr>

<tr><td>Final refinement</td><td>
<a href="ablations/cec2017/d10/budget_100000/REFINEMENT/README.md">Contribution</a>
</td></tr>

<tr>
<td colspan="2" align="center">
<a href="ablations/README.md">
<strong>Ablation overview</strong></a>
</td>
</tr>

</table>

</td>
</tr>

</table>

## Overview

CMA-ES is, per run, a local optimizer. MSC-CMA-ES makes its restarts
structure-aware: each cycle evaluates a Sobol pre-sample, partitions it into
approximate basins of attraction by nearest-better clustering (NBC) with an
automatic staircase choice of the cutting threshold, then launches one CMA-ES
restart per basin (smallest first) with a per-basin step size and population
size. Redundant basin visits are detected by a k-NN vote and excluded. Cycles
alternate two fixed configurations (C: many small basins / short runs, B: few
large basins / long runs), reusing the Sobol sample on alternate cycles at zero
extra cost. The remaining budget is spent on a single unbounded local
refinement of the incumbent.

## Configuration and tuning

The two configurations B and C were tuned **once**, with Optuna, on a single
cell — CEC2017 at D=10 under the official 100k budget. The resulting parameters
are then held **fixed** and reused unchanged for every function, suite, and
dimension. The only dimension-dependent quantity is the CMA step size, which
follows a fixed analytical law anchored at D=10,

```
sigma_divisor(class, D) = sigma_divisor_ref(class) * sqrt(10 / D)
```

(standard sqrt(D) box scaling). No per-suite or per-dimension re-tuning is
performed; the tuning script itself is not part of the released tree.

## Repository layout

```
algorithms/    Core MSC-CMA-ES
  msc_cma.py        orchestrator (cycles, phases, refinement)
  basin_detector.py Phase-0: sampling, NBC, staircase phi, basin extraction
  auto_config.py    the two tuned configurations (B and C)
  config.py         configuration container
  cpp/              optional C++ nearest-better tree (pybind11); pure-Python fallback exists
analysis/      Aggregation, comparison, and figures
  cell_report.py    per-cell report: ranking + budget-scaling figures + README
  suite_report.py   per-suite report: per-dimension figures + cross-dim README
  compare.py        per-function comparison vs a reference algorithm
  summary_grid_clean.py  shared metric/class definitions (FBTC, function classes)
benchmark/     Runners and wrappers
  msc.py            run MSC-CMA-ES on a CEC suite
  run_baselines.py  run BIPOP-CMA-ES (pycma) and the DE baselines (minionpy)
experiments/   Results tree: <suite>/d<dim>/<algorithm>/maxevals_<N>/summary.csv,
               per-cell and per-suite READMEs, and ranking / budget-scaling figures
```

## Installation

```bash
pip install -r requirements.txt
```

Core experiments used Python 3.13 (Intel Distribution for Python). The DE
baselines run through their `minionpy` C++ reference implementations; the
BIPOP-CMA-ES baseline and the CMA-ES engine use `pycma`.

### Optional: build the C++ nearest-better tree

The Phase-0 NBC tree has a C++ implementation (~20x faster). It is optional —
`basin_detector.py` falls back to pure Python automatically if the module is
absent.

```bash
cd algorithms/cpp
pip install pybind11
./build.sh
```

## Reproducing the experiments

The runner scripts add `algorithms/` and `benchmark/` to `sys.path`
themselves, so run them from the repository root.

**MSC-CMA-ES** (default schedule is the alternating C/B cycle; `--conly` runs
C-only; `--maxevals 0` uses the suite's official budget):

```bash
python benchmark/msc.py --suite cec2017 --dim 10 \
    --functions 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 \
    --maxevals 100000 --runs 51 --jobs 51
```

Results are written to
`experiments/<suite>/d<dim>/MSC-CMA/maxevals_<N>/summary.csv`.

**Baselines** (BIPOP-CMA-ES and the five DE algorithms):

```bash
python benchmark/run_baselines.py --runs 51 --jobs 51            # all
python benchmark/run_baselines.py --algos ARRDE,jSO --runs 51    # a subset
```

**Tables and figures.** Two report generators read the `*.pkl` run data
and (re)build the figures and READMEs in a fixed, reproducible style:

```bash
# One cell: ranking + budget-scaling figures + README for a (suite, dim).
python analysis/cell_report.py --base-dir experiments/cec2014/d10 --official 100000

# One suite: per-dimension figures + cross-dimension README.
python analysis/suite_report.py --suite cec2017 --dims 10,30 \
    --official 10,100000 --official 30,300000
```

Ranking figures place the seven algorithms on four aggregate axes
(worst / median / coverage / best); budget-scaling figures show raw FBTC(B) separately at each evaluated
fixed budget.

## Results

Per-(suite, dimension, algorithm, budget) `summary.csv` files (mean, median,
best, and fixed-budget target coverage per function, 51 runs) are committed
under `experiments/`. Each leaf is at
`experiments/<suite>/d<dim>/<algorithm>/maxevals_<N>/summary.csv`.

## Citation

```bibtex
@article{msccmaes2026,
  title   = {MSC-CMA-ES: Structure-Aware Restarts for CMA-ES via Cyclic Nearest-Better Basin Discovery},
  author  = {Nedanovski, Dimitar and Nenov, Svetoslav and Pilev, Dimitar},
  journal = {arXiv preprint arXiv:2606.15830},
  year    = {2026}
}
```

## AI assistance

Parts of the code in this repository were written with the assistance of
Claude (Anthropic). All code has been read, reviewed, and verified by the
authors, who take full responsibility for its correctness.

## License

MIT — see [LICENSE](LICENSE).
