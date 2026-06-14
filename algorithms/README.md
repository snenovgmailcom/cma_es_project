# `algorithms/` — Core MSC-CMA-ES

The MSC-CMA-ES solver and its Phase-0 nearest-better-clustering (NBC) basin
detector. This package is self-contained; the runners in `benchmark/` import
from here (they add this directory to `sys.path`).

## Module map

| File | What it provides |
|---|---|
| `msc_cma.py` | The solver. Class `MSC_CMA` with `solve()`: the cycle loop, the two phases, alternating C/B schedule, Sobol sample reuse, and final refinement. |
| `basin_detector.py` | Phase-0. Sampling, the nearest-better tree, NBC (Rule 1 + Rule 2), staircase φ selection, basin extraction, and k-NN basin membership. |
| `auto_config.py` | The two tuned configurations, `get_B(dim)` and `get_C(dim)`, with the universal √(10/D) σ-scaling anchored at D = 10. |
| `config.py` | `MSCConfig` — the parameter container (one set of algorithm parameters). |
| `basin_id.py` | The `BasinId` type and helpers (`root_basin_id`, `format_basin_id`, `serialize_*`). |
| `result.py` | Result dataclasses: `RunResult`, `RestartRecord`, `CycleStats`, `PhaseStats`, `BasinSnapshot`, `BenchmarkResult`. |
| `cpp/` | Optional C++ nearest-better tree (`nb_tree.cpp`, `build.sh`); ~20× faster. A pure-Python fallback is used automatically if it is not built. |

## Pipeline

The solver runs a sequence of cycles and closes with one refinement
(`MSC_CMA.solve`):

1. **Phase 0** (`NBCDetector.discover` in `basin_detector.py`)
   - `sample_points` draws a space-filling design (`lhs` / `sobol` / `halton`).
   - `nearest_better_tree` connects each point to its nearest *better*
     neighbour in normalized coordinates.
   - `nbc_clustering` cuts the tree by **Rule 1** (edges longer than φ·mean) and
     **Rule 2** (hubs: high in-degree with a long outgoing edge), then labels
     basins by pointer jumping.
   - `_staircase_phi` picks φ automatically as the largest value yielding at
     least `n_initial_basins` basins of size ≥ `min_basin_size`.
   - Each basin becomes a `BasinInfo` (size, centroid, diameter, and a per-basin
     `sigma0`).
2. **Phase 1** (`_run_topo_phase`)
   - One CMA-ES restart per basin, smallest first, from the basin's best
     sampled point, with a per-basin step size and population size
     (`compute_popsize`). A k-NN vote (`identify_basin_knn`) detects the basin
     each restart converges to; a twice-resolved basin is excluded for the rest
     of the cycle.
3. **Cycles / schedule**
   - Single config (`mode_schedule=None`, C-only) or alternating C/B
     (`mode_schedule=[cfg_C, cfg_B]`). On alternating cycles the Sobol sample of
     the previous cycle is reused (`_reuse_eligible`), at zero extra evaluations.
4. **Refinement** (`_run_refinement`)
   - A single CMA-ES run from the incumbent, with all tolerance stops disabled,
     spending the reserved remainder of the budget.

## Usage

Run with this directory on `sys.path` (the `benchmark/` scripts do this for
you).

```python
import numpy as np
from auto_config import get_B, get_C
from msc_cma import MSC_CMA

D = 10
bounds = np.array([[-100.0, 100.0]] * D)     # [lower, upper] per coordinate

def f(X):                                    # batch objective:
    X = np.asarray(X)                        #   takes a list/array of points,
    return (X ** 2).sum(axis=1)              #   returns one value per point

cfg_C, cfg_B = get_C(D), get_B(D)
solver = MSC_CMA(
    f, bounds, maxevals=100_000, seed=0,
    config=cfg_C,                # used for the refine-budget reservation
    mode_schedule=[cfg_C, cfg_B] # alternating C/B; pass None for C-only
)
res = solver.solve()             # -> RunResult
print(res.fun, res.best_x)       # best objective value and point
```

`res` (a `RunResult`) also carries `restarts`, `cycles`, `phi_used`,
`best_f_pre_refine`, and per-phase statistics for analysis.

## Configuration keys (`MSCConfig`)

Symbols in the right column match Table 1 of the paper.

| Field | Symbol | Role |
|---|---|---|
| `n_phase0` | M (= 4096) | Sobol sample size (rounded to a power of two) |
| `n_initial_basins` | n_b | staircase target basin count |
| `min_basin_size` | s_min | smallest basin kept as useful |
| `k` | k | nearest-better tree query size |
| `nbc_b` | b | Rule-2 ratio (hub cut) |
| `nbc_min_incoming` | m (= 3) | Rule-2 minimum in-degree |
| `sigma_elite_frac` | ε | elite-centre fraction for σ₀ |
| `sigma_divisor` | δ_ref | σ₀ divisor (rescaled by √(10/D)) |
| `popsize_frac` | ρ | population-size fraction |
| `cma_popsize` | λ_max | population-size cap |
| `tolfun_exp` / `tolx_exp` | τ_f / τ_x | CMA tolerances (10^−τ) |
| `s_tol` | s_tol | population-range stop |
| `refine_frac` | r | refinement budget reservation |
| `nearest_better_k` | — | k for the membership vote (= 5) |
| `sampling_method` | — | `lhs` / `sobol` / `halton` (default `sobol`) |

The shipped `get_B` / `get_C` values are Optuna-tuned once on CEC2017 D = 10;
all parameters except `sigma_divisor` are fixed across dimensions and budgets.

## Optional C++ acceleration

```bash
cd cpp
pip install pybind11
./build.sh          # produces nb_tree<ext>.so
```

If the module is absent, `basin_detector.py` uses its pure-Python
nearest-better tree automatically — results are identical, only slower.