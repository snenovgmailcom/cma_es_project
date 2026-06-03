"""
benchmark/_common.py — shared foundation for per-algorithm benchmark scripts.

Each algorithm script (msc.py, bipop.py, arrde.py) writes to its own output
directory:

    experiments/<suite>/d<D>/<algorithm>/maxevals_<N>/
        f<k>.pkl          — per-function results
        summary.csv       — aggregated stats

PKL structure per file (single algorithm, single function):

    {
        'suite':       'cec2020',
        'dim':         10,
        'func':        'f10',
        'f_opt':       2500.0,
        'algorithm':   'MSC-CMA',
        'maxevals':    10000000,
        'n_runs':      51,
        'seeds':       np.ndarray int64 (n_runs,),
        'errors':      np.ndarray float64 (n_runs,),     # final best_f - f_opt
        'improvements': list of np.ndarray float64 (N_i, 2),  # per seed: [nfev, err]
                       # recorded on every improvement while err > COCO_ZERO.
                       # After err <= COCO_ZERO we stop recording (flat line).
        'params':      dict,   # algorithm-specific config + CLI args
        'meta':        dict,   # hostname, timestamp, software versions
    }

Precision conventions:
  - Raw errors in pkl: float64, no clipping, no rounding (historical record).
  - Reporting tables: "%.2e" scientific notation (CEC paper convention).
  - Wilcoxon / ECDF: NO clipping (user decision — rely on float64 precision
    and BH correction to handle roundoff noise).
"""

import datetime
import os
import pickle
import platform
import sys

import numpy as np


# =========================================================================
# Constants
# =========================================================================

# COCO "numerical zero" — once the best-so-far error drops at or below this,
# we stop recording further improvements (everything below is noise).
COCO_ZERO = 1e-8

# Canonical algorithm names.
ALGO_MSC    = 'MSC-CMA'
ALGO_BIPOP  = 'BIPOP-CMA'
ALGO_ARRDE  = 'ARRDE'
ALGO_LSRTDE = 'LSRTDE'
ALGO_JSO    = 'jSO'
ALGO_MSC             = 'MSC-CMA'
ALGO_BIPOP           = 'BIPOP-CMA'
ALGO_ARRDE           = 'ARRDE'
ALGO_LSRTDE          = 'LSRTDE'
ALGO_NLSHADE_RSP     = 'NLSHADE-RSP'        
ALGO_J2020           = 'j2020'              
ALGO_LSHADE          = 'LSHADE'             
ALGO_LSHADE_CNEPSIN  = 'LSHADE-cnEpSin'     


# =========================================================================
# Suite defaults
# =========================================================================

# CEC2020 BCC (Bound-Constrained Competition) official budgets.
CEC2020_MAXEVALS = {5: 50_000, 10: 1_000_000,
                    15: 3_000_000, 20: 10_000_000}

# CEC2022 competition budgets.
CEC2022_MAXEVALS = {10: 200_000, 20: 1_000_000}


def suite_default_maxevals(suite: str, dim: int) -> int:
    """Return the official suite default max function evaluations."""
    if suite == 'cec2020':
        return CEC2020_MAXEVALS[dim]
    if suite == 'cec2022':
        return CEC2022_MAXEVALS[dim]
    if suite in ('cec2014', 'cec2017', 'cec2019'):
        return dim * 10_000
    if suite == 'cec2011':
        return 150_000
    raise ValueError(f"Unknown suite: {suite!r}")


# =========================================================================
# Suite config — bounds and CEC class lookup
# =========================================================================

def suite_config(suite: str, fnum: int, dim: int):
    """Return (cec_class, bias, bounds).

    bias: the true global optimum value (shift) for fnum.
    bounds: np.ndarray shape (dim, 2) with [lb, ub] per axis.
    """
    from minionpy import (CEC2014Functions, CEC2017Functions,
                          CEC2019Functions, CEC2020Functions,
                          CEC2022Functions)

    # CEC biases (global optima for error = f - bias)
    CEC2017_BIAS = {i: 100 * i for i in range(1, 31)}
    CEC2020_BIAS = {1: 100, 2: 1100, 3: 700, 4: 1900, 5: 1700,
                    6: 1600, 7: 2100, 8: 2200, 9: 2400, 10: 2500}
    CEC2022_BIAS = {1: 300, 2: 400, 3: 600, 4: 800, 5: 900,
                    6: 1800, 7: 2000, 8: 2200, 9: 2300, 10: 2400,
                    11: 2600, 12: 2700}
    CEC2014_BIAS = {i: 100 * i for i in range(1, 31)}
    # CEC2019 "100-Digit Challenge" — all functions have f_opt = 1.0
    CEC2019_BIAS = {i: 1.0 for i in range(1, 11)}

    # Standard CEC bounds: [-100, 100]^D (CEC2014 same, CEC2017 same).
    # CEC2022 also uses [-100, 100]^D.
    # CEC2020 uses [-100, 100]^D.
    bounds = np.array([[-100.0, 100.0]] * dim, dtype=float)

    if suite == 'cec2017':
        return CEC2017Functions, CEC2017_BIAS[fnum], bounds
    if suite == 'cec2014':
        return CEC2014Functions, CEC2014_BIAS[fnum], bounds
    if suite == 'cec2020':
        return CEC2020Functions, CEC2020_BIAS[fnum], bounds
    if suite == 'cec2022':
        return CEC2022Functions, CEC2022_BIAS[fnum], bounds

    if suite == 'cec2019':
        # CEC2019 has fixed per-function dimensions and heterogeneous bounds:
        #   f1 (Storn's Chebyshev):   D=9,  bounds [-8192, 8192]
        #   f2 (Inverse Hilbert):     D=16, bounds [-16384, 16384]
        #   f3 (Lennard-Jones):       D=18, bounds [-4, 4]
        #   f4 (Rastrigin):           D=10, bounds [-100, 100]
        #   f5 (Griewank):            D=10, bounds [-100, 100]
        #   f6 (Weierstrass):         D=10, bounds [-100, 100]
        #   f7 (Modified Schwefel):   D=10, bounds [-100, 100]
        #   f8 (Expanded Schaffer):   D=10, bounds [-100, 100]
        #   f9 (Happy Cat):           D=10, bounds [-100, 100]
        #   f10 (Ackley):             D=10, bounds [-100, 100]
        CEC2019_DIMS = {1: 9, 2: 16, 3: 18}  # f4-f10 all D=10
        CEC2019_BOUNDS = {
            1: (-8192.0, 8192.0),
            2: (-16384.0, 16384.0),
            3: (-4.0, 4.0),
        }
        required_dim = CEC2019_DIMS.get(fnum, 10)
        if dim != required_dim:
            raise ValueError(
                f"CEC2019 f{fnum} requires dim={required_dim}, got dim={dim}"
            )
        lb, ub = CEC2019_BOUNDS.get(fnum, (-100.0, 100.0))
        bounds = np.array([[lb, ub]] * dim, dtype=float)

        # CEC2019Functions API is (fnum,) only — wrap it so callers can
        # use the uniform (fnum, dim) signature used for other suites.
        class _CEC2019Wrapper:
            def __init__(self, fnum_inner, dim_inner):
                self._inner = CEC2019Functions(fnum_inner)
            def __call__(self, X):
                return self._inner(X)

        return _CEC2019Wrapper, CEC2019_BIAS[fnum], bounds

    raise ValueError(f"Unknown suite: {suite!r}")


# =========================================================================
# Improvement recorder
# =========================================================================

class ImprovementRecorder:
    """Wraps a batch objective. Records every improvement in best-so-far
    error while error > COCO_ZERO.

    Usage:
        recorder = ImprovementRecorder(cec_instance, f_opt=bias, maxevals=N)
        # Pass `recorder` wherever the algorithm expects the objective:
        solver.solve(recorder, ...)
        # Get results:
        final_err = recorder.best_err
        improvements = recorder.improvements   # (N, 2) array, cols [nfev, err]

    The callable interface follows minionpy / pycma convention:
        F = recorder(X)   where X is (popsize, D) or list-of-lists,
                          and F is a list of floats, one per row.

    After the algorithm finishes, call recorder.finalize() to freeze state.
    """

    def __init__(self, func, f_opt: float, maxevals: int):
        self.func = func
        self.f_opt = float(f_opt)
        self.maxevals = int(maxevals)

        self.nfev = 0
        self.best_f = np.inf          # raw f (not error)
        self.best_err = np.inf        # best_f - f_opt
        self._improvements = []       # list of (nfev, err) tuples

        # Stop recording once we go below COCO_ZERO (numerical zero).
        self._below_zero = False

    def __call__(self, X):
        """Batch evaluate X, update state, return list of floats.

        Vectorized: no Python per-element loop. nfev in improvements
        is batch-granular (±popsize) — negligible for attainment curves.
        """
        F = self.func(X)
        n = len(F) if isinstance(F, (list, np.ndarray)) else 1
        self.nfev += n

        # Fast path: numpy min instead of Python loop
        F_arr = np.asarray(F, dtype=np.float64)
        min_val = float(F_arr.min())

        if min_val < self.best_f:
            self.best_f = min_val
            err = min_val - self.f_opt
            self.best_err = err
            if not self._below_zero:
                self._improvements.append((self.nfev, err))
                if err <= COCO_ZERO:
                    self._below_zero = True
        return F

    def finalize(self):
        """Call after the algorithm terminates. Currently a no-op because
        we track on every evaluation; provided for symmetry and future use."""
        return

    @property
    def improvements(self) -> np.ndarray:
        """Return (N, 2) float64 array: columns are [nfev, err]."""
        if not self._improvements:
            return np.zeros((0, 2), dtype=np.float64)
        return np.asarray(self._improvements, dtype=np.float64)


# =========================================================================
# Output directory layout
# =========================================================================

def build_outdir(suite: str, dim: int, algorithm: str, maxevals: int,
                 base: str = 'experiments') -> str:
    """Construct the canonical output directory path."""
    return os.path.join(
        base, suite, f'd{dim}', algorithm, f'maxevals_{maxevals}')


# =========================================================================
# PKL writer (one file per function, per algorithm, per budget)
# =========================================================================

def write_function_pkl(outdir: str,
                       suite: str,
                       dim: int,
                       func_name: str,
                       f_opt: float,
                       algorithm: str,
                       maxevals: int,
                       seeds: np.ndarray,
                       errors: np.ndarray,
                       improvements: list,
                       params: dict,
                       extra_meta: dict = None,
                       force: bool = False,
                       cycles_per_seed: list = None,
                       pre_refine_errors_per_seed=None,
                       nfev_pre_refine_per_seed=None,
                       nfev_total_per_seed=None) -> str:
    """Write single-algorithm, single-function pkl.

    Raises FileExistsError if file exists and force=False.
    Returns the full path of the written file.

    Optional MSC-CMA cycle persistence:
        cycles_per_seed:            list of (per-seed) list of cycle dicts.
                                    Each cycle dict carries cycle, nfev_start/end,
                                    best_f_start/end, improvement, nfev_phase0,
                                    n_basins_phase0, phi_used, sampling_method,
                                    cycle_local_best, mode. Same outer index as
                                    seeds/errors.
        pre_refine_errors_per_seed: array-like float, length n_runs. Error
                                    (raw - bias) just before end-game refinement.
                                    inf if refinement did not run (no cycles).
    """
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f'{func_name}.pkl')

    if os.path.exists(path) and not force:
        raise FileExistsError(
            f"{path} already exists. Use --force to overwrite.")

    meta = {
        'timestamp':      datetime.datetime.now().isoformat(timespec='seconds'),
        'hostname':       platform.node(),
        'python_version': sys.version.split()[0],
        'numpy_version':  np.__version__,
    }
    # Capture library versions if available.
    try:
        import scipy
        meta['scipy_version'] = scipy.__version__
    except ImportError:
        pass
    try:
        import cma
        meta['cma_version'] = cma.__version__
    except (ImportError, AttributeError):
        pass
    try:
        import minionpy
        meta['minionpy_version'] = getattr(minionpy, '__version__', 'unknown')
    except ImportError:
        pass

    if extra_meta:
        meta.update(extra_meta)

    payload = {
        'suite':        suite,
        'dim':          dim,
        'func':         func_name,
        'f_opt':        float(f_opt),
        'algorithm':    algorithm,
        'maxevals':     int(maxevals),
        'n_runs':       len(errors),
        'seeds':        np.asarray(seeds, dtype=np.int64),
        'errors':       np.asarray(errors, dtype=np.float64),
        'improvements': improvements,    # list of (N_i, 2) float64 arrays
        'params':       params,
        'meta':         meta,
    }

    # Optional MSC-CMA cycle data — only stored if explicitly provided.
    # Old analysis code keeps working; new code does payload.get('cycles_per_seed').
    if cycles_per_seed is not None:
        payload['cycles_per_seed'] = cycles_per_seed
    if pre_refine_errors_per_seed is not None:
        payload['pre_refine_errors_per_seed'] = np.asarray(
            pre_refine_errors_per_seed, dtype=np.float64)
    if nfev_pre_refine_per_seed is not None:
        payload['nfev_pre_refine_per_seed'] = np.asarray(
            nfev_pre_refine_per_seed, dtype=np.int64)
    if nfev_total_per_seed is not None:
        payload['nfev_total_per_seed'] = np.asarray(
            nfev_total_per_seed, dtype=np.int64)

    with open(path, 'wb') as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    return path


# =========================================================================
# Summary CSV writer (one row per function)
# =========================================================================

def write_summary_csv(outdir: str,
                      rows: list,
                      filename: str = 'summary.csv') -> str:
    """Write/append summary stats. rows is a list of dicts with at least:
        func, mean, median, std, best, worst, elapsed_sec, n_runs, maxevals
    Overwrites if file exists (single-algorithm dir = no merge semantics).
    """
    import csv

    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, filename)

    if not rows:
        return path

    fieldnames = list(rows[0].keys())
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    return path


def summary_row(func_name: str, errors: np.ndarray,
                elapsed_sec: float, maxevals: int) -> dict:
    """Build a summary row dict from the per-seed errors array."""
    e = np.asarray(errors, dtype=np.float64)
    return {
        'func':        func_name,
        'n_runs':      len(e),
        'maxevals':    maxevals,
        'mean':        float(e.mean()),
        'median':      float(np.median(e)),
        'std':         float(e.std()),
        'best':        float(e.min()),
        'worst':       float(e.max()),
        'elapsed_sec': round(float(elapsed_sec), 1),
    }


# =========================================================================
# Function-list parsing helper (shared by all scripts)
# =========================================================================

def parse_functions(arg: str) -> list:
    """Parse '1,2,3' or 'f1,f2,f3' → [1, 2, 3]."""
    out = []
    for part in arg.split(','):
        part = part.strip()
        if not part:
            continue
        if part.startswith('f') or part.startswith('F'):
            part = part[1:]
        out.append(int(part))
    return out


# =========================================================================
# Console printing helpers
# =========================================================================

def print_header(suite: str, dim: int, algorithm: str,
                 maxevals: int, n_runs: int, n_jobs: int):
    print("=" * 72)
    print(f"{algorithm}  on {suite} D={dim}  "
          f"maxevals={maxevals}  runs={n_runs}  jobs={n_jobs}")
    print("=" * 72)


def print_func_result(func_name: str, errors: np.ndarray,
                      elapsed_sec: float):
    e = np.asarray(errors, dtype=np.float64)
    print(f"  {func_name:>4s}  mean={e.mean():10.3e}  "
          f"median={np.median(e):10.3e}  "
          f"std={e.std():10.3e}  "
          f"best={e.min():10.3e}  "
          f"worst={e.max():10.3e}  "
          f"time={elapsed_sec:6.1f}s")
