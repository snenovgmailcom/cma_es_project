#!/usr/bin/env python3
"""
probe_lsrtde_reltol.py — definitive check of whether minionpy's default relTol
cuts LSRTDE short, by measuring the REAL evaluation count (recorder.nfev),
which the result pkls do not store.

For each function it runs LSRTDE once (1 seed) twice:
    A) default relTol  (relTol arg omitted — minionpy default 1e-4)
    B) relTol = 0.0    (early-stop disabled, the intended full-budget run)
and prints, side by side, the actual nfev used and the final error.

Interpretation:
    - nfev_A ≈ nfev_B ≈ maxevals  → relTol does NOT cut LSRTDE short; the early
      last-improvement seen in the pkls is LSRTDE's own restart/termination or
      a plateau. The existing default-relTol results are comparable.
    - nfev_A << maxevals and nfev_B larger (and/or err_B better)  → default
      relTol DID cut LSRTDE short; re-run LSRTDE with relTol=0.0 for fairness.

Run on srv-01 (needs minionpy). 1 seed × few functions = fast.

Usage:
    python benchmark/probe_lsrtde_reltol.py --suite cec2017 --dim 10 \\
        --functions 24,25,27 --maxevals 100000 --seed 0
"""

import argparse
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from _common import ImprovementRecorder, suite_config, suite_default_maxevals

from minionpy import Minimizer


def _run(suite, fnum, dim, maxevals, seed, rel_tol):
    """Run one LSRTDE seed; return (nfev_used, best_err). rel_tol=None → default."""
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)
    bounds_pairs = list(zip(bounds[:, 0].tolist(), bounds[:, 1].tolist()))

    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)

    def objective(X):
        return [float(f) for f in recorder(X)]

    kwargs = dict(x0=[], algo='LSRTDE', maxevals=maxevals, seed=int(seed))
    if rel_tol is not None:
        kwargs['relTol'] = rel_tol
    try:
        Minimizer(objective, bounds_pairs, **kwargs).optimize()
    except Exception as exc:
        print(f"    WARN f{fnum} relTol={rel_tol}: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)

    recorder.finalize()
    return recorder.nfev, recorder.best_err


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--suite', required=True)
    ap.add_argument('--dim', type=int, required=True)
    ap.add_argument('--functions', type=str, default='24,25,27',
                    help="functions where LSRTDE stopped earliest")
    ap.add_argument('--maxevals', type=int, default=0,
                    help='0 = suite default')
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)
    fnums = [int(x.lstrip('fF')) for x in args.functions.split(',') if x.strip()]

    print(f"\nLSRTDE relTol probe — {args.suite} D={args.dim}  "
          f"maxevals={maxevals}  seed={args.seed}\n")
    print(f"{'func':>5}  {'nfev(default)':>14}  {'nfev(relTol=0)':>15}  "
          f"{'err(default)':>13}  {'err(relTol=0)':>14}  verdict")
    print('-' * 88)

    cut_any = False
    for fnum in fnums:
        nfev_a, err_a = _run(args.suite, fnum, args.dim, maxevals, args.seed, None)
        nfev_b, err_b = _run(args.suite, fnum, args.dim, maxevals, args.seed, 0.0)
        # "cut short" if default used materially fewer evals than relTol=0.
        cut = nfev_a < 0.95 * nfev_b and nfev_a < 0.95 * maxevals
        cut_any = cut_any or cut
        verdict = 'CUT SHORT' if cut else 'full / same'
        print(f"{('f'+str(fnum)):>5}  {nfev_a:>14,}  {nfev_b:>15,}  "
              f"{err_a:>13.3e}  {err_b:>14.3e}  {verdict}")

    print('-' * 88)
    if cut_any:
        print("→ default relTol cut LSRTDE short on at least one function. "
              "Re-run LSRTDE with relTol=0.0 for a fair comparison.")
    else:
        print("→ default relTol did NOT cut LSRTDE short (nfev matches). "
              "The early last-improvement is LSRTDE's own termination / a "
              "plateau; existing results are comparable.")


if __name__ == '__main__':
    main()
