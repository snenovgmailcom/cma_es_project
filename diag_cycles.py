#!/usr/bin/env python3
"""
diag_cycles.py — per-cycle reliability diagnostic for MSC-CMA.

Goal: decide whether the f25/f21/f27 failures are BUDGET-limited (few
independent cycle-attempts) or DETECTION-limited (bad seeds whose cycles
never reach the global basin). Reuses the exact harness configs/seeds.

Run from the repo root (same place you run benchmark/msc.py):

    python diag_cycles.py --suite cec2017 --functions 25 --dim 10 \
        --runs 21 --jobs 21 --maxevals 10_000_000 --thr 1e-6

It does NOT write any pkl/csv — it only prints. Lower --runs (e.g. 15-21)
is enough to estimate the per-cycle hit rate before committing to a sweep.

What it reports, per function:
  * C  = cycles per run (mean/min/max)        -> number of independent attempts
  * p  = per-cycle hit rate (cycle reached err < thr, pooled over all cycles)
  * observed run-failure rate vs the i.i.d. model (1-p)^C_mean  [consistency check]
  * extrapolation of failure rate to larger budgets (assumes C scales linearly)
  * per-seed table: C, #hits, final err  -> shows if failures are concentrated
The model is a lens, not proof: it assumes cycles are ~independent attempts
with a constant hit rate p. If observed != model at m=1, that assumption is
violated (heterogeneous seeds) and the extrapolation is unreliable -> that
itself is the answer (detection-limited / seed-structural, budget won't fix).
"""

import argparse
import dataclasses
import os
import sys

import numpy as np
from joblib import Parallel, delayed

# --- make the project importable exactly like benchmark/msc.py does ---
_REPO = os.path.abspath(os.environ.get("MSC_REPO", os.getcwd()))
for _p in (os.path.join(_REPO, "algorithms"), os.path.join(_REPO, "benchmark"),
           os.path.join(_REPO, "cma_es_project", "algorithms"),
           os.path.join(_REPO, "cma_es_project", "benchmark")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from _common import suite_config, suite_default_maxevals, parse_functions  # noqa: E402
from auto_config import get_B, get_C                                       # noqa: E402
from msc_cma import MSC_CMA                                                 # noqa: E402
from _common import ImprovementRecorder                                     # noqa: E402


def run_one(suite, fnum, dim, maxevals, seed, cfg_C, cfg_B, conly, bias):
    """One seed. Returns (seed, final_err, per_cycle_errs)."""
    cec_cls, _bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)
    recorder = ImprovementRecorder(cec, f_opt=bias, maxevals=maxevals)
    schedule = None if conly else [cfg_C, cfg_B]
    solver = MSC_CMA(recorder, bounds, maxevals, seed=seed,
                     config=cfg_C, mode_schedule=schedule, disp=False)
    result = solver.solve()
    recorder.finalize()
    # cycle_local_best is raw f-space; error convention is raw - bias.
    cle = [float(c.cycle_local_best) - float(bias) for c in result.cycles]
    return seed, float(recorder.best_err), cle


def analyse(fnum, results, thr, maxevals):
    finals = np.array([r[1] for r in results], float)
    cyc_counts = np.array([len(r[2]) for r in results], int)
    # pooled per-cycle hits across ALL runs
    all_cle = [e for r in results for e in r[2]]
    hits = sum(1 for e in all_cle if e < thr)
    total_cycles = len(all_cle)
    p = hits / total_cycles if total_cycles else float("nan")
    C_mean = cyc_counts.mean() if len(cyc_counts) else 0.0

    n = len(finals)
    n_success = int(np.sum(finals < thr))
    obs_fail = 1.0 - n_success / n if n else float("nan")
    model_fail = (1.0 - p) ** C_mean if total_cycles else float("nan")

    print(f"\n==================== f{fnum} ====================")
    print(f"runs={n}  thr(err)={thr:.1e}  maxevals={maxevals:,}")
    print(f"final err: best={finals.min():.3e}  median={np.median(finals):.3e}"
          f"  worst={finals.max():.3e}")
    print(f"success (err<thr): {n_success}/{n}   "
          f"observed FAIL rate = {obs_fail:.3f}")
    print(f"cycles per run C: mean={C_mean:.1f}  min={cyc_counts.min()}  "
          f"max={cyc_counts.max()}   (~{maxevals/max(C_mean,1):,.0f} evals/cycle)")
    print(f"per-cycle hit rate p = {hits}/{total_cycles} = {p:.4f}")
    print(f"i.i.d. model FAIL rate (1-p)^C_mean = {model_fail:.3f}   "
          f"[vs observed {obs_fail:.3f}]")
    if not np.isnan(model_fail):
        gap = abs(model_fail - obs_fail)
        verdict = ("model ~ matches observed -> failures look like unlucky "
                   "draws; MORE BUDGET (more cycles) should help."
                   if gap < 0.10 else
                   "model != observed -> failures are concentrated in specific "
                   "seeds (heterogeneous p). Budget alone likely won't fix "
                   "those; detection/N0 or seed/seeding policy is the lever.")
        print(f"  -> {verdict}")

    # Extrapolation to larger budgets (assumes C grows linearly with budget).
    if 0.0 < p < 1.0 and C_mean > 0:
        print("  extrapolated FAIL rate if budget x m (C -> C*m):")
        for m in (1, 2, 5, 10):
            print(f"     {m:>2}x  ({maxevals*m:,} evals)  "
                  f"fail ~= {(1.0 - p) ** (C_mean * m):.3f}")

    # Per-seed view: are failures concentrated? Sort worst-first.
    print("  per-seed [seed | C | #hits | final_err]:")
    rows = sorted(((r[0], len(r[2]), sum(1 for e in r[2] if e < thr), r[1])
                   for r in results), key=lambda t: -t[3])
    for seed, c, h, fe in rows:
        flag = "" if fe < thr else "  <-- FAIL"
        print(f"     {seed:>4} | {c:>3} | {h:>4} | {fe:.3e}{flag}")


def main():
    ap = argparse.ArgumentParser(description="MSC-CMA per-cycle diagnostic")
    ap.add_argument("--suite", default="cec2017")
    ap.add_argument("--dim", type=int, default=10)
    ap.add_argument("--functions", default="25")
    ap.add_argument("--runs", type=int, default=21)
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--maxevals", type=int, default=0, help="0 = suite default")
    ap.add_argument("--jobs", type=int, default=0, help="0 = --runs")
    ap.add_argument("--thr", type=float, default=1e-6,
                    help="success threshold in ERROR space (raw - bias)")
    ap.add_argument("--conly", action="store_true")
    ap.add_argument("--sampling-method",
                    choices=["lhs", "sobol", "halton"], default=None)
    args = ap.parse_args()

    fnums = parse_functions(args.functions)
    seeds = list(range(args.seed_start, args.seed_start + args.runs))
    maxevals = args.maxevals or suite_default_maxevals(args.suite, args.dim)
    jobs = args.jobs or args.runs

    cfg_C = get_C(args.dim)
    cfg_B = None if args.conly else get_B(args.dim)
    if args.sampling_method:
        cfg_C = dataclasses.replace(cfg_C, sampling_method=args.sampling_method)
        if cfg_B is not None:
            cfg_B = dataclasses.replace(cfg_B, sampling_method=args.sampling_method)

    print(f"diag_cycles: suite={args.suite} dim={args.dim} "
          f"funcs={fnums} runs={args.runs} jobs={jobs} "
          f"maxevals={maxevals:,} mode={'C-only' if args.conly else 'alt-CB'} "
          f"sampling={cfg_C.sampling_method}")

    for fnum in fnums:
        _, bias, _ = suite_config(args.suite, fnum, args.dim)
        results = Parallel(n_jobs=jobs)(
            delayed(run_one)(args.suite, fnum, args.dim, maxevals, s,
                             cfg_C, cfg_B, args.conly, bias)
            for s in seeds
        )
        results.sort(key=lambda t: t[0])
        analyse(fnum, results, args.thr, maxevals)


if __name__ == "__main__":
    main()
