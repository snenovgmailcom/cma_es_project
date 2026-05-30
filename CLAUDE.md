# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A research codebase for **MSC-CMA-ES** (Multi-Start Cyclic CMA-ES with nearest-better-clustering basin detection), benchmarked against state-of-the-art differential-evolution and CMA baselines on the CEC bound-constrained suites (CEC2014/2017/2019/2020/2022). The work centers on developing MSC-CMA, tuning it with Optuna, and producing comparison tables/figures (mean error, COCO ECDF, fixed-budget target coverage) for a paper.

There is no `setup.py`/`requirements.txt`/README. It is a flat set of scripts run from the project root.

## Environment & dependencies

Python 3.13. Key libraries (must already be importable; not pinned anywhere):
- `cma` (pycma 4.4.x) — the CMA-ES engine used by MSC and the BIPOP baseline.
- `minionpy` — provides the CEC function suites (`CEC2017Functions`, etc.) **and** the C++ DE baselines (ARRDE, jSO, j2020, NLSHADE-RSP, LSRTDE, LSHADE) via `minionpy.Minimizer(algo=...)`.
- `scipy` (QMC samplers, KDTree, stats), `numpy`, `joblib` (parallel seeds), `optuna` (tuning), `pybind11` (only to build the optional C++ extension).

### Optional C++ acceleration

`basin_detector.py` transparently uses a compiled nearest-better-tree extension (~20× faster) if present, else falls back to pure NumPy. The `.so` is checked in. Rebuild only if `nb_tree.cpp` changes:

```bash
cd algorithms/cpp && ./build.sh    # produces nb_tree.cpython-*.so
```

## Running things

**Always run from the project root** (`/home/svety/cma_es_project`). Scripts manipulate `sys.path` to put `algorithms/` and `benchmark/` on the path, so they work both as `python benchmark/msc.py` and `python -m benchmark.arrde`.

### Run MSC-CMA on a suite/dim

```bash
# --auto = the alt-CB scheduler (the production mode); see "alt-CB" below.
python benchmark/msc.py --suite cec2020 --dim 10 \
    --functions 1,2,3,4,5,6,7,8,9,10 --runs 51 --jobs 51 --auto

# Single-config mode (CLI hyperparameter overrides on top of default MSCConfig):
python benchmark/msc.py --suite cec2017 --dim 10 --functions f22,f28 \
    --runs 51 --maxevals 5000000 --force

# One seed, verbose per-cycle/per-restart trace (debugging):
python benchmark/msc.py --suite cec2017 --dim 10 --functions 1 \
    --runs 1 --jobs 1 --auto --logs --force
```

### Run baselines

```bash
# Single baseline:
python -m benchmark.arrde --suite cec2020 --dim 10 --functions 1,2,3 --runs 51 --jobs 51

# All non-MSC baselines across a grid of cells (resumable driver):
python benchmark/run_baselines.py --dry-run        # preview the plan
python benchmark/run_baselines.py --runs 51 --jobs 51
```

`run_baselines.py` holds the canonical grid of `(suite, dim, maxevals)` CELLS, runs each `(cell, algo)` in a fresh subprocess (so worker memory is released), and is **resumable**: it skips functions whose pkl already exists and is valid (right seed count, no NaN/inf). Use `--force` to redo. BIPOP and MSC are intentionally driven separately (they are slow / configured differently).

### Tuning (Optuna)

`experiments/optuna_v3.py` tunes one MSC class (B or C) by launching `benchmark/msc.py --auto --tune-class {B|C}` subprocesses, scoring each trial by COCO endpoint ECDF. The other class stays fixed at its `auto_config` base ("alternating optimization"). Winners are pasted by hand into `algorithms/auto_config.py` (`_B_BASE` / `_C_BASE`). Studies persist to `sqlite:///optuna_studies_v3/study.db`.

### Analysis / figures

`analysis/` scripts walk the `experiments/` tree and emit comparison tables and plots. Two main entry points:
- `analysis/compare.py --base-dir experiments/<suite>/d<dim> --ref MSC-CMA --metric {mean|median|ecdf|hits} [--correction bh] [--latex]` — per-function comparison vs a reference, with Wilcoxon + Benjamini-Hochberg.
- `analysis/summary_grid.py` — compact cross-suite/dim grid of SUM(mean), SUM(median), SUM(std), SUM(FBTC).
- `analysis/ecdf_v3.py` — COCO runtime ECDF figures, partitioned into HIGH/LOW function buckets.

## Output data contract (read before touching anything that reads/writes results)

Every algorithm run writes to a canonical directory built by `_common.build_outdir`:

```
experiments/<suite>/d<dim>/<ALGO>/maxevals_<N>/
    f<k>.pkl        # one pickle per function
    summary.csv     # aggregated per-function stats
```

`<ALGO>` is a canonical name from `_common.py` (e.g. `MSC-CMA`, `ARRDE-minionpy`, `BIPOP-CMA-pycma`). The pkl schema is documented in `benchmark/_common.py` (`write_function_pkl`). Critical fields:
- `errors`: float64 array, `final_best_f - f_opt`. **Raw, never clipped or rounded** — this is the historical record. Reporting tables format as `%.2e`; Wilcoxon/ECDF use the raw float64 (no clipping is a deliberate decision).
- `improvements`: per-seed `(N, 2)` arrays of `[nfev, err]`, recorded on each best-so-far improvement until `err <= COCO_ZERO` (1e-8), then recording stops. This is the attainment curve used for ECDF.
- MSC-CMA also stores `cycles_per_seed`, `pre_refine_errors_per_seed`, `nfev_pre_refine_per_seed`, `nfev_total_per_seed` (optional keys; baseline pkls lack them).

`ImprovementRecorder` (in `_common.py`) is the universal objective wrapper: it counts `nfev`, tracks best error, and records the attainment curve. Every runner wraps the bare CEC function in it. `f_opt` (the bias / known optimum) comes from `suite_config()`, which also returns the CEC class and `[-100,100]^D` bounds (CEC2019 is the exception: per-function dims and bounds).

## MSC-CMA architecture (`algorithms/`)

The solver is split across small modules; each uses a `try: from .x import ... except ImportError: from x import ...` dual-import so it works whether `algorithms/` is a package or is flat on `sys.path`.

- **`config.py`** — `MSCConfig` dataclass: every tunable in one place (Phase-0 sample size, NBC params, CMA sigma/popsize, tolerances, refinement). `resolve_refine_frac()` maps `refine_frac=-1` (auto) to a piecewise-linear fraction of budget based on `maxevals / ref_budget`.

- **`basin_detector.py`** — Phase-0. `NBCDetector.discover()` runs: QMC sampling (LHS/Sobol/Halton) → evaluate → nearest-better tree → NBC clustering (Preuss Rule 1 long-edge cut + Rule 2 hub cut) → a "staircase" search over φ to hit `n_initial_basins` → `BasinInfo` list sorted small→large. `identify_basin_knn()` does kNN-majority basin membership used for convergence tracking. `BasinInfo.sigma0()` derives the CMA σ₀ from per-axis Q75 spread of the basin elite.

- **`msc_cma.py`** — `MSC_CMA.solve()`, the orchestrator. Loops **cycles** until the main budget is spent, reserving a tail for end-game refinement:
  - **Phase-0**: detect basins for this cycle.
  - **Phase-1 (topo)**: for each basin small→large, start a CMA restart from the basin's best point; a basin that two restarts converge into gets excluded. Each restart stops on the *first* of: pycma `es.stop()`, `std(F) < s_tol` (absolute fitness convergence), or budget exhaustion.
  - **End-game refinement**: one CMA restart from the global best with **all** pycma convergence stops disabled (tolfun/tolx/conditioncov/etc. set to 0 or huge) so budget alone terminates it — lets it dig to float-epsilon.
  - Returns a `RunResult` (see `result.py`: `RestartRecord`, `CycleStats`, `PhaseStats`).

- **`auto_config.py` + "alt-CB"** — the production scheduler. Two global configs, **B** (few large basins, big popsize — exploit) and **C** (many small basins, small popsize — explore), live as `_B_BASE`/`_C_BASE`. `--auto` makes `MSC_CMA` cycle `[cfg_C, cfg_B, cfg_C, ...]` via `mode_schedule`, with no upfront classifier. The only dim-dependent law is `sigma_divisor *= sqrt(10/D)` (anchored at D=10); everything else is universal and tuned at the D=10/100k anchor cell. `get_B(dim)`/`get_C(dim)` apply the scaling. `--anchor` instead assigns one fixed class per function by a suite-specific boundary.

- **`result.py`** — result dataclasses; `CycleStats.as_dict()` is the plain-dict form persisted into pkls (so readers need no class import). `basin_id.py` — basin id is an int for Phase-0, nested tuples for split children; helpers format/serialize it.

### Phase-0 reuse subtlety

In alt-CB + Sobol/Halton mode, odd cycles reuse a prefix of the previous even cycle's Phase-0 sample (Sobol/Halton sequences are nested, so `stream[0:N] ⊂ stream[0:M]`), spending **zero** new evals on that Phase-0 while re-clustering with the odd cycle's own NBC params. Disabled for LHS, single-config mode, or `--no-phase0-reuse`.

## Conventions & gotchas

- `COCO_ZERO = 1e-8` is the numerical-zero floor; attainment recording stops below it.
- **FBTC** (in `summary_grid.py`) is the fixed-budget target coverage: mean over 51 log-uniform targets in `[1e2, 1e-8]` of the per-target success rate at the final eval count. This is the Optuna objective and is **not** the COCO runtime-integrated ECDF (which `ecdf_v3.py` computes).
- The B/C numbers in `auto_config.py` are tuned champions — changing them changes the deployed algorithm. Don't edit casually; they come from specific Optuna trials (noted in comments).
- Files like `*.bak_pre_import_fix` are abandoned backups; ignore them.
