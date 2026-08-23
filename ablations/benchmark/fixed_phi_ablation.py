#!/usr/bin/env python3
"""
ablations/benchmark/fixed_phi_ablation.py -- FIXED-PHI ablation runner.

Ablation semantics (confirmed by S.N., 13.08.2026):
    The FULL MSC-CMA-ES pipeline (alt-CB cycles, prefix reuse, budget
    gates, refinement, stops) with the staircase phi selection replaced
    by the fixed NBC cutting threshold phi = 2.0 for BOTH configurations.
    Rule 2 keeps the tuned parameters (b, n_min); min_basin_size stays
    (7 C / 155 B); n_initial_basins becomes unused.

Implementation: FixedPhiDetector overrides NBCDetector._staircase_phi to
return (2.0, []); parent discover() then clusters at that phi. MSC_FixedPhi
overrides only the per-cycle detector factory. No root file is modified.

Output: ablations/experiments/<suite>/d<dim>/FIXED-PHI/maxevals_<N>/
f<k>.pkl + summary.csv (root _common schema, incl. cycle/refinement
fields as written by benchmark/msc.py).
"""

import argparse
import dataclasses
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

_ABL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_ABL_DIR)
for _p in (os.path.join(_ROOT, 'algorithms'),
           os.path.join(_ROOT, 'benchmark')):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from _common import (  # noqa: E402
    ImprovementRecorder, build_outdir, parse_functions, print_func_result,
    print_header, suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)
from auto_config import get_B, get_C  # noqa: E402
from basin_detector import NBCDetector  # noqa: E402
from msc_cma import MSC_CMA  # noqa: E402

ALGO = 'FIXED-PHI'
PHI_FIXED = 2.0


class FixedPhiDetector(NBCDetector):
    """NBCDetector with the staircase replaced by a fixed phi."""

    def _staircase_phi(self, n_target):
        return float(PHI_FIXED), []


class MSC_FixedPhi(MSC_CMA):
    """FULL MSC-CMA-ES with FixedPhiDetector as the Phase-0 detector."""

    def _make_detector_for_cycle(self, cycle, cfg):
        cycle_seed = self.seed + cycle * 10000
        return (FixedPhiDetector(self.dim, self.bounds, cfg, cycle_seed),
                cfg.sampling_method)


# =========================================================================
# Worker: single seed (mirrors benchmark/msc.py alt-CB path)
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, cfg_C, cfg_B, disp=False):
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)
    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)

    solver = MSC_FixedPhi(recorder, bounds, maxevals, seed=seed,
                          config=cfg_C, mode_schedule=[cfg_C, cfg_B],
                          disp=disp)
    result = solver.solve()
    recorder.finalize()

    cycles_dicts = [c.as_dict() for c in result.cycles]
    pre_refine_err = float(result.best_f_pre_refine) - float(bias)
    nfev_pre_refine = int(result.cycles[-1].nfev_end) if result.cycles else 0

    return (seed, recorder.best_err, recorder.improvements,
            dict(solver.popsize_hist), cycles_dicts, pre_refine_err,
            nfev_pre_refine, int(solver.nfev))


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description='FIXED-PHI ablation runner (staircase replaced by '
                    'phi=2.0; everything else = FULL).')
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
    p.add_argument('--outdir', type=str, default='')
    p.add_argument('--force', action='store_true')
    p.add_argument('--logs', action='store_true',
                   help='Verbose per-cycle output. Best with --runs 1.')
    return p


def main():
    args = build_parser().parse_args()
    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)

    cfg_C = get_C(args.dim)
    cfg_B = get_B(args.dim)

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
    print(f'Variant: fixed-phi  phi={PHI_FIXED}  (staircase off, Rule 2 '
          f'tuned, s_min kept)  C[{cfg_C.summary()}]  B[{cfg_B.summary()}]')

    params_record = {
        'cli_args':  vars(args),
        'variant':   'fixed-phi',
        'phi_fixed': PHI_FIXED,
        'mode':      'alt-CB',
        'config_C':  dataclasses.asdict(cfg_C),
        'config_B':  dataclasses.asdict(cfg_B),
    }

    summary_rows = []
    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f'-- {func_name} --', flush=True)

        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals,
                               s, cfg_C, cfg_B, disp=args.logs)
            for s in seeds
        )
        elapsed = time.time() - t0

        results.sort(key=lambda t: t[0])
        ret_seeds = np.array([r[0] for r in results], dtype=np.int64)
        errors = np.array([r[1] for r in results], dtype=np.float64)
        imps = [r[2] for r in results]
        cycles_per_seed = [r[4] for r in results]
        pre_refine_errors = np.array([r[5] for r in results],
                                     dtype=np.float64)
        nfev_pre_refine_arr = np.array([r[6] for r in results],
                                       dtype=np.int64)
        nfev_total_arr = np.array([r[7] for r in results], dtype=np.int64)

        _, bias, _ = suite_config(args.suite, fnum, args.dim)
        path = write_function_pkl(
            outdir=outdir, suite=args.suite, dim=args.dim,
            func_name=func_name, f_opt=bias, algorithm=ALGO,
            maxevals=maxevals, seeds=ret_seeds, errors=errors,
            improvements=imps, params=params_record, force=args.force,
            cycles_per_seed=cycles_per_seed,
            pre_refine_errors_per_seed=pre_refine_errors,
            nfev_pre_refine_per_seed=nfev_pre_refine_arr,
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
