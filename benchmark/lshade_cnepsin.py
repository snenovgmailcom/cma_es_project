#!/usr/bin/env python3
"""
benchmark/lshade_cnepsin.py — LSHADE-cnEpSin (Awad, Ali, Suganthan 2017)
benchmark runner using minionpy's C++ backend as reference implementation.

LSHADE-cnEpSin extends LSHADE with two mechanisms: an ensemble of sinusoidal
schemes for adapting the scaling factor F (mixing a non-adaptive decreasing
and an adaptive increasing scheme), and a covariance-matrix-based crossover
operator constructed from a Euclidean neighborhood around the current best.
It ranked third in the CEC2017 competition and is particularly strong at
high dimensions on rotated, non-separable landscapes. Per the ARRDE v3
paper, LSHADE-cnEpSin wins all three metrics (E, R, S) at CEC2017 D=100.

NOTE on relTol:
    minionpy.Minimizer has a global early-stop criterion `relTol` (default
    1e-4). We pass relTol=0.0 explicitly for configuration consistency
    across all DE wrappers.

Writes to experiments/<suite>/d<dim>/LSHADE-cnEpSin-minionpy/maxevals_<N>/.

Usage
-----
    python benchmark/lshade_cnepsin.py --suite cec2017 --dim 50 \\
        --functions 1,3,4,5,6,7,8,9,10 \\
        --runs 51 --jobs 51

Overwrite protection: existing f<k>.pkl files cause an error unless
--force is passed.
"""

import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from _common import (
    ALGO_LSHADE_CNEPSIN, ImprovementRecorder, build_outdir,
    parse_functions, print_func_result, print_header,
    suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)

from minionpy import Minimizer


_REL_TOL = 0.0


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed):
    """Run one LSHADE-cnEpSin seed. Returns (seed, final_err, improvements)."""
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    lb = bounds[:, 0].tolist()
    ub = bounds[:, 1].tolist()
    bounds_pairs = list(zip(lb, ub))

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)

    def objective(X):
        return [float(f) for f in recorder(X)]

    try:
        Minimizer(
            objective,
            bounds_pairs,
            x0=[],
            algo='LSHADE_cnEpSin',
            relTol=_REL_TOL,
            maxevals=maxevals,
            seed=int(seed),
        ).optimize()
    except Exception as exc:
        print(f"  WARN seed {seed}: {type(exc).__name__}: {exc}",
              file=sys.stderr)

    recorder.finalize()
    return seed, recorder.best_err, recorder.improvements


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='LSHADE-cnEpSin (minionpy C++) benchmark runner.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument('--suite', required=True,
                   choices=['cec2014', 'cec2017', 'cec2019', 'cec2020', 'cec2022'])
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--functions', type=str, required=True,
                   help="Comma-separated: '1,2,3' or 'f1,f2,f3'")
    p.add_argument('--runs', type=int, default=51)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--maxevals', type=int, default=0,
                   help='0 = use suite default')
    p.add_argument('--jobs', type=int, default=1)
    p.add_argument('--outdir', type=str, default='')
    p.add_argument('--force', action='store_true')
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))

    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    outdir = args.outdir or build_outdir(
        args.suite, args.dim, ALGO_LSHADE_CNEPSIN, maxevals)

    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f"ERROR: {path} already exists. "
                      f"Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, ALGO_LSHADE_CNEPSIN,
                 maxevals, args.runs, args.jobs)
    print(f"Outdir: {outdir}")
    print(f"relTol: {_REL_TOL}  (minionpy early-stop disabled)")
    print()

    summary_rows = []
    params_record = {
        'cli_args':              vars(args),
        'lshade_cnepsin_config': {
            'algo_source': 'minionpy.Minimizer(algo="LSHADE_cnEpSin")',
            'relTol':      _REL_TOL,
        },
    }

    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f"── {func_name} ──", flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals, s)
            for s in seeds
        )
        elapsed = time.time() - t0

        results.sort(key=lambda t: t[0])
        ret_seeds = np.array([r[0] for r in results], dtype=np.int64)
        errors    = np.array([r[1] for r in results], dtype=np.float64)
        imps      = [r[2] for r in results]

        _, bias, _ = suite_config(args.suite, fnum, args.dim)
        path = write_function_pkl(
            outdir=outdir,
            suite=args.suite,
            dim=args.dim,
            func_name=func_name,
            f_opt=bias,
            algorithm=ALGO_LSHADE_CNEPSIN,
            maxevals=maxevals,
            seeds=ret_seeds,
            errors=errors,
            improvements=imps,
            params=params_record,
            force=args.force,
        )

        print_func_result(func_name, errors, elapsed)
        print(f"       → {path}", flush=True)

        summary_rows.append(summary_row(func_name, errors, elapsed, maxevals))

    csv_path = write_summary_csv(outdir, summary_rows)
    print()
    print(f"Summary → {csv_path}")


if __name__ == '__main__':
    main()
