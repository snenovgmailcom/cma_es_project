#!/usr/bin/env python3
"""
benchmark/rrcma.py — RR-CMA-ES benchmark runner (modcma reference).

Repelling Restart CMA-ES (de Nobel, Vermetten, Kononova, Shir, Bäck, PPSN 2024):
    "Avoiding Redundant Restarts in Multimodal Global Optimization"
    https://doi.org/10.5281/zenodo.10997200

Idea: maintain a tabu archive of previously-converged basins; re-sampling
biased away from them. Mitigates the "Coupon Collector" problem on
multimodal landscapes where naive restart strategies repeatedly land in
already-explored regions.

Implementation: uses modcma's c_maes (C++ binding) ModularCMAES with
modules.repelling_restart = True, on top of a BIPOP base restart strategy
(matches the strongest configuration in the paper's Table 4).

Writes to experiments/<suite>/d<dim>/RR-CMA-modcma/maxevals_<N>/.

Usage
-----
    python benchmark/rrcma.py --suite cec2020 --dim 10 \\
        --functions 1,2,3,4,5,6,7,8,9,10 \\
        --runs 51 --jobs 51

    python benchmark/rrcma.py --suite cec2017 --dim 10 \\
        --functions 1,2,3,4,5 --runs 51 --jobs 51

API source
----------
modcma installed from source at /home/svety/ModularCMAES
- c_maes.parameters.Modules: instance with .repelling_restart bool +
                             .restart_strategy enum (NONE/STOP/RESTART/IPOP/BIPOP)
- c_maes.parameters.Settings(dim): wrapper for problem definition
- c_maes.Parameters(dim_or_settings): top-level wrapper
- c_maes.ModularCMAES(params): main solver, has .run(callable) and .step()

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
    ImprovementRecorder, build_outdir,
    parse_functions, print_func_result, print_header,
    suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)

import modcma  # noqa: E402
from modcma import c_maes  # noqa: E402

# Algorithm name (added here; promote to _common.py once paper is final).
ALGO_RRCMA = 'RR-CMA-modcma'

# Resolve RestartStrategy enum once at import.
# Modules().restart_strategy is an enum value of class RestartStrategy.
_RESTART_STRATEGY_CLS = type(c_maes.parameters.Modules().restart_strategy)
_RESTART_STRATEGY = {
    'NONE':    _RESTART_STRATEGY_CLS.NONE,
    'STOP':    _RESTART_STRATEGY_CLS.STOP,
    'RESTART': _RESTART_STRATEGY_CLS.RESTART,
    'IPOP':    _RESTART_STRATEGY_CLS.IPOP,
    'BIPOP':   _RESTART_STRATEGY_CLS.BIPOP,
}


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, sigma0_arg,
              base_restart, repelling):
    """Run one RR-CMA-ES seed.

    Parameters
    ----------
    sigma0_arg : str | float
        'auto' -> sigma0 = (ub - lb) / 4   (Hansen recommendation)
        float  -> explicit sigma0
    base_restart : str
        Restart strategy on top of which repelling is layered.
        One of {'BIPOP', 'IPOP', 'RESTART'}.
    repelling : bool
        Enable repelling-restart module. False = vanilla BIPOP/IPOP/RESTART
        without tabu archive (useful for ablation).

    Returns
    -------
    (seed, final_err, improvements)
    """
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    lb = bounds[:, 0].astype(np.float64)
    ub = bounds[:, 1].astype(np.float64)

    # Resolve sigma0.
    if isinstance(sigma0_arg, str) and sigma0_arg.strip().lower() == 'auto':
        sigma0 = float((ub - lb).min()) / 4.0
    else:
        sigma0 = float(sigma0_arg)

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)
    rng = np.random.default_rng(seed)

    # modcma's run() expects a single-input callable returning a scalar.
    # We bridge through the (batch-friendly) recorder.
    def objective(x):
        F = recorder([np.asarray(x, dtype=float).tolist()])
        return float(F[0])

    # ── Build modules ────────────────────────────────────────────────
    modules = c_maes.parameters.Modules()
    modules.repelling_restart = bool(repelling)
    modules.restart_strategy = _RESTART_STRATEGY[base_restart]

    # ── Build settings (immutable: all params via constructor) ───────
    settings = c_maes.parameters.Settings(
        dim,
        modules=modules,
        sigma0=sigma0,
        budget=int(maxevals),
        lb=lb,
        ub=ub,
        x0=rng.uniform(lb, ub).astype(np.float64),
        verbose=False,
    )

    # ── Build parameters & solver ────────────────────────────────────
    params = c_maes.Parameters(settings)
    es = c_maes.ModularCMAES(params)

    # ── Run ──────────────────────────────────────────────────────────
    try:
        es.run(objective)
    except Exception as exc:
        # Defensive: record what we have if modcma blows up mid-run.
        print(f"  WARN seed {seed}: {type(exc).__name__}: {exc}",
              file=sys.stderr)

    recorder.finalize()
    return seed, recorder.best_err, recorder.improvements


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='RR-CMA-ES (modcma) benchmark runner.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument('--suite', required=True,
                   choices=['cec2014', 'cec2017', 'cec2019',
                            'cec2020', 'cec2022'])
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

    # RR-CMA-ES specific
    p.add_argument('--sigma0', type=str, default='auto',
                   help="Initial step size. 'auto' = (ub-lb)/4 per-func "
                        "(50 for [-100,100]). Or an explicit float.")
    p.add_argument('--base-restart', type=str, default='BIPOP',
                   choices=['BIPOP', 'IPOP', 'RESTART'],
                   help="Base restart strategy on top of which repelling "
                        "is layered. Paper default: BIPOP.")
    p.add_argument('--no-repelling', action='store_true',
                   help="Disable repelling-restart module. Useful for "
                        "ablation against vanilla BIPOP/IPOP/RESTART.")
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))

    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)
    repelling = not args.no_repelling

    # If repelling is disabled, name the algorithm differently so the
    # output dir doesn't collide with the canonical RR-CMA-ES results.
    if repelling:
        algo_name = ALGO_RRCMA
    else:
        algo_name = f'CMA-{args.base_restart}-modcma-noRR'

    outdir = args.outdir or build_outdir(
        args.suite, args.dim, algo_name, maxevals)

    # Overwrite pre-check.
    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f"ERROR: {path} already exists. "
                      f"Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, algo_name,
                 maxevals, args.runs, args.jobs)
    print(f"RR-CMA params: sigma0={args.sigma0}  "
          f"base_restart={args.base_restart}  repelling={repelling}")
    modcma_path = getattr(modcma, '__file__', 'unknown')
    print(f"modcma path:   {modcma_path}")
    print(f"Outdir: {outdir}")
    print()

    summary_rows = []
    params_record = {
        'cli_args':       vars(args),
        'rrcma_config':   {
            'sigma0':            args.sigma0,
            'base_restart':      args.base_restart,
            'repelling_restart': repelling,
            'modcma_path':       modcma_path,
            'algo_source':       (
                f'modcma.c_maes.ModularCMAES with '
                f'modules.repelling_restart={repelling}, '
                f'restart_strategy=RestartStrategy.{args.base_restart}'
            ),
        },
    }

    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f"── {func_name} ──", flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals,
                               s, args.sigma0, args.base_restart,
                               repelling)
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
            algorithm=algo_name,
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
