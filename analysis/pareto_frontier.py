#!/usr/bin/env python3
"""
pareto_frontier.py — Pareto frontier of an Optuna study with two objectives:
  * maximize value (depth-weighted target-depth score)
  * minimize sum_mean (sum of per-function mean final errors)

Both metrics are already stored in trial.user_attrs of the study DB,
so this is a pure post-hoc analysis — no re-evaluation needed.

Usage:
    python experiments/pareto_frontier.py --dim 5 --cls C
    python experiments/pareto_frontier.py --dim 30 --cls B

Output:
  1. Frontier trials (non-dominated set), sorted by value descending
  2. Knee point identification (closest to normalized ideal)
  3. ASCII scatter plot of all trials with frontier highlighted
"""

import argparse
import math
import numpy as np
import optuna


SUITE_BY_DIM = {30: "cec2017", 5: "cec2020"}


def is_dominated(p, others):
    """p = (value, sum_mean); other dominates iff value≥p.v AND sum_mean≤p.s
    with strict inequality on at least one axis."""
    pv, ps = p[0], p[1]
    for o in others:
        if o is p:
            continue
        ov, os_ = o[0], o[1]
        if ov >= pv and os_ <= ps and (ov > pv or os_ < ps):
            return True
    return False


def compute_frontier(points):
    """Return list of non-dominated points."""
    return [p for p in points if not is_dominated(p, points)]


def knee_point(frontier):
    """Closest frontier point to normalized ideal (1, 0) in [0,1]² space."""
    if not frontier:
        return None
    vs = [p[0] for p in frontier]
    ss = [p[1] for p in frontier]
    v_min, v_max = min(vs), max(vs)
    s_min, s_max = min(ss), max(ss)
    v_range = max(v_max - v_min, 1e-12)
    s_range = max(s_max - s_min, 1e-12)

    best = None
    best_dist = float("inf")
    for p in frontier:
        v_norm = (p[0] - v_min) / v_range          # 0 at worst v, 1 at best v
        s_norm = (p[1] - s_min) / s_range          # 0 at best s, 1 at worst s
        dist = math.hypot(1.0 - v_norm, s_norm)    # ideal = (1, 0)
        if dist < best_dist:
            best_dist = dist
            best = p
    return best


def ascii_scatter(all_pts, frontier_pts, width=70, height=20):
    """ASCII scatter of (value, sum_mean) with frontier marked."""
    if not all_pts:
        return

    vs = [p[0] for p in all_pts]
    ss = [p[1] for p in all_pts]
    v_min, v_max = min(vs), max(vs)
    s_min, s_max = min(ss), max(ss)
    v_range = max(v_max - v_min, 1e-12)
    s_range = max(s_max - s_min, 1e-12)

    # Build grid; '.' for non-frontier, '★' for frontier
    grid = [[" "] * width for _ in range(height)]
    frontier_set = {id(p) for p in frontier_pts}

    def to_xy(p):
        # x = value (higher → right)
        x = int((p[0] - v_min) / v_range * (width - 1))
        # y = sum_mean (lower → bottom)
        y = (height - 1) - int(
            (p[1] - s_min) / s_range * (height - 1))
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))
        return x, y

    for p in all_pts:
        x, y = to_xy(p)
        ch = "★" if id(p) in frontier_set else "·"
        # Frontier always wins if both at same position
        if grid[y][x] != "★":
            grid[y][x] = ch

    # Print with axis labels
    print(f"  sum_mean (lower = better)")
    print(f"  {s_max:9.2e} ┌" + "─" * width + "┐")
    for y, row in enumerate(grid):
        if y == 0 or y == height - 1 or y == height // 2:
            label = f"{s_min + (height - 1 - y) / (height - 1) * s_range:9.2e} "
        else:
            label = " " * 10
        print(f"  {label}│" + "".join(row) + "│")
    print(f"  {s_min:9.2e} └" + "─" * width + "┘")
    print(f"            {v_min:.4f}" + " " * (width - 12)
          + f"{v_max:.4f}")
    print(f"            value (higher = better) →")


def main():
    p = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--dim", required=True, type=int, choices=[5, 30])
    p.add_argument("--cls", required=True, choices=["A", "B", "C"])
    p.add_argument("--storage", default=None)
    p.add_argument("--study-name", default=None)
    args = p.parse_args()

    suite = SUITE_BY_DIM[args.dim]
    storage = (args.storage
               or f"sqlite:///optuna_canonical_d{args.dim}_{args.cls}.db")
    study_name = (args.study_name
                  or f"{suite}_d{args.dim}_{args.cls}_canonical")

    study = optuna.load_study(study_name=study_name, storage=storage)
    completed = [t for t in study.trials
                 if t.state.name == "COMPLETE"
                 and t.value is not None and np.isfinite(t.value)]

    # Build points: (value, sum_mean, trial)
    points = []
    for t in completed:
        sm = t.user_attrs.get("sum_mean")
        if sm is None or not np.isfinite(sm):
            continue
        points.append((t.value, float(sm), t))

    if not points:
        print("No valid trials with sum_mean.")
        return

    frontier = compute_frontier(points)
    # Sort frontier by value descending (and then by sum_mean ascending)
    frontier.sort(key=lambda p: (-p[0], p[1]))

    knee = knee_point(frontier)

    print("=" * 96)
    print(f"Pareto frontier — {study_name}")
    print("=" * 96)
    print(f"Total valid trials: {len(points)}")
    print(f"Frontier size:      {len(frontier)}  (non-dominated)")
    if knee is not None:
        print(f"Knee point:         T{knee[2].number:03d}  "
              f"(value={knee[0]:.4f}, sum_mean={knee[1]:.4e})")
    print()

    # Frontier table
    print("Frontier trials (sorted by value descending):")
    print(f"  {'T#':>4s}  {'value':>8s}  {'sum_mean':>11s}  "
          f"{'M':>4s}  {'cma':>4s}  {'k':>3s}  {'nb':>3s}  "
          f"{'mbs':>4s}  {'sd':>5s}  {'tolx':>4s}  {'rf':>6s}  notes")
    for p in frontier:
        v, sm, t = p
        is_knee = (knee is not None and p is knee)
        note = " ← KNEE" if is_knee else ""
        # Also flag value-best and sum_mean-best
        if v == max(f[0] for f in frontier):
            note += " (best value)"
        if sm == min(f[1] for f in frontier):
            note += " (best sum_mean)"

        par = t.params
        print(f"  T{t.number:03d}  {v:8.4f}  {sm:11.4e}  "
              f"{par['M_factor']:>4}  {par['cma_popsize']:>4}  "
              f"{par['k']:>3}  {par['n_initial_basins']:>3}  "
              f"{par['min_basin_size']:>4}  {par['sigma_divisor']:>5.2f}  "
              f"{par['tolx_exp']:>4}  {par['refine_frac']:>6.3f}"
              f"{note}")
    print()

    # ASCII scatter
    print("Scatter (· = trial, ★ = frontier):")
    print()
    ascii_scatter(points, frontier)
    print()

    # Spread of frontier
    if len(frontier) > 1:
        v_span = frontier[0][0] - frontier[-1][0]
        s_span = max(p[1] for p in frontier) - min(p[1] for p in frontier)
        print(f"Frontier span: Δvalue = {v_span:.4f}, "
              f"Δsum_mean = {s_span:.4e}")
        print(f"  → value range: {(1 - v_span/frontier[0][0])*100:.1f}% "
              f"of best, sum_mean range: "
              f"{s_span / max(p[1] for p in frontier) * 100:.1f}% "
              f"of worst on frontier")


if __name__ == "__main__":
    main()
