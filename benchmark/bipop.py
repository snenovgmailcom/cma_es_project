#!/usr/bin/env python3
"""
benchmark/bipop.py — BIPOP-CMA-ES benchmark runner (pycma reference).

Uses Hansen's official BIPOP-CMA-ES via cma.fmin2(bipop=True). No custom
restart logic; algorithm behaviour matches pycma reference.

Writes to experiments/<suite>/d<dim>/BIPOP-CMA-pycma/maxevals_<N>/.

Usage
-----
    python benchmark/bipop.py --suite cec2020 --dim 10 \\
        --functions 1,2,3,4,5,6,7,8,9,10 \\
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

# Put benchmark/ on sys.path for _common.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from _common import (
    ALGO_BIPOP, ImprovementRecorder, build_outdir,
    parse_functions, print_func_result, print_header,
    suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)

import cma  # pycma


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, sigma0_arg, restarts):
    """Run one BIPOP-CMA-ES seed. Returns (seed, final_err, improvements).

    sigma0_arg:
        'auto'  -> sigma0 = (ub - lb) / 4   (Hansen recommendation)
        float   -> explicit sigma0
    """
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    lb = bounds[:, 0].tolist()
    ub = bounds[:, 1].tolist()

    # Resolve sigma0. Bounds are per-axis but (so far) uniform per function;
    # take the min range across axes for a safe scalar.
    if isinstance(sigma0_arg, str) and sigma0_arg.strip().lower() == 'auto':
        rng_min = float((bounds[:, 1] - bounds[:, 0]).min())
        sigma0 = rng_min / 4.0
    else:
        sigma0 = float(sigma0_arg)

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)
    rng = np.random.default_rng(seed)

    # Hansen's recommended: callable x0 = fresh random point per restart.
    def random_x0():
        return rng.uniform(bounds[:, 0], bounds[:, 1])

    # Batch objective via recorder (pycma parallel_objective convention).
    def batch_objective(X):
        return [float(f) for f in recorder([x.tolist() for x in X])]

    opts = {
        'seed':                int(seed),
        'maxfevals':           int(maxevals),
        'bounds':              [lb, ub],
        'tolfun':              1e-12,
        'tolx':                1e-12,
        'verbose':             -9,
        'verb_disp':           0,
        'verb_log':            0,
        'verb_plot':           0,
        'verb_time':           0,
        'verb_filenameprefix': os.devnull,
    }

    try:
        cma.fmin2(
            None,
            random_x0,
            sigma0,
            options=opts,
            parallel_objective=batch_objective,
            bipop=True,
            restarts=restarts,
        )
    except Exception as exc:
        # Defensive: if pycma blows up on some seed, record what we have.
        print(f"  WARN seed {seed}: {type(exc).__name__}: {exc}",
              file=sys.stderr)

    recorder.finalize()
    return seed, recorder.best_err, recorder.improvements


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='BIPOP-CMA-ES (pycma) benchmark runner.',
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

    # BIPOP-specific
    p.add_argument('--sigma0', type=str, default='auto',
                   help="Initial step size. 'auto' = (ub-lb)/4 per-func "
                        "(Hansen: 50 for [-100,100]; scales for CEC2019 "
                        "heterogeneous bounds). Or an explicit float.")
    p.add_argument('--restarts', type=int, default=9,
                   help="BIPOP restart schedule length (Hansen default: 9)")
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))

    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    outdir = args.outdir or build_outdir(
        args.suite, args.dim, ALGO_BIPOP, maxevals)

    # Overwrite pre-check.
    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f"ERROR: {path} already exists. "
                      f"Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, ALGO_BIPOP,
                 maxevals, args.runs, args.jobs)
    print(f"BIPOP params: sigma0={args.sigma0}  restarts={args.restarts}")
    print(f"Outdir: {outdir}")
    print()

    summary_rows = []
    params_record = {
        'cli_args':      vars(args),
        'bipop_config':  {
            'sigma0':    args.sigma0,
            'restarts':  args.restarts,
            'tolfun':    1e-12,
            'tolx':      1e-12,
            'algo_source': f'cma.fmin2(bipop=True, restarts={args.restarts})',
        },
    }

    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f"── {func_name} ──", flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals,
                               s, args.sigma0, args.restarts)
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
            algorithm=ALGO_BIPOP,
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
