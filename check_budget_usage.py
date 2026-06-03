#!/usr/bin/env python3
"""
check_budget_usage.py — proxy diagnostic for whether DE baselines used the full
evaluation budget or stopped early (e.g. minionpy relTol early-stop).

IMPORTANT — what the pkl actually contains:
    Baseline pkls store `improvements`: per seed, a list of (nfev, err) points
    recorded on each best-so-far improvement, and recording STOPS once
    err <= 1e-8 (COCO_ZERO).  The TOTAL evaluations used is NOT stored.

So the only budget signal here is the nfev of the LAST recorded improvement.
That is a PROXY, not a measurement:
    - A seed that solved the function (err <= 1e-8) stops recording at the
      solve point — its last nfev says nothing about early-stop.
    - A seed that did NOT solve but plateaued would also stop improving early
      even on a full-budget run.
    - Only on UNSOLVED seeds does a last-improvement nfev far below budget,
      AND consistently below a relTol=0 reference algo on the same function,
      hint at relTol early-stop.

Therefore this script reports, per (algo, function), how deep into the budget
the LAST improvement landed on UNSOLVED seeds, and lets you compare the
suspects (default relTol) against a reference algo run with relTol=0.  A
clear, systematic gap on hard functions is suggestive — not proof.  The only
definitive check is a re-instrumented run that records final nfev.

Usage:
    python analysis/check_budget_usage.py experiments/cec2017/d10 --maxevals 100000
    python analysis/check_budget_usage.py experiments/cec2017/d10 --maxevals 100000 \\
        --algos ARRDE,LSRTDE,jSO
"""

from __future__ import annotations

import argparse
import os
import pickle
import sys

import numpy as np

COCO_ZERO = 1e-8


def _load(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as exc:
        return {'__err__': f'{type(exc).__name__}: {exc}'}


def _seed_last(improvements):
    """Return (last_nfev, last_err) for one seed's improvement curve.
    Empty curve → (0, inf) (never improved / no record)."""
    arr = np.asarray(improvements, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0:
        return 0.0, float('inf')
    return float(arr[-1, 0]), float(arr[-1, 1])


def scan_algo(algo_dir, maxevals):
    """Per function: (n_seeds, n_solved, unsolved_deepest_fracs list)."""
    out = {}
    for fn in sorted(f for f in os.listdir(algo_dir)
                     if f.startswith('f') and f.endswith('.pkl')):
        payload = _load(os.path.join(algo_dir, fn))
        if '__err__' in payload:
            out[fn[:-4]] = ('ERR', payload['__err__'])
            continue
        mx = payload.get('maxevals', maxevals)
        imps = payload.get('improvements', [])
        n_solved = 0
        unsolved_fracs = []
        for seed_imps in imps:
            last_nfev, last_err = _seed_last(seed_imps)
            if last_err <= COCO_ZERO:
                n_solved += 1
            else:
                unsolved_fracs.append(last_nfev / mx if mx else 0.0)
        out[fn[:-4]] = (len(imps), n_solved, unsolved_fracs)
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('base_dir', help='e.g. experiments/cec2017/d10')
    ap.add_argument('--maxevals', type=int, required=True,
                    help='budget (selects the maxevals_<N> subdir)')
    ap.add_argument('--algos', default='ARRDE,LSRTDE,jSO',
                    help='comma list of algorithm dir names; include a '
                         'relTol=0 reference (default jSO) for comparison')
    args = ap.parse_args()

    algos = [a.strip() for a in args.algos.split(',') if a.strip()]
    sub = f'maxevals_{args.maxevals}'

    print(f"\nBudget-usage proxy (last-improvement nfev) — {args.base_dir} "
          f"@ {sub}")
    print("Per algo/function: solved/total, and on UNSOLVED seeds the "
          "deepest\nlast-improvement as % of budget (median / max).\n")

    deepest_overall = {}
    for algo in algos:
        algo_dir = os.path.join(args.base_dir, algo, sub)
        if not os.path.isdir(algo_dir):
            print(f"  [{algo}] no dir: {algo_dir}")
            continue
        print(f"  ── {algo} ──")
        per_func = scan_algo(algo_dir, args.maxevals)
        algo_deepest = 0.0
        for func in sorted(per_func, key=_fkey):
            rec = per_func[func]
            if rec[0] == 'ERR':
                print(f"    {func:>4}  load error: {rec[1]}")
                continue
            n, solved, unsolved = rec
            if unsolved:
                med = 100.0 * float(np.median(unsolved))
                mx = 100.0 * float(np.max(unsolved))
                algo_deepest = max(algo_deepest, mx)
                print(f"    {func:>4}  solved {solved:>2}/{n:<2}  "
                      f"unsolved deepest: med {med:5.1f}%  max {mx:5.1f}%")
            else:
                print(f"    {func:>4}  solved {solved:>2}/{n:<2}  "
                      f"(all seeds solved → no budget signal)")
        deepest_overall[algo] = algo_deepest
        print(f"    → {algo}: deepest last-improvement on any unsolved "
              f"function = {algo_deepest:.1f}% of budget")

    print("\nReading the result:")
    print("  Compare the suspects (ARRDE, LSRTDE) against the relTol=0 "
          "reference.")
    print("  If the suspects' deepest %% is systematically far below the "
          "reference\n  on the SAME hard functions, that is consistent with "
          "relTol early-stop.")
    print("  If they reach comparable depth, relTol did not cut them short.")
    if deepest_overall:
        line = "  deepest%: " + "  ".join(
            f"{a}={deepest_overall[a]:.1f}" for a in deepest_overall)
        print(line)
    print("\nNote: this is a proxy. A plateau at full budget looks the same "
          "as an\nearly stop here. The only definitive measure is total nfev, "
          "which the\npkls do not store — a 1-seed re-run printing "
          "recorder.nfev would settle it.")


def _fkey(name):
    digits = ''.join(c for c in name if c.isdigit())
    return int(digits) if digits else 0


if __name__ == '__main__':
    main()
