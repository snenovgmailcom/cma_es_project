#!/usr/bin/env python3
"""
compare_study_vs_baselines.py — Snapshot of MSC-CMA Optuna study + side-by-side
comparison vs ARRDE and LSRTDE baselines.

Supports two dim/suite combinations via --dim:
  --dim 30  →  cec2017 d30, maxevals 300_000
  --dim 5   →  cec2020 d5,  maxevals 50_000

Each combination has its own class partition, study DB, and baseline pkl paths.

Usage:
    python experiments/compare_study_vs_baselines.py --dim 30 --cls B
    python experiments/compare_study_vs_baselines.py --dim 30 --cls C
    python experiments/compare_study_vs_baselines.py --dim 5  --cls B
    python experiments/compare_study_vs_baselines.py --dim 5  --cls C

Output:
  1. Study snapshot (trials count, top-N trial params, best params) —
     WITHOUT per-function values.
  2. ONE comparison table per study: MSC_best vs ARRDE vs LSRTDE
     (score and mean per function, plus SUM row).
"""

import argparse
import pickle
import sys
import numpy as np
import optuna
from pathlib import Path


# Identical with target_depth_score in optuna_canonical_d{5,30}.py
COCO_TAUS = 10.0 ** np.linspace(2.0, -8.0, 51)
COCO_W = np.linspace(1.0, 6.0, 51)


# ---------------------------------------------------------------------------
# Per-dim configuration tables
# ---------------------------------------------------------------------------

SUITE_BY_DIM = {
    30: "cec2017",
    5:  "cec2020",
}

MAXEVALS_BY_DIM = {
    30: 300_000,
    5:  50_000,
}

CLASS_FUNCS_BY_DIM = {
    30: {
        # cec2017 d30 cls_abc majority partition
        "B": [1, 2, 3, 10, 11, 12, 13, 14, 15, 18, 19, 22, 29, 30],
        "C": [4, 5, 7, 9, 16, 17, 20, 21, 23, 24, 25, 26, 27, 28],
    },
    5: {
        # cec2020 d5 cls_abc majority partition (51 seeds, M=200)
        "B": [1, 2, 5, 7],
        "C": [4, 6, 8, 9, 10],
    },
}


# ---------------------------------------------------------------------------
# Per-function stats from improvements
# ---------------------------------------------------------------------------

def compute_stats(improvements):
    finals = []
    for imp in improvements:
        imp = np.asarray(imp)
        finals.append(float(imp[-1, 1]) if imp.size else np.inf)
    fe = np.array(finals)
    if fe.size == 0:
        return dict(score=0.0, mean=np.nan, median=np.nan,
                    std=np.nan, best=np.nan, worst=np.nan)
    reached = fe[:, None] <= COCO_TAUS[None, :]
    per_seed = (reached * COCO_W).sum(axis=1) / COCO_W.sum()
    return dict(
        score=float(per_seed.mean()),
        mean=float(np.mean(fe)),
        median=float(np.median(fe)),
        std=float(np.std(fe, ddof=1)) if fe.size > 1 else 0.0,
        best=float(np.min(fe)),
        worst=float(np.max(fe)),
    )


def load_baseline_stats(funcs, baseline_dir, label):
    stats = {}
    bd = Path(baseline_dir)
    if not bd.exists():
        print(f"WARNING: {label} dir does not exist: {bd}", file=sys.stderr)
        return {fn: None for fn in funcs}
    for fn in funcs:
        pkl = bd / f"f{fn}.pkl"
        if not pkl.exists():
            print(f"  [{label}] WARNING: {pkl.name} missing", file=sys.stderr)
            stats[fn] = None
            continue
        try:
            with open(pkl, "rb") as f:
                data = pickle.load(f)
            stats[fn] = compute_stats(data["improvements"])
        except Exception as e:
            print(f"  [{label}] WARNING: f{fn} load error: {e}",
                  file=sys.stderr)
            stats[fn] = None
    return stats


def msc_stats_from_trial(trial, funcs):
    ua = trial.user_attrs
    return {fn: {k: ua.get(f"{k}_f{fn}", np.nan)
                 for k in ("score", "mean", "median",
                          "std", "best", "worst")}
            for fn in funcs}


# ---------------------------------------------------------------------------
# Study snapshot (NO per-function values)
# ---------------------------------------------------------------------------

def print_study_snapshot(study, top_n=5):
    trials = study.trials
    states = {}
    for t in trials:
        states[t.state.name] = states.get(t.state.name, 0) + 1

    print("=" * 96)
    print(f"Study: {study.study_name}")
    print("=" * 96)
    print(f"Total trials: {len(trials)}")
    for s, c in sorted(states.items()):
        print(f"  {s}: {c}")

    valid = [t for t in trials
             if t.state.name == "COMPLETE" and np.isfinite(t.value)]
    if not valid:
        print("\n(no completed valid trials yet)")
        return None

    valid.sort(key=lambda t: t.value, reverse=True)
    n = min(top_n, len(valid))
    print(f"\nTop {n} trials by value:")
    print(f"  {'T#':>4s} {'value':>8s} {'sum_mean':>11s} {'M':>4s} "
          f"{'sd':>6s} {'s_tol':>6s} {'rf':>6s} {'cma':>4s} "
          f"{'k':>3s} {'nb':>3s} {'mbs':>4s} {'elapsed':>9s}")
    for t in valid[:n]:
        elapsed = t.user_attrs.get("elapsed_s")
        el_str = f"{elapsed/60:.1f}min" if elapsed else "—"
        sum_mean = t.user_attrs.get("sum_mean", np.nan)
        sm_str = (f"{sum_mean:11.4e}"
                  if isinstance(sum_mean, (int, float))
                  and np.isfinite(sum_mean)
                  else f"{'n/a':>11s}")
        p = t.params
        print(f"  T{t.number:03d} {t.value:8.4f} {sm_str} "
              f"{p['M_factor']:4d} "
              f"{p['sigma_divisor']:6.3f} "
              f"{p['s_tol']:6.2f} "
              f"{p['refine_frac']:6.3f} "
              f"{p['cma_popsize']:4d} "
              f"{p['k']:3d} "
              f"{p['n_initial_basins']:3d} "
              f"{p['min_basin_size']:4d} "
              f"{el_str:>9s}")

    best = valid[0]
    print(f"\nBest trial T{best.number} params (value={best.value:.4f}):")
    for k, v in sorted(best.params.items()):
        if isinstance(v, float):
            print(f"  {k:>20s}: {v:.6f}")
        else:
            print(f"  {k:>20s}: {v}")
    return best


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def _fmt_sc(x):
    return f"{x:9.4f}" if not np.isnan(x) else f"{'n/a':>9s}"


def _fmt_mean(x):
    return f"{x:12.4e}" if not np.isnan(x) else f"{'n/a':>12s}"


def print_comparison_table(funcs, msc_stats, arrde_stats, lsrtde_stats,
                           cls, dim, msc_trial_label):
    print()
    print("=" * 96)
    print(f"Comparison: MSC-CMA-auto {msc_trial_label} "
          f"vs ARRDE vs LSRTDE — d{dim} Class {cls}")
    print("=" * 96)
    print(f"  {'func':>5s}  "
          f"{'MSC_sc':>9s}  {'ARRDE_sc':>9s}  {'LSRT_sc':>9s}  "
          f"{'MSC_mean':>12s}  {'ARRDE_mean':>12s}  {'LSRT_mean':>12s}")
    print("  " + "-" * 89)

    sums = dict(msc_sc=0.0, arrde_sc=0.0, lsrt_sc=0.0,
                msc_mean=0.0, arrde_mean=0.0, lsrt_mean=0.0)

    def _safe_add(s, key, val):
        if val is not None and not np.isnan(val) and np.isfinite(val):
            s[key] += val

    for fn in funcs:
        m = msc_stats.get(fn) if msc_stats else None
        a = arrde_stats.get(fn)
        l = lsrtde_stats.get(fn)

        m_sc = m["score"] if m else np.nan
        m_me = m["mean"]  if m else np.nan
        a_sc = a["score"] if a else np.nan
        a_me = a["mean"]  if a else np.nan
        l_sc = l["score"] if l else np.nan
        l_me = l["mean"]  if l else np.nan

        print(f"  f{fn:<4d}  "
              f"{_fmt_sc(m_sc)}  {_fmt_sc(a_sc)}  {_fmt_sc(l_sc)}  "
              f"{_fmt_mean(m_me)}  {_fmt_mean(a_me)}  {_fmt_mean(l_me)}")

        _safe_add(sums, "msc_sc", m_sc)
        _safe_add(sums, "arrde_sc", a_sc)
        _safe_add(sums, "lsrt_sc", l_sc)
        _safe_add(sums, "msc_mean", m_me)
        _safe_add(sums, "arrde_mean", a_me)
        _safe_add(sums, "lsrt_mean", l_me)

    print("  " + "-" * 89)
    print(f"  {'SUM':>5s}  "
          f"{_fmt_sc(sums['msc_sc'])}  "
          f"{_fmt_sc(sums['arrde_sc'])}  "
          f"{_fmt_sc(sums['lsrt_sc'])}  "
          f"{_fmt_mean(sums['msc_mean'])}  "
          f"{_fmt_mean(sums['arrde_mean'])}  "
          f"{_fmt_mean(sums['lsrt_mean'])}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Compare MSC-CMA-auto study results with ARRDE/LSRTDE "
                    "baselines on cec2017 d30 or cec2020 d5.")
    p.add_argument("--dim", required=True, type=int, choices=[5, 30],
                   help="5 → cec2020 d5; 30 → cec2017 d30")
    p.add_argument("--cls", required=True, choices=["B", "C"])
    p.add_argument("--storage", default=None,
                   help="Override db path. "
                        "Default: sqlite:///optuna_canonical_d<dim>_<cls>.db")
    p.add_argument("--study-name", default=None,
                   help="Override study name. "
                        "Default: <suite>_d<dim>_<cls>_canonical")
    p.add_argument("--arrde-dir", default=None,
                   help="Override ARRDE pkl directory. "
                        "Default: ../cma_es_project_v33/experiments/"
                        "<suite>/d<dim>/ARRDE-minionpy/maxevals_<maxevals>")
    p.add_argument("--lsrtde-dir", default=None,
                   help="Override LSRTDE pkl directory. "
                        "Default: same pattern but LSRTDE-minionpy")
    p.add_argument("--top-n", type=int, default=5)
    args = p.parse_args()

    # Resolve dim-dependent configuration
    suite = SUITE_BY_DIM[args.dim]
    maxevals = MAXEVALS_BY_DIM[args.dim]
    funcs = CLASS_FUNCS_BY_DIM[args.dim][args.cls]

    # Resolve paths with sensible defaults
    storage = (args.storage
               or f"sqlite:///optuna_canonical_d{args.dim}_{args.cls}.db")
    study_name = (args.study_name
                  or f"{suite}_d{args.dim}_{args.cls}_canonical")
    baseline_root = (f"../cma_es_project_v33/experiments/"
                     f"{suite}/d{args.dim}")
    arrde_dir = (args.arrde_dir
                 or f"{baseline_root}/ARRDE-minionpy/maxevals_{maxevals}")
    lsrtde_dir = (args.lsrtde_dir
                  or f"{baseline_root}/LSRTDE-minionpy/maxevals_{maxevals}")

    # Part 1: study snapshot (no per-function values)
    study = optuna.load_study(study_name=study_name, storage=storage)
    best = print_study_snapshot(study, top_n=args.top_n)
    if best is None:
        return

    # Part 2 & 3: load baselines, get MSC best trial stats
    msc_stats = msc_stats_from_trial(best, funcs)
    arrde_stats = load_baseline_stats(funcs, arrde_dir, "ARRDE")
    lsrtde_stats = load_baseline_stats(funcs, lsrtde_dir, "LSRTDE")

    # Part 4: one comparison table
    label = f"T{best.number} (best, value={best.value:.4f})"
    print_comparison_table(funcs, msc_stats, arrde_stats, lsrtde_stats,
                           args.cls, args.dim, label)


if __name__ == "__main__":
    main()
