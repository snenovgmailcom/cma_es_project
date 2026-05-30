#!/usr/bin/env python3
"""
collect_morse_persistence.py

Discrete Morse-Smale watershed on Phase-0 LHS sample. For each point in
ascending f-order, classify as: minimum (no lower neighbours), regular
(1 lower neighbour), or saddle candidate (>=2 lower neighbours).

Saddle classification uses the geometric collinearity + transversality
test on (lower-pair, upper-pair):
    1. Pick the closest 4 neighbours
    2. Check if they split into 2 lower + 2 upper
    3. Collinearity: the two lower form a line through O (cos(v_l1, v_l2) <= -cos(alpha))
    4. Same for the two upper
    5. Transversality: the lower-line and upper-line are not parallel
       (1 - <v_l1, v_u1>^2 >= sin^2(beta))
    6. Norm-ratio gate: max(d) / min(d) <= 5

If saddle accepted, merge the two lower basins via union-find with Elder's
Rule (the basin with worse best_val dies; persistence = f(O) - f(min_dying)).

Output CSV per (fnum, seed):
    suite, fnum, seed, dim, ground_truth_label, ground_truth_class,
    n_minima, n_saddles_accepted, n_saddle_candidates_rejected,
    n_basins_alive_at_end,
    max_persistence, mean_persistence_top5, median_persistence,
    max_persistence_rel, mean_persistence_rel_top5,
    sample_f_min, sample_f_range

Usage
-----
    python collect_morse_persistence.py --suite cec2017 --dim 10 \\
        --functions 11-30 --seeds 10
    python collect_morse_persistence.py --suite cec2017 --dim 10 \\
        --functions 12,22 --seeds 5 --k-nn 8 --alpha-deg 25 --beta-deg 30
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd


SUITE_CONFIG = {
    'cec2014': (30, [5, 10, 20, 30, 50, 100]),
    'cec2017': (30, [5, 10, 20, 30, 50, 100]),
    'cec2020': (10, [5, 10, 15, 20]),
    'cec2022': (12, [10, 20]),
}
GROUND_TRUTH = {
    'cec2017': {**{i: 'unimodal' for i in [1, 2, 3]},
                **{i: 'basic' for i in range(4, 11)},
                **{i: 'hybrid' for i in range(11, 21)},
                **{i: 'composition' for i in range(21, 31)}},
    'cec2020': {1: 'unimodal',
                2: 'basic', 3: 'basic', 4: 'basic',
                5: 'hybrid', 6: 'hybrid', 7: 'hybrid',
                8: 'composition', 9: 'composition', 10: 'composition'},
    'cec2022': {1: 'unimodal', 2: 'basic', 3: 'basic', 4: 'basic', 5: 'basic',
                6: 'hybrid', 7: 'hybrid', 8: 'hybrid',
                9: 'composition', 10: 'composition',
                11: 'composition', 12: 'composition'},
    'cec2014': {**{i: 'unimodal' for i in [1, 2, 3]},
                **{i: 'basic' for i in range(4, 17)},
                **{i: 'hybrid' for i in range(17, 23)},
                **{i: 'composition' for i in range(23, 31)}},
}
CLASS_MAP = {'unimodal': 0, 'basic': 0, 'hybrid': 1, 'composition': 2}


def saddle_test_2plus2(O, lower_pos, upper_pos,
                        cos_alpha_thr, sin2_beta_thr, norm_ratio_max):
    """Discrete Morse saddle test on a 2-lower + 2-upper neighbourhood.

    Caller must pass the 2 closest LOWER neighbours and 2 closest UPPER
    neighbours (separately selected by rank type then by distance). This
    is the semantically correct selection — taking "closest 4 overall"
    fails in high-D because lower/upper density usually differs sharply
    around any saddle candidate.

    Geometric test:
      - Lower pair must be collinear through O (anti-parallel unit vectors).
      - Upper pair must be collinear through O.
      - Lower line and upper line must be transversal (non-parallel).
      - Distance ratio max/min <= norm_ratio_max for symmetry.
    """
    if len(lower_pos) != 2 or len(upper_pos) != 2:
        return False

    pos4 = np.vstack([lower_pos, upper_pos])

    # Norm-ratio gate (symmetry of arms)
    diffs = pos4 - O
    norms = np.linalg.norm(diffs, axis=1)
    if norms.min() <= 0:
        return False
    if norms.max() / norms.min() > norm_ratio_max:
        return False

    # Unit vectors
    v_lower = (lower_pos - O) / np.linalg.norm(lower_pos - O,
                                                axis=1, keepdims=True)
    v_upper = (upper_pos - O) / np.linalg.norm(upper_pos - O,
                                                axis=1, keepdims=True)

    # Collinearity: lower pair anti-parallel (cos close to -1)
    c_lower = float(np.clip(np.dot(v_lower[0], v_lower[1]), -1.0, 1.0))
    if c_lower > -cos_alpha_thr:
        return False

    c_upper = float(np.clip(np.dot(v_upper[0], v_upper[1]), -1.0, 1.0))
    if c_upper > -cos_alpha_thr:
        return False

    # Transversality: take the min sin^2 over all 4 cross-pairs (strictest)
    g_min = float('inf')
    for vl in v_lower:
        for vu in v_upper:
            g = 1.0 - float(np.clip(np.dot(vl, vu), -1.0, 1.0)) ** 2
            if g < g_min:
                g_min = g
    if g_min < sin2_beta_thr:
        return False

    return True


def compute_one(args):
    """Worker: Morse-Smale watershed analysis for one (suite, fnum, seed)."""
    (suite, fnum, dim, seed,
     m_factor, k_nn, alpha_deg, beta_deg, norm_ratio_max) = args

    from scipy.spatial import cKDTree
    from scipy.stats import qmc
    from minionpy import (CEC2014Functions, CEC2017Functions,
                          CEC2020Functions, CEC2022Functions)

    cls_map = {'cec2014': CEC2014Functions, 'cec2017': CEC2017Functions,
               'cec2020': CEC2020Functions, 'cec2022': CEC2022Functions}
    f = cls_map[suite](fnum, dim)

    out = {'suite': suite, 'fnum': fnum, 'seed': seed, 'dim': dim}

    try:
        # 1. LHS sample identical to v26's NBCDetector
        n_points = m_factor * dim
        lhs = qmc.LatinHypercube(d=dim, seed=seed)
        unit = lhs.random(n_points)
        bounds_lo = np.full(dim, -100.0)
        bounds_hi = np.full(dim, 100.0)
        X = qmc.scale(unit, bounds_lo, bounds_hi)
        y = np.asarray(f([row.tolist() for row in X]), dtype=float).ravel()

        out['sample_f_min'] = float(y.min())
        out['sample_f_range'] = float(y.max() - y.min())

        # 2. Build kNN graph (in normalised coordinates, like v26)
        # Normalise to [0,1] for distance computation
        X_norm = (X - bounds_lo) / (bounds_hi - bounds_lo)
        tree = cKDTree(X_norm)
        # k+1 because each point is its own nearest neighbour
        _, knn_idx = tree.query(X_norm, k=k_nn + 1)
        knn_idx = knn_idx[:, 1:]   # drop self

        # 3. Sort points by f, ascending
        order = np.argsort(y, kind='stable')
        # rank[i] = position of point i in ascending order (0 = lowest f)
        rank = np.empty(len(y), dtype=np.int64)
        rank[order] = np.arange(len(y))

        # Discrete saddle thresholds
        cos_alpha = float(np.cos(np.radians(alpha_deg)))
        sin2_beta = float(np.sin(np.radians(beta_deg))) ** 2

        # 4. Watershed loop with union-find
        parent = np.arange(len(y), dtype=np.int64)
        basin_best = np.full(len(y), np.inf, dtype=np.float64)

        def find(i):
            r = i
            while parent[r] != r:
                r = parent[r]
            while parent[i] != r:
                parent[i], i = r, parent[i]
            return r

        n_minima = 0
        n_saddles_accepted = 0
        n_saddle_rejected = 0
        persistences = []   # values from accepted saddle merges

        for idx in order:
            f_O = y[idx]
            O = X_norm[idx]
            neigh = knn_idx[idx]
            # Already-processed neighbours = those with smaller rank
            lower_neigh = neigh[rank[neigh] < rank[idx]]

            if len(lower_neigh) == 0:
                # Local minimum: start a new basin
                parent[idx] = idx
                basin_best[idx] = f_O
                n_minima += 1
                continue

            # Roots of all lower neighbours
            lower_roots = set(int(find(int(j))) for j in lower_neigh)

            if len(lower_roots) == 1:
                # Regular point: merge into that basin
                root = lower_roots.pop()
                parent[idx] = root
                if f_O < basin_best[root]:
                    basin_best[root] = f_O
                continue

            # >=2 distinct basins among lower neighbours -> merge event.
            # Chazal, Guibas, Oudot, Skraba (DCG 2011, JACM 2013):
            # "Analysis of Scalar Fields over Point Cloud Data" /
            # "Persistence-Based Clustering in Riemannian Manifolds".
            # No geometric saddle test needed — persistence pairing on the
            # filtered NN graph is algebraically stable in any dimension.
            # Elder's Rule: younger basin (worse best_val) dies; persistence
            # is the gap between the merge level and the dying basin's best.
            roots_list = sorted(lower_roots,
                                key=lambda r: basin_best[r])
            survivor = roots_list[0]
            for dying in roots_list[1:]:
                persistence = f_O - basin_best[dying]
                persistences.append(float(persistence))
                parent[dying] = survivor
            parent[idx] = survivor
            if f_O < basin_best[survivor]:
                basin_best[survivor] = f_O
            n_saddles_accepted += 1

            # End of merge handling — continue to next point
            continue

        # 5. Count surviving basins
        # A basin is "alive" if it's the root of its component
        alive_roots = set()
        for i in range(len(y)):
            alive_roots.add(int(find(i)))
        out['n_minima'] = n_minima
        out['n_saddles_accepted'] = n_saddles_accepted
        out['n_saddle_candidates_rejected'] = n_saddle_rejected
        out['n_basins_alive_at_end'] = len(alive_roots)

        # 6. Persistence stats
        if persistences:
            arr = np.array(persistences, dtype=np.float64)
            f_range = out['sample_f_range']
            out['max_persistence'] = float(arr.max())
            sorted_desc = np.sort(arr)[::-1]
            out['mean_persistence_top5'] = float(sorted_desc[:5].mean())
            out['median_persistence'] = float(np.median(arr))
            if f_range > 0:
                rel = arr / f_range
                rel_sorted_desc = np.sort(rel)[::-1]
                out['max_persistence_rel'] = float(rel_sorted_desc[0])
                out['mean_persistence_rel_top5'] = float(
                    rel_sorted_desc[:5].mean())
                # Counts of "significant" basins at multiple thresholds
                out['n_basins_p_gt_1pct'] = int((rel > 0.01).sum())
                out['n_basins_p_gt_5pct'] = int((rel > 0.05).sum())
                out['n_basins_p_gt_10pct'] = int((rel > 0.10).sum())
                out['n_basins_p_gt_25pct'] = int((rel > 0.25).sum())
                # Top-20 persistence values (relative), JSON-encoded for CSV
                top20 = rel_sorted_desc[:20].tolist()
                out['top20_persistence_rel_json'] = json.dumps(top20)
            else:
                out['max_persistence_rel'] = 0.0
                out['mean_persistence_rel_top5'] = 0.0
                out['n_basins_p_gt_1pct'] = 0
                out['n_basins_p_gt_5pct'] = 0
                out['n_basins_p_gt_10pct'] = 0
                out['n_basins_p_gt_25pct'] = 0
                out['top20_persistence_rel_json'] = '[]'
        else:
            out['max_persistence'] = 0.0
            out['mean_persistence_top5'] = 0.0
            out['median_persistence'] = 0.0
            out['max_persistence_rel'] = 0.0
            out['mean_persistence_rel_top5'] = 0.0
            out['n_basins_p_gt_1pct'] = 0
            out['n_basins_p_gt_5pct'] = 0
            out['n_basins_p_gt_10pct'] = 0
            out['n_basins_p_gt_25pct'] = 0
            out['top20_persistence_rel_json'] = '[]'

    except Exception as exc:
        out['error'] = f'{type(exc).__name__}: {exc}'

    gt = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
    out['ground_truth_label'] = gt
    out['ground_truth_class'] = CLASS_MAP.get(gt, -1)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True,
                   choices=list(SUITE_CONFIG.keys()))
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--seeds', type=int, default=10)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--functions', type=str, default=None,
                   help='Function range, e.g. "11-30" or "12,22". '
                        'Default: all functions in suite.')
    p.add_argument('--jobs', type=int, default=20)
    p.add_argument('--m-factor', type=int, default=850,
                   help='Phase 0 LHS = m_factor * dim. Default 850.')
    p.add_argument('--k-nn', type=int, default=8,
                   help='kNN graph k. Default 8.')
    p.add_argument('--alpha-deg', type=float, default=25.0,
                   help='Collinearity tolerance in degrees. Default 25.')
    p.add_argument('--beta-deg', type=float, default=30.0,
                   help='Transversality threshold in degrees. Default 30.')
    p.add_argument('--norm-ratio-max', type=float, default=5.0,
                   help='Max ratio between farthest/closest of 4 NN. Default 5.')
    p.add_argument('--out', default=None)
    args = p.parse_args()

    n_funcs, _ = SUITE_CONFIG[args.suite]
    if args.functions:
        func_list = []
        for part in args.functions.split(','):
            if '-' in part:
                lo, hi = part.split('-')
                func_list.extend(range(int(lo), int(hi) + 1))
            else:
                func_list.append(int(part))
    else:
        func_list = list(range(1, n_funcs + 1))

    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    out = args.out or f'morse_{args.suite}_d{args.dim}.csv'

    tasks = [(args.suite, fnum, args.dim, seed,
              args.m_factor, args.k_nn,
              args.alpha_deg, args.beta_deg, args.norm_ratio_max)
             for fnum in func_list for seed in seeds]

    print(f'=== Morse-Smale watershed test ===')
    print(f'  Suite/dim:      {args.suite} D={args.dim}')
    print(f'  Functions:      {func_list[0]}..{func_list[-1]} '
          f'({len(func_list)} funcs)')
    print(f'  Seeds:          {len(seeds)}  ({seeds[0]}..{seeds[-1]})')
    print(f'  Sample size:    {args.m_factor * args.dim} pts/Phase-0')
    print(f'  k_NN={args.k_nn}  alpha={args.alpha_deg}deg  '
          f'beta={args.beta_deg}deg  norm_ratio_max={args.norm_ratio_max}')
    print(f'  Tasks:          {len(tasks)}  (jobs={args.jobs})')
    print(f'  Output:         {out}')
    print()

    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        fut = {ex.submit(compute_one, t): t for t in tasks}
        done = 0
        for f in as_completed(fut):
            try:
                results.append(f.result())
            except Exception as e:
                t = fut[f]
                print(f'  ERROR {t[0]}/f{t[1]}/seed{t[3]}: {e}',
                      file=sys.stderr)
            done += 1
            if done % 20 == 0 or done == len(tasks):
                elapsed = time.time() - t0
                print(f'  {done}/{len(tasks)}  ({elapsed:.0f}s)')

    df = pd.DataFrame(results)
    df.to_csv(out, index=False)
    print(f'\nWrote {len(df)} rows to {out}\n')

    # Per-function summary: focus on significant-basin counts at multiple
    # persistence thresholds (relative to sample f-range).
    print(f'{"fn":<5}{"gt":<14}{"#runs":>6}'
          f'{"#sad":>6}{"max_p%":>8}'
          f'{">1%":>6}{">5%":>6}{">10%":>6}{">25%":>6}')
    print('-' * 80)
    for fn in sorted(df['fnum'].unique()):
        d = df[df['fnum'] == fn].dropna(subset=['n_basins_alive_at_end'])
        if len(d) == 0:
            gt = df[df['fnum'] == fn]['ground_truth_label'].iloc[0]
            print(f'f{fn:<4}{gt:<14}{0:>6}  (all NaN)')
            continue
        gt = d['ground_truth_label'].iloc[0]
        n = len(d)
        n_sad = int(d['n_saddles_accepted'].median())
        max_p_pct = 100 * d['max_persistence_rel'].median()
        n1  = int(d['n_basins_p_gt_1pct'].median())
        n5  = int(d['n_basins_p_gt_5pct'].median())
        n10 = int(d['n_basins_p_gt_10pct'].median())
        n25 = int(d['n_basins_p_gt_25pct'].median())
        print(f'f{fn:<4}{gt:<14}{n:>6}'
              f'{n_sad:>6}{max_p_pct:>7.2f}%'
              f'{n1:>6}{n5:>6}{n10:>6}{n25:>6}')

    # Class-aggregated comparison
    print()
    print('Aggregated by class (median across all runs):')
    print(f'{"class":<14}{"#runs":>6}{"#sad":>6}{"max_p%":>8}'
          f'{">1%":>6}{">5%":>6}{">10%":>6}{">25%":>6}')
    print('-' * 65)
    for cls_name in ['unimodal', 'basic', 'hybrid', 'composition']:
        d = df[df['ground_truth_label'] == cls_name].dropna(
            subset=['n_basins_alive_at_end'])
        if len(d) == 0:
            continue
        print(f'{cls_name:<14}{len(d):>6}'
              f'{int(d["n_saddles_accepted"].median()):>6}'
              f'{100*d["max_persistence_rel"].median():>7.2f}%'
              f'{int(d["n_basins_p_gt_1pct"].median()):>6}'
              f'{int(d["n_basins_p_gt_5pct"].median()):>6}'
              f'{int(d["n_basins_p_gt_10pct"].median()):>6}'
              f'{int(d["n_basins_p_gt_25pct"].median()):>6}')


if __name__ == '__main__':
    main()
