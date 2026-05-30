#!/usr/bin/env python3
"""
optuna_canonical_v3.py — Optuna tuning of MSC-CMA-ES, v3.

Differences from v2:
  - DROP M_factor: n_phase0 fixed at 4096 for both B and C classes (frozen
    in algorithms/auto_config.py).  No M_factor search dimension.
  - ADD sigma_elite_frac ∈ [0.05, 0.5] and popsize_frac ∈ [0.10, 0.5] to
    search space (previously hardcoded 0.2 constants).
  - Trial subprocess runs alt-CB --auto with --tune-class {B|C} and CLI
    overrides for the tuned class fields.  The OTHER class is taken from
    MATRIX (alternating-optimization mode (a): "fixed = current MATRIX").
  - Sampling: Sobol with policy 'arbitrary' (n_phase0=4096 is already pow2).
  - Sobol-n-policy NOT in CLI (removed: we set n directly).
  - Canary uses median (was mean) and only enabled for C-study.
  - user_attr "median_ecdf" recorded for Pareto visualization post-hoc.
  - Direction='maximize' on mean ECDF (pure COCO endpoint formula).
  - Search space is now 12-dimensional (10 per-cell + 2 frac).

Objective: uniform fixed-budget target coverage in [0, 1].  Endpoint COCO ECDF.
direction='maximize'.
"""

import argparse
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
import time
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np

import sys as _sys, os as _os
_SCRIPT_DIR = _os.path.dirname(_os.path.abspath(__file__))
_sys.path = [p for p in _sys.path if _os.path.abspath(p) != _SCRIPT_DIR]

import optuna
import optuna.samplers
import optuna.study
import optuna.trial
from optuna.samplers import TPESampler


# ---------------------------------------------------------------------------
# COCO endpoint ECDF
# ---------------------------------------------------------------------------

# 51 log-spaced COCO targets in [1e2, 1e-8] (COCO standard).
COCO_TAUS = 10.0 ** np.linspace(2.0, -8.0, 51)


def _final_errs(improvements_by_seed):
    """Final best error per seed. inf if no improvements were recorded."""
    n = len(improvements_by_seed)
    out = np.empty(n, dtype=np.float64)
    for k, imp in enumerate(improvements_by_seed):
        imp = np.asarray(imp)
        out[k] = float(imp[-1, 1]) if imp.size else np.inf
    return out


def coverage_score(improvements_by_seed):
    """Per-function ECDF in [0, 1].  Pure COCO endpoint:
        per_seed_score = #targets_reached / 51
        function_ecdf  = mean over seeds of per_seed_score
    """
    final_errs = _final_errs(improvements_by_seed)
    if final_errs.size == 0:
        return 0.0
    reached = final_errs[:, None] <= COCO_TAUS[None, :]
    per_seed = reached.sum(axis=1) / 51.0
    return float(per_seed.mean())


# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_MSC = os.path.join(SCRIPT_DIR, "..", "benchmark", "msc.py")
BENCHMARK_MSC = os.path.abspath(BENCHMARK_MSC)


# ---------------------------------------------------------------------------
# Known anchors — enqueued as trial 0 for warm start.
# Keyed by (cls, sorted-fnums).  Values are MSCConfig kwargs WITHOUT
# n_phase0 (fixed at 4096).  Float keys match the v3 search space.
# ---------------------------------------------------------------------------

KNOWN_ANCHORS = {
    # B-anchor: T278 from the v2 B_type study (cec2017_d10_100k_B_type),
    # post-swap-deployed in production as of 2026-05.  sigma_divisor is
    # already the D=10-resolved value (frozen layer scales by sqrt(10/D) at
    # runtime; the trial fixes dim, so the resolved value is what the study
    # sees).
    ('B', (11, 12, 13, 14, 15, 16, 17, 18, 19)): {
        "sigma_divisor":    2.9982922607822964,
        "s_tol":            9.875513421780317,
        "tolfun_exp":       7,
        "tolx_exp":         12,
        "refine_frac":      0.07135048978927226,
        "n_initial_basins": 2,
        "cma_popsize":      296,
        "k":                5,
        "min_basin_size":   187,
        "nbc_b":            3.1595382659454923,
        "sigma_elite_frac": 0.20,        # previous hardcoded value
        "popsize_frac":     0.20,        # previous hardcoded value
    },

    # C-anchor: T0 from the v2 C_type study (current deployed MATRIX C).
    ('C', (21, 22, 23, 24, 25, 26, 27, 28, 29, 30)): {
        "sigma_divisor":    4.5133351148995553,
        "s_tol":            10.213553039135522,
        "tolfun_exp":       9,
        "tolx_exp":         13,
        "refine_frac":      0.029848063612822013,
        "n_initial_basins": 10,
        "cma_popsize":      11,
        "k":                1,
        "min_basin_size":   9,
        "nbc_b":            2.3586134147033113,
        "sigma_elite_frac": 0.20,
        "popsize_frac":     0.20,
    },
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Optuna v3 tuner: alt-CB --tune-class with fixed n_phase0=4096.",
    )
    # Suite / problem
    p.add_argument("--suite", default="cec2017",
                   choices=["cec2014", "cec2017", "cec2019", "cec2020", "cec2022"])
    p.add_argument("--dim", type=int, default=10)
    p.add_argument("--functions", required=True,
                   help='Comma-separated function numbers (e.g. "21,22,...,30")')
    p.add_argument("--runs", type=int, default=51)
    p.add_argument("--maxevals", type=int, default=100_000)

    # Which class to tune.  The OTHER class is taken from MATRIX (alt-CB
    # alternating-optimization mode (a)).
    p.add_argument("--tune-class", required=True, choices=['B', 'C'],
                   help="Class whose params Optuna varies.  The other class "
                        "is fixed at its current MATRIX cell.")

    # Optuna study
    p.add_argument("--trials", type=int, default=300)
    p.add_argument("--jobs", type=int, default=51,
                   help="Parallel seeds inside one trial")
    p.add_argument("--study-name", required=True)
    p.add_argument("--storage", default="sqlite:///optuna_studies_v3/study.db")
    p.add_argument("--startup-trials", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--timeout-per-trial", type=float, default=3600.0)
    p.add_argument("--log-dir", default="./optuna_logs_v3")
    p.add_argument("--out-json", default=None)

    # Canary — single-function early reject.  Only used for C-study by
    # convention (point 8 of the v3 plan: prune trial if median f30 > 500).
    p.add_argument("--canary-func", type=int, default=None,
                   help="Function number used as canary (None to disable). "
                        "If set, this function is run first and the trial "
                        "is rejected (-inf) if MEDIAN final error exceeds "
                        "--canary-threshold (v3: median, was mean in v2).")
    p.add_argument("--canary-threshold", type=float, default=500.0)

    return p.parse_args()


# ---------------------------------------------------------------------------
# Single trial: subprocess benchmark/msc.py with --auto --tune-class
# ---------------------------------------------------------------------------

def run_msc_subprocess(params, suite, fnums, dim, maxevals, runs, jobs,
                       tune_class, timeout, tmpdir):
    """Run benchmark/msc.py in alt-CB mode with --tune-class overrides.
    Returns (improvements_by_func, error_msg).
    """
    func_str = ",".join(str(f) for f in fnums)

    cmd = [
        sys.executable, BENCHMARK_MSC,
        "--suite", suite,
        "--dim", str(dim),
        "--functions", func_str,
        "--runs", str(runs),
        "--jobs", str(jobs),
        "--maxevals", str(maxevals),
        "--outdir", tmpdir,
        "--force",
        # Alt-CB schedule with class-selective override.
        "--auto",
        "--tune-class", tune_class,
        # Production-matching sampling: Sobol with n=4096 already pow2.
        "--sampling-method", "sobol",
        # No --sobol-n-policy (default 'arbitrary' is fine for n=4096).
        # Trial-tuned hyperparameters (the OTHER class stays MATRIX):
        "--sigma-divisor",     str(params["sigma_divisor"]),
        "--s-tol",             str(params["s_tol"]),
        "--tolfun-exp",        str(params["tolfun_exp"]),
        "--tolx-exp",          str(params["tolx_exp"]),
        "--refine-frac",       str(params["refine_frac"]),
        "--n-initial-basins",  str(params["n_initial_basins"]),
        "--cma-popsize",       str(params["cma_popsize"]),
        "--k",                 str(params["k"]),
        "--min-basin-size",    str(params["min_basin_size"]),
        "--nbc-b",             str(params["nbc_b"]),
        "--sigma-elite-frac",  str(params["sigma_elite_frac"]),
        "--popsize-frac",      str(params["popsize_frac"]),
    ]

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )

    t_start = time.time()
    try:
        for line in proc.stdout:
            if time.time() - t_start > timeout:
                proc.kill()
                proc.wait(timeout=10)
                return None, f"timeout ({timeout}s)"
    except Exception as e:
        try:
            proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass
        return None, f"stream error: {e}"

    rc = proc.wait()
    if rc != 0:
        stderr = proc.stderr.read()[-500:] if proc.stderr else ""
        return None, f"rc={rc}: {stderr}"

    improvements_by_func = {}
    for fnum in fnums:
        pkl_path = os.path.join(tmpdir, f"f{fnum}.pkl")
        if not os.path.exists(pkl_path):
            return None, f"missing f{fnum}.pkl"
        try:
            with open(pkl_path, "rb") as fh:
                d = pickle.load(fh)
            improvements_by_func[fnum] = d.get("improvements", [])
        except Exception as e:
            return None, f"pkl parse f{fnum}: {e}"

    return improvements_by_func, None


# ---------------------------------------------------------------------------
# Objective
# ---------------------------------------------------------------------------

def make_objective(args, fnums, log_dir):
    jsonl_path = os.path.join(log_dir, "trials.jsonl") if log_dir else None
    use_canary = (args.canary_func is not None
                  and args.canary_func in fnums
                  and len(fnums) > 1)

    def objective(trial):
        # 12-dimensional search space (v3): drop M_factor, add elite/popsize fracs.
        params = {
            "sigma_divisor":    trial.suggest_float("sigma_divisor",    1.5,  8.0),
            "s_tol":            trial.suggest_float("s_tol",            5.0, 15.0),
            "tolfun_exp":       trial.suggest_int  ("tolfun_exp",       3,    14),
            "tolx_exp":         trial.suggest_int  ("tolx_exp",         4,    18),
            "refine_frac":      trial.suggest_float("refine_frac",      0.0,  0.30),
            "n_initial_basins": trial.suggest_int  ("n_initial_basins", 1,    25),
            "cma_popsize":      trial.suggest_int  ("cma_popsize",      4,    300),
            "k":                trial.suggest_int  ("k",                1,    10),
            "min_basin_size":   trial.suggest_int  ("min_basin_size",   5,    200),
            "nbc_b":            trial.suggest_float("nbc_b",            1.2,  4.0),
            "sigma_elite_frac": trial.suggest_float("sigma_elite_frac", 0.05, 0.50),
            "popsize_frac":     trial.suggest_float("popsize_frac",     0.10, 0.50),
        }

        tmpdir = tempfile.mkdtemp(prefix=f"optuna_v3_T{trial.number:04d}_")
        canary_median = None
        try:
            t0 = time.time()

            if use_canary:
                # Stage 1: canary func alone — v3 uses MEDIAN (was mean in v2).
                canary_imps, err = run_msc_subprocess(
                    params, args.suite, [args.canary_func], args.dim,
                    args.maxevals, args.runs, args.jobs,
                    args.tune_class, args.timeout_per_trial, tmpdir,
                )
                if canary_imps is None:
                    print(f"  T{trial.number} FAILED "
                          f"(canary f{args.canary_func}): {err}",
                          flush=True)
                    return float("-inf")

                canary_median = float(np.median(
                    _final_errs(canary_imps[args.canary_func])))
                trial.set_user_attr(f"canary_f{args.canary_func}_median",
                                    canary_median)

                if (not np.isfinite(canary_median)
                        or canary_median > args.canary_threshold):
                    elapsed = time.time() - t0
                    print(f"  T{trial.number} PRUNED: "
                          f"f{args.canary_func} median={canary_median:.1f} > "
                          f"{args.canary_threshold:.0f} ({elapsed:.0f}s)",
                          flush=True)
                    trial.set_user_attr(
                        "pruned_reason",
                        f"f{args.canary_func}_median={canary_median:.3f}")
                    if jsonl_path:
                        with open(jsonl_path, "a") as f:
                            f.write(json.dumps({
                                "trial":         trial.number,
                                "pruned":        True,
                                "canary_median": canary_median,
                                "params":        dict(trial.params),
                                "elapsed_s":     elapsed,
                                "timestamp":     datetime.now().isoformat(),
                            }) + "\n")
                    return float("-inf")

                rest = [f for f in fnums if f != args.canary_func]
                rest_imps, err = run_msc_subprocess(
                    params, args.suite, rest, args.dim, args.maxevals,
                    args.runs, args.jobs, args.tune_class,
                    args.timeout_per_trial, tmpdir,
                )
                if rest_imps is None:
                    print(f"  T{trial.number} FAILED: {err}", flush=True)
                    return float("-inf")
                improvements_by_func = {**canary_imps, **rest_imps}
            else:
                improvements_by_func, err = run_msc_subprocess(
                    params, args.suite, fnums, args.dim, args.maxevals,
                    args.runs, args.jobs, args.tune_class,
                    args.timeout_per_trial, tmpdir,
                )
                if improvements_by_func is None:
                    print(f"  T{trial.number} FAILED: {err}", flush=True)
                    return float("-inf")

            elapsed = time.time() - t0

            # Per-function metrics: ecdf, mean, median, best, worst.
            per_func_ecdf, per_func_mean = {}, {}
            per_func_median, per_func_best, per_func_worst = {}, {}, {}
            for fnum in fnums:
                imps = improvements_by_func[fnum]
                fe = _final_errs(imps)
                per_func_ecdf[fnum]   = coverage_score(imps)
                if fe.size:
                    per_func_mean[fnum]   = float(np.mean(fe))
                    per_func_median[fnum] = float(np.median(fe))
                    per_func_best[fnum]   = float(np.min(fe))
                    per_func_worst[fnum]  = float(np.max(fe))
                else:
                    per_func_mean[fnum] = float("nan")
                    per_func_median[fnum] = float("nan")
                    per_func_best[fnum] = float("nan")
                    per_func_worst[fnum] = float("nan")

            mean_ecdf   = float(np.mean(list(per_func_ecdf.values())))     # objective
            median_ecdf = float(np.median(list(per_func_ecdf.values())))   # user_attr only
            sum_ecdf    = float(np.sum(list(per_func_ecdf.values())))
            sum_mean    = float(np.sum(list(per_func_mean.values())))
            sum_median  = float(np.sum(list(per_func_median.values())))
            sum_best    = float(np.sum(list(per_func_best.values())))
            sum_worst   = float(np.sum(list(per_func_worst.values())))

            for fnum in fnums:
                trial.set_user_attr(f"ecdf_f{fnum}",   per_func_ecdf[fnum])
                trial.set_user_attr(f"mean_f{fnum}",   per_func_mean[fnum])
                trial.set_user_attr(f"median_f{fnum}", per_func_median[fnum])
                trial.set_user_attr(f"best_f{fnum}",   per_func_best[fnum])
                trial.set_user_attr(f"worst_f{fnum}",  per_func_worst[fnum])

            trial.set_user_attr("sum_ecdf",    sum_ecdf)
            trial.set_user_attr("sum_mean",    sum_mean)
            trial.set_user_attr("sum_median",  sum_median)
            trial.set_user_attr("sum_best",    sum_best)
            trial.set_user_attr("sum_worst",   sum_worst)
            trial.set_user_attr("median_ecdf", median_ecdf)    # for Pareto post-hoc
            trial.set_user_attr("elapsed_s",   elapsed)

            if jsonl_path:
                with open(jsonl_path, "a") as f:
                    f.write(json.dumps({
                        "trial":       trial.number,
                        "pruned":      False,
                        "mean_ecdf":   mean_ecdf,
                        "median_ecdf": median_ecdf,
                        "sum_ecdf":    sum_ecdf,
                        "sum_mean":    sum_mean,
                        "sum_median":  sum_median,
                        "sum_best":    sum_best,
                        "sum_worst":   sum_worst,
                        "canary_median": canary_median,
                        "per_func_ecdf":   {f"f{fn}": v for fn, v in per_func_ecdf.items()},
                        "per_func_mean":   {f"f{fn}": v for fn, v in per_func_mean.items()},
                        "per_func_median": {f"f{fn}": v for fn, v in per_func_median.items()},
                        "per_func_best":   {f"f{fn}": v for fn, v in per_func_best.items()},
                        "per_func_worst":  {f"f{fn}": v for fn, v in per_func_worst.items()},
                        "params":     dict(trial.params),
                        "elapsed_s":  elapsed,
                        "timestamp":  datetime.now().isoformat(),
                    }) + "\n")

            canary_str = (f" canary_f{args.canary_func}_med={canary_median:.1f}"
                          if canary_median is not None else "")
            print(f"  T{trial.number} mean_ecdf={mean_ecdf:.4f} "
                  f"med_ecdf={median_ecdf:.4f} "
                  f"sum_mean={sum_mean:.1f}{canary_str}  "
                  f"sd={params['sigma_divisor']:.3f} "
                  f"ef={params['sigma_elite_frac']:.3f} pf={params['popsize_frac']:.3f} "
                  f"cma={params['cma_popsize']:3d} k={params['k']} "
                  f"nb={params['n_initial_basins']:2d} mbs={params['min_basin_size']:3d}  "
                  f"({elapsed:.0f}s)",
                  flush=True)
            return mean_ecdf
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    return objective


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    if not os.path.exists(BENCHMARK_MSC):
        sys.exit(f"ERROR: benchmark/msc.py not found at {BENCHMARK_MSC}")

    fnums = sorted(int(x) for x in args.functions.split(",") if x.strip())
    log_dir = os.path.join(args.log_dir, args.study_name)
    os.makedirs(log_dir, exist_ok=True)

    if args.storage.startswith("sqlite:///"):
        db_path = args.storage[len("sqlite:///"):]
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    out_json = args.out_json or f"{args.study_name}_best.json"
    canary_on = (args.canary_func is not None
                 and args.canary_func in fnums
                 and len(fnums) > 1)

    print("=" * 72)
    print("Optuna v3 — alt-CB --tune-class, fixed n_phase0=4096")
    print("=" * 72)
    print(f"Suite        : {args.suite}  Dim: {args.dim}  Maxevals: {args.maxevals}")
    print(f"Functions    : {fnums}  ({len(fnums)} funcs)")
    print(f"Tune class   : {args.tune_class}  (other class fixed at MATRIX cell)")
    print(f"Seeds        : {args.runs}  (jobs: {args.jobs})")
    print(f"Trials       : {args.trials}  (startup: {args.startup_trials})")
    print(f"Storage      : {args.storage}")
    print(f"Study        : {args.study_name}")
    print(f"Search dims  : 12  (M_factor dropped; elite_frac + popsize_frac added)")
    if canary_on:
        print(f"Canary       : f{args.canary_func}, reject if MEDIAN > "
              f"{args.canary_threshold:.0f}")
    else:
        print("Canary       : off")
    print(f"Objective    : mean ECDF across functions (pure COCO endpoint), MAXIMIZE")
    print(f"Started      : {datetime.now().isoformat()}")
    print()

    sampler = TPESampler(
        n_startup_trials=args.startup_trials,
        seed=args.seed,
        constant_liar=True,
        multivariate=True,
        group=True,
    )

    study = optuna.create_study(
        study_name=args.study_name,
        storage=args.storage,
        direction="maximize",
        sampler=sampler,
        load_if_exists=True,
    )

    if len(study.trials) > 0:
        print(f"Resuming existing study ({len(study.trials)} trials in DB) — "
              f"anchor NOT re-enqueued")
    else:
        anchor_key = (args.tune_class, tuple(fnums))
        anchor = KNOWN_ANCHORS.get(anchor_key)
        if anchor is not None:
            study.enqueue_trial(anchor)
            print(f"Enqueued known anchor as trial 0 "
                  f"({args.tune_class}, fnums={fnums}, "
                  f"{len(anchor)} params)")
        else:
            print(f"No known anchor for (cls={args.tune_class}, fnums={fnums}) — "
                  f"starting cold")
    print()

    objective = make_objective(args, fnums, log_dir)

    def cb(study, trial):
        if trial.value is None or not np.isfinite(trial.value):
            return
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"best so far: {study.best_value:.4f}", flush=True)

    t_start = time.time()
    try:
        study.optimize(
            objective,
            n_trials=args.trials,
            gc_after_trial=True,
            catch=(Exception,),
            callbacks=[cb],
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    t_elapsed = time.time() - t_start

    print()
    print("=" * 72)
    print("Optimization summary")
    print("=" * 72)
    print(f"Trials completed : {len(study.trials)}")
    print(f"Wall time        : {t_elapsed / 60:.1f} min")
    if study.best_trial is not None:
        print(f"Best score (mean_ecdf): {study.best_value:.6f}")
        ba = study.best_trial.user_attrs
        if "sum_mean" in ba:
            print(f"  median_ecdf={ba.get('median_ecdf'):.4f}  "
                  f"sum_ecdf={ba.get('sum_ecdf'):.4f}  "
                  f"sum_mean={ba.get('sum_mean'):.3f}  "
                  f"sum_median={ba.get('sum_median'):.3f}")
        print("Best params:")
        for k, v in sorted(study.best_params.items()):
            print(f"  {k:>20s} : {v}")

        with open(out_json, "w") as f:
            json.dump({
                "study_name":  args.study_name,
                "suite":       args.suite,
                "dim":         args.dim,
                "tune_class":  args.tune_class,
                "functions":   fnums,
                "maxevals":    args.maxevals,
                "best_value":  study.best_value,
                "best_params": study.best_params,
                "best_sums": {
                    "sum_ecdf":    study.best_trial.user_attrs.get("sum_ecdf"),
                    "sum_mean":    study.best_trial.user_attrs.get("sum_mean"),
                    "sum_median":  study.best_trial.user_attrs.get("sum_median"),
                    "sum_best":    study.best_trial.user_attrs.get("sum_best"),
                    "sum_worst":   study.best_trial.user_attrs.get("sum_worst"),
                    "median_ecdf": study.best_trial.user_attrs.get("median_ecdf"),
                },
                "best_per_func": {
                    k: study.best_trial.user_attrs[k]
                    for k in study.best_trial.user_attrs
                    if (k.startswith("ecdf_f")
                        or k.startswith("mean_f")
                        or k.startswith("median_f")
                        or k.startswith("best_f")
                        or k.startswith("worst_f"))
                },
                "search_space_v3": {
                    "sigma_divisor":    {"low": 1.5,  "high": 8.0},
                    "s_tol":            {"low": 5.0,  "high": 15.0},
                    "tolfun_exp":       {"low": 3,    "high": 14},
                    "tolx_exp":         {"low": 4,    "high": 18},
                    "refine_frac":      {"low": 0.0,  "high": 0.30},
                    "n_initial_basins": {"low": 1,    "high": 25},
                    "cma_popsize":      {"low": 4,    "high": 300},
                    "k":                {"low": 1,    "high": 10},
                    "min_basin_size":   {"low": 5,    "high": 200},
                    "nbc_b":            {"low": 1.2,  "high": 4.0},
                    "sigma_elite_frac": {"low": 0.05, "high": 0.50},
                    "popsize_frac":     {"low": 0.10, "high": 0.50},
                },
                "canary": ({"func": args.canary_func,
                            "threshold": args.canary_threshold,
                            "metric": "median"}
                           if canary_on else None),
                "fixed": {"n_phase0": 4096, "sampling_method": "sobol"},
                "n_trials":  len(study.trials),
                "elapsed_s": t_elapsed,
                "timestamp": datetime.now().isoformat(),
            }, f, indent=2)
        print(f"\nBest params saved to: {out_json}")


if __name__ == "__main__":
    main()
