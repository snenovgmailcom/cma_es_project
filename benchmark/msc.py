#!/usr/bin/env python3
"""
benchmark/msc.py — MSC-CMA-ES benchmark runner (rewrite).

Schedule over the three specialists B / H / C (auto_config.CLASS_PARAMS, sigma
scaled per dim by sqrt(10/D)):

    --schedule BHC     three-way rotation B→H→C→…   (default; algo 'MSC-CMA')
    --schedule H       single specialist            (algo 'MSC-CMA-Honly')
    --schedule HC, ... any combination of B/H/C letters

    --cycle-cap / --no-cycle-cap   soft per-cycle Phase-1 budget cap (default on)

Configuration comes from auto_config.CLASS_PARAMS (the champions live in code);
the Optuna tuner overrides per label via run_experiment(overrides=...) directly.

The core is `run_experiment(...)`, a library function used BOTH by this CLI and
by the Optuna objective in-process. With save_dir=None it computes only (no PKL),
returning raw per-function results (errors + per-seed arrays) for FBTC.

Usage
-----
    python benchmark/msc.py --suite cec2017 --dim 10 \\
        --functions $(seq -s, 1 30) --runs 51 --jobs 51

    python benchmark/msc.py --suite cec2017 --dim 10 --schedule H \\
        --functions $(seq -s, 11 20) --runs 51 --force
"""

import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

# Put algorithms/ and benchmark/ on sys.path (also enables the dd_cma import).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_THIS_DIR, '..', 'algorithms'), _THIS_DIR):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from _common import (
    ALGO_MSC, ImprovementRecorder, build_outdir, parse_functions,
    print_func_result, print_header, suite_config, suite_default_maxevals,
    summary_row, write_function_pkl, write_summary_csv,
)

from auto_config import REFINE_FRAC, build_config, build_schedule
from msc_cma import MSC_CMA


# =========================================================================
# Labelling
# =========================================================================

def algo_label(schedule: str) -> str:
    """Output algo folder name. Canonical BHC → 'MSC-CMA'; single → 'MSC-CMA-Xonly'."""
    schedule = schedule.upper()
    if schedule == 'BHC':
        return ALGO_MSC
    if len(schedule) == 1:
        return f'MSC-CMA-{schedule}only'
    return f'MSC-CMA-{schedule}'


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, schedule_cfgs, schedule_labels,
              cycle_cap, refine_frac, bias, disp=False):
    """Run one MSC-CMA seed. Returns the per-seed result tuple."""
    cec_cls, _bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)
    solver = MSC_CMA(
        recorder, bounds, maxevals, seed=seed,
        schedule=schedule_cfgs, schedule_labels=schedule_labels,
        cycle_cap=cycle_cap, refine_frac=refine_frac, disp=disp,
    )
    result = solver.solve()
    recorder.finalize()

    cycles_dicts = [c.as_dict() for c in result.cycles]
    pre_refine_err = float(result.best_f_pre_refine) - float(bias)
    nfev_pre_refine = int(result.cycles[-1].nfev_end) if result.cycles else 0
    nfev_total = int(solver.nfev)

    return (seed, recorder.best_err, recorder.improvements,
            dict(solver.popsize_hist), cycles_dicts, pre_refine_err,
            nfev_pre_refine, nfev_total)


# =========================================================================
# Library core — used by the CLI and by the Optuna objective (in-process)
# =========================================================================

def run_experiment(*, suite, dim, functions, maxevals, seeds,
                   schedule='BHC', overrides=None, jobs=1, cycle_cap=True,
                   refine_frac=None, save_dir=None, force=False,
                   params_record=None, disp=False) -> dict:
    """Run schedule over functions×seeds. Returns {fnum: {...}}.

    overrides : {label: {param: value}} layered on CLASS_PARAMS via build_config
                (one Optuna trial → overrides={label: trial_params}).
    save_dir  : None → compute only (no PKL) — the Optuna path.
                str  → also write f<k>.pkl + summary.csv — the CLI path.
    Each result carries 'errors' (np.ndarray over seeds) plus the per-seed arrays
    the PKL and FBTC need.
    """
    schedule = schedule.upper()
    refine_frac = REFINE_FRAC if refine_frac is None else float(refine_frac)
    overrides = overrides or {}

    # Build per-label configs once (dim-scaled, overrides applied), then the
    # schedule list + labels the solver stamps on each cycle.
    labels = sorted(set(schedule))
    cfgs = {lab: build_config(lab, dim, overrides.get(lab)) for lab in labels}
    schedule_cfgs = [cfgs[ch] for ch in schedule]
    schedule_labels = list(schedule)

    out = {}
    summary_rows = []
    for fnum in functions:
        func_name = f'f{fnum}'
        _cls, bias, _bounds = suite_config(suite, fnum, dim)

        t0 = time.time()
        results = Parallel(n_jobs=jobs)(
            delayed(_run_seed)(suite, fnum, dim, maxevals, s, schedule_cfgs,
                               schedule_labels, cycle_cap, refine_frac, bias, disp)
            for s in seeds
        )
        elapsed = time.time() - t0
        results.sort(key=lambda t: t[0])

        ret_seeds = np.array([r[0] for r in results], dtype=np.int64)
        errors    = np.array([r[1] for r in results], dtype=np.float64)
        imps      = [r[2] for r in results]
        cycles_ps = [r[4] for r in results]
        pre_err   = np.array([r[5] for r in results], dtype=np.float64)
        nfev_pre  = np.array([r[6] for r in results], dtype=np.int64)
        nfev_tot  = np.array([r[7] for r in results], dtype=np.int64)

        agg_hist: dict = {}
        for r in results:
            for k, v in r[3].items():
                agg_hist[k] = agg_hist.get(k, 0) + v

        out[fnum] = {
            'errors': errors, 'seeds': ret_seeds, 'bias': bias,
            'improvements': imps, 'cycles_per_seed': cycles_ps,
            'pre_refine_errors_per_seed': pre_err,
            'nfev_pre_refine_per_seed': nfev_pre,
            'nfev_total_per_seed': nfev_tot,
            'popsize_hist': agg_hist, 'elapsed_sec': elapsed,
        }

        if save_dir is not None:
            write_function_pkl(
                outdir=save_dir, suite=suite, dim=dim, func_name=func_name,
                f_opt=bias, algorithm=params_record.get('algo', algo_label(schedule)),
                maxevals=maxevals, seeds=ret_seeds, errors=errors,
                improvements=imps, params=params_record, force=force,
                cycles_per_seed=cycles_ps, pre_refine_errors_per_seed=pre_err,
                nfev_pre_refine_per_seed=nfev_pre, nfev_total_per_seed=nfev_tot,
            )
            print_func_result(func_name, errors, elapsed)
            summary_rows.append(summary_row(func_name, errors, elapsed, maxevals))

    if save_dir is not None and summary_rows:
        write_summary_csv(save_dir, summary_rows)
    return out


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='MSC-CMA-ES benchmark runner.',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True,
                   choices=['cec2014', 'cec2017', 'cec2019', 'cec2020', 'cec2022'])
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--functions', type=str, required=True,
                   help="Comma-separated: '1,2,3' or 'f1,f2,f3'")
    p.add_argument('--runs', type=int, default=51)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--maxevals', type=int, default=0, help='0 = suite default')
    p.add_argument('--jobs', type=int, default=1, help='Parallel seeds (joblib)')
    p.add_argument('--outdir', type=str, default='')
    p.add_argument('--force', action='store_true', help='Overwrite existing pkl')
    p.add_argument('--schedule', type=str, default='BHC',
                   help="Schedule over B/H/C, e.g. BHC (default), HCB, HC, B, H, C.")
    cap = p.add_mutually_exclusive_group()
    cap.add_argument('--cycle-cap', dest='cycle_cap', action='store_true',
                     help='Enable soft per-cycle Phase-1 budget cap (default).')
    cap.add_argument('--no-cycle-cap', dest='cycle_cap', action='store_false',
                     help='Disable the cap (reactive tolerances only).')
    p.set_defaults(cycle_cap=True)
    p.add_argument('--logs', action='store_true',
                   help='Verbose per-cycle/per-restart output (best with --runs 1).')
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    schedule = args.schedule.upper()
    bad = set(schedule) - set('BHC')
    if not schedule or bad:
        raise SystemExit(f"Invalid --schedule {schedule!r}; use only B/H/C.")

    algo = algo_label(schedule)
    outdir = args.outdir or build_outdir(args.suite, args.dim, algo, maxevals)

    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f"ERROR: {path} already exists. Use --force.", file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, algo, maxevals, args.runs, args.jobs)
    # Materialise the actual configs used (dim-scaled) for the record.
    used = {lab: build_config(lab, args.dim).to_dict()
            for lab in sorted(set(schedule))}
    print(f"Config: schedule={schedule}  cycle_cap={args.cycle_cap}  "
          f"refine_frac={REFINE_FRAC}")
    for lab in sorted(used):
        print(f"  {lab}[{build_config(lab, args.dim).summary()}]")

    params_record = {
        'cli_args':  vars(args),
        'algo':      algo,
        'schedule':  schedule,
        'cycle_cap': args.cycle_cap,
        'refine_frac': REFINE_FRAC,
        # config_B / config_H / config_C (whichever the schedule uses).
        **{f'config_{lab}': used[lab] for lab in used},
    }

    t0 = time.time()
    run_experiment(
        suite=args.suite, dim=args.dim, functions=fnums, maxevals=maxevals,
        seeds=seeds, schedule=schedule, jobs=args.jobs,
        cycle_cap=args.cycle_cap, refine_frac=REFINE_FRAC, save_dir=outdir,
        force=args.force, params_record=params_record, disp=args.logs,
    )
    print(f"\nDone in {time.time()-t0:.1f}s → {outdir}")


if __name__ == '__main__':
    main()
