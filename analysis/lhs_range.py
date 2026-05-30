#!/usr/bin/env python3
"""
lhs_range.py — LHS sample N points per function, report distribution stats.

For each function, prints:
  min, max, range, mean, median
  - mean_q : which quartile of (min, max) interval the mean falls in
  - med_q  : which quartile of (min, max) interval the median falls in

Quartile interpretation:
  Q1 = lower quarter (close to min)         — heavy lower tail
  Q2 = lower-middle quarter (close to mean) — symmetric / balanced
  Q3 = upper-middle quarter
  Q4 = upper quarter (close to max)         — heavy upper tail

Usage:
    python lhs_range.py
    python lhs_range.py --suite cec2017 --dim 10 --n 1000 --seed 42
"""

import argparse
import numpy as np
from scipy.stats import qmc


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", default="cec2017",
                   choices=["cec2014", "cec2017", "cec2019", "cec2020", "cec2022"])
    p.add_argument("--dim", type=int, default=10)
    p.add_argument("--n", type=int, default=1000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--functions", default=None,
                   help="Comma-separated list (default: all)")
    return p.parse_args()


def get_suite_funcs(suite):
    if suite == "cec2017":  return list(range(1, 31))
    if suite == "cec2014":  return list(range(1, 31))
    if suite == "cec2020":  return list(range(1, 11))
    if suite == "cec2022":  return list(range(1, 13))
    if suite == "cec2019":  return list(range(1, 11))
    raise ValueError(f"Unknown suite: {suite}")


def get_bounds(suite, fnum, dim):
    if suite == "cec2019":
        bounds_2019 = {1: (-8192, 8192), 2: (-16384, 16384), 3: (-4, 4)}
        if fnum in bounds_2019:
            lb, ub = bounds_2019[fnum]
        else:
            lb, ub = -100, 100
    else:
        lb, ub = -100, 100
    return np.full(dim, lb, dtype=np.float64), np.full(dim, ub, dtype=np.float64)


def get_evaluator(suite, fnum, dim):
    import minionpy
    cls_map = {
        "cec2014": "CEC2014Functions",
        "cec2017": "CEC2017Functions",
        "cec2019": "CEC2019Functions",
        "cec2020": "CEC2020Functions",
        "cec2022": "CEC2022Functions",
    }
    cls_name = cls_map[suite]
    cls = getattr(minionpy, cls_name)
    evaluator = cls(fnum, dim)
    return lambda X: np.asarray(evaluator(X), dtype=np.float64)


def quartile_label(value, fmin, fmax):
    """Return Q1/Q2/Q3/Q4 indicating which quartile of (fmin, fmax) value falls in.
    Also returns normalized position in [0, 1]."""
    if fmax == fmin:
        return "—", 0.0
    pos = (value - fmin) / (fmax - fmin)
    pos = max(0.0, min(1.0, pos))
    if pos < 0.25:
        return "Q1", pos
    elif pos < 0.50:
        return "Q2", pos
    elif pos < 0.75:
        return "Q3", pos
    else:
        return "Q4", pos


def main():
    args = parse_args()
    funcs = (list(map(int, args.functions.split(",")))
             if args.functions else get_suite_funcs(args.suite))

    print(f"Suite: {args.suite}  Dim: {args.dim}  LHS samples: {args.n}  Seed: {args.seed}")
    print()
    print(f"{'f':>4}  {'min':>11}  {'max':>11}  {'range':>11}  "
          f"{'mean':>11}  {'mean_q':>8}  {'median':>11}  {'med_q':>8}")
    print("-" * 95)

    for fnum in funcs:
        lb, ub = get_bounds(args.suite, fnum, args.dim)
        sampler = qmc.LatinHypercube(d=args.dim, seed=args.seed + fnum)
        unit = sampler.random(n=args.n)
        X = lb + (ub - lb) * unit
        try:
            F = get_evaluator(args.suite, fnum, args.dim)(X)
            fmin = float(np.min(F))
            fmax = float(np.max(F))
            frange = fmax - fmin
            fmean = float(np.mean(F))
            fmedian = float(np.median(F))

            mean_q, mean_pos = quartile_label(fmean, fmin, fmax)
            med_q, med_pos = quartile_label(fmedian, fmin, fmax)

            print(f"f{fnum:<3d}  {fmin:>11.4e}  {fmax:>11.4e}  {frange:>11.4e}  "
                  f"{fmean:>11.4e}  {mean_q} ({mean_pos:.2f})  "
                  f"{fmedian:>11.4e}  {med_q} ({med_pos:.2f})")
        except Exception as e:
            print(f"f{fnum:<3d}  ERROR: {e}")


if __name__ == "__main__":
    main()
