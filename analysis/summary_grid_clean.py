#!/usr/bin/env python3
"""
analysis/summary_grid.py — compact cross-suite/dim summary tables.

Walks the experiments/ directory tree, discovers every
    experiments/<suite>/d<dim>/<algo>/maxevals_<N>/
cell that contains pkls, and produces compact tables aggregated per
(suite, dim, maxevals) cell × algorithm.

Six tables emitted (all in the same SUM(...) style):
    1. SUM(mean error)        — total mean error across functions in the cell
    2. SUM(median error)      — total median error (robust)
    3. SUM(std)               — total per-function std across functions
    4. SUM(best error)        — total best (min) final error across functions
    5. SUM(worst error)       — total worst (max) final error across functions
    6. SUM(FBTC)              — total Fixed-Budget Target Coverage
                                (higher is better, bounded by n_funcs)

THR_k (per-target hit counts) are still computed per function but are only
used by the optional --by-dim bucket tables; the standalone FBTC
visualization table and the per-function wins table have been removed.

Metric definitions
------------------
  hit(seed, f, k)  = 1 if final error of (seed, f) <= 10^k, else 0

  FBTC_f(algo)     = (1/51) * sum over the 51 log-uniform targets in
                     [10^+2, 10^-8] of the per-target success rate at
                     final budget.  Anchored to the Optuna optimization
                     objective — the target set must remain 51 points.
                     Range: [0, 1].
                     NOT the COCO runtime-integrated ECDF — this is the
                     fixed-budget horizontal slice at the final eval count.
                     NOT mean(THR_k): THR_k uses the 11-decade grid.

  SUM(FBTC)(cell)  = sum over functions in the cell of FBTC_f.
                     Range: [0, n_functions].  Higher is better.

  THR_k(cell, a)   = #(seed × function) hits at threshold 10^k in the cell.
                     Computed on the 11-decade grid, k in [+2, -8].  Only
                     used by the --by-dim bucket tables now.
                     max = n_seeds × n_functions in cell.

  SUM(best)(cell)  = sum over functions in the cell of the best (minimum)
                     final error across seeds.  Lower is better.

  SUM(worst)(cell) = sum over functions in the cell of the worst (maximum)
                     final error across seeds.  Lower is better.

  SUM(std)(cell)   = sum over functions in the cell of per-function
                     standard deviation of final errors across seeds.
                     Caveat: scale-sensitive — same caveat as SUM(mean).

Algorithm-name normalization (so MSC-CMA-B1M, MSC-CMA-B3M, MSC-CMA-B10M etc.
all show up under the same "MSC-CMA" column):
    MSC-CMA*           → MSC-CMA
    ARRDE-*            → ARRDE
    LSRTDE-*           → LSRTDE
    BIPOP-CMA-*        → BIPOP-CMA

Usage
-----
    python analysis/summary_grid.py
    python analysis/summary_grid.py --root experiments
    python analysis/summary_grid.py --metric fbtc
    python analysis/summary_grid.py --metric best
    python analysis/summary_grid.py --csv summary.csv
    python analysis/summary_grid.py --func-class hybrid
    python analysis/summary_grid.py --basic-dims --func-class composition
"""

import argparse
import csv
import os
import pickle
import re
import sys
from collections import defaultdict

import numpy as np


# =========================================================================
# COCO target convention (51 log-uniform targets, anchors FBTC)
# =========================================================================

COCO_ZERO = 1e-8
N_TARGETS = 51
TARGET_HI = 1e+2
TARGET_LO = 1e-8
COCO_TARGETS = np.logspace(np.log10(TARGET_HI), np.log10(TARGET_LO),
                           num=N_TARGETS, dtype=np.float64)

# Canonical COCO/CEC display target grid: 11 decade depths from 10^2 to 10^-8.
COCO_DEPTH_EXPONENTS = list(range(2, -9, -1))      # 2, 1, 0, -1, ..., -8
COCO_DEPTHS = np.array([10.0 ** k for k in COCO_DEPTH_EXPONENTS],
                       dtype=np.float64)


# =========================================================================
# Algorithm name normalization
# =========================================================================

ALGO_PATTERNS = [
    # (re.compile(r'^MSC-CMA(-.*)?$'),       'MSC-CMA'),  # commented: keep MSC-CMA variants distinct
    (re.compile(r'^ARRDE(-.*)?$'),         'ARRDE'),
    (re.compile(r'^jSO(-.*)?$'),           'jSO'),
    (re.compile(r'^j2020(-.*)?$'),         'j2020'),
    (re.compile(r'^NLSHADE-RSP(-.*)?$'),   'NLSHADE-RSP'),
    (re.compile(r'^LSRTDE(-.*)?$'),        'LSRTDE'),
    (re.compile(r'^BIPOP-CMA(-.*)?$'),     'BIPOP-CMA'),
]


# =========================================================================
# CEC function classes, per the CEC technical-report groupings.
# 'basic' = unimodal + simple multimodal (everything before the hybrids).
# Edit the ranges here if your suite implementation numbers differ.
# =========================================================================

FUNC_CLASSES = {
    'cec2014': {
        'basic':       set(range(1, 17)),   # f1-f3 unimodal, f4-f16 simple multimodal
        'hybrid':      set(range(17, 23)),  # f17-f22
        'composition': set(range(23, 31)),  # f23-f30
    },
    'cec2017': {
        'basic':       set(range(1, 11)),   # f1-f3 unimodal (f2 deprecated), f4-f10 simple multimodal
        'hybrid':      set(range(11, 21)),  # f11-f20
        'composition': set(range(21, 31)),  # f21-f30
    },
    'cec2020': {
        'basic':       set(range(1, 5)),    # f1 unimodal, f2-f4 basic
        'hybrid':      set(range(5, 8)),    # f5-f7
        'composition': set(range(8, 11)),   # f8-f10
    },
    'cec2022': {
        'basic':       set(range(1, 6)),    # f1 unimodal, f2-f5 basic
        'hybrid':      set(range(6, 9)),    # f6-f8
        'composition': set(range(9, 13)),   # f9-f12
    },
}


# =========================================================================
# Standard (suite, dim) -> {budgets} whitelist for --basic-dims.
# =========================================================================

STANDARD_CELLS = {
    ('cec2014', 10): {100_000, 300_000, 600_000, 1_000_000},
    ('cec2014', 30): {300_000, 600_000, 1_000_000},
    ('cec2017', 10): {100_000, 300_000, 600_000, 1_000_000},
    ('cec2017', 30): {300_000, 600_000, 1_000_000},
    ('cec2020',  5): {50_000, 100_000, 300_000, 500_000},
    ('cec2020', 10): {1_000_000, 3_000_000, 10_000_000},
    ('cec2020', 15): {3_000_000, 9_000_000},
    ('cec2022', 10): {200_000, 600_000, 1_000_000},
    ('cec2022', 20): {1_000_000, 3_000_000, 6_000_000},
}


# =========================================================================
# Official CEC MaxFES per (suite, dim) for --cec-budget — exactly one
# budget per cell, as defined by the competitions:
#   CEC2014 / CEC2017 : 10^4 * D
#   CEC2020           : 50K (D5), 1M (D10), 3M (D15), 10M (D20)
#   CEC2022           : 200K (D10), 1M (D20)
# =========================================================================

CEC_BUDGET = {
    ('cec2014', 10):    100_000,
    ('cec2014', 30):    300_000,
    ('cec2014', 50):    500_000,
    ('cec2014', 100): 1_000_000,
    ('cec2017', 10):    100_000,
    ('cec2017', 30):    300_000,
    ('cec2017', 50):    500_000,
    ('cec2017', 100): 1_000_000,
    ('cec2020',  5):     50_000,
    ('cec2020', 10):  1_000_000,
    ('cec2020', 15):  3_000_000,
    ('cec2020', 20): 10_000_000,
    ('cec2022', 10):    200_000,
    ('cec2022', 20):  1_000_000,
}


# =========================================================================
# v33 LOW/HIGH partitions, computed via lhs_range_saddles.py at seed=0,
# M_factor=500. These are the verified outputs from the CEC suites you've
# been running. Add new (suite, dim) keys here as you classify them.
# =========================================================================

KNOWN_PARTITIONS = {
    ('cec2014', 10): {
        'HIGH': [1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14, 16, 17, 18, 20, 21],
        'LOW':  [4, 7, 10, 15, 19, 22, 23, 24, 25, 26, 27, 28, 29, 30],
    },
    ('cec2017', 10): {
        'HIGH': [1, 2, 3, 5, 6, 8, 10, 11, 12, 13, 14, 15, 18, 19, 22, 30],
        'LOW':  [4, 7, 9, 16, 17, 20, 21, 23, 24, 25, 26, 27, 28, 29],
    },
    ('cec2020', 10): {
        'HIGH': [1, 2, 5, 7],
        'LOW':  [3, 4, 6, 8, 9, 10],
    },
    ('cec2020', 15): {
        'HIGH': [1, 2, 5, 7],
        'LOW':  [3, 4, 6, 8, 9, 10],
    },
    ('cec2022', 10): {
        'HIGH': [1, 3, 4, 6, 10],
        'LOW':  [2, 5, 7, 8, 9, 11, 12],
    },
    ('cec2022', 20): {
        'HIGH': [1, 3, 4, 6, 7, 8, 10],
        'LOW':  [2, 5, 9, 11, 12],
    },
}


def partition_for(suite, dim):
    """Return {'HIGH': [...], 'LOW': [...]} for (suite, dim) or None."""
    return KNOWN_PARTITIONS.get((suite, dim))


# =========================================================================
# Deprecated / excluded functions — dropped UNIFORMLY for every algorithm,
# in every cell of the listed suite, so all methods are compared on the same
# function set.
#
# CEC2017 f2 is numerically unstable across platforms (it can yield wildly
# different final errors depending on the math library / compiler) and was
# deprecated by the CEC2017 organizers; the convention is to evaluate on the
# remaining 29 functions.  Removing it only where a method explodes would be
# cherry-picking that favours the exploding method, so it is removed for ALL
# algorithms here.
#
# Disable with --keep-deprecated to reproduce the with-f2 numbers.
# =========================================================================

DEPRECATED_FUNCS = {
    'cec2017': {'f2'},
}

# Keep FUNC_CLASSES consistent with DEPRECATED_FUNCS (single source of truth):
# a function withdrawn from a suite must not remain in any of its classes,
# otherwise the "whole class present" budget check can never be satisfied.
for _suite, _dep in DEPRECATED_FUNCS.items():
    _depnums = {int(f[1:]) for f in _dep}          # {'f2'} -> {2}
    for _cls in FUNC_CLASSES.get(_suite, {}).values():
        _cls -= _depnums                            # sets mutated in place


def normalize_algo(raw_name):
    for pat, canon in ALGO_PATTERNS:
        if pat.match(raw_name):
            return canon
    return raw_name


def filter_func_class(grid, func_class):
    """Restrict every cell to functions of one class.

    func_class : 'all' (no-op), 'basic', 'hybrid', or 'composition'.
    Cells from suites missing in FUNC_CLASSES are dropped with a warning.
    Algorithms left with zero functions in a cell are removed from it;
    cells left with zero algorithms are removed from the grid.
    """
    if func_class == 'all':
        return grid
    out = {}
    for cell_key, algos in grid.items():
        suite = cell_key[0]
        classes = FUNC_CLASSES.get(suite)
        if classes is None:
            print(f"WARNING: no FUNC_CLASSES entry for suite '{suite}' "
                  f"— cell {cell_key} dropped under --func-class",
                  file=sys.stderr)
            continue
        keep = {f'f{i}' for i in classes[func_class]}
        new_algos = {}
        for algo, per_func in algos.items():
            sub = {f: m for f, m in per_func.items() if f in keep}
            if sub:
                new_algos[algo] = sub
        if new_algos:
            out[cell_key] = new_algos
    return out


# =========================================================================
# FBTC helpers (lightweight, per-function, no improvements -> just final err)
# =========================================================================

def _sr_per_target(errors, targets=COCO_TARGETS):
    """Per-target success rate vector of length len(targets).
    SR[i] = fraction of seeds whose final (floored) error <= targets[i].
    Returns np.zeros(len(targets)) if no errors.
    """
    if errors is None or len(errors) == 0:
        return np.zeros(len(targets), dtype=np.float64)
    e = _floor(np.asarray(errors, dtype=np.float64))
    hits = (e[:, None] <= targets[None, :]).astype(np.float64)  # (n_runs, n_tau)
    return hits.mean(axis=0)                                    # (n_tau,)


def _hits_per_depth(errors, depths=COCO_DEPTHS):
    """For each canonical COCO depth target, count seeds whose floored final
    error <= depth. Returns int vector of length len(depths).
    """
    if errors is None or len(errors) == 0:
        return np.zeros(len(depths), dtype=np.int64)
    e = _floor(np.asarray(errors, dtype=np.float64))
    return (e[:, None] <= depths[None, :]).sum(axis=0).astype(np.int64)


def _fbtc_from_final_errs(errors, targets=COCO_TARGETS):
    """Fixed-Budget Target Coverage (FBTC) per function.

    Mean across the 51 log-uniform targets in [10^+2, 10^-8] of the
    per-target success rate at final budget.  Anchored to the Optuna
    optimization objective — the 51-target set must NOT change.

    NOT the COCO runtime-integrated ECDF — this is the fixed-budget
    horizontal slice at the final evaluation count.
    NOT mean(THR_k) — THR_k uses the 11-decade grid, FBTC the 51-pt grid.

    Returns:
        float in [0, 1].  Equivalent to mean of _sr_per_target().
    """
    sr = _sr_per_target(errors, targets)
    return float(sr.mean())


def _std_from_final_errs(errors):
    """Per-function standard deviation of final errors across seeds.

    Computed on the floored error array (errors below COCO_ZERO = 1e-8
    are treated as zero).  Uses ddof=1 (sample std).

    Caveat: scale-sensitive across functions, same as mean error.
    Functions with large error ranges dominate SUM(std).

    Returns:
        float >= 0, or 0.0 if fewer than 2 seeds.
    """
    if errors is None or len(errors) < 2:
        return 0.0
    return float(_floor(np.asarray(errors, dtype=np.float64)).std(ddof=1))


def _floor(arr, eps=COCO_ZERO):
    out = np.asarray(arr, dtype=np.float64).copy()
    out[np.abs(out) <= eps] = 0.0
    return out


# =========================================================================
# Discovery + loading
# =========================================================================

CELL_RX = re.compile(r'^maxevals_(\d+)$')


def discover_cells(root):
    """Yield (suite, dim, raw_algo, maxevals, pkl_dir) for every populated cell."""
    if not os.path.isdir(root):
        return
    for suite in sorted(os.listdir(root)):
        sd = os.path.join(root, suite)
        if not os.path.isdir(sd):
            continue
        for dim_dir in sorted(os.listdir(sd)):
            if not dim_dir.startswith('d'):
                continue
            try:
                dim = int(dim_dir[1:])
            except ValueError:
                continue
            dd = os.path.join(sd, dim_dir)
            for algo in sorted(os.listdir(dd)):
                ad = os.path.join(dd, algo)
                if not os.path.isdir(ad):
                    continue
                for me_dir in sorted(os.listdir(ad)):
                    m = CELL_RX.match(me_dir)
                    if not m:
                        continue
                    maxevals = int(m.group(1))
                    md = os.path.join(ad, me_dir)
                    pkls = [f for f in os.listdir(md) if f.endswith('.pkl')]
                    if not pkls:
                        continue
                    yield suite, dim, algo, maxevals, md


def load_cell_metrics(pkl_dir):
    """Per-function: mean_err, median_err, std, best, worst, fbtc.
    Returns {func_name: dict}. Skips unloadable pkls.
    """
    out = {}
    for fn in sorted(os.listdir(pkl_dir)):
        if not fn.endswith('.pkl'):
            continue
        path = os.path.join(pkl_dir, fn)
        try:
            with open(path, 'rb') as f:
                d = pickle.load(f)
        except Exception:
            continue
        errs = np.asarray(d.get('errors', []), dtype=np.float64)
        if errs.size == 0:
            continue
        errs_floor = _floor(errs)
        fname = d.get('func', fn[:-4])
        out[fname] = {
            'mean':       float(errs_floor.mean()),
            'median':     float(np.median(errs_floor)),
            'std':        _std_from_final_errs(errs),
            'best':       float(errs_floor.min()),    # best (min) final error
            'worst':      float(errs_floor.max()),    # worst (max) final error
            'fbtc':       _fbtc_from_final_errs(errs),
            'sr':         _sr_per_target(errs),       # 51 log-uniform (FBTC basis)
            'depth_hits': _hits_per_depth(errs),      # 11 decade depths (THR_k)
            'n_runs':     int(d.get('n_runs', errs.size)),
            'maxevals':   int(d.get('maxevals', 0)),
        }
    return out


# =========================================================================
# Aggregation
# =========================================================================

def aggregate(root, exclude_deprecated=True):
    """Returns (grid, raw_seen, excluded).

    grid     : {(suite, dim, maxevals): {canon_algo: {func: metrics}}}
    raw_seen : {(suite, dim, maxevals): {raw_algo, ...}}
    excluded : {suite: {func, ...}}  funcs actually dropped as deprecated.

    Multiple raw algos that normalize to the same canonical name are MERGED
    (last write wins per function — this only matters if both MSC-CMA and
    MSC-CMA-B1M exist in the same cell, which shouldn't happen).

    Deprecated functions (DEPRECATED_FUNCS) are dropped for EVERY algorithm
    in the affected suite, before merging, so every downstream table, the CSV,
    and the by-dim aggregation see the same reduced function set.
    """
    grid = defaultdict(lambda: defaultdict(dict))
    raw_seen = defaultdict(set)
    excluded = defaultdict(set)
    for suite, dim, raw_algo, maxevals, md in discover_cells(root):
        canon = normalize_algo(raw_algo)
        cell_key = (suite, dim, maxevals)
        raw_seen[cell_key].add(raw_algo)
        per_func = load_cell_metrics(md)
        if exclude_deprecated:
            drop = DEPRECATED_FUNCS.get(suite, set())
            for f in list(per_func):
                if f in drop:
                    del per_func[f]
                    excluded[suite].add(f)
        # Merge into canonical bucket
        existing = grid[cell_key].get(canon, {})
        existing.update(per_func)
        grid[cell_key][canon] = existing
    return grid, raw_seen, excluded


# =========================================================================
# Pretty printing
# =========================================================================

def _fmt_budget(n):
    if n >= 1_000_000:
        return f'{n//1_000_000}M'
    if n >= 1_000:
        return f'{n//1_000}K'
    return str(n)


def _fmt_value(v, metric):
    if v is None or not np.isfinite(v):
        return '       —'
    if metric == 'fbtc':
        return f'{v:8.4f}'
    if abs(v) >= 1e4 or (0 < abs(v) < 1e-3):
        return f'{v:8.2e}'
    return f'{v:8.2f}'


def print_table(grid, metric, algo_order):
    """metric in {'mean','median','std','best','worst','fbtc'}.
    Higher-is-better only for fbtc.  No winner column, no asterisks — just SUMs.
    """
    higher_better = (metric == 'fbtc')
    label = {'mean':   'SUM(mean err)',
             'median': 'SUM(median err)',
             'std':    'SUM(std)',
             'best':   'SUM(best err)',
             'worst':  'SUM(worst err)',
             'fbtc':   'SUM(FBTC)'}[metric]

    print(f"\n{label}  ({'higher' if higher_better else 'lower'} is better)")
    if metric == 'fbtc':
        print("  (FBTC = mean per-target success rate over 51 log-uniform "
              "targets in [10^+2, 10^-8];")
        print("   range [0, nF]; NOT mean(THR_k) — THR_k uses the 11-decade grid)")

    header = f"{'suite':<8} {'D':>3} {'budget':>7} {'nF':>3} | "
    header += ' '.join(f'{a:>10}' for a in algo_order)
    print(header)
    print('-' * len(header))

    cells = sorted(grid.keys(),
                   key=lambda k: (k[0], k[1], k[2]))
    for cell_key in cells:
        suite, dim, maxevals = cell_key
        cell = grid[cell_key]
        fset = set()
        for funcs in cell.values():
            fset |= set(funcs.keys())
        n_funcs = len(fset)

        sums = {}
        partial = []
        for algo in algo_order:
            funcs = cell.get(algo, {})
            if not funcs:
                sums[algo] = None
                continue
            vals = [funcs[f][metric] for f in fset if f in funcs]
            sums[algo] = float(np.sum(vals)) if vals else None
            if vals and len(vals) < n_funcs:
                partial.append((algo, len(vals)))

        row = (f"{suite:<8} {dim:>3} {_fmt_budget(maxevals):>7} "
               f"{n_funcs:>3} | ")
        row += ' '.join(f'{_fmt_value(sums.get(a), metric):>10}'
                        for a in algo_order)
        print(row)
        for algo, nf in partial:
            print(f"  !! PARTIAL: {algo} has {nf}/{n_funcs} funcs in this "
                  f"cell — SUM not comparable (missing: "
                  f"{','.join(sorted(fset - set(cell[algo]), key=lambda s: int(s[1:]) if s[1:].isdigit() else 0))})")


# =========================================================================
# CSV
# =========================================================================

def write_csv(path, grid, algo_order):
    rows = []
    for cell_key in sorted(grid.keys()):
        suite, dim, maxevals = cell_key
        cell = grid[cell_key]
        fset = set()
        for funcs in cell.values():
            fset |= set(funcs.keys())
        n_funcs = len(fset)
        for algo in algo_order:
            funcs = cell.get(algo, {})
            if not funcs:
                continue
            sm   = sum(funcs[f]['mean']   for f in funcs)
            smd  = sum(funcs[f]['median'] for f in funcs)
            ssd  = sum(funcs[f]['std']    for f in funcs)
            sb   = sum(funcs[f]['best']   for f in funcs)
            sw   = sum(funcs[f]['worst']  for f in funcs)
            se   = sum(funcs[f]['fbtc']   for f in funcs)
            rows.append({
                'suite': suite, 'dim': dim, 'maxevals': maxevals,
                'algo': algo, 'n_funcs': n_funcs,
                'sum_mean': sm, 'sum_median': smd, 'sum_std': ssd,
                'sum_best': sb, 'sum_worst': sw, 'sum_fbtc': se,
            })
    if not rows:
        return
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# =========================================================================
# Main
# =========================================================================

def print_by_dim_bucket(grid, bucket, algo_order):
    """Aggregate across cells (suites) per (dimension, bucket).

    bucket ∈ {'ALL', 'HIGH', 'LOW'}. ALL ignores the partition.
    Only cells with a known partition are included for HIGH/LOW.
    """
    label = {
        'ALL':  'all functions',
        'HIGH': 'HIGH bucket (LHS v1)',
        'LOW':  'LOW bucket (LHS v1)',
    }[bucket]
    print(f"\nBy-dimension aggregation — {label}")

    # by_dim[dim][algo] = aggregated dict
    by_dim = defaultdict(lambda: defaultdict(lambda: {
        'fbtc_sum':      0.0,
        'depth_total':   np.zeros(len(COCO_DEPTH_EXPONENTS), dtype=np.int64),
        'n_funcs_total': 0,
        'max_total':     0,
        'cells':         set(),
    }))

    for cell_key, cell in grid.items():
        suite, dim, maxevals = cell_key
        if bucket == 'ALL':
            allowed_funcs = None  # everything
        else:
            part = partition_for(suite, dim)
            if part is None:
                continue
            allowed_funcs = {f'f{n}' for n in part[bucket]}

        for algo in algo_order:
            funcs = cell.get(algo, {})
            if not funcs:
                continue
            relevant = [f for f in funcs
                        if (allowed_funcs is None or f in allowed_funcs)]
            if not relevant:
                continue
            fbtc_sum = float(np.sum([funcs[f]['fbtc'] for f in relevant]))
            depth_total = sum((funcs[f]['depth_hits'] for f in relevant),
                              np.zeros(len(COCO_DEPTH_EXPONENTS),
                                       dtype=np.int64))
            n_runs = funcs[relevant[0]]['n_runs']
            entry = by_dim[dim][algo]
            entry['fbtc_sum']      += fbtc_sum
            entry['depth_total']   += depth_total
            entry['n_funcs_total'] += len(relevant)
            entry['max_total']     += n_runs * len(relevant)
            entry['cells'].add(cell_key)

    if not by_dim:
        print("  (no cells with known partition for this bucket)")
        return

    # Header
    h_left = (f"{'D':>3} {'cells':>5} {'nF':>3} {'algo':<7} | "
              f"{'FBTC':>7} {'FBTC/nF':>8} {'max':>6} | ")
    depth_hdr = '  '.join(f"{k:>+3d}" for k in COCO_DEPTH_EXPONENTS)
    header = h_left + depth_hdr
    print(header)
    print('-' * len(header))

    SHORT = {'MSC-CMA': 'MSC', 'ARRDE': 'ARRDE',
             'LSRTDE': 'LSRTDE', 'BIPOP-CMA': 'BIPOP-CMA'}

    for dim in sorted(by_dim.keys()):
        first = True
        for algo in algo_order:
            if algo not in by_dim[dim]:
                continue
            e = by_dim[dim][algo]
            fbtc_per_nf = (e['fbtc_sum'] / e['n_funcs_total']
                           if e['n_funcs_total'] else 0.0)
            n_cells = len(e['cells'])

            if first:
                left = (f"{dim:>3} {n_cells:>5} {e['n_funcs_total']:>3} "
                        f"{SHORT.get(algo, algo):<7} | ")
                first = False
            else:
                left = (f"{'':>3} {'':>5} {e['n_funcs_total']:>3} "
                        f"{SHORT.get(algo, algo):<7} | ")
            left += f"{e['fbtc_sum']:>7.3f} {fbtc_per_nf:>8.3f} "
            left += f"{e['max_total']:>6d} | "
            cells_str = '  '.join(f"{int(c):>4d}" for c in e['depth_total'])
            print(left + cells_str)
        print()


def print_class_summary(grid, algo_order, common=True, latex=False):
    """Per-class totals (Basic / Hybrid / Composition x mean / median /
    best / FBTC) summed over the cells currently in `grid`.  This is the
    Table 1 ("per-class totals") layout used in the article.

    Run WITHOUT --func-class: this routine subsets the three classes
    itself via FUNC_CLASSES.  With --common-cells, each cell is restricted
    to the functions present for ALL algorithms (guards against partial
    cells contaminating the totals).
    """
    classes = ['basic', 'hybrid', 'composition']
    metrics = [('mean', False), ('median', False),
               ('best', False), ('fbtc', True)]   # fbtc: higher is better
    tot = {c: {a: {m: 0.0 for m, _ in metrics} for a in algo_order}
           for c in classes}
    partial = []
    for (suite, dim, mx), cell in sorted(grid.items()):
        cf = FUNC_CLASSES.get(suite)
        if cf is None:
            continue
        present = [set(cell[a]) for a in algo_order if cell.get(a)]
        if not present:
            continue
        union = set.union(*present)
        funcs = set.intersection(*present) if common else union
        for a in algo_order:                         # audit partial coverage
            miss = union - set(cell.get(a, {}))
            if miss:
                partial.append((suite, dim, mx, a, sorted(miss)))
        for cls in classes:
            cfuncs = {f'f{i}' for i in cf[cls]} & funcs
            for a in algo_order:
                fa = cell.get(a, {})
                for m, _ in metrics:
                    tot[cls][a][m] += sum(fa[fn][m] for fn in cfuncs if fn in fa)

    label = {'mean': 'mean', 'median': 'median', 'best': 'best', 'fbtc': 'FBTC'}
    for cls in classes:
        cls_lbl = {'basic': 'USM'}.get(cls, cls.capitalize())
        print(f'\\multirow{{4}}{{*}}{{{cls_lbl}}}'
              if latex else f'\n{cls_lbl}')
        for m, higher in metrics:
            vals = {a: tot[cls][a][m] for a in algo_order}
            win = (max if higher else min)(vals, key=vals.get)

            def fmt(a):
                s = f'{vals[a]:.2f}'
                if latex:
                    return f'\\textbf{{{s}}}' if a == win else s
                return f'*{s}' if a == win else f' {s}'
            body = (' & ' if latex else '  ').join(fmt(a) for a in algo_order)
            print((f' & {label[m]:6} & {body} \\\\') if latex
                  else f'  {label[m]:7} {body}')
        if latex:
            print('\\midrule')
    if common and partial:
        print('\n# PARTIAL cells (functions missing for some algorithm — '
              'EXCLUDED under --common-cells):', file=sys.stderr)
        for suite, dim, mx, a, miss in partial:
            print(f'#   {suite} d{dim} @{mx}  {a}: missing {",".join(miss)}',
                  file=sys.stderr)


def print_dim_summary(grid, algo_order, common=True, latex=False):
    """Per-dimension totals (SUM mean / median / FBTC) across the cells at
    each dimension.  Rows = dimension (with function count), columns =
    algorithms.  A TOTAL row sums all dimensions, but note that the summed
    errors live on very different scales across D, so the per-dimension rows
    are the comparable unit; the TOTAL is reported for completeness only.
    Run WITHOUT --func-class.  With --common-cells each cell is restricted to
    functions present for ALL algorithms.
    """
    from collections import defaultdict
    metrics = [('mean', False), ('median', False), ('fbtc', True)]
    perdim = defaultdict(lambda: {a: {m: 0.0 for m, _ in metrics}
                                  for a in algo_order})
    nfdim = defaultdict(int)
    partial = []
    for (suite, dim, mx), cell in sorted(grid.items()):
        present = [set(cell[a]) for a in algo_order if cell.get(a)]
        if not present:
            continue
        union = set.union(*present)
        funcs = set.intersection(*present) if common else union
        for a in algo_order:
            miss = union - set(cell.get(a, {}))
            if miss:
                partial.append((suite, dim, mx, a, sorted(miss)))
        nfdim[dim] += len(funcs)
        for a in algo_order:
            fa = cell.get(a, {})
            for m, _ in metrics:
                perdim[dim][a][m] += sum(fa[fn][m] for fn in funcs if fn in fa)

    dims = sorted(perdim)
    total = {a: {m: sum(perdim[d][a][m] for d in dims) for m, _ in metrics}
             for a in algo_order}
    nftot = sum(nfdim[d] for d in dims)
    label = {'mean': 'mean', 'median': 'median', 'fbtc': 'FBTC'}

    def emit(rowname, vals_by_algo):
        first = True
        if latex:
            print(f'\\multirow{{3}}{{*}}{{{rowname}}}')
        else:
            print(rowname)
        for m, higher in metrics:
            vals = {a: vals_by_algo[a][m] for a in algo_order}
            win = (max if higher else min)(vals, key=vals.get)

            def fmt(a):
                s = f'{vals[a]:.2f}'
                if latex:
                    return f'\\textbf{{{s}}}' if a == win else s
                return f'*{s}' if a == win else f' {s}'
            body = (' & ' if latex else '  ').join(fmt(a) for a in algo_order)
            print((f' & {label[m]:6} & {body} \\\\') if latex
                  else f'  {label[m]:7} {body}')
        if latex:
            print('\\midrule')

    for d in dims:
        emit(f'$D{{=}}{d}$ ({nfdim[d]})', perdim[d])
    emit(f'TOTAL ({nftot})', total)
    if common and partial:
        print('\n# PARTIAL cells (functions missing for some algorithm — '
              'EXCLUDED under --common-cells):', file=sys.stderr)
        for suite, dim, mx, a, miss in partial:
            print(f'#   {suite} d{dim} @{mx}  {a}: missing {",".join(miss)}',
                  file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='experiments')
    p.add_argument('--metric', default='all',
                   choices=['mean', 'median', 'std', 'best', 'worst',
                            'fbtc', 'all'],
                   help='Which table(s) to print (default: all six)')
    p.add_argument('--csv', default='',
                   help='Optional CSV output path (long format)')
    p.add_argument('--by-dim', action='store_true',
                   help='Add the by-dimension aggregation table (all functions).')
    p.add_argument('--keep-deprecated', action='store_true',
                   help='Keep functions normally dropped as deprecated '
                        '(e.g. CEC2017 f2). Default: removed for all algos.')
    p.add_argument('--extra-algos', default='',
                   help='Comma-separated extra algo dir names to include as '
                        'separate columns (e.g. check_frozen,MSC-CMA-v2). '
                        'They are matched literally against directory names.')
    p.add_argument('--func-class', default='all',
                   choices=['all', 'basic', 'hybrid', 'composition'],
                   help='Restrict every cell to one CEC function class '
                        '(see FUNC_CLASSES). Default: all functions.')
    p.add_argument('--basic-dims', '--basic_dims', dest='basic_dims',
                   action='store_true',
                   help='Keep only the standard (suite, dim, budget) cells '
                        'listed in STANDARD_CELLS.')
    p.add_argument('--cec-budget', '--CEC-budget', dest='cec_budget',
                   action='store_true',
                   help='Keep only the OFFICIAL CEC budget per (suite, dim) '
                        '— exactly one row per cell, see CEC_BUDGET.')
    p.add_argument('--all-algos', action='store_true',
                   help='Auto-discover and include every algo directory '
                        'present in the experiments tree.')
    p.add_argument('--class-summary', action='store_true',
                   help='Emit per-class totals (Basic/Hybrid/Composition x '
                        'mean/median/best/FBTC) over the selected cells — '
                        'the Table 1 layout. Run without --func-class.')
    p.add_argument('--dim-summary', action='store_true',
                   help='Emit per-dimension totals (rows = D, with function '
                        'counts; SUM mean/median/FBTC) over the selected '
                        'cells, with a TOTAL row. Run without --func-class.')
    p.add_argument('--max-dim', type=int, default=None,
                   help='Drop cells with dim > MAX_DIM (e.g. --max-dim 20 '
                        'excludes the d30 cells).')
    p.add_argument('--drop-cell', action='append', default=[], metavar='SUITE:DIM',
                   help='Exclude a (suite, dim) cell, e.g. --drop-cell cec2020:20. '
                        'Repeatable.')
    p.add_argument('--common-cells', action='store_true',
                   help='Per cell, restrict to functions present for ALL '
                        'algorithms (guards partial cells). Recommended for totals.')
    p.add_argument('--latex', action='store_true',
                   help='Emit LaTeX table rows (use with --class-summary).')
    args = p.parse_args()

    grid, raw_seen, excluded = aggregate(
        args.root, exclude_deprecated=not args.keep_deprecated)
    if not grid:
        sys.exit(f"No populated experiments cells found under {args.root}/")

    # Optional cell whitelist.
    if args.basic_dims:
        grid = {k: v for k, v in grid.items()
                if k[2] in STANDARD_CELLS.get((k[0], k[1]), set())}
        if not grid:
            sys.exit("No cells left after --basic-dims filter.")

    # Optional: only the official CEC budget per (suite, dim).
    if args.cec_budget:
        grid = {k: v for k, v in grid.items()
                if CEC_BUDGET.get((k[0], k[1])) == k[2]}
        if not grid:
            sys.exit("No cells left after --cec-budget filter.")

    # Optional: drop high dimensions (e.g. --max-dim 20 excludes d30).
    if args.max_dim is not None:
        grid = {k: v for k, v in grid.items() if k[1] <= args.max_dim}
        if not grid:
            sys.exit(f"No cells left after --max-dim={args.max_dim}.")

    # Optional: drop explicit (suite, dim) cells.
    if args.drop_cell:
        drop = {tuple(c.split(':')) for c in args.drop_cell}
        grid = {k: v for k, v in grid.items()
                if (k[0], str(k[1])) not in drop}
        if not grid:
            sys.exit("No cells left after --drop-cell filter.")

    # --class-summary / --dim-summary subset classes themselves, so skip here.
    if (args.class_summary or args.dim_summary) and args.func_class != 'all':
        print("NOTE: --class-summary/--dim-summary ignore --func-class.",
              file=sys.stderr)
    if not (args.class_summary or args.dim_summary):
        grid = filter_func_class(grid, args.func_class)
        if not grid:
            sys.exit(f"No cells left after --func-class={args.func_class}.")

    # Filter: keep only cells where MSC-CMA has at least one function.
    grid = {k: v for k, v in grid.items() if v.get('MSC-CMA')}
    if not grid:
        sys.exit("No cells with MSC-CMA data found — nothing to compare.")

    # Algorithm column order: MSC-CMA first, BIPOP-CMA second, then the
    # remaining algorithms alphabetically. Plus user-requested extras,
    # plus everything else discovered if --all-algos.
    canonical = ['MSC-CMA', 'BIPOP-CMA',
                 'ARRDE', 'j2020', 'jSO', 'LSRTDE', 'NLSHADE-RSP']
    extras_cli = [a.strip() for a in args.extra_algos.split(',') if a.strip()]

    if args.all_algos:
        # Every algo that appears in any cell, minus the canonical ones.
        discovered = sorted({a for cell in grid.values() for a in cell})
        extras_disc = [a for a in discovered if a not in canonical]
    else:
        extras_disc = []

    # Preserve order: canonical[0] (MSC-CMA), extras (CLI first, then
    # auto-discovered), then canonical[1:] (BIPOP-CMA, rest alphabetical).
    seen = {'MSC-CMA'}
    extras = []
    for a in extras_cli + extras_disc:
        if a not in seen:
            extras.append(a); seen.add(a)
    algo_order = ['MSC-CMA'] + extras + [a for a in canonical[1:] if a not in seen]

    # Inventory header
    print(f"Root: {args.root}")
    print(f"Cells with MSC-CMA: {len(grid)}")
    if args.basic_dims:
        print("  (--basic-dims: standard cell whitelist applied)")
    if args.cec_budget:
        print("  (--cec-budget: official CEC budget per suite/dim only)")
    if args.func_class != 'all':
        print(f"  (--func-class={args.func_class}: "
              f"per-suite function subset, see FUNC_CLASSES)")
    if excluded:
        parts = ', '.join(f"{s} {'/'.join(sorted(fs))}"
                          for s, fs in sorted(excluded.items()))
        print(f"  (deprecated funcs removed for ALL algos: {parts})")
    elif args.keep_deprecated:
        print("  (--keep-deprecated: deprecated funcs KEPT)")
    n_raw_msc = sum(1 for s in raw_seen.values()
                    for n in s if n.startswith('MSC-CMA-B'))
    if n_raw_msc:
        print(f"  (collapsed MSC-CMA-B* variants: {n_raw_msc} budget-marked dirs)")

    # Table 1 layout: per-class totals over the selected cells.
    if args.class_summary:
        print_class_summary(grid, algo_order,
                            common=args.common_cells, latex=args.latex)
        if args.csv:
            write_csv(args.csv, grid, algo_order)
            print(f"\nCSV → {args.csv}")
        return

    # Per-dimension totals over the selected cells.
    if args.dim_summary:
        print_dim_summary(grid, algo_order,
                          common=args.common_cells, latex=args.latex)
        if args.csv:
            write_csv(args.csv, grid, algo_order)
            print(f"\nCSV → {args.csv}")
        return

    if args.metric in ('mean', 'all'):
        print_table(grid, 'mean', algo_order)
    if args.metric in ('median', 'all'):
        print_table(grid, 'median', algo_order)
    if args.metric in ('std', 'all'):
        print_table(grid, 'std', algo_order)
    if args.metric in ('best', 'all'):
        print_table(grid, 'best', algo_order)
    if args.metric in ('worst', 'all'):
        print_table(grid, 'worst', algo_order)
    if args.metric in ('fbtc', 'all'):
        print_table(grid, 'fbtc', algo_order)

    if args.by_dim:
        print_by_dim_bucket(grid, 'ALL',  algo_order)

    if args.csv:
        write_csv(args.csv, grid, algo_order)
        print(f"\nCSV → {args.csv}")


if __name__ == '__main__':
    main()
