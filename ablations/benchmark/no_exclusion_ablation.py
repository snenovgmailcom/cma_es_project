#!/usr/bin/env python3
"""
ablations/benchmark/no_exclusion_ablation.py -- NO-EXCLUSION ablation runner.

Ablation semantics (S.N., 19.08.2026):
    The FULL MSC-CMA-ES pipeline (alt-CB cycles, prefix reuse, budget
    gates, refinement, stops) with the within-cycle basin exclusion
    removed: no restart is skipped because its x0 probe maps to an
    already-converged basin, and no basin is ever added to an exclusion
    set. The kNN convergence vote itself still runs and conv_basin is
    still recorded; converge_count remains as a dead counter so the
    control flow of the loop is otherwise identical to FULL.

Implementation: MSC_NoExclusion overrides only _run_topo_phase with a
verbatim copy of the parent method minus (a) the pre-start probe skip
and (b) the excluded_bids bookkeeping. No root file is modified.

Output: ablations/experiments/<suite>/d<dim>/NO-EXCLUSION/maxevals_<N>/
f<k>.pkl + summary.csv (root _common schema, incl. cycle/refinement
fields as written by benchmark/msc.py).
"""

import argparse
import dataclasses
import os
import sys
import time
from collections import Counter
from typing import List

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
from config import MSCConfig  # noqa: E402
from msc_cma import MSC_CMA, compute_popsize  # noqa: E402
from result import PhaseStats, RestartRecord  # noqa: E402
from basin_detector import BasinInfo  # noqa: E402

ALGO = 'NO-EXCLUSION'


class MSC_NoExclusion(MSC_CMA):
    """FULL MSC-CMA-ES with within-cycle basin exclusion removed."""

    def _run_topo_phase(self,
                        detector: NBCDetector,
                        basins_sorted: List[BasinInfo],
                        cfg: MSCConfig,
                        main_budget: int,
                        restart_idx: int,
                        all_restarts: List[RestartRecord],
                        phase_stats: PhaseStats,
                        cycle: int,
                        ) -> int:
        """Phase-1 topo restarts, exclusion removed (copy of parent)."""
        D = self.dim
        topo_queue = [b.basin_id for b in basins_sorted]

        # Exclusion removed: no excluded_bids set, no probe skip.
        converge_count: Counter = Counter()

        for bid in topo_queue:
            if self.nfev >= main_budget:
                break
            if bid not in detector.basins:
                continue

            basin = detector.basins[bid]

            x0 = detector.jitter_x0(bid, self.rng)

            remaining = main_budget - self.nfev
            sigma0 = basin.sigma0(cfg.sigma_divisor)
            if self.disp and sigma0 <= 1.0:
                print(f"  sigma0 safety net: computed->1.0 bid={bid}")
            popsize = compute_popsize(basin.size, cfg, D)

            rec = self._run_cma(x0, sigma0, popsize, remaining,
                                restart_idx, phase='topo', cycle=cycle)
            rec.seed_basin = bid

            # Convergence tracking kept; result no longer feeds exclusion.
            conv_bid = detector.identify_basin_knn(rec.best_x)
            rec.conv_basin = conv_bid

            if conv_bid is not None:
                converge_count[conv_bid] += 1

            all_restarts.append(rec)
            restart_idx += 1
            phase_stats.nfev += rec.nfev
            phase_stats.n_restarts += 1
            phase_stats.best_f_end = self.best_f

            if self.disp:
                print(f"  R{restart_idx-1} topo(bid={bid}) "
                      f"nfev={rec.nfev} best={rec.best_f:.4e} "
                      f"stop={rec.stop_reason} conv={conv_bid}")

        return restart_idx


# =========================================================================
# Worker: single seed (mirrors benchmark/msc.py alt-CB path)
# =========================================================================

def _run_seed(suite, fnum, dim, maxevals, seed, cfg_C, cfg_B, disp=False):
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)
    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)

    solver = MSC_NoExclusion(recorder, bounds, maxevals, seed=seed,
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
        description='NO-EXCLUSION ablation runner (within-cycle basin '
                    'exclusion removed; everything else = FULL).')
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
    print(f'Variant: no-exclusion  (probe skip and exclusion set removed, '
          f'vote recorded only)  C[{cfg_C.summary()}]  B[{cfg_B.summary()}]')

    params_record = {
        'cli_args': vars(args),
        'variant':  'no-exclusion',
        'mode':     'alt-CB',
        'config_C': dataclasses.asdict(cfg_C),
        'config_B': dataclasses.asdict(cfg_B),
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
