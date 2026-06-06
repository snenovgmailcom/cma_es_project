#!/usr/bin/env python3
"""
analysis/summary_grid.py — compact cross-suite/dim summary tables.

Walks the experiments/ directory tree, discovers every
    experiments/<suite>/d<dim>/<algo>/maxevals_<N>/
cell that contains pkls, and produces compact tables aggregated per
(suite, dim, maxevals) cell × algorithm.

Four tables emitted:
    1. SUM(mean error)        — total mean error across functions in the cell
    2. SUM(median error)      — total median error (robust)
    3. SUM(std)               — total per-function std across functions
    4. SUM(FBTC)              — total Fixed-Budget Target Coverage
                                (higher is better, bounded by n_funcs)

Plus per-target hit count breakdown (THR_k) shown alongside the FBTC table
for visualization (NOT used in FBTC computation).

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

  SUM(FBTC)(cell)  = sum over functions in the cell of FBTC_f.
                     Range: [0, n_functions].

  THR_k(cell, a)   = #(seed × function) hits at threshold 10^k in the cell.
                     Shown in tables for VISUALIZATION only, k in [+2, -8].
                     max = n_seeds × n_functions in cell.

  SUM(std)(cell)   = sum over functions in the cell of per-function
                     standard deviation of final errors across seeds.
                     Caveat: scale-sensitive — same caveat as SUM(mean).

Algorithm-name normalization (so MSC-CMA-B1M, MSC-CMA-B3M, MSC-CMA-B10M etc.
all show up under the same "MSC-CMA" column):
    MSC-CMA*           → MSC-CMA
    ARRDE-*            → ARRDE
    LSRTDE-*           → LSRTDE
    BIPOP-CMA-*        → BIPOP

Each cell shows its winner (best algo) marked with *.

Usage
-----
    python analysis/summary_grid.py
    python analysis/summary_grid.py --root experiments
    python analysis/summary_grid.py --metric fbtc
    python analysis/summary_grid.py --csv summary.csv
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
    (re.compile(r'^LSHADE-cnEpSin(-.*)?$'), 'LSHADE-cnEpSin'),  # MUST come before LSHADE
    (re.compile(r'^LSHADE(-.*)?$'),        'LSHADE'),
    (re.compile(r'^LSRTDE(-.*)?$'),        'LSRTDE'),
    (re.compile(r'^BIPOP-CMA(-.*)?$'),     'BIPOP'),
]


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
# in every cell of the listed suite, so all methods are compared on the
# same function set. CEC2017 f2 was deprecated by the organizers; the
# convention is to evaluate on the remaining 29 functions.
# Disable with --keep-deprecated.
# =========================================================================

DEPRECATED_FUNCS = {
    'cec2017': {'f2'},
}


def normalize_algo(raw_name):
    for pat, canon in ALGO_PATTERNS:
        if pat.match(raw_name):
            return canon
    return raw_name


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
    """Per-function: mean_err, median_err, std, fbtc.
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
    """Returns {(suite, dim, maxevals): {canon_algo: {func: metrics}}}.

    Multiple raw algos that normalize to the same canonical name are MERGED
    (last write wins per function — this only matters if both MSC-CMA and
    MSC-CMA-B1M exist in the same cell, which shouldn't happen).

    Deprecated functions (DEPRECATED_FUNCS) are dropped for EVERY algorithm
    in the affected suite, before merging, so every downstream table, the
    CSV, and the by-dim aggregation see the same reduced function set.
    """
    grid = defaultdict(lambda: defaultdict(dict))
    raw_seen = defaultdict(set)
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
        # Merge into canonical bucket
        existing = grid[cell_key].get(canon, {})
        existing.update(per_func)
        grid[cell_key][canon] = existing
    return grid, raw_seen


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
    """metric in {'mean','median','std','fbtc'}.  Higher-is-better only for fbtc.
    No winner column, no asterisks — just SUMs.
    """
    higher_better = (metric == 'fbtc')
    label = {'mean':   'SUM(mean err)',
             'median': 'SUM(median err)',
             'std':    'SUM(std)',
             'fbtc':   'SUM(FBTC)'}[metric]

    print(f"\n{label}  ({'higher' if higher_better else 'lower'} is better)")

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
        for algo in algo_order:
            funcs = cell.get(algo, {})
            if not funcs:
                sums[algo] = None
                continue
            vals = [funcs[f][metric] for f in fset if f in funcs]
            sums[algo] = float(np.sum(vals)) if vals else None

        row = (f"{suite:<8} {dim:>3} {_fmt_budget(maxevals):>7} "
               f"{n_funcs:>3} | ")
        row += ' '.join(f'{_fmt_value(sums.get(a), metric):>10}'
                        for a in algo_order)
        print(row)


def print_fbtc_extended_table(grid, algo_order):
    """SUM(FBTC) + per-target hit count breakdown THR_k.

    For each (cell, algo) row, show:
        FBTC SUM     — sum over functions in cell of FBTC_f (mean
                       per-target success rate over 51 log-uniform targets).
                       Range [0, n_funcs].
        THR_k counts — Σ_f (# seeds with final err <= 10^k) for the 11
                       decade depths k ∈ {+2, +1, 0, ..., -7, -8}.
                       Max per cell per algo = n_runs × n_funcs.

    Note: SUM(FBTC) uses the 51-target log-uniform grid (Optuna-anchored);
    THR_k is computed on the 11-decade grid for visualization only.
    The two are NOT arithmetically equivalent.
    """
    print("\nSUM(FBTC) + per-target hit counts THR_k  "
          f"(11 decade targets 10^k, k ∈ [+2, -8] for visualization; "
          "FBTC uses 51 log-uniform targets and is NOT mean(THR_k))")

    # Header
    h_left = f"{'suite':<8} {'D':>3} {'budget':>7} {'nF':>3} {'algo':<7} | "
    h_left += f"{'FBTC':>7}  {'max':>5} | "
    depth_hdr = '  '.join(f"{k:>+3d}" for k in COCO_DEPTH_EXPONENTS)
    header = h_left + depth_hdr
    print(header)
    print('-' * len(header))

    SHORT = {'MSC-CMA': 'MSC', 'ARRDE': 'ARRDE',
             'LSRTDE': 'LSRTDE', 'BIPOP': 'BIPOP'}

    for cell_key in sorted(grid.keys()):
        suite, dim, maxevals = cell_key
        cell = grid[cell_key]
        # Function set + per-cell row label printed only on first algo line
        msc = cell.get('MSC-CMA', {})
        fset = sorted(set(msc.keys())
                      | {f for a in algo_order for f in cell.get(a, {})},
                      key=lambda s: int(s.lstrip('f')))
        n_funcs = len(fset)
        # Common n_runs: take from MSC if present else first algo with funcs
        n_runs = 0
        for a in algo_order:
            for f in cell.get(a, {}):
                n_runs = cell[a][f]['n_runs']
                if n_runs:
                    break
            if n_runs:
                break
        max_total = n_runs * n_funcs

        first_row = True
        for a in algo_order:
            funcs = cell.get(a, {})
            if not funcs:
                continue

            fbtc_sum = float(np.sum([funcs[f]['fbtc']
                                     for f in fset if f in funcs]))
            # Sum hits per depth across functions (using the union fset; missing
            # functions contribute zero — that's truthful, since the algo failed
            # to even produce data for them).
            depth_total = np.zeros(len(COCO_DEPTH_EXPONENTS), dtype=np.int64)
            for f in fset:
                if f in funcs:
                    depth_total += funcs[f]['depth_hits']

            # Print
            if first_row:
                left = (f"{suite:<8} {dim:>3} {_fmt_budget(maxevals):>7} "
                        f"{n_funcs:>3} {SHORT.get(a, a):<7} | ")
                first_row = False
            else:
                left = (f"{'':<8} {'':>3} {'':>7} {'':>3} "
                        f"{SHORT.get(a, a):<7} | ")
            left += f"{fbtc_sum:>7.3f}  {max_total:>5d} | "
            cells_str = '  '.join(f"{int(c):>4d}" for c in depth_total)
            print(left + cells_str)
        print()


def print_wins_vs_msc(grid, algo_order):
    """For each cell: count of functions where each algo strictly beats MSC
    on per-function mean error (after COCO_ZERO floor). MSC missing → skip.
    """
    print("\nPer-function wins on mean error vs MSC-CMA  "
          "(strictly lower; ties not counted)")

    header = f"{'suite':<8} {'D':>3} {'budget':>7} {'nF':>3} | "
    other = [a for a in algo_order if a != 'MSC-CMA']
    header += ' '.join(f'{a:>10}' for a in other)
    print(header)
    print('-' * len(header))

    for cell_key in sorted(grid.keys()):
        suite, dim, maxevals = cell_key
        cell = grid[cell_key]
        msc = cell.get('MSC-CMA')
        if not msc:
            continue
        n_funcs = len(msc)
        row = (f"{suite:<8} {dim:>3} {_fmt_budget(maxevals):>7} "
               f"{n_funcs:>3} | ")
        for a in other:
            other_d = cell.get(a, {})
            if not other_d:
                row += f"{'—':>10} "
                continue
            wins = 0
            for fname, m in msc.items():
                o = other_d.get(fname)
                if o is None:
                    continue
                if o['mean'] < m['mean']:
                    wins += 1
            row += f'{wins:>5}/{n_funcs:<4} '
        print(row.rstrip())


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
            sm  = sum(funcs[f]['mean']   for f in funcs)
            sd_ = sum(funcs[f]['median'] for f in funcs)
            se  = sum(funcs[f]['fbtc']   for f in funcs)
            rows.append({
                'suite': suite, 'dim': dim, 'maxevals': maxevals,
                'algo': algo, 'n_funcs': n_funcs,
                'sum_mean': sm, 'sum_median': sd_, 'sum_fbtc': se,
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
             'LSRTDE': 'LSRTDE', 'BIPOP': 'BIPOP'}

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


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='experiments')
    p.add_argument('--metric', default='all',
                   choices=['mean', 'median', 'std', 'fbtc', 'all'],
                   help='Which table(s) to print (default: all four)')
    p.add_argument('--csv', default='',
                   help='Optional CSV output path (long format)')
    p.add_argument('--no-wins', action='store_true',
                   help='Skip the wins-vs-MSC table')
    p.add_argument('--by-dim', action='store_true',
                   help='Add by-dimension aggregation tables (ALL, HIGH, LOW)')
    p.add_argument('--extra-algos', default='',
                   help='Comma-separated extra algo dir names to include as '
                        'separate columns (e.g. check_frozen,MSC-CMA-v2). '
                        'They are matched literally against directory names.')
    p.add_argument('--all-algos', action='store_true',
                   help='Auto-discover and include every algo directory '
                        'present in the experiments tree.')
    p.add_argument('--keep-deprecated', action='store_true',
                   help='Keep deprecated functions (e.g. CEC2017 f2) instead '
                        'of dropping them uniformly for all algorithms.')
    args = p.parse_args()

    grid, raw_seen = aggregate(args.root,
                               exclude_deprecated=not args.keep_deprecated)
    if args.keep_deprecated:
        print("  (--keep-deprecated: deprecated funcs KEPT)")
    elif any(DEPRECATED_FUNCS.values()):
        drops = ', '.join(f"{s}:{','.join(sorted(fs))}"
                          for s, fs in sorted(DEPRECATED_FUNCS.items()))
        print(f"  (deprecated funcs excluded uniformly: {drops}; "
              f"--keep-deprecated to include)")
    if not grid:
        sys.exit(f"No populated experiments cells found under {args.root}/")

    # Filter: keep only cells where MSC-CMA has at least one function.
    grid = {k: v for k, v in grid.items() if v.get('MSC-CMA')}
    if not grid:
        sys.exit("No cells with MSC-CMA data found — nothing to compare.")

    # Algorithm column order: canonical 4, plus user-requested extras,
    # plus everything else discovered if --all-algos.
    canonical = ['MSC-CMA', 'ARRDE', 'jSO', 'LSHADE-cnEpSin',
                 'j2020', 'NLSHADE-RSP', 'LSHADE', 'LSRTDE', 'BIPOP']
    extras_cli = [a.strip() for a in args.extra_algos.split(',') if a.strip()]

    if args.all_algos:
        # Every algo that appears in any cell, minus the canonical ones.
        discovered = sorted({a for cell in grid.values() for a in cell})
        extras_disc = [a for a in discovered if a not in canonical]
    else:
        extras_disc = []

    # Preserve order: canonical[0] (MSC-CMA), extras (CLI first, then
    # auto-discovered), then canonical[1:] (ARRDE/LSRTDE/BIPOP).
    seen = {'MSC-CMA'}
    extras = []
    for a in extras_cli + extras_disc:
        if a not in seen:
            extras.append(a); seen.add(a)
    algo_order = ['MSC-CMA'] + extras + [a for a in canonical[1:] if a not in seen]

    # Inventory header
    print(f"Root: {args.root}")
    print(f"Cells with MSC-CMA: {len(grid)}")
    n_raw_msc = sum(1 for s in raw_seen.values()
                    for n in s if n.startswith('MSC-CMA-B'))
    if n_raw_msc:
        print(f"  (collapsed MSC-CMA-B* variants: {n_raw_msc} budget-marked dirs)")

    if args.metric in ('mean', 'all'):
        print_table(grid, 'mean', algo_order)
    if args.metric in ('median', 'all'):
        print_table(grid, 'median', algo_order)
    if args.metric in ('std', 'all'):
        print_table(grid, 'std', algo_order)
    if args.metric in ('fbtc', 'all'):
        print_fbtc_extended_table(grid, algo_order)

    if not args.no_wins:
        print_wins_vs_msc(grid, algo_order)

    if args.by_dim:
        print_by_dim_bucket(grid, 'ALL',  algo_order)
        print_by_dim_bucket(grid, 'HIGH', algo_order)
        print_by_dim_bucket(grid, 'LOW',  algo_order)

    if args.csv:
        write_csv(args.csv, grid, algo_order)
        print(f"\nCSV → {args.csv}")


if __name__ == '__main__':
    main()
