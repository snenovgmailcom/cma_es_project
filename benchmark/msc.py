#!/usr/bin/env python3
"""
benchmark/msc.py — MSC-CMA-ES benchmark runner (MSC only, no baselines).

Writes to experiments/<suite>/d<dim>/MSC-CMA/maxevals_<N>/.

Usage
-----
    python benchmark/msc.py --suite cec2020 --dim 10 \\
        --functions 1,2,3,4,5,6,7,8,9,10 \\
        --runs 51 --jobs 51 --auto

    python benchmark/msc.py --suite cec2017 --dim 10 \\
        --functions f22,f28 --runs 51 --maxevals 5000000 --force

--auto: alt-CB scheduler (the only scheduler). Loads cfg_B and cfg_C from
algorithms.auto_config (two global configs, sigma scaled by sqrt(10/D)) and
cycles cfg_C / cfg_B / cfg_C / ... through the solver.  No upfront classifier;
no decision phase.

Without --auto: single-config mode using CLI overrides (--n-phase0, --k, ...)
on top of the default MSCConfig.

One output file per function:   experiments/<path>/f<k>.pkl
Plus a summary.csv in the same directory.

Overwrite protection: existing f<k>.pkl files cause an error unless
--force is passed.
"""

import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

# Put algorithms/ and benchmark/ on sys.path.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_THIS_DIR, '..', 'algorithms'),
           _THIS_DIR):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from _common import (
    ALGO_MSC, ImprovementRecorder, build_outdir,
    parse_functions, print_func_result, print_header,
    suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)

from config import MSCConfig
from msc_cma import MSC_CMA


# =========================================================================
# Worker: single seed
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, cfg_dict, disp=False,
              auto=False,
              refine_frac_override=None,
              refine_mult=1.0,
              sampling_method=None, rotate_sampling=False,
              sobol_n_policy=None,
              enable_phase0_reuse=True,
              tune_class=None, tune_overrides=None,
              anchor=False):
    """Run one MSC-CMA seed.

    Returns (seed, final_err, improvements, popsize_hist,
             cycles_dicts, pre_refine_err,
             nfev_pre_refine, nfev_total).

    cycles_dicts is a list of plain-dict cycle records (see CycleStats.as_dict).
    pre_refine_err is best_f_pre_refine - f_opt (inf if no cycle ran;
    equals final_err if refinement was skipped).
    nfev_pre_refine is self.nfev at end of the last cycle, just before
    refinement (0 if no cycle ran).
    nfev_total is self.nfev after solve() returns (after refinement).

    refine_mult (alt-CB / --auto only):
      Multiplier applied to base refine_frac in both cfg_B and cfg_C
      (passed through to auto_config.get_B/get_C).  Default 1.0 = unchanged.

    tune_class ∈ {None, 'B', 'C'}:
      When set (alt-CB mode), the named class config is loaded from
      auto_config.get_B/get_C and then overridden field-by-field from
      `tune_overrides` (a dict of MSCConfig kwargs).  The OTHER class
      remains pure auto_config base.  Used by the Optuna tuner.
      Requires auto=True.
    """
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)
    if auto:
        # alt-CB scheduler: load cfg_B and cfg_C from auto_config (two global
        # configs, sigma scaled by sqrt(10/D)), then let MSC_CMA cycle cfg_C /
        # cfg_B indefinitely.
        try:
            from algorithms.auto_config import get_B, get_C
            from algorithms.config import MSCConfig as _MSCConfig  # noqa
        except ImportError:  # algorithms/ on sys.path
            from auto_config import get_B, get_C
            from config import MSCConfig as _MSCConfig  # noqa
        cfg_B = get_B(dim, refine_mult=refine_mult)
        cfg_C = get_C(dim, refine_mult=refine_mult)
        # CLI override: --sampling-method / --rotate-sampling / --sobol-n-policy
        # are not in the MATRIX lookup, so cfg defaults apply.  Apply CLI
        # override here so Sobol/Halton actually propagate to the detector.
        import dataclasses as _dc
        if sampling_method is not None:
            cfg_B = _dc.replace(cfg_B, sampling_method=sampling_method)
            cfg_C = _dc.replace(cfg_C, sampling_method=sampling_method)
        if rotate_sampling:
            cfg_B = _dc.replace(cfg_B, rotate_sampling=True)
            cfg_C = _dc.replace(cfg_C, rotate_sampling=True)
        if sobol_n_policy is not None:
            cfg_B = _dc.replace(cfg_B, sobol_n_policy=sobol_n_policy)
            cfg_C = _dc.replace(cfg_C, sobol_n_policy=sobol_n_policy)
        # --refine-frac override (otherwise MATRIX cell wins).
        if refine_frac_override is not None and refine_frac_override != -1.0:
            cfg_B = _dc.replace(cfg_B, refine_frac=refine_frac_override)
            cfg_C = _dc.replace(cfg_C, refine_frac=refine_frac_override)

        # Alternating optimization mode: override one class's fields with
        # tune_overrides; keep the other class pure MATRIX.
        if tune_class is not None and tune_overrides:
            clean = {k: v for k, v in tune_overrides.items() if v is not None}
            if tune_class == 'B':
                cfg_B = _dc.replace(cfg_B, **clean)
            elif tune_class == 'C':
                cfg_C = _dc.replace(cfg_C, **clean)
            else:
                raise ValueError(f"tune_class must be 'B' or 'C', got {tune_class!r}")

        if anchor:
            # Anchor mode: per-function single-class deploy.  Class boundary
            # is suite-specific: B for unimodal/hybrid prefix, C for the
            # composition tail (per each CEC suite's structure).
            anchor_boundary = {
                'cec2017': 20,   # f1-f20 -> B, f21-f30 -> C
                'cec2014': 22,   # f1-f22 -> B, f23-f30 -> C (compositions)
                'cec2020': 7,    # f1-f7  -> B, f8-f10 -> C (compositions)
            }
            if suite not in anchor_boundary:
                raise ValueError(
                    f"--anchor: no class boundary defined for suite="
                    f"{suite!r}. Add an entry to anchor_boundary in "
                    f"benchmark/msc.py:_run_seed or run without --anchor.")
            cutoff = anchor_boundary[suite]
            chosen_cfg = cfg_B if int(fnum) <= cutoff else cfg_C
            solver = MSC_CMA(
                recorder, bounds, maxevals, seed=seed, disp=disp,
                config=chosen_cfg,
                mode_schedule=None,
                enable_phase0_reuse=enable_phase0_reuse)
        else:
            # alt-CB: cycle through [cfg_C, cfg_B] indefinitely, no decision.
            solver = MSC_CMA(
                recorder, bounds, maxevals, seed=seed, disp=disp,
                config=cfg_C,
                mode_schedule=[cfg_C, cfg_B],
                enable_phase0_reuse=enable_phase0_reuse)
    else:
        cfg = MSCConfig(**cfg_dict)
        solver = MSC_CMA(recorder, bounds, maxevals, seed=seed, config=cfg,
                         disp=disp,
                         enable_phase0_reuse=enable_phase0_reuse)
    result = solver.solve()
    recorder.finalize()

    # Cycle records as plain dicts (no class dependency for PKL readers).
    cycles_dicts = [c.as_dict() for c in result.cycles]

    # Pre-refine error: best_f_pre_refine is in raw f-space; subtract bias
    # to match the `errors` convention. Stays inf if no cycle ran.
    pre_refine_err = float(result.best_f_pre_refine) - float(bias)

    # Budget tracking.  nfev_pre_refine = self.nfev at end of last cycle
    # (= result.cycles[-1].nfev_end, captured before _run_refinement runs).
    # nfev_total = self.nfev after solve() returns (after refinement).
    nfev_pre_refine = int(result.cycles[-1].nfev_end) if result.cycles else 0
    nfev_total = int(solver.nfev)

    return (seed, recorder.best_err, recorder.improvements,
            dict(solver.popsize_hist),
            cycles_dicts, pre_refine_err,
            nfev_pre_refine, nfev_total)


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='MSC-CMA-ES benchmark runner (single-algorithm).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Common benchmark args
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
                   help="Override output directory (default: "
                        "experiments/<suite>/d<dim>/MSC-CMA/maxevals_<N>/)")
    p.add_argument('--force', action='store_true',
                   help='Overwrite existing pkl files')
    p.add_argument('--auto', action='store_true',
                   help='Self-configuring mode: alt-CB scheduler.  Loads '
                        'cfg_B and cfg_C from algorithms.auto_config (two '
                        'global configs, sigma scaled by sqrt(10/D)) and '
                        'cycles cfg_C / cfg_B / cfg_C / ... through the '
                        'solver.  CLI hyperparameter flags are ignored in '
                        'this mode (--sampling-method, --rotate-sampling, '
                        '--sobol-n-policy, --refine-frac, --refine-mult '
                        'are honored as overrides on top of the base cfgs).')
    p.add_argument('--popsize-hist', action='store_true',
                   help='Print aggregated popsize histogram per function '
                        '(diagnostic; can be very long)')
    p.add_argument('--logs', action='store_true',
                   help='Enable verbose per-cycle/per-restart diagnostic '
                   'output from MSC_CMA.  Best used with --runs 1 --jobs 1.')
    p.add_argument('--no-phase0-reuse', action='store_true',
                   help='Disable Sobol/Halton cross-cycle Phase-0 reuse '
                        '(alt-CB only).  Default: reuse enabled.  No effect '
                        'for LHS or single-cfg mode.')
    p.add_argument('--anchor', action='store_true',
                   help='Anchor deploy (requires --auto): replace alt-CB '
                        'schedule with per-function single-class assignment '
                        '(CEC2017 convention: f1-f20 use cfg_B only, f21-f30 '
                        'use cfg_C only).  Mimics legacy MSC-CMA MATRIX '
                        'behaviour.  Default: False = alt-CB schedule.')
    p.add_argument('--refine-mult', type=float, default=1.0,
                   help='Multiplier applied to base refine_frac of both '
                        'cfg_B and cfg_C (alt-CB / --auto only).  Default '
                        '1.0 = no scaling.  Use to compensate for budget '
                        'anchor mismatch (e.g. 0.5 halves refinement '
                        'reservation when running at >5x the tune-anchor '
                        'maxevals).  Ignored without --auto.')
    p.add_argument('--tune-class', choices=['B', 'C'], default=None,
                   help='Alternating-optimization tuner mode (requires --auto). '
                        'Load cfg_B/cfg_C from auto_config, then override fields '
                        'of the named class with the CLI hyperparameter flags. '
                        'The other class stays pure auto_config.  Used by '
                        'experiments/optuna_v3.py for trial subprocesses.')

    # MSC-CMA hyperparameters (mirrors MSCConfig fields)
    p.add_argument('--n-phase0', type=int, default=None,
                   help='Phase-0 sample size N (direct value, ideally 2^m for '
                        'Sobol balance).  Replaces the deprecated --M-factor.')
    p.add_argument('--k', type=int, default=None)
    p.add_argument('--n-initial-basins', type=int, default=None)
    p.add_argument('--min-basin-size', type=int, default=None)
    p.add_argument('--sigma-elite-frac', type=float, default=None,
                   help='Top fraction of basin points defining elite center for sigma0.')
    p.add_argument('--popsize-frac', type=float, default=None,
                   help='Fraction of basin size used as CMA popsize (before clamp).')
    p.add_argument('--sampling-method', choices=['lhs', 'sobol', 'halton'],
                   default=None)
    p.add_argument('--rotate-sampling', action='store_true',
                   help='Rotate Phase-0 sampling method per cycle: '
                        'cycle 0=lhs, 1=sobol, 2=halton, 3=lhs, ... '
                        'Overrides --sampling-method per cycle.')
    p.add_argument('--sobol-n-policy',
                   choices=['arbitrary', 'nearest_pow2',
                            'floor_pow2', 'ceil_pow2'],
                   default=None,
                   help='How to map target n (M*D) to actual sample size '
                        'when --sampling-method=sobol.  arbitrary keeps raw n '
                        '(Sobol balance warning).  nearest_pow2/floor_pow2/'
                        'ceil_pow2 round to a 2^m for proper Sobol balance.')
    p.add_argument('--sigma-divisor', type=float, default=None)
    p.add_argument('--cma-popsize', type=int, default=None)
    p.add_argument('--tolfun-exp', type=int, default=None)
    p.add_argument('--tolx-exp', type=int, default=None)
    p.add_argument('--s-tol', type=float, default=None)
    p.add_argument('--refine-frac', type=str, default=None,
                   help="Optional override: 'auto' (scales with budget ratio) "
                        "or explicit float (e.g. 0.1, 0.2).  If omitted, "
                        "the selected config value is kept.  In --auto "
                        "mode, this overrides both cfg_B and cfg_C refine_frac.")
    p.add_argument('--nearest-better-k', type=int, default=None)
    p.add_argument('--nbc-b', type=float, default=None)
    p.add_argument('--nbc-min-incoming', type=int, default=None)
    p.add_argument('--phi-override', type=float, default=None)

    return p


def _parse_refine_frac(x):
    """CLI value -> float.  'auto' (or sentinel) -> -1.0; else float."""
    if x is None:
        return None
    if isinstance(x, str) and x.strip().lower() == 'auto':
        return -1.0
    return float(x)


def build_msc_config(args) -> dict:
    """Return an MSCConfig-compatible dict, applying CLI overrides."""
    cfg = MSCConfig()
    overrides = {
        'n_phase0':          args.n_phase0,
        'k':                 args.k,
        'n_initial_basins':  args.n_initial_basins,
        'min_basin_size':    args.min_basin_size,
        'sigma_elite_frac':  args.sigma_elite_frac,
        'popsize_frac':      args.popsize_frac,
        'sampling_method':   args.sampling_method,
        'sobol_n_policy':    args.sobol_n_policy,
        'sigma_divisor':     args.sigma_divisor,
        'cma_popsize':       args.cma_popsize,
        'tolfun_exp':        args.tolfun_exp,
        'tolx_exp':          args.tolx_exp,
        's_tol':             args.s_tol,
        'refine_frac':       _parse_refine_frac(args.refine_frac),
        'nearest_better_k':  args.nearest_better_k,
        'nbc_b':             args.nbc_b,
        'nbc_min_incoming':  args.nbc_min_incoming,
        'phi_override':      args.phi_override,
    }
    d = {f.name: getattr(cfg, f.name) for f in cfg.__dataclass_fields__.values()}
    for k, v in overrides.items():
        if v is not None:
            d[k] = v

    # Boolean flag — only override default when True (False == default)
    if args.rotate_sampling:
        d['rotate_sampling'] = True

    return d


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))

    # Resolve maxevals (may be per-dim for some suites; MSC only supports
    # fixed dim per invocation, so one value suffices).
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    # Resolve output directory.
    outdir = args.outdir or build_outdir(
        args.suite, args.dim, ALGO_MSC, maxevals)

    # Build config.  In --auto mode the config is chosen per-seed inside
    # _run_seed via the MATRIX lookup, so the CLI-built config is not used;
    # cfg_dict is left as None and the hyperparameter flags ignored.
    if args.auto:
        cfg_dict = None
    else:
        cfg_dict = build_msc_config(args)
        cfg_dict['ref_budget'] = suite_default_maxevals(args.suite, args.dim)

    # Overwrite pre-check — catch early before running expensive seeds.
    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                print(f"ERROR: {path} already exists.  "
                      f"Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)

    print_header(args.suite, args.dim, ALGO_MSC,
                 maxevals, args.runs, args.jobs)
    if args.auto:
        mult_str = (f", refine_mult={args.refine_mult}"
                    if args.refine_mult != 1.0 else "")
        if args.anchor:
            anchor_descs = {
                'cec2017': 'f1-f20 → cfg_B, f21-f30 → cfg_C',
                'cec2014': 'f1-f22 → cfg_B, f23-f30 → cfg_C',
                'cec2020': 'f1-f7 → cfg_B, f8-f10 → cfg_C',
            }
            desc = anchor_descs.get(args.suite, f'suite={args.suite!r} unsupported')
            print(f"Config: --auto --anchor (per-function single-class: "
                  f"{desc}, from auto_config{mult_str})")
        else:
            print(f"Config: --auto (alt-CB scheduler: cycle through "
                  f"[cfg_C, cfg_B] from auto_config{mult_str})")
    else:
        print(f"Config: {MSCConfig(**cfg_dict).summary()}")
    print(f"Outdir: {outdir}")
    print()

    # Build tuning overrides for --tune-class mode.  Only the fields actually
    # set on the CLI propagate (others stay None and are filtered downstream).
    tune_overrides = None
    if args.tune_class is not None:
        if not args.auto:
            print("ERROR: --tune-class requires --auto.", file=sys.stderr)
            sys.exit(1)
        tune_overrides = {
            'n_phase0':         args.n_phase0,
            'k':                args.k,
            'n_initial_basins': args.n_initial_basins,
            'min_basin_size':   args.min_basin_size,
            'sigma_elite_frac': args.sigma_elite_frac,
            'popsize_frac':     args.popsize_frac,
            'sigma_divisor':    args.sigma_divisor,
            'cma_popsize':      args.cma_popsize,
            'tolfun_exp':       args.tolfun_exp,
            'tolx_exp':         args.tolx_exp,
            's_tol':            args.s_tol,
            'refine_frac':      _parse_refine_frac(args.refine_frac),
            'nbc_b':            args.nbc_b,
        }
        print(f"Config: --auto with --tune-class {args.tune_class} "
              f"(override {sum(1 for v in tune_overrides.values() if v is not None)} fields, "
              f"other class from auto_config)")

    summary_rows = []
    params_record = {
        'cli_args':    vars(args),
        'msc_config':  cfg_dict,    # None in --auto mode
        'auto':        args.auto,
    }

    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f"── {func_name} ──", flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals,
                               s, cfg_dict, disp=args.logs, auto=args.auto,
                               refine_frac_override=_parse_refine_frac(args.refine_frac),
                               refine_mult=args.refine_mult,
                               sampling_method=args.sampling_method,
                               rotate_sampling=args.rotate_sampling,
                               sobol_n_policy=args.sobol_n_policy,
                               enable_phase0_reuse=not args.no_phase0_reuse,
                               tune_class=args.tune_class,
                               tune_overrides=tune_overrides,
                               anchor=args.anchor)
            for s in seeds
        )
        elapsed = time.time() - t0

        # Sort by seed (joblib may return out of order).
        results.sort(key=lambda t: t[0])
        ret_seeds = np.array([r[0] for r in results], dtype=np.int64)
        errors    = np.array([r[1] for r in results], dtype=np.float64)
        imps      = [r[2] for r in results]
        # r[3] = popsize_hist (aggregated separately below)
        # r[4] = cycles_dicts (per seed); r[5] = pre_refine_err (per seed)
        # r[6] = nfev_pre_refine (per seed); r[7] = nfev_total (per seed)
        cycles_per_seed = [r[4] for r in results]
        pre_refine_errors = np.array([r[5] for r in results], dtype=np.float64)
        nfev_pre_refine_arr = np.array([r[6] for r in results], dtype=np.int64)
        nfev_total_arr      = np.array([r[7] for r in results], dtype=np.int64)

        # Aggregate popsize histograms across seeds for this function
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
            algorithm=ALGO_MSC,
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
            hist_str = " ".join(f"{k}:{v}"
                                for k, v in sorted(agg_hist.items()))
            print(f"       popsize_hist: {hist_str}", flush=True)

        summary_rows.append(summary_row(func_name, errors, elapsed, maxevals))

    csv_path = write_summary_csv(outdir, summary_rows)
    print()
    print(f"Summary → {csv_path}")


if __name__ == '__main__':
    main()
