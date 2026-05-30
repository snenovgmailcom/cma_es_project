#!/usr/bin/env python3
"""
collect_basin_distribution.py

Recursively bisect an LHS sample of a CEC function and record the size
distribution of resulting basins. Two splitting strategies:

1. --splitting nbc      Cut longest internal NB-tree edge (Preuss Rule 1,
                        same logic as v26 split_basin).
2. --splitting sbisect  Spectral bisection of weighted NN-graph Laplacian
                        with critical-point-aware weights:
                            w_ij = 1 / (1 + 1_crit(i)*1_crit(j)*max(f_i,f_j))
                        Critical points are the top X% by f globally.
                        Cut minimises sum of crossed weights, so the cut
                        prefers to traverse critical-critical edges (low w)
                        and avoid regular edges (w=1) -> the cut follows
                        the topological ridge.

Stopping criteria:
  * Max number of leaf basins reached (default 32).
  * Sub-basin has <= D points -> it becomes a leaf, no further split.

Hypothesis being tested:
  * Composition (CEC f21-f30): roughly uniform basin sizes.
  * Hybrid     (CEC f11-f20): one dominant basin + many small ones (skewed).

Output CSV per (suite, fnum, seed) records:
  n_leaf_basins, max_basin_size, min_basin_size,
  basin_size_gini, basin_size_largest_share,
  basin_size_top1_share, basin_size_top3_share,
  full_size_list_json (sizes of all leaf basins, JSON-encoded)

Usage
-----
    python collect_basin_distribution.py --suite cec2017 --dim 10 \\
        --functions 11-30 --seeds 10 --splitting sbisect

    python collect_basin_distribution.py --suite cec2017 --dim 10 \\
        --functions 11-30 --seeds 10 --splitting nbc
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


# ----------------------------------------------------------------------
# NBC splitting (Preuss Rule 1: cut longest internal NB-tree edge)
# ----------------------------------------------------------------------

def nb_tree_indices(X_norm, y):
    """For each point, find its nearest better neighbour (by f) within the
    sample. Returns: nb_idx (int array, -1 for global best), nb_dist.

    Note: we DO NOT use the v26 C++ nb_tree module here. That module uses
    incremental kNN expansion with k_cap=256, and falls back to "connect
    to global best" when no better point is found within 256 NN. Those
    fallback edges have artificially large length and are NOT the true
    nearest-better. They poison the "longest internal edge" bisection
    strategy below.

    For bisection analysis we need EXACT nearest-better connections —
    so we use an exhaustive prefix-KDTree-based search.
    """
    from scipy.spatial import cKDTree
    n = len(y)
    order = np.argsort(y, kind='stable')

    nb_idx = np.full(n, -1, dtype=np.int64)
    nb_dist = np.full(n, np.inf, dtype=np.float64)

    # For each point at rank k, search nearest among rank<k points.
    # Rebuild KDTree at exponential intervals to amortise cost.
    seen_pts = []
    seen_orig = []
    chunk = max(1, n // 32)
    next_rebuild = 1
    tree = None
    for k_step in range(n):
        i = order[k_step]
        if k_step == 0:
            seen_pts.append(X_norm[i])
            seen_orig.append(int(i))
            continue
        if tree is None or len(seen_pts) >= next_rebuild:
            tree = cKDTree(np.asarray(seen_pts))
            next_rebuild = max(next_rebuild + chunk, len(seen_pts) + chunk)
        d, j_local = tree.query(X_norm[i], k=1)
        nb_idx[i] = seen_orig[int(j_local)]
        nb_dist[i] = float(d)
        seen_pts.append(X_norm[i])
        seen_orig.append(int(i))
    return nb_idx, nb_dist


def nbc_partition_preuss_lin(point_indices, X_norm, y, nb_idx, nb_dist,
                              phi=2.0, min_size=10, max_share=0.5,
                              max_recurse_depth=5):
    """
    Canonical NBC partition (Preuss 2010, 2012) with Lin et al. (2019)
    constraints.

    Algorithm:
      1. Preuss phi-cut: collect internal NB edges of this basin, compute
         mean edge length, cut all edges with length > phi * mean.
         Connected components of the remaining forest are raw basins.
      2. Lin constraint 1 (min size): basins with fewer than min_size
         points are absorbed into the nearest large basin (by Euclidean
         distance from absorbed-basin centroid to candidate-basin centroid).
      3. Lin constraint 2 (max share): if any single basin contains more
         than max_share of the points, recursively re-apply the partition
         on that basin's points only. Recurses up to max_recurse_depth
         times to avoid infinite loops on indivisible basins.

    Returns a list of point-index arrays (one per final basin).
    Always returns at least one basin.
    """
    n_total = len(point_indices)
    if n_total <= min_size:
        return [point_indices]

    set_in_basin = set(int(i) for i in point_indices)

    # === Step 1: Preuss phi-cut ===
    # Collect internal edges (i -> nb_idx[i]) where both ends are in basin.
    internal = []
    for i in point_indices:
        ji = int(nb_idx[i])
        if ji < 0 or ji not in set_in_basin:
            continue
        internal.append((int(i), ji, float(nb_dist[i])))

    if not internal:
        return [point_indices]   # no internal NB structure to partition

    mean_len = np.mean([d for _, _, d in internal])
    cut_threshold = phi * mean_len

    # Union-find: union all edges with length <= threshold
    parent = {idx: idx for idx in set_in_basin}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, j, d in internal:
        if d <= cut_threshold:
            union(i, j)

    # Group points by root
    roots_to_pts = {}
    for idx in set_in_basin:
        r = find(idx)
        roots_to_pts.setdefault(r, []).append(idx)

    raw_basins = [np.asarray(sorted(pts), dtype=np.int64)
                  for pts in roots_to_pts.values()]

    # === Step 2: Lin constraint 1 (absorb small basins) ===
    # Compute centroids in normalized x-space
    def centroid(b):
        return X_norm[b].mean(axis=0)

    while True:
        # Recompute small/large after each absorption
        small = [k for k, b in enumerate(raw_basins)
                 if len(b) < min_size]
        large = [k for k, b in enumerate(raw_basins)
                 if len(b) >= min_size]
        if not small or not large:
            break

        # For each small basin, find nearest large basin (by centroid dist)
        # and merge it in. Process one absorption per iteration so centroids
        # stay current.
        sb_idx = small[0]
        sb_centroid = centroid(raw_basins[sb_idx])
        best_lb_idx = None
        best_d = np.inf
        for lb_idx in large:
            d = np.linalg.norm(sb_centroid - centroid(raw_basins[lb_idx]))
            if d < best_d:
                best_d = d
                best_lb_idx = lb_idx

        # Merge sb into best_lb
        merged = np.concatenate([raw_basins[sb_idx], raw_basins[best_lb_idx]])
        raw_basins[best_lb_idx] = np.sort(merged)
        raw_basins.pop(sb_idx)

    # If ALL basins were small (no "large" to absorb into), keep them as is
    # but report (should be rare for our use case).

    # === Step 3: Lin constraint 2 (split dominant basins) ===
    if max_recurse_depth > 0 and n_total > 0:
        final_basins = []
        for b in raw_basins:
            if len(b) / n_total > max_share and len(b) >= 2 * min_size:
                # Recurse into this basin
                sub = nbc_partition_preuss_lin(
                    b, X_norm, y, nb_idx, nb_dist,
                    phi=phi, min_size=min_size, max_share=max_share,
                    max_recurse_depth=max_recurse_depth - 1)
                # If recursion didn't actually split (returned single
                # basin same size), keep as is to avoid infinite loops.
                if len(sub) <= 1 or len(sub[0]) == len(b):
                    final_basins.append(b)
                else:
                    final_basins.extend(sub)
            else:
                final_basins.append(b)
        raw_basins = final_basins

    return raw_basins


# ----------------------------------------------------------------------
# Spectral bisection with critical-point weights
# ----------------------------------------------------------------------

def split_basin_sbisect(point_indices, X_norm, y, is_critical_global,
                        k_nn, eps_balance, full_knn=None, alpha=1.0):
    """Spectral bisection on a critical-weighted NN-graph Laplacian.

    Edge weight (with normalized y in [0,1]):
        w_ij = 1 / (1 + alpha * 1_crit(i)*1_crit(j)*max(f_i, f_j))

    With alpha=1, edge weights are in [0.5, 1] -> spectral cut behaves
    geometrically (almost-uniform Laplacian).

    With alpha=1e10, critical-critical edges have w ~= 1e-10 while other
    edges have w = 1 -> extreme contrast that forces Fiedler vector to be
    dominated by critical-point geometry. This is the "lucky" regime that
    accidentally worked on CEC2017 (because numerical degeneracy made
    eigsh fail for hybrid landscapes -> "no split" -> 1 leaf).

    If `full_knn` is provided, top-level call reuses it instead of
    rebuilding kNN.
    """
    from scipy.spatial import cKDTree
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import laplacian, connected_components
    from scipy.sparse.linalg import eigsh

    n = len(point_indices)
    if n <= 1:
        return point_indices, None

    sub_X = X_norm[point_indices]
    sub_y = y[point_indices]
    sub_crit = is_critical_global[point_indices]

    if full_knn is not None and n == len(X_norm):
        knn = full_knn
    else:
        k_actual = min(k_nn + 1, n)
        tree = cKDTree(sub_X)
        _, knn = tree.query(sub_X, k=k_actual)
        knn = knn[:, 1:]

    n_loc = len(sub_X)
    k_loc = knn.shape[1]
    src = np.repeat(np.arange(n_loc), k_loc)
    tgt = knn.ravel().astype(np.int64)
    valid = src != tgt
    src = src[valid]; tgt = tgt[valid]

    f_src = sub_y[src]; f_tgt = sub_y[tgt]
    crit_src = sub_crit[src]; crit_tgt = sub_crit[tgt]
    both_crit = crit_src & crit_tgt
    max_f = np.where(both_crit, np.maximum(f_src, f_tgt), 0.0)
    # Apply amplification factor alpha
    #w = 1.0 / (1.0 + alpha * max_f)
    #w = 2.0 - crit_src.astype(float) - crit_tgt.astype(float)
    #w = np.where(both_crit, 0.01, 1.0)
    y_norm = (y - y.min()) / (y.max() - y.min() + 1e-30)   # to [0, 1]
    f_edge = 0.5 * (y_norm[src] + y_norm[tgt])             # mid-f of edge
    w = np.exp(-beta * f_edge)        # high-f edges weak, low-f edges strong
    

    rows = np.concatenate([src, tgt])
    cols = np.concatenate([tgt, src])
    data = np.concatenate([w, w])
    A = csr_matrix((data, (rows, cols)), shape=(n_loc, n_loc))
    A.sum_duplicates()

    n_comp, labels_cc = connected_components(A, directed=False)
    if n_comp >= 2:
        sizes = np.bincount(labels_cc)
        ord_cc = np.argsort(-sizes)
        left_mask = (labels_cc == ord_cc[0])
        right_mask = ~left_mask
        if right_mask.sum() == 0 or left_mask.sum() == 0:
            return point_indices, None
        return point_indices[left_mask], point_indices[right_mask]

    L = laplacian(A, normed=False).astype(np.float64)
    try:
        if n_loc < 1500:
            from scipy.linalg import eigh
            eigvals, eigvecs = eigh(L.toarray())
            fiedler = eigvecs[:, 1]
        else:
            eigvals, eigvecs = eigsh(L, k=2, which='SM',
                                     maxiter=5000, tol=1e-6)
            order = np.argsort(eigvals)
            fiedler = eigvecs[:, order[1]]
    except Exception:
        return point_indices, None

    left_mask = fiedler > 0
    right_mask = ~left_mask

    if left_mask.sum() == 0 or right_mask.sum() == 0:
        return point_indices, None

    return point_indices[left_mask], point_indices[right_mask]


# ----------------------------------------------------------------------
# Recursive bisection driver
# ----------------------------------------------------------------------

def recursive_bisect_v2(X_norm, y, splitting, max_basins, min_basin_size,
                        is_critical_global=None, k_nn=8,
                        nb_idx=None, nb_dist=None, full_knn=None,
                        phi=2.0, max_share=0.5, alpha=1.0):
    """Driver for basin discovery.

    For splitting='nbc', this calls Preuss+Lin partition ONCE
    (no recursive bisection — Preuss+Lin already handles the partition
    structure including dominant-basin recursion internally).

    For splitting='sbisect', this still uses recursive spectral bisection
    until max_basins or min_basin_size is reached.
    """
    n_total = len(y)

    if splitting == 'nbc':
        # Single-call canonical NBC partition with Preuss phi-cut + Lin
        # constraints (min size, max share). Recursive splitting of the
        # dominant basin is handled inside nbc_partition_preuss_lin.
        all_indices = np.arange(n_total)
        basins = nbc_partition_preuss_lin(
            all_indices, X_norm, y, nb_idx, nb_dist,
            phi=phi, min_size=min_basin_size, max_share=max_share)
        return basins, 1, 0

    # === splitting == 'sbisect': recursive spectral bisection ===
    basins = [np.arange(n_total)]
    frozen = [False]
    is_top_level = [True]

    n_split_attempts = 0
    n_split_failures = 0

    while True:
        cand_ord = sorted(range(len(basins)),
                          key=lambda i: -len(basins[i]))
        target = None
        for ci in cand_ord:
            if not frozen[ci] and len(basins[ci]) > min_basin_size:
                target = ci
                break
        if target is None or len(basins) >= max_basins:
            break

        basin_to_split = basins[target]
        n_split_attempts += 1

        knn_arg = full_knn if is_top_level[target] else None
        left, right = split_basin_sbisect(
            basin_to_split, X_norm, y,
            is_critical_global, k_nn, eps_balance=0.0,
            full_knn=knn_arg, alpha=alpha)

        if right is None:
            frozen[target] = True
            n_split_failures += 1
            continue

        # SBISECT: do NOT reject splits where one side is small. The
        # original "lucky" behaviour required outlier-removal cuts (8499+1)
        # to be accepted — those small leaves cap recursion at exactly the
        # right structural granularity for composition functions.
        # NBC continues to reject small-side splits (handled in its own
        # branch via nbc_partition_preuss_lin's min_size constraint).

        basins.pop(target)
        frozen.pop(target)
        is_top_level.pop(target)
        basins.append(left)
        frozen.append(False)
        is_top_level.append(False)
        basins.append(right)
        frozen.append(False)
        is_top_level.append(False)

    return basins, n_split_attempts, n_split_failures

    return basins, n_split_attempts, n_split_failures


# ----------------------------------------------------------------------
# Worker: one (suite, fnum, seed)
# ----------------------------------------------------------------------

def compute_one(args):
    (suite, fnum, dim, seed, m_factor, splitting,
     critical_pct, k_nn, max_basins, min_basin_size,
     phi, max_share, alpha) = args

    from scipy.stats import qmc
    from minionpy import (CEC2014Functions, CEC2017Functions,
                          CEC2020Functions, CEC2022Functions)
    cls_map = {'cec2014': CEC2014Functions, 'cec2017': CEC2017Functions,
               'cec2020': CEC2020Functions, 'cec2022': CEC2022Functions}
    f = cls_map[suite](fnum, dim)

    out = {'suite': suite, 'fnum': fnum, 'seed': seed, 'dim': dim,
           'splitting': splitting}

    try:
        # 1. LHS sample
        n_points = m_factor * dim
        lhs = qmc.LatinHypercube(d=dim, seed=seed)
        unit = lhs.random(n_points)
        bounds_lo = np.full(dim, -100.0)
        bounds_hi = np.full(dim, 100.0)
        X = qmc.scale(unit, bounds_lo, bounds_hi)
        X_norm = (X - bounds_lo) / (bounds_hi - bounds_lo)

        # Evaluate
        y_native = np.asarray(f([row.tolist() for row in X]),
                              dtype=np.float64).ravel()
        out['sample_n'] = n_points
        out['sample_f_min_native'] = float(y_native.min())
        out['sample_f_range_native'] = float(y_native.max() - y_native.min())

        # Per-method y handling:
        # - NBC: normalize to [0,1]. NBC ranking is invariant to affine
        #   y-transforms, so this doesn't change the NB tree structure.
        #   It just keeps reporting consistent across suites.
        # - SBISECT: keep RAW y. The extreme weight contrast (critical-
        #   critical edges with w ~= 1e-11 vs other edges with w = 1)
        #   IS the design — it forces the Fiedler vector to be dominated
        #   by critical-point geometry. Normalizing kills this contrast
        #   and reduces SBISECT to balanced geometric partitioning.
        if splitting == 'sbisect':
            y = y_native    # raw values for extreme weight contrast
        else:
            if out['sample_f_range_native'] > 0:
                y = (y_native - y_native.min()) / out['sample_f_range_native']
            else:
                y = y_native - y_native.min()

        # 2. Pre-compute structures based on splitting strategy
        is_crit = None; nb_idx = None; nb_dist = None; full_knn = None
        if splitting == 'sbisect':
            n_critical = max(1, int(n_points * critical_pct / 100))
            critical_idx = np.argsort(-y)[:n_critical]   # highest f
            is_crit = np.zeros(n_points, dtype=bool)
            is_crit[critical_idx] = True
            out['n_critical_points'] = int(n_critical)
            # Pre-compute full kNN once — saves the most expensive part of
            # the first (full-sample) split. Sub-basin splits still rebuild
            # locally because density may differ.
            from scipy.spatial import cKDTree
            tree = cKDTree(X_norm)
            _, full_knn = tree.query(X_norm, k=k_nn + 1)
            full_knn = full_knn[:, 1:]
        elif splitting == 'nbc':
            nb_idx, nb_dist = nb_tree_indices(X_norm, y)

        # 3. Discover basins
        basins, n_attempts, n_fails = recursive_bisect_v2(
            X_norm, y, splitting,
            max_basins=max_basins,
            min_basin_size=min_basin_size,
            is_critical_global=is_crit,
            k_nn=k_nn, nb_idx=nb_idx, nb_dist=nb_dist,
            full_knn=full_knn,
            phi=phi, max_share=max_share, alpha=alpha)

        # 4. Stats on basin sizes
        sizes = np.array(sorted([len(b) for b in basins], reverse=True))
        out['n_leaf_basins'] = len(sizes)
        out['n_split_attempts'] = n_attempts
        out['n_split_failures'] = n_fails
        out['max_basin_size'] = int(sizes.max())
        out['min_basin_size_actual'] = int(sizes.min())

        total = float(sizes.sum())
        if total > 0:
            shares = sizes / total
            out['top1_share'] = float(shares[0])
            out['top3_share'] = float(shares[:3].sum())
            # Gini coefficient on basin sizes
            n = len(sizes)
            if n > 1:
                cum = np.cumsum(np.sort(sizes))
                gini = (2 * np.sum((np.arange(1, n + 1)) * np.sort(sizes))) \
                        / (n * cum[-1]) - (n + 1) / n
                out['size_gini'] = float(gini)
            else:
                out['size_gini'] = 0.0
            out['mean_size'] = float(sizes.mean())
            out['std_size'] = float(sizes.std())
        else:
            out['top1_share'] = 0.0
            out['top3_share'] = 0.0
            out['size_gini'] = 0.0
            out['mean_size'] = 0.0
            out['std_size'] = 0.0

        out['size_list_json'] = json.dumps(sizes.tolist())

    except Exception as exc:
        import traceback
        out['error'] = f'{type(exc).__name__}: {exc}'
        out['traceback'] = traceback.format_exc()[:500]

    gt = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
    out['ground_truth_label'] = gt
    out['ground_truth_class'] = CLASS_MAP.get(gt, -1)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True,
                   help='One or comma-separated suites: cec2014,cec2017,cec2020,cec2022')
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--seeds', type=int, default=10)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--functions', type=str, default=None,
                   help='Optional subset (e.g. "11-30"). Default: all in suite.')
    p.add_argument('--jobs', type=int, default=20)
    p.add_argument('--m-factor', type=int, default=850)
    p.add_argument('--splitting', choices=['nbc', 'sbisect'],
                   default='sbisect')
    p.add_argument('--critical-pct', type=float, default=10.0,
                   help='Percent of points marked critical (sbisect only)')
    p.add_argument('--k-nn', type=int, default=8)
    p.add_argument('--max-basins', type=int, default=32,
                   help='Hard cap on basin count (sbisect only — nbc count '
                        'is determined by phi/min-size/max-share)')
    p.add_argument('--min-basin-size', type=int, default=None,
                   help='Default: D (dimension)')
    p.add_argument('--phi', type=float, default=2.0,
                   help='Preuss NBC cut threshold: edges with length > phi '
                        '* mean_edge_length are cut. Default 2.0.')
    p.add_argument('--max-share', type=float, default=0.5,
                   help='Lin constraint: any basin holding >max_share of '
                        'points is recursively re-partitioned. Default 0.5.')
    p.add_argument('--alpha', type=float, default=1.0,
                   help='SBISECT critical-edge weight amplification: '
                        'w = 1/(1 + alpha * 1_crit*1_crit*max(f)). '
                        'Default 1.0 (mild). Try 1e10 to reproduce the '
                        '"lucky" pre-normalization signal.')
    p.add_argument('--out', default=None)
    args = p.parse_args()

    if args.min_basin_size is None:
        args.min_basin_size = args.dim

    # Parse suites (comma-separated, or single)
    suite_list = [s.strip() for s in args.suite.split(',')]
    for s in suite_list:
        if s not in SUITE_CONFIG:
            print(f'Unknown suite: {s}. Choices: {list(SUITE_CONFIG.keys())}',
                  file=sys.stderr)
            sys.exit(1)

    # Build task list across all suites
    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    tasks = []
    suite_funcs = {}
    for suite in suite_list:
        n_funcs, _ = SUITE_CONFIG[suite]
        if args.functions:
            func_list = []
            for part in args.functions.split(','):
                if '-' in part:
                    lo, hi = part.split('-')
                    func_list.extend(range(int(lo), int(hi) + 1))
                else:
                    func_list.append(int(part))
            # Filter to what exists in the suite
            func_list = [f for f in func_list if 1 <= f <= n_funcs]
        else:
            func_list = list(range(1, n_funcs + 1))
        suite_funcs[suite] = func_list
        for fnum in func_list:
            for seed in seeds:
                tasks.append((suite, fnum, args.dim, seed, args.m_factor,
                              args.splitting, args.critical_pct, args.k_nn,
                              args.max_basins, args.min_basin_size,
                              args.phi, args.max_share, args.alpha))

    out = args.out or (f'basin_distrib_{"_".join(suite_list)}_d{args.dim}_'
                       f'{args.splitting}.csv')

    print(f'=== Basin discovery: {args.splitting.upper()} ===')
    print(f'  Suites:       {", ".join(suite_list)}')
    for s in suite_list:
        fl = suite_funcs[s]
        print(f'    {s}: {len(fl)} funcs ({fl[0]}..{fl[-1]})')
    print(f'  Dim:          D={args.dim}')
    print(f'  Seeds:        {len(seeds)}  ({seeds[0]}..{seeds[-1]})')
    print(f'  Sample size:  {args.m_factor * args.dim} pts')
    print(f'  min_size:     {args.min_basin_size}')
    if args.splitting == 'nbc':
        print(f'  phi:          {args.phi}  (Preuss cut threshold)')
        print(f'  max_share:    {args.max_share}  (Lin dominant-basin recursion)')
    elif args.splitting == 'sbisect':
        print(f'  k_NN:         {args.k_nn}')
        print(f'  max_basins:   {args.max_basins}')
        print(f'  critical_pct: {args.critical_pct}%')
        print(f'  alpha:        {args.alpha}  (weight amplification)')
    print(f'  Tasks:        {len(tasks)}  (jobs={args.jobs})')
    print(f'  Output:       {out}')
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
                print(f'  {done}/{len(tasks)}  ({time.time()-t0:.0f}s)')

    df = pd.DataFrame(results)
    df.to_csv(out, index=False)
    print(f'\nWrote {len(df)} rows to {out}\n')

    # Summary table
    if 'n_leaf_basins' not in df.columns:
        print('No successful runs to summarise.')
        return

    # Per-suite, per-function summary
    for suite in suite_list:
        sd = df[df['suite'] == suite]
        if len(sd) == 0:
            continue
        print(f'\n--- {suite.upper()} D={args.dim} ---')
        print(f'{"fn":<5}{"gt":<14}{"#runs":>6}'
              f'{"#leaves":>9}{"top1%":>8}{"top3%":>8}{"gini":>7}'
              f'{"max_size":>10}{"min_size":>10}')
        print('-' * 80)
        for fn in sorted(sd['fnum'].unique()):
            d = sd[sd['fnum'] == fn].dropna(subset=['n_leaf_basins'])
            if len(d) == 0:
                gt = sd[sd['fnum'] == fn]['ground_truth_label'].iloc[0]
                print(f'f{fn:<4}{gt:<14}{0:>6}  (all NaN)')
                continue
            gt = d['ground_truth_label'].iloc[0]
            print(f'f{fn:<4}{gt:<14}{len(d):>6}'
                  f'{int(d["n_leaf_basins"].median()):>9}'
                  f'{100*d["top1_share"].median():>7.1f}%'
                  f'{100*d["top3_share"].median():>7.1f}%'
                  f'{d["size_gini"].median():>7.3f}'
                  f'{int(d["max_basin_size"].median()):>10}'
                  f'{int(d["min_basin_size_actual"].median()):>10}')

    # Aggregated by class across ALL suites
    print()
    print('Aggregated by class (median across ALL suites):')
    print(f'{"class":<14}{"#runs":>6}{"#leaves":>9}{"top1%":>8}{"top3%":>8}'
          f'{"gini":>7}{"max":>10}{"min":>10}')
    print('-' * 70)
    for cls_name in ['unimodal', 'basic', 'hybrid', 'composition']:
        d = df[df['ground_truth_label'] == cls_name].dropna(
            subset=['n_leaf_basins'])
        if len(d) == 0:
            continue
        print(f'{cls_name:<14}{len(d):>6}'
              f'{int(d["n_leaf_basins"].median()):>9}'
              f'{100*d["top1_share"].median():>7.1f}%'
              f'{100*d["top3_share"].median():>7.1f}%'
              f'{d["size_gini"].median():>7.3f}'
              f'{int(d["max_basin_size"].median()):>10}'
              f'{int(d["min_basin_size_actual"].median()):>10}')


if __name__ == '__main__':
    main()
