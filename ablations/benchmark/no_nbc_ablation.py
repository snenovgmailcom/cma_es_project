#!/usr/bin/env python3
"""
ablations/benchmark/no_nbc_ablation.py -- NO-NBC ablation runner.

Ablation semantics (fixed by S.N., 13.08.2026):
    1. Evaluate M = 4096 Sobol points. Same sampler call and seed
       convention as FULL's cycle-0 Phase-0 (cycle seed = run seed), so
       for equal run seeds the sample is identical to FULL's first sample.
    2. Sort the points ascending by f.
    3. Sequentially start classic CMA-ES from x_(1), x_(2), ... until the
       budget is exhausted; the start index wraps (k mod M).
    No basins, no C/B cycles, no reuse, no k-NN vote, no exclusion,
    no refinement.

Per-restart settings (confirmed 13.08.2026):
    sigma0  = median(u - l) / 4          (BIPOP default initial step size)
    popsize = 4 + floor(3 ln D)          (Hansen default lambda_H)
    stops   = pycma defaults; the global budget terminates the run
    CMA seed of restart k = run_seed + k * 1000 (FULL convention)

Output: ablations/experiments/<suite>/d<dim>/NO-NBC/maxevals_<N>/f<k>.pkl
plus summary.csv, both in the root _common schema. Existing pkl files
cause an error unless --force is passed.
NOTE: write_summary_csv keeps only the rows of the current invocation --
run complete function sets per output dir.

Usage
-----
    python ablations/benchmark/no_nbc_ablation.py --suite cec2017 --dim 10 \\
        --functions 1,3,4,5,6,7,8,9,10 --runs 51 --jobs 51
"""

import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

# ablations/benchmark/ -> ablations/ -> repo root; import root modules.
_ABL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_ABL_DIR)
for _p in (os.path.join(_ROOT, 'algorithms'),
           os.path.join(_ROOT, 'benchmark')):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import cma  # noqa: E402

from basin_detector import sample_points  # noqa: E402
from _common import (  # noqa: E402
    ImprovementRecorder, build_outdir, parse_functions, print_func_result,
    print_header, suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)

ALGO = 'NO-NBC'
N_PHASE0 = 4096


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, disp=False):
    """Run one NO-NBC seed.

    Returns: (seed, final_err, improvements, nfev_total, n_restarts)
    """
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)
    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)

    bounds = np.asarray(bounds, dtype=float)
    lower, upper = bounds[:, 0], bounds[:, 1]

    # 1. Phase-0 sample: identical call to FULL cycle 0 for equal seeds.
    points = sample_points(dim, N_PHASE0, bounds, seed, method='sobol')
    fvals = np.asarray(recorder(points), dtype=float)
    M = len(points)

    # 2. Sort ascending by f (stable for reproducible tie order).
    order = np.argsort(fvals, kind='stable')

    # 3. Classic CMA-ES restarts down the sorted list.
    sigma0 = float(np.median(upper - lower)) / 4.0
    popsize = 4 + int(3 * np.log(dim))
    bounds_list = [lower.tolist(), upper.tolist()]

    n_restarts = 0
    k = 0
    while recorder.nfev < maxevals:
        x0 = points[order[k % M]].copy()
        opts = {
            'seed':      seed + k * 1000,
            'maxfevals': maxevals - recorder.nfev,
            'bounds':    bounds_list,
            'popsize':   popsize,
            'verbose':   -9,
            'verb_disp': 0, 'verb_log': 0,
            'verb_plot': 0, 'verb_time': 0,
        }
        nfev_before = recorder.nfev
        stop_reason = 'budget'
        try:
            es = cma.CMAEvolutionStrategy(x0, sigma0, opts)
            while not es.stop() and recorder.nfev < maxevals:
                X = es.ask()
                F = recorder(np.asarray(X, dtype=float))
                es.tell(X, F)
            if es.stop():
                stop_reason = next(iter(es.stop()), 'budget')
        except Exception as exc:
            stop_reason = f'exception:{type(exc).__name__}'
            if recorder.nfev == nfev_before:
                # No evaluations consumed: abort instead of spinning.
                print(f'ERROR seed={seed} f{fnum}: restart {k} consumed '
                      f'0 evals ({stop_reason}); aborting seed.',
                      file=sys.stderr)
                break

        n_restarts += 1
        if disp:
            print(f'  seed={seed} R{k} x0#{int(order[k % M])} '
                  f'nfev={recorder.nfev - nfev_before} '
                  f'best_err={recorder.best_err:.4e} stop={stop_reason}')
        k += 1

    return (seed, recorder.best_err, recorder.improvements,
            int(recorder.nfev), int(n_restarts))


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='NO-NBC ablation runner (sorted classic CMA-ES '
                    'multistart over one Sobol sample).')
    p.add_argument('--suite', required=True,
                   choices=['cec2014', 'cec2017', 'cec2019', 'cec2020',
                            'cec2022'])
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--functions', type=str, required=True,
                   help="Comma-separated: '1,2,3' or 'f1,f2,f3'")
    p.add_argument('--runs', type=int, default=51)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--maxevals', type=int, default=0,
                   help='0 = use suite default')
    p.add_argument('--jobs', type=int, default=1)
    p.add_argument('--outdir', type=str, default='',
                   help='Override output directory (default: '
                        'ablations/experiments/<suite>/d<dim>/NO-NBC/'
                        'maxevals_<N>/)')
    p.add_argument('--force', action='store_true')
    p.add_argument('--logs', action='store_true',
                   help='Per-restart output. Best with --runs 1 --jobs 1.')
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    if maxevals <= N_PHASE0:
        print(f'ERROR: maxevals={maxevals} must exceed the Phase-0 sample '
              f'size ({N_PHASE0}).', file=sys.stderr)
        sys.exit(1)

    outdir = args.outdir or build_outdir(
        args.suite, args.dim, ALGO, maxevals,
        base=os.path.join(_ABL_DIR, 'experiments'))

    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f'ERROR: {path} already exists. Use --force to '
                      f'overwrite.', file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, ALGO, maxevals, args.runs, args.jobs)
    print(f'Variant: no-nbc  M={N_PHASE0} sobol  sigma0=(u-l)/4  '
          f'popsize=4+floor(3lnD)  stops=pycma defaults')

    params_record = {
        'cli_args':       vars(args),
        'variant':        'no-nbc',
        'n_phase0':       N_PHASE0,
        'sampling':       'sobol, seed = run seed (== FULL cycle-0 sample)',
        'sigma0_rule':    'median(u-l)/4',
        'popsize_rule':   '4 + floor(3 ln D)',
        'cma_stops':      'pycma defaults; global budget terminates',
        'cma_seed_rule':  'run_seed + k*1000',
        'start_order':    'f-ascending, index wraps k mod M',
    }

    summary_rows = []
    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f'-- {func_name} --', flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals, s,
                               disp=args.logs)
            for s in seeds
        )
        elapsed = time.time() - t0

        results.sort(key=lambda t: t[0])
        ret_seeds = np.array([r[0] for r in results], dtype=np.int64)
        errors = np.array([r[1] for r in results], dtype=np.float64)
        imps = [r[2] for r in results]
        nfev_total_arr = np.array([r[3] for r in results], dtype=np.int64)
        n_restarts_arr = np.array([r[4] for r in results], dtype=np.int64)

        _, bias, _ = suite_config(args.suite, fnum, args.dim)
        path = write_function_pkl(
            outdir=outdir, suite=args.suite, dim=args.dim,
            func_name=func_name, f_opt=bias, algorithm=ALGO,
            maxevals=maxevals, seeds=ret_seeds, errors=errors,
            improvements=imps, params=params_record,
            extra_meta={'n_restarts_per_seed': n_restarts_arr},
            force=args.force,
            nfev_total_per_seed=nfev_total_arr,
        )

        print_func_result(func_name, errors, elapsed)
        print(f'       -> {path}', flush=True)
        summary_rows.append(summary_row(func_name, errors, elapsed, maxevals))

    csv_path = write_summary_csv(outdir, summary_rows)
    print()
    print(f'Summary -> {csv_path}')


if __name__ == '__main__':
    main()
