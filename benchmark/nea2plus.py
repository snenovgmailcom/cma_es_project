#!/usr/bin/env python3
"""Port of the public Preuss/Wessing NEA2+ Python code to CEC benchmarks.

This runner preserves the algorithmic defaults of the public ``nea2.py``
archive (version 1.1, 28 September 2016) while replacing its hard-coded
CEC2013 maximization wrapper and GECCO-2016 output with the project's CEC/PKL
interfaces.

Important naming point
----------------------
The downloadable source calls its main function ``nea2plus`` and uses
``edgeLengthFactor=1.3``.  It is therefore recorded as ``NEA2PLUS-PY``.  It
must not be described as an exact reproduction of the 2012 NEA2 experiment
with Rule-1 factor phi=2.

Preserved public-code semantics
-------------------------------
* normalized search domain [0,1]^D;
* fresh ``diversipy.maximin_reconstruction`` sample, M=400, per epoch;
* NearestBetterClustering Rules 1+2, Rule-1 factor 1.3, original mean
  nearest-better-edge reference distance;
* graph minima sorted by objective value and searched sequentially;
* one bounded CMA-ES from each graph minimum, without local restarts;
* sigma0=max(0.025*sqrt(D), Normal(0.05*sqrt(D),0.025*sqrt(D)));
* bundled pycma 1.1.06 defaults, with tolfun=1e-6;
* a new epoch only while more than M evaluations remain.

The logical project seeds remain 0,...,50.  The internal public-code seed
convention is ``21062016 + 100*fnum + logical_seed``.

Expected layout after extracting the supplied bundle into the repository:

    benchmark/nea2plus_preuss.py
    third_party/nea2_preuss/cma.py
    benchmark/_common.py

Example
-------
python benchmark/nea2plus_preuss.py \
    --suite cec2017 --dim 10 \
    --functions 1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 \
    --runs 51 --jobs 51
"""

import argparse
import collections
import collections.abc
import os
import random
import sys
import time

import numpy as np
from joblib import Parallel, delayed


# -------------------------------------------------------------------------
# Repository paths and legacy compatibility
# -------------------------------------------------------------------------

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BENCHMARK_DIR = _THIS_DIR
_ROOT = os.path.dirname(_BENCHMARK_DIR)
_VENDOR_DIR = os.path.join(_ROOT, "third_party", "nea2_preuss")

for _path in (_BENCHMARK_DIR, _VENDOR_DIR):
    if os.path.isdir(_path):
        if _path in sys.path:
            sys.path.remove(_path)
        sys.path.insert(0, _path)

if not os.path.isfile(os.path.join(_VENDOR_DIR, "cma.py")):
    raise RuntimeError(
        "Missing third_party/nea2_preuss/cma.py. Extract the complete "
        "nea2plus_cec2017_port bundle into the repository root."
    )

# The bundled 2015 pycma uses names removed from modern Python.
if not hasattr(collections, "MutableMapping"):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(time, "clock"):
    time.clock = time.process_time
# NumPy 2 removed these historical aliases used by cma.py 1.1.06.
if not hasattr(np, "Inf"):
    np.Inf = np.inf
if not hasattr(np, "NaN"):
    np.NaN = np.nan

import cma  # noqa: E402  (must resolve to the bundled public-code version)
import diversipy  # noqa: E402
import evoalgos  # noqa: E402
import optproblems  # noqa: E402
from diversipy import maximin_reconstruction  # noqa: E402
from evoalgos.niching import NearestBetterClustering  # noqa: E402
from optproblems import Individual, ResourcesExhausted  # noqa: E402

# NumPy 2 rejects ``array(..., copy=False)`` when a copy is unavoidable,
# whereas NumPy 1.x treated it as a best-effort request.  Restore precisely
# that legacy behavior inside the bundled CMA module.
_cma_array = cma.array


def _legacy_numpy_array(obj, *args, **kwargs):
    if kwargs.get("copy") is False:
        kwargs.pop("copy")
        return np.asarray(obj, *args, **kwargs)
    return _cma_array(obj, *args, **kwargs)


cma.array = _legacy_numpy_array

_expected_vendor_modules = {
    "cma": os.path.join(_VENDOR_DIR, "cma.py"),
    "diversipy": os.path.join(_VENDOR_DIR, "diversipy", "__init__.py"),
    "evoalgos": os.path.join(_VENDOR_DIR, "evoalgos", "__init__.py"),
    "optproblems": os.path.join(_VENDOR_DIR, "optproblems", "__init__.py"),
}
for _name, _expected in _expected_vendor_modules.items():
    _actual = os.path.realpath(sys.modules[_name].__file__)
    if _actual != os.path.realpath(_expected):
        raise RuntimeError(
            f"{_name} imported from {_actual}, expected vendored {_expected}"
        )

from _common import (  # noqa: E402
    ImprovementRecorder,
    build_outdir,
    parse_functions,
    print_func_result,
    print_header,
    suite_config,
    suite_default_maxevals,
    summary_row,
    write_function_pkl,
    write_summary_csv,
)


ALGO = "NEA2PLUS-PY"
GLOBAL_SAMPLE_SIZE = 400
EDGE_LENGTH_FACTOR = 1.3
USED_RULES = (1, 2)
BASE_SEED = 21062016
PUBLIC_ARCHIVE_SHA256 = (
    "641c3fdcffd6c326f0a7aef5bbf3edf8cc5458aad8c9ad92b036ec2811862fa6"
)
PUBLIC_ARCHIVE_URL = (
    "https://web.archive.org/web/20240415220454id_/"
    "https://ls11-www.cs.tu-dortmund.de/_media/rudolph/multimodal/nea2.zip"
)


def _sort_key(individual):
    """Public nea2.py lexicographic key, specialized safely to scalars."""
    value = individual.objective_values
    if value is None:
        return float("inf")
    try:
        values = list(value)
    except TypeError:
        return float(value)
    return tuple(float("inf") if x is None else float(x) for x in values)


def _reflect_unit_cube(x):
    """Reflect arbitrary coordinates into [0,1], as in the public wrapper."""
    y = np.mod(np.asarray(x, dtype=float), 2.0)
    return np.where(y <= 1.0, y, 2.0 - y)


class _CECUnitCubeProblem:
    """Scalar, hard-budgeted CEC objective in normalized coordinates."""

    def __init__(self, recorder, lower, upper, maxevals):
        self.recorder = recorder
        self.lower = np.asarray(lower, dtype=float)
        self.upper = np.asarray(upper, dtype=float)
        self.maxevals = int(maxevals)

    @property
    def consumed_evaluations(self):
        return int(self.recorder.nfev)

    @property
    def remaining_evaluations(self):
        return self.maxevals - self.consumed_evaluations

    def __call__(self, phenome):
        if self.remaining_evaluations <= 0:
            raise ResourcesExhausted("problem evaluations")
        unit = _reflect_unit_cube(phenome)
        real = self.lower + unit * (self.upper - self.lower)
        values = self.recorder(np.atleast_2d(real))
        return float(np.asarray(values, dtype=float).reshape(-1)[0])

    def evaluate(self, individual):
        individual.objective_values = self(individual.phenome)


def _run_local_cma(problem, start_point, step_size, cma_seed):
    """Run one local search and return (budget_exhausted, stop_dict)."""
    options = {
        "maxfevals": problem.remaining_evaluations,
        "maxiter": float("inf"),
        "bounds": [[0.0] * len(start_point), [1.0] * len(start_point)],
        "tolfun": 1e-6,
        "verb_time": False,
        "verb_log": 0,
        "verbose": -1,
        "verb_disp": 0,
        "seed": int(cma_seed),
    }

    nfev_start = problem.consumed_evaluations
    try:
        result = cma.fmin(
            problem,
            # The 2015 cma.py expects a Python sequence here.  With modern
            # NumPy, passing an ndarray makes its legacy ``x0 == str(x0)``
            # check raise an ambiguous-truth-value ValueError.
            np.asarray(start_point, dtype=float).tolist(),
            float(step_size),
            options=options,
            restarts=0,
        )
    except ResourcesExhausted:
        # The external problem wrapper, not pycma's generation counter, owns
        # the hard global cap.  No evaluation beyond maxevals is performed.
        return True, {"global_budget": problem.maxevals}
    except (StopIteration, ValueError) as exc:
        # Artifact-faithful behavior: public nea2.py catches every ValueError
        # raised by its legacy CMA wrapper and continues with the next basin.
        if problem.remaining_evaluations <= 0:
            return True, {"global_budget": problem.maxevals}
        # Its fallback evaluates x0 when CMA failed before evaluating any
        # candidate.  The CEC-wide incumbent is already retained by recorder.
        if problem.consumed_evaluations == nfev_start:
            problem(start_point)
        return False, {
            "legacy_value_error_recovery": str(exc),
            "nfev_consumed": problem.consumed_evaluations - nfev_start,
        }

    stop = result[-3]
    try:
        stop = dict(stop)
    except (TypeError, ValueError):
        stop = {"pycma_stop": str(stop)}
    return False, stop


def _run_seed(suite, fnum, dim, maxevals, logical_seed, disp=False):
    """Run one public-code NEA2+ port seed."""
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)
    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)

    bounds = np.asarray(bounds, dtype=float)
    lower, upper = bounds[:, 0], bounds[:, 1]
    problem = _CECUnitCubeProblem(recorder, lower, upper, maxevals)

    internal_seed = BASE_SEED + 100 * int(fnum) + int(logical_seed)
    random.seed(internal_seed)
    np.random.seed(internal_seed)

    nbc = NearestBetterClustering(
        edge_length_factor=EDGE_LENGTH_FACTOR,
        used_rules=USED_RULES,
        use_edge_lengths_for_threshold=True,
        sort_key=_sort_key,
    )

    epoch = 0
    restart_counter = 0
    restart_log = []
    budget_exhausted = False

    while problem.remaining_evaluations > GLOBAL_SAMPLE_SIZE:
        if disp:
            print(
                f"  seed={logical_seed} epoch={epoch} "
                f"remaining={problem.remaining_evaluations}",
                flush=True,
            )

        # Exact public nea2.py call/defaults: random-uniform initial design,
        # 100*M reconstruction steps, default L1 toroidal distance.
        global_sample = maximin_reconstruction(
            num_points=GLOBAL_SAMPLE_SIZE,
            dimension=dim,
            num_steps=None,
            initial_points=None,
            existing_points=None,
            use_reflection_edge_correction=False,
            dist_matrix_function=None,
            callback=None,
        )

        sample_individuals = [
            Individual(phenome=np.asarray(point, dtype=float))
            for point in global_sample
        ]
        for individual in sample_individuals:
            problem.evaluate(individual)

        starts = nbc.select(sample_individuals)
        starts.sort(key=_sort_key)

        if disp:
            print(
                f"  seed={logical_seed} epoch={epoch} starts={len(starts)}",
                flush=True,
            )

        diagonal = float(np.sqrt(dim))
        for start in starts:
            if problem.remaining_evaluations <= 0:
                budget_exhausted = True
                break

            # Drawn immediately before each CMA, exactly as in public code.
            step_size = max(
                0.025 * diagonal,
                float(np.random.normal(0.05 * diagonal,
                                       0.025 * diagonal, 1)[0]),
            )
            cma_seed = internal_seed + restart_counter
            nfev_start = problem.consumed_evaluations
            exhausted, stop = _run_local_cma(
                problem, start.phenome, step_size, cma_seed
            )
            restart_log.append({
                "epoch": int(epoch),
                "restart": int(restart_counter),
                "cma_seed": int(cma_seed),
                "sigma0_unit": float(step_size),
                "nfev_start": int(nfev_start),
                "nfev_end": int(problem.consumed_evaluations),
                "stop": stop,
            })
            restart_counter += 1

            if exhausted:
                budget_exhausted = True
                break

        epoch += 1
        if budget_exhausted:
            break

    recorder.finalize()
    if recorder.nfev > maxevals:
        raise AssertionError(
            f"hard budget violated: {recorder.nfev} > {maxevals}"
        )

    return (
        int(logical_seed),
        float(recorder.best_err),
        recorder.improvements,
        int(recorder.nfev),
        int(epoch),
        int(restart_counter),
        int(internal_seed),
        restart_log,
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Public Preuss/Wessing NEA2+ Python implementation ported "
            "to the project's CEC fixed-budget protocol."
        )
    )
    parser.add_argument(
        "--suite",
        required=True,
        choices=["cec2017", "cec2020", "cec2022"],
    )
    parser.add_argument("--dim", type=int, required=True)
    parser.add_argument("--functions", required=True,
                        help="Comma-separated list, e.g. 1,3,4 or f1,f3,f4")
    parser.add_argument("--runs", type=int, default=51)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--maxevals", type=int, default=0,
                        help="0 = suite- and dimension-specific default")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--outdir", default="",
                        help="Override output directory")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--logs", action="store_true",
                        help="Per-epoch output; use with --runs 1 --jobs 1")
    return parser


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    if maxevals <= GLOBAL_SAMPLE_SIZE:
        raise ValueError(
            f"maxevals={maxevals} must exceed M={GLOBAL_SAMPLE_SIZE}"
        )
    if args.suite == "cec2017" and any(f == 2 for f in fnums):
        print(
            "WARNING: CEC2017 f2 was withdrawn; exclude it from the "
            "publication comparison.",
            file=sys.stderr,
        )

    outdir = args.outdir or build_outdir(
        args.suite,
        args.dim,
        ALGO,
        maxevals,
        base=os.path.join(_ROOT, "experiments"),
    )

    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f"f{fnum}.pkl")
            if os.path.exists(path):
                print(
                    f"ERROR: {path} already exists. Use --force to overwrite.",
                    file=sys.stderr,
                )
                return 1

    print_header(
        args.suite, args.dim, ALGO, maxevals, args.runs, args.jobs
    )
    print(
        "Variant: public nea2.py/nea2plus (2016)  "
        f"M={GLOBAL_SAMPLE_SIZE} maximin  phi={EDGE_LENGTH_FACTOR}  "
        "rules=1,2  rule1-ref=mean-NB-edge  basins=best-first  "
        "cma=1.1.06  tolfun=1e-6"
    )

    params_record = {
        "cli_args": vars(args),
        "variant": "public-nea2plus-python-2016-cec-port",
        "algorithm_label": ALGO,
        "public_archive_url": PUBLIC_ARCHIVE_URL,
        "public_archive_sha256": PUBLIC_ARCHIVE_SHA256,
        "global_sample_size": GLOBAL_SAMPLE_SIZE,
        "sampling": (
            "diversipy 0.5 maximin_reconstruction; i.i.d.-uniform "
            "initial design; num_steps=None (100*M); default L1 "
            "toroidal distance; fresh sample per epoch"
        ),
        "historical_exception_policy": (
            "catch StopIteration/ValueError from local CMA; retain recorder "
            "incumbent; evaluate x0 once only if CMA consumed zero FEs"
        ),
        "normalized_domain": "[0,1]^D; reflection; affine CEC map",
        "edge_length_factor": EDGE_LENGTH_FACTOR,
        "used_rules": USED_RULES,
        "rule1_reference": "mean nearest-better edge length (Preuss2012)",
        "rule2": "public evoalgos 0.6 median incoming-edge rule",
        "basin_order": "graph minima sorted by objective, best first",
        "cma_start": "one graph-minimum point",
        "sigma0_rule": (
            "max(0.025*sqrt(D), Normal(0.05*sqrt(D), "
            "0.025*sqrt(D))) in unit cube"
        ),
        "cma_version": getattr(cma, "__version__", "unknown"),
        "diversipy_version": getattr(diversipy, "__version__", "0.5"),
        "evoalgos_version": getattr(evoalgos, "__version__", "0.6"),
        "optproblems_version": getattr(optproblems, "__version__", "0.9"),
        "cma_stops": "bundled defaults, tolfun=1e-6; no local restarts",
        "seed_rule": "21062016 + 100*fnum + logical_seed",
        "epoch_gate": "start fresh M-sample iff remaining_evaluations > M",
        "budget": (
            "hard cap owned by scalar problem wrapper; native epoch gate "
            "may leave <=M evaluations unused"
        ),
        "interpretation": (
            "Port of public NEA2+ Python code; not exact NEA2-2012 phi=2"
        ),
    }

    summary_rows = []
    for fnum in fnums:
        func_name = f"f{fnum}"
        print(f"-- {func_name} --", flush=True)
        started = time.time()

        # The legacy cma.py must already be imported after the Python-3
        # compatibility aliases above.  joblib's default ``loky`` workers
        # may import it while unpickling, before those aliases run.  The
        # multiprocessing backend forks this initialized process and also
        # preserves the public code's process-isolated global RNG streams.
        results = Parallel(n_jobs=args.jobs, backend="multiprocessing")(
            delayed(_run_seed)(
                args.suite,
                fnum,
                args.dim,
                maxevals,
                seed,
                disp=args.logs,
            )
            for seed in seeds
        )
        elapsed = time.time() - started
        results.sort(key=lambda item: item[0])

        ret_seeds = np.asarray([r[0] for r in results], dtype=np.int64)
        errors = np.asarray([r[1] for r in results], dtype=np.float64)
        improvements = [r[2] for r in results]
        nfev_total = np.asarray([r[3] for r in results], dtype=np.int64)
        n_epochs_started = np.asarray([r[4] for r in results], dtype=np.int64)
        n_restarts = np.asarray([r[5] for r in results], dtype=np.int64)
        internal_seeds = np.asarray([r[6] for r in results], dtype=np.int64)
        restart_logs = [r[7] for r in results]

        _, bias, _ = suite_config(args.suite, fnum, args.dim)
        path = write_function_pkl(
            outdir=outdir,
            suite=args.suite,
            dim=args.dim,
            func_name=func_name,
            f_opt=bias,
            algorithm=ALGO,
            maxevals=maxevals,
            seeds=ret_seeds,
            errors=errors,
            improvements=improvements,
            params=params_record,
            extra_meta={
                "internal_seeds": internal_seeds,
                "n_epochs_started_per_seed": n_epochs_started,
                "n_local_cma_per_seed": n_restarts,
                "restart_logs_per_seed": restart_logs,
            },
            force=args.force,
            nfev_total_per_seed=nfev_total,
        )

        print_func_result(func_name, errors, elapsed)
        print(
            f"       nfev=[{nfev_total.min()},{nfev_total.max()}] "
            f"epochs-started=[{n_epochs_started.min()},"
            f"{n_epochs_started.max()}] "
            f"local-CMA=[{n_restarts.min()},{n_restarts.max()}]",
            flush=True,
        )
        print(f"       -> {path}", flush=True)
        summary_rows.append(
            summary_row(func_name, errors, elapsed, maxevals)
        )

    csv_path = write_summary_csv(outdir, summary_rows)
    print()
    print(f"Summary -> {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
