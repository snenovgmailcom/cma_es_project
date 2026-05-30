#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import math
import os
import pickle
import re
from collections import defaultdict

import numpy as np


# Fallback anchors if algorithms.auto_config cannot resolve a cell.
FALLBACK_M_FACTOR = {
    "A": 360,
    "B": 320,
    "C": 870,
}

FALLBACK_REFINE_FRAC_D10 = {
    "A": 0.018240796208954635,
    "B": 0.06602569843708656,
    "C": 0.029848063612822013,
}

FALLBACK_REFINE_FRAC_D5 = {
    "A": 0.05354417612731951,
    "B": 0.07006402813849283,
    "C": 0.062033723403463734,
}

FALLBACK_M_INITIAL = {
    5: 200,
    10: 300,
    15: 500,
    20: 500,
    30: 300,
}


def parse_func_number(path: str) -> int:
    m = re.search(r"f(\d+)\.pkl$", path)
    return int(m.group(1)) if m else -1


def safe_auto_config_lookup(dim: int, maxevals: int, cls: str) -> dict:
    """
    Try to use algorithms.auto_config; otherwise fallback to known anchors.
    Only M_factor and refine_frac are needed for cycle estimates.
    """
    try:
        from algorithms.auto_config import lookup

        # New auto_config (post classifier-strip): lookup() is keyed by
        # canonical maxevals directly, with nearest-cell fallback inside.
        # m_initial is no longer tracked in auto_config; estimate from the
        # FALLBACK table below (matches the values used by the old classifier
        # for back-compat with old PKLs that recorded auto_class_counts).
        p = lookup(dim, int(maxevals), cls)
        return {
            "M_factor": int(p["M_factor"]),
            "refine_frac": float(p["refine_frac"]),
            "m_initial": int(FALLBACK_M_INITIAL.get(dim, 300)),
        }
    except Exception:
        # Fallback: enough for approximate cycle accounting.
        if dim == 5:
            rf = FALLBACK_REFINE_FRAC_D5[cls]
        else:
            rf = FALLBACK_REFINE_FRAC_D10[cls]

        return {
            "M_factor": int(FALLBACK_M_FACTOR[cls]),
            "refine_frac": float(rf),
            "m_initial": int(FALLBACK_M_INITIAL.get(dim, 300)),
        }


def infer_seed_classes(d: dict, dim: int) -> list[str]:
    """
    Infer per-seed class.

    Preferred:
      1. Explicit class list if future pkls contain it.
      2. auto_class_counts + last_nfev clustering around class refine_start.
      3. Single manual config fallback.
    """
    params = d.get("params", {})

    for key in ("seed_classes", "classes", "auto_seed_classes", "class_by_seed"):
        if key in params:
            return [str(x) for x in params[key]]

    n_runs = int(d.get("n_runs", len(d.get("errors", []))))
    maxevals = int(d["maxevals"])

    # Manual single-config run.
    if "auto_class_counts" not in params:
        cfg = params.get("msc_config", {})
        # If no class stored, label as X. Still estimate using cfg directly elsewhere.
        return ["X"] * n_runs

    # Auto run: infer class from last useful nfev.
    # This works because A/B/C refine_frac values are distinct.
    improvements = d.get("improvements", [])
    last_nfev = []
    for imp in improvements:
        if len(imp):
            last_nfev.append(float(imp[-1, 0]))
        else:
            last_nfev.append(0.0)

    pred = {}
    for cls in ("A", "B", "C"):
        p = safe_auto_config_lookup(dim, maxevals, cls)
        pred[cls] = (1.0 - p["refine_frac"]) * maxevals

    classes = []
    for x in last_nfev:
        cls = min(pred, key=lambda c: abs(x - pred[c]))
        classes.append(cls)

    return classes


def get_seed_cfg(d: dict, dim: int, cls: str) -> dict:
    """
    Return M_factor/refine_frac/m_initial for this seed/class.
    """
    maxevals = int(d["maxevals"])

    if cls in ("A", "B", "C"):
        return safe_auto_config_lookup(dim, maxevals, cls)

    # Manual single-config fallback.
    cfg = d.get("params", {}).get("msc_config", {})
    return {
        "M_factor": int(cfg.get("M_factor")),
        "refine_frac": float(cfg.get("refine_frac", 0.0)),
        "m_initial": 0,
    }


def estimate_for_seed(d: dict, seed_idx: int, cls: str, dim: int) -> dict:
    maxevals = int(d["maxevals"])
    cfg = get_seed_cfg(d, dim, cls)

    m_factor = int(cfg["M_factor"])
    refine_frac = float(cfg["refine_frac"])
    m_initial = int(cfg.get("m_initial", 0))

    n_phase0 = max(1, m_factor * dim)
    classification_cost = m_initial * dim if cls in ("A", "B", "C") else 0
    refine_start = int(round((1.0 - refine_frac) * maxevals))

    main_budget = max(0, refine_start - classification_cost)
    cycle_upper = main_budget / n_phase0

    imp = d.get("improvements", [])[seed_idx]
    if len(imp):
        nfev = np.asarray(imp[:, 0], dtype=float)
    else:
        nfev = np.asarray([], dtype=float)

    main_nfev = nfev[nfev < refine_start]

    if len(main_nfev):
        bins = np.floor((main_nfev - classification_cost) / n_phase0).astype(int)
        bins = bins[bins >= 0]
        active_cycles = len(set(int(x) for x in bins))
        last_cycle_equiv = float((main_nfev[-1] - classification_cost) / n_phase0)
    else:
        active_cycles = 0
        last_cycle_equiv = 0.0

    return {
        "cycle_upper": float(cycle_upper),
        "active_cycles": int(active_cycles),
        "last_cycle_equiv": float(last_cycle_equiv),
        "n_phase0": int(n_phase0),
        "refine_start": int(refine_start),
        "classification_cost": int(classification_cost),
    }


def summarize(xs: list[float]) -> dict:
    if not xs:
        return {k: float("nan") for k in ("min", "mean", "median", "max")}
    a = np.asarray(xs, dtype=float)
    return {
        "min": float(np.min(a)),
        "mean": float(np.mean(a)),
        "median": float(np.median(a)),
        "max": float(np.max(a)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="experiments")
    ap.add_argument("--algo", default="check_frozen_v2")
    ap.add_argument("--csv", default="")
    args = ap.parse_args()

    pattern = os.path.join(
        args.root,
        "*",
        "d*",
        args.algo,
        "maxevals_*",
        "f*.pkl",
    )

    paths = sorted(glob.glob(pattern), key=lambda p: (
        p.split(os.sep)[1],
        p.split(os.sep)[2],
        p.split(os.sep)[4],
        parse_func_number(p),
    ))

    rows = []

    for path in paths:
        with open(path, "rb") as f:
            d = pickle.load(f)

        suite = str(d.get("suite", path.split(os.sep)[1]))
        dim = int(d.get("dim", path.split(os.sep)[2].replace("d", "")))
        func = int(d.get("func", parse_func_number(path)))
        maxevals = int(d.get("maxevals"))

        seed_classes = infer_seed_classes(d, dim)
        n_runs = int(d.get("n_runs", len(seed_classes)))

        per_seed = []
        for i in range(n_runs):
            cls = seed_classes[i] if i < len(seed_classes) else "X"
            try:
                est = estimate_for_seed(d, i, cls, dim)
            except Exception:
                continue
            est["cls"] = cls
            per_seed.append(est)

        if not per_seed:
            continue

        class_mix = defaultdict(int)
        for r in per_seed:
            class_mix[r["cls"]] += 1

        upper = summarize([r["cycle_upper"] for r in per_seed])
        active = summarize([r["active_cycles"] for r in per_seed])
        last_eq = summarize([r["last_cycle_equiv"] for r in per_seed])

        class_mix_str = ",".join(f"{k}:{v}" for k, v in sorted(class_mix.items()))

        rows.append({
            "suite": suite,
            "dim": dim,
            "maxevals": maxevals,
            "func": func,
            "n": len(per_seed),
            "class_mix": class_mix_str,
            "cycle_upper_min": upper["min"],
            "cycle_upper_mean": upper["mean"],
            "cycle_upper_median": upper["median"],
            "cycle_upper_max": upper["max"],
            "active_min": active["min"],
            "active_mean": active["mean"],
            "active_median": active["median"],
            "active_max": active["max"],
            "last_eq_min": last_eq["min"],
            "last_eq_mean": last_eq["mean"],
            "last_eq_median": last_eq["median"],
            "last_eq_max": last_eq["max"],
        })

    header = (
        f"{'cell':<24} {'f':>4} {'n':>3} {'class_mix':<14} "
        f"{'upper μ':>9} {'upper med':>10} {'upper max':>10} "
        f"{'active μ':>9} {'active max':>10} "
        f"{'last_eq med':>12} {'last_eq max':>12}"
    )
    print(header)
    print("-" * len(header))

    for r in rows:
        cell = f"{r['suite']}/d{r['dim']}/{r['maxevals']//1000}K"
        print(
            f"{cell:<24} f{r['func']:<3} {r['n']:>3} {r['class_mix']:<14} "
            f"{r['cycle_upper_mean']:9.1f} {r['cycle_upper_median']:10.1f} {r['cycle_upper_max']:10.1f} "
            f"{r['active_mean']:9.1f} {r['active_max']:10.1f} "
            f"{r['last_eq_median']:12.1f} {r['last_eq_max']:12.1f}"
        )

    if args.csv:
        import csv
        with open(args.csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {args.csv}")


if __name__ == "__main__":
    main()
