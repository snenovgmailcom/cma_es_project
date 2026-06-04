#!/usr/bin/env python3
"""
benchmark/msc.py — MSC-CMA-ES benchmark runner.

Two modes, both built from the B and C class configs in algorithms.auto_config
(sigma_divisor scaled per dim by sqrt(10/D)):

    default            alt-CB scheduler: cycle C / B / C / B ... indefinitely.
                       Output → experiments/<suite>/d<dim>/MSC-CMA/maxevals_<N>/
    --conly            C-class only (single config, no alternation, no reuse).
                       Output → experiments/<suite>/d<dim>/MSC-CMA-Conly/maxevals_<N>/

The output algorithm folder self-labels the mode, so alt-CB and C-only results
never share a directory.

Usage
-----
    python benchmark/msc.py --suite cec2017 --dim 10 \\
        --functions 1,2,3,4,5,6,7,8,9,10 --runs 51 --jobs 51

    python benchmark/msc.py --suite cec2017 --dim 10 \\
        --functions f21,f22 --runs 51 --maxevals 400000 --conly --force

One output file per function: f<k>.pkl, plus a summary.csv in the same dir.
Existing f<k>.pkl files cause an error unless --force is passed.
"""

import argparse
import dataclasses
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

# Put algorithms/ and benchmark/ on sys.path.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_THIS_DIR, '..', 'algorithms'), _THIS_DIR):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from _common import (
    ALGO_MSC, ALGO_MSC_CONLY, ImprovementRecorder, build_outdir,
    parse_functions, print_func_result, print_header,
    suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)

from auto_config import get_B, get_C
from msc_cma import MSC_CMA


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, cfg_C, cfg_B, conly,
              disp=False):
    """Run one MSC-CMA seed.

    cfg_C / cfg_B are prebuilt, per-dim class configs (cfg_B is None for
    --conly).  Returns:
        (seed, final_err, improvements, popsize_hist, cycles_dicts,
         pre_refine_err, nfev_pre_refine, nfev_total)
    """
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)
    if conly:
        solver = MSC_CMA(recorder, bounds, maxevals, seed=seed,
                         config=cfg_C, mode_schedule=None, disp=disp)
    else:
        solver = MSC_CMA(recorder, bounds, maxevals, seed=seed,
                         config=cfg_C, mode_schedule=[cfg_C, cfg_B], disp=disp)

    result = solver.solve()
    recorder.finalize()

    cycles_dicts = [c.as_dict() for c in result.cycles]

    # Pre-refine error: raw f-space best_f_pre_refine minus bias (matches the
    # `errors` convention). Stays inf if no cycle ran.
    pre_refine_err = float(result.best_f_pre_refine) - float(bias)
    nfev_pre_refine = int(result.cycles[-1].nfev_end) if result.cycles else 0
    nfev_total = int(solver.nfev)

    return (seed, recorder.best_err, recorder.improvements,
            dict(solver.popsize_hist),
            cycles_dicts, pre_refine_err, nfev_pre_refine, nfev_total)


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='MSC-CMA-ES benchmark runner.',
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
    p.add_argument('--jobs', type=int, default=1,
                   help='Parallel seeds (joblib)')
    p.add_argument('--outdir', type=str, default='',
                   help='Override output directory (default: '
                        'experiments/<suite>/d<dim>/<algo>/maxevals_<N>/)')
    p.add_argument('--force', action='store_true',
                   help='Overwrite existing pkl files')
    p.add_argument('--conly', action='store_true',
                   help='C-class only (single config, no C/B alternation). '
                        'Default (no flag) is the alt-CB scheduler.')
    p.add_argument('--sampling-method', choices=['lhs', 'sobol', 'halton'],
                   default=None,
                   help='Override Phase-0 sampling for both B and C '
                        '(default: each class keeps its own, currently sobol).')
    p.add_argument('--popsize-hist', action='store_true',
                   help='Print aggregated popsize histogram per function.')
    p.add_argument('--logs', action='store_true',
                   help='Verbose per-cycle/per-restart output from MSC_CMA. '
                        'Best with --runs 1 --jobs 1.')
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    # Build the per-dim class configs once (shared across functions/seeds).
    cfg_C = get_C(args.dim)
    cfg_B = None if args.conly else get_B(args.dim)
    if args.sampling_method:
        cfg_C = dataclasses.replace(cfg_C, sampling_method=args.sampling_method)
        if cfg_B is not None:
            cfg_B = dataclasses.replace(cfg_B,
                                        sampling_method=args.sampling_method)

    algo = ALGO_MSC_CONLY if args.conly else ALGO_MSC
    outdir = args.outdir or build_outdir(args.suite, args.dim, algo, maxevals)

    # Overwrite pre-check — catch early before running expensive seeds.
    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f"ERROR: {path} already exists. Use --force to "
                      f"overwrite.", file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, algo, maxevals, args.runs, args.jobs)
    if args.conly:
        print(f"Config: --conly (C-class single)  {cfg_C.summary()}")
    else:
        print(f"Config: alt-CB (cycle C/B)  C[{cfg_C.summary()}]  "
              f"B[{cfg_B.summary()}]")

    params_record = {
        'cli_args': vars(args),
        'mode':     'C-only' if args.conly else 'alt-CB',
        'config_C': dataclasses.asdict(cfg_C),
        'config_B': dataclasses.asdict(cfg_B) if cfg_B is not None else None,
    }

    summary_rows = []
    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f"── {func_name} ──", flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals,
                               s, cfg_C, cfg_B, args.conly, disp=args.logs)
            for s in seeds
        )
        elapsed = time.time() - t0

        results.sort(key=lambda t: t[0])
        ret_seeds = np.array([r[0] for r in results], dtype=np.int64)
        errors    = np.array([r[1] for r in results], dtype=np.float64)
        imps      = [r[2] for r in results]
        cycles_per_seed   = [r[4] for r in results]
        pre_refine_errors = np.array([r[5] for r in results], dtype=np.float64)
        nfev_pre_refine_arr = np.array([r[6] for r in results], dtype=np.int64)
        nfev_total_arr      = np.array([r[7] for r in results], dtype=np.int64)

        # Aggregate popsize histograms across seeds for this function.
        agg_hist: dict = {}
        for r in results:
            for k, v in r[3].items():
                agg_hist[k] = agg_hist.get(k, 0) + v

        _, bias, _ = suite_config(args.suite, fnum, args.dim)
        path = write_function_pkl(
            outdir=outdir,
            suite=args.suite,
            dim=args.dim,
            func_name=func_name,
            f_opt=bias,
            algorithm=algo,
            maxevals=maxevals,
            seeds=ret_seeds,
            errors=errors,
            improvements=imps,
            params=params_record,
            force=args.force,
            cycles_per_seed=cycles_per_seed,
            pre_refine_errors_per_seed=pre_refine_errors,
            nfev_pre_refine_per_seed=nfev_pre_refine_arr,
            nfev_total_per_seed=nfev_total_arr,
        )

        print_func_result(func_name, errors, elapsed)
        print(f"       → {path}", flush=True)
        if args.popsize_hist and agg_hist:
            hist_str = " ".join(f"{k}:{v}" for k, v in sorted(agg_hist.items()))
            print(f"       popsize_hist: {hist_str}", flush=True)

        summary_rows.append(summary_row(func_name, errors, elapsed, maxevals))

    csv_path = write_summary_csv(outdir, summary_rows)
    print()
    print(f"Summary → {csv_path}")


if __name__ == '__main__':
    main()
