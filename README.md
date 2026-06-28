# MSC-CMA-ES

**Multi-Start Clustering CMA-ES** — structure-aware restarts for CMA-ES via cyclic
nearest-better basin discovery.

Reference implementation, baselines, and experimental results for the paper:

> D. Nedanovski, S. Nenov, D. Pilev.
> *MSC-CMA-ES: Structure-Aware Restarts for CMA-ES via Cyclic Nearest-Better Basin Discovery.*
> arXiv:2606.15830, 2026. https://doi.org/10.48550/arXiv.2606.15830

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
  compare.py        per-function Wilcoxon comparison vs a reference algorithm
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
(worst / median / coverage / best); budget-scaling figures show the
fixed-budget target coverage (FBTC) as a monotone envelope across budgets.

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