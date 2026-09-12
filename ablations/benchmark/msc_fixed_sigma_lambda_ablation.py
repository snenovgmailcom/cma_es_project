#!/usr/bin/env python3
r"""Joint sigma0/population ablation of FULL MSC-CMA-ES (MSC-fixed_sigma_lambda).

Only initialization of executed Phase-1 (topo) CMA restarts is replaced:
    sigma_unit = max(0.025*sqrt(D), Normal(0.05*sqrt(D), 0.025*sqrt(D)))
    sigma0 = domain_width * sigma_unit
    lambda = 4 + floor(3*ln(D))
The Normal arguments above are mean and standard deviation. These are the
initialization rules of the public NEA2+ implementation used by the project.
Equal coordinate widths are required; the four supported CEC suites have
width 200. One independent RNG draw is made per executed topo restart.

The parent MSC solver owns sampling, NBC, basin ordering, exclusion, C/B
cycles, sample reuse, CMA seeds, stopping, budget accounting and refinement.
Refinement keeps its original rule, which can receive a different final
sigma from a preceding topo restart. No NEA2+ solver or vendor code is loaded.

Output: ablations/experiments/<suite>/d<D>/MSC-fixed_sigma_lambda/maxevals_<B>/f<k>.pkl
Uses the shared benchmark schema, with cycle/pre-refinement fields and
actual local-search settings in params['local_searches_per_seed'].

Example (all 29 valid CEC2017 functions):
    python ablations/benchmark/msc_fixed_sigma_lambda_ablation.py \
        --suite cec2017 --dim 10 --maxevals 100000 --runs 51 --jobs 51
"""

import argparse
import dataclasses
import os
from pathlib import Path
import sys
import time

import numpy as np
from joblib import Parallel, delayed

_ABL_DIR = Path(__file__).resolve().parents[1]
_ROOT = _ABL_DIR.parent
for _p in (_ROOT / 'algorithms', _ROOT / 'benchmark'):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from _common import (  # noqa: E402
    ImprovementRecorder, build_outdir, parse_functions, print_func_result,
    print_header, suite_config, suite_default_maxevals, summary_row,
    write_function_pkl, write_summary_csv,
)
from auto_config import get_B, get_C  # noqa: E402
from msc_cma import MSC_CMA  # noqa: E402

ALGO = 'MSC-fixed_sigma_lambda'
_SIGMA_STREAM = 0x4E454132  # Fixed namespace: ASCII "NEA2".
_FUNCTIONS = {
    'cec2014': tuple(range(1, 31)),
    'cec2017': (1, *range(3, 31)),
    'cec2020': tuple(range(1, 11)),
    'cec2022': tuple(range(1, 13)),
}


class MSC_FixedSigmaLambda(MSC_CMA):
    """FULL MSC with NEA2+ sigma0/lambda for topo restarts only."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widths = self.bounds[:, 1] - self.bounds[:, 0]
        if (not len(widths) or not np.all(np.isfinite(widths))
                or np.any(widths <= 0) or not np.all(widths == widths[0])):
            raise ValueError('MSC-fixed_sigma_lambda requires equal, finite, positive '
                             'coordinate widths for scalar sigma conversion.')
        self._domain_width = float(widths[0])
        # Do not consume MSC's jitter RNG or CMA's global NumPy RNG.
        self._sigma_rng = np.random.Generator(np.random.PCG64(
            np.random.SeedSequence([int(self.seed), _SIGMA_STREAM])))

    def _run_cma(self, x0, sigma0, popsize, budget, restart_idx,
                 phase='topo', cycle=-1):
        if phase == 'topo':
            diagonal = float(np.sqrt(self.dim))
            sigma_unit = max(
                0.025 * diagonal,
                float(self._sigma_rng.normal(0.05 * diagonal,
                                             0.025 * diagonal)),
            )
            sigma0 = self._domain_width * sigma_unit
            popsize = 4 + int(3 * np.log(self.dim))
            if self.disp:
                print(f'    MSC-fixed_sigma_lambda R{restart_idx}: '
                      f'sigma_unit={sigma_unit:.8g} '
                      f'sigma0={sigma0:.8g} popsize={popsize}')
        return super()._run_cma(x0, sigma0, popsize, budget, restart_idx,
                                phase=phase, cycle=cycle)


def _run_seed(suite, fnum, dim, maxevals, seed, cfg_C, cfg_B, disp=False):
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    recorder = ImprovementRecorder(cec_cls(fnum, dim), f_opt=bias,
                                    maxevals=maxevals)
    solver = MSC_FixedSigmaLambda(recorder, bounds, maxevals, seed=seed,
                          config=cfg_C, mode_schedule=[cfg_C, cfg_B],
                          disp=disp)
    result = solver.solve()
    recorder.finalize()
    local_searches = [
        {'idx': int(r.idx), 'phase': r.phase, 'cycle': int(r.cycle),
         'sigma0': float(r.sigma0), 'popsize': int(r.popsize),
         'final_sigma': float(r.final_sigma), 'nfev': int(r.nfev),
         'best_error': float(r.best_f) - float(bias),
         'stop_reason': r.stop_reason}
        for r in result.restarts
    ]
    return {
        'seed': int(seed), 'error': recorder.best_err,
        'improvements': recorder.improvements,
        'cycles': [c.as_dict() for c in result.cycles],
        'pre_refine_error': float(result.best_f_pre_refine) - float(bias),
        'nfev_pre_refine': (int(result.cycles[-1].nfev_end)
                            if result.cycles else 0),
        'nfev_total': int(solver.nfev), 'local_searches': local_searches,
    }


def build_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True, choices=list(_FUNCTIONS))
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--functions', default='',
                   help='Comma-separated functions; default: all valid '
                        'functions in the suite (CEC2017 f2 excluded).')
    p.add_argument('--runs', type=int, default=51)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--maxevals', type=int, default=0,
                   help='0 = use suite default')
    p.add_argument('--jobs', type=int, default=1)
    p.add_argument('--outdir', default='')
    p.add_argument('--force', action='store_true')
    p.add_argument('--logs', action='store_true',
                   help='Verbose MSC output plus actual ablated initialization.')
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.dim <= 0 or args.runs <= 0 or args.seed_start < 0:
        parser.error('dim/runs must be positive and seed-start nonnegative')
    if args.jobs == 0 or args.maxevals < 0:
        parser.error('jobs must be nonzero and maxevals nonnegative')
    try:
        fnums = (parse_functions(args.functions) if args.functions
                 else list(_FUNCTIONS[args.suite]))
        maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    if (not fnums or len(set(fnums)) != len(fnums)
            or set(fnums) - set(_FUNCTIONS[args.suite])):
        parser.error('functions must be unique valid suite functions '
                     '(CEC2017 f2 is excluded)')
    # Validate CEC availability/bounds before starting a parallel job.
    for fnum in fnums:
        suite_config(args.suite, fnum, args.dim)

    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    cfg_C, cfg_B = get_C(args.dim), get_B(args.dim)
    outdir = args.outdir or build_outdir(
        args.suite, args.dim, ALGO, maxevals,
        base=str(_ABL_DIR / 'experiments'))
    if not args.force:
        for fnum in fnums:
            path = os.path.join(outdir, f'f{fnum}.pkl')
            if os.path.exists(path):
                parser.error(f'{path} already exists; use --force to overwrite')

    print_header(args.suite, args.dim, ALGO, maxevals, args.runs, args.jobs)
    print('Variant: joint topo sigma0/lambda replacement; '
          'FULL MSC scheduler and refinement rule retained.')
    print(f'C[{cfg_C.summary()}]  B[{cfg_B.summary()}]', flush=True)
    params = {
        'cli_args': vars(args), 'variant': 'fixed_sigma_lambda',
        'ablation_version': 1, 'mode': 'alt-CB',
        'config_C': dataclasses.asdict(cfg_C),
        'config_B': dataclasses.asdict(cfg_B),
        'initialization': {
            'scope': 'topo only; joint sigma0 and population replacement',
            'source': 'public NEA2+ v1.1 (2016-09-28)',
            'sigma_unit': 'max(0.025*sqrt(D), Normal(mean=0.05*sqrt(D), '
                          'sd=0.025*sqrt(D)))',
            'sigma_conversion': 'sigma0 = sigma_unit * common coordinate width',
            'population': '4 + floor(3*ln(D))',
            'rng': 'PCG64(SeedSequence([run_seed, 0x4E454132])); '
                   'independent of MSC jitter and CMA RNG; '
                   'one normal draw per executed topo restart',
            'refinement': 'inherited MSC rule, not replaced',
        },
        # Preserve FULL MSC's existing batch-end evaluation convention.
        'errors_at_exact_budget': False,
    }
    summary_rows = []
    for fnum in fnums:
        func_name = f'f{fnum}'
        print(f'-- {func_name} --', flush=True)
        t0 = time.time()
        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(args.suite, fnum, args.dim, maxevals, seed,
                               cfg_C, cfg_B, disp=args.logs)
            for seed in seeds)
        elapsed = time.time() - t0
        results.sort(key=lambda r: r['seed'])
        errors = np.asarray([r['error'] for r in results], dtype=np.float64)
        _, bias, bounds = suite_config(args.suite, fnum, args.dim)
        function_params = dict(params)
        function_params['domain_width'] = float(bounds[0, 1] - bounds[0, 0])
        function_params['local_searches_per_seed'] = [
            r['local_searches'] for r in results]
        path = write_function_pkl(
            outdir=outdir, suite=args.suite, dim=args.dim,
            func_name=func_name, f_opt=bias, algorithm=ALGO,
            maxevals=maxevals,
            seeds=np.asarray([r['seed'] for r in results], dtype=np.int64),
            errors=errors, improvements=[r['improvements'] for r in results],
            params=function_params, force=args.force,
            cycles_per_seed=[r['cycles'] for r in results],
            pre_refine_errors_per_seed=[r['pre_refine_error'] for r in results],
            nfev_pre_refine_per_seed=[r['nfev_pre_refine'] for r in results],
            nfev_total_per_seed=[r['nfev_total'] for r in results],
        )
        print_func_result(func_name, errors, elapsed)
        print(f'       -> {path}', flush=True)
        summary_rows.append(summary_row(func_name, errors, elapsed, maxevals))
    print(f'Summary -> {write_summary_csv(outdir, summary_rows)}')


if __name__ == '__main__':
    main()
