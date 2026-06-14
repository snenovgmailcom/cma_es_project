# `benchmark/` — Runners and baselines

Entry points for running MSC-CMA-ES and the baseline algorithms on the CEC
suites, plus the per-algorithm wrappers they call. Every run writes to
`experiments/<suite>/d<dim>/<ALGO>/maxevals_<N>/` as one `fK.pkl` per function
plus a `summary.csv`.

Run the scripts from the repository root — they add `algorithms/` and
`benchmark/` to `sys.path` themselves.

## Module map

| File | Role |
|---|---|
| `msc.py` | Run **MSC-CMA-ES** (this repository's method) on a suite/dimension. |
| `run_baselines.py` | Batch driver for the baselines: runs the DE algorithms and BIPOP-CMA-ES over a built-in grid of cells, resumably. |
| `bipop.py` | BIPOP-CMA-ES baseline (via `pycma`). |
| `arrde.py`, `jso.py`, `j2020.py`, `nlshade_rsp.py`, `lsrtde.py` | The five DE baselines, via their `minionpy` C++ reference implementations. |
| `lshade.py`, `lshade_cnepsin.py` | Extra DE variants — kept for reference, excluded from the default run plan (not part of the paper's set). |
| `rrcma.py`, `probe_lsrtde_reltol.py`, `probe_modcma.py` | Exploratory/diagnostic scripts, not used in the paper. |
| `_common.py` | Shared helpers: suite configuration, default budgets, output-path builder, and the `ALGO_*` name constants. |
| `__init__.py` | Package marker. |

Suites supported: `cec2014`, `cec2017`, `cec2019`, `cec2020`, `cec2022`.

## Command-line flags

Common to `msc.py` and the per-algorithm runners (the latter are invoked with
these by `run_baselines.py`):

| Flag | Default | Meaning |
|---|---|---|
| `--suite` | *(required)* | CEC suite |
| `--dim` | *(required)* | Dimension D |
| `--functions` | *(required)* | Comma-separated ids: `1,2,3` or `f1,f2,f3` |
| `--runs` | 51 | Independent runs (seeds) per function |
| `--maxevals` | 0 | Budget; `0` = the suite's official budget |
| `--jobs` | 1 | Parallel seeds (joblib) |
| `--outdir` | *(auto)* | Override output directory |
| `--force` | off | Overwrite existing results |
| `--seed-start` | 0 | First seed (`msc.py`) |

`msc.py` additionally:

| Flag | Default | Meaning |
|---|---|---|
| `--conly` | off | C-class only (no C/B alternation). Default is the alternating C/B scheduler. |
| `--sampling-method` | *(per class)* | Override Phase-0 sampling: `lhs` / `sobol` / `halton` |
| `--popsize-hist` | off | Print the population-size histogram per function |
| `--logs` | off | Verbose per-cycle/per-restart output (use with `--runs 1 --jobs 1`) |

`run_baselines.py`: `--runs` (51), `--jobs` (51), `--algos` (comma list, e.g.
`ARRDE,jSO`; empty = all), `--force`, `--dry-run` (print the plan and exit),
`--logdir` (`logs`). The grid of cells is the `CELLS` list inside the file.

## Usage

`$(seq -s, 1 N)` is a handy way to write the function list (`1,2,…,N`).

**MSC-CMA-ES, official budget, alternating C/B (default):**

```bash
python benchmark/msc.py --suite cec2017 --dim 10 \
    --functions $(seq -s, 1 30) --runs 51 --jobs 51
# -> experiments/cec2017/d10/MSC-CMA/maxevals_100000/
```

**C-only:**

```bash
python benchmark/msc.py --suite cec2020 --dim 5 \
    --functions $(seq -s, 1 10) --conly --runs 51 --jobs 51
```

**One function, verbose:**

```bash
python benchmark/msc.py --suite cec2017 --dim 10 --functions 1 \
    --runs 1 --jobs 1 --logs
```

**Budget scaling (same cell, larger budget):**

```bash
python benchmark/msc.py --suite cec2020 --dim 5 \
    --functions $(seq -s, 1 10) --maxevals 1000000 --runs 51 --jobs 51
```

**Baselines (DE algorithms + BIPOP):**

```bash
python benchmark/run_baselines.py --dry-run               # preview the plan
python benchmark/run_baselines.py --runs 51 --jobs 51     # run everything in CELLS
python benchmark/run_baselines.py --algos ARRDE,jSO --runs 51 --jobs 51
```

**A single baseline directly** (same CLI as `msc.py`):

```bash
python -m benchmark.arrde --suite cec2017 --dim 10 \
    --functions $(seq -s, 1 30) --maxevals 100000 --runs 51 --jobs 51 \
    --outdir experiments/cec2017/d10/ARRDE/maxevals_100000
```

## Output and analysis

Each run produces `experiments/<suite>/d<dim>/<ALGO>/maxevals_<N>/fK.pkl`
(raw per-seed errors) and a `summary.csv` (mean, median, best, fixed-budget
target coverage). The scripts in `analysis/` read this tree to build the
paper's tables and figures:

```bash
python analysis/summary_grid.py        # per-dimension / per-class totals
python analysis/budget_slopes.py       # budget-scaling slopes
python analysis/fig_budget_slopes.py   # budget-slope figures
python analysis/class_rank_figures.py  # per-class rank figures
```