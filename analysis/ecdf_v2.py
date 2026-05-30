#!/usr/bin/env python3
"""
ecdf_v2.py — COCO-compliant runtime ECDF + SR/aRT metrics from per-algorithm pkls.

Reads the directory layout produced by benchmark/{msc,arrde,bipop}.py:

    experiments/<suite>/d<dim>/<ALGO>/maxevals_<N>/f<k>.pkl

Each pkl contains:
    suite, dim, func, f_opt, algorithm, maxevals, n_runs,
    seeds, errors(n_runs,), improvements(list of (N_i,2) arrays)

COCO conventions followed
-------------------------
* Targets:  FIXED log-uniform grid over [10^2, 10^-8], 51 targets.
            Independent of algorithm performance or per-function scales.

* ECDF:  fraction of (function × run × target) tasks solved.
    A task (f, run, τ) is solved at budget B iff the run's best-so-far
    error reached ≤ τ within B function evaluations.

* X-axis:  FEvals / D — dimension-normalised budget.  Tick labels
    COCO-style: D, 10D, 100D, ..., 10^k·D.

* Step-function rendering (drawstyle='steps-post').

* SR(f, τ) = n_success / n_runs.
* aRT(f, τ) = Price estimator:
      (T_max · N_unsucc + Σ RT_succ) / N_succ        if N_succ > 0
      +inf                                            otherwise
  where T_max = maxevals.

Outputs
-------
    targets.csv   — 51 rows × 2 cols: target_idx, tau
    metrics.csv   — long format: func, algo, tau, SR, aRT,
                    n_success, n_runs, maxevals
    ecdf_all.png  — global ECDF across all active functions
    ecdf_groups.png — per-CEC-group ECDF panels
    ecdf_f<k>.png — per-function ECDF (for --funcs arg)

With --zoom, every plot gains a second panel below the main one,
showing the last zoom_frac (default 0.15) of the evaluation budget on
a linear x-axis.  Useful for inspecting the refinement-phase jump.

Usage
-----
    python analysis/ecdf_v2.py \\
        --base-dir experiments/cec2020/d5 \\
        --maxevals 500000 \\
        --out plots/cec2020_d5

    # With zoom on refinement phase
    python analysis/ecdf_v2.py \\
        --base-dir experiments/cec2020/d5 \\
        --maxevals 500000 \\
        --out plots/cec2020_d5 \\
        --zoom --zoom-frac 0.15

    # Per-function ECDFs
    python analysis/ecdf_v2.py \\
        --base-dir experiments/cec2020/d5 \\
        --maxevals 500000 \\
        --funcs f6,f10 \\
        --out plots/cec2020_d5
"""

import argparse
import csv
import os
import pickle
import sys

import numpy as np

import matplotlib
matplotlib.use('Agg')
# Force Latin-glyph font for consistent PNG rendering (avoid Cyrillic
# font substitution for embedded algorithm names like "pycma").
matplotlib.rcParams['font.family']       = 'DejaVu Sans'
matplotlib.rcParams['font.sans-serif']   = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# =====================================================================
# COCO target grid — FIXED, independent of functions or algorithms
# =====================================================================

# COCO convention: 51 log-uniform targets spanning [10^2, 10^-8].
N_TARGETS = 51
TARGET_HI = 1e+2
TARGET_LO = 1e-8

# COCO_TARGETS[0] = 1e+2 (easiest), COCO_TARGETS[-1] = 1e-8 (hardest).
COCO_TARGETS = np.logspace(np.log10(TARGET_HI), np.log10(TARGET_LO),
                           num=N_TARGETS, dtype=np.float64)

# Evaluation grid: reconstruct error curves on this many log-spaced
# nfev points for smooth ECDF.
GRID_SIZE = 500


# =====================================================================
# Algorithm display
# =====================================================================

ALGO_STYLES = {
    'MSC-CMA':            {'color': '#d62728', 'ls': '-',  'lw': 2.0},
    'ARRDE-minionpy':     {'color': '#2ca02c', 'ls': '-',  'lw': 2.0},
    'BIPOP-CMA-pycma':    {'color': '#1f77b4', 'ls': '--', 'lw': 2.0},
}
DEFAULT_STYLE = {'color': '#7f7f7f', 'ls': '-.', 'lw': 1.5}


# =====================================================================
# CEC function groups (for per-group panels)
# =====================================================================

# Source: Yue, Price, Suganthan et al., Tech. Rep. 201911 (2019),
# "Problem Definitions and Evaluation Criteria for the CEC 2020 Special
# Session and Competition on Single Objective Bound Constrained
# Numerical Optimization".
CEC2020_GROUPS = {
    'Unimodal':    range(1, 2),    # f1
    'Basic':       range(2, 5),    # f2, f3, f4
    'Hybrid':      range(5, 8),    # f5, f6, f7
    'Composition': range(8, 11),   # f8, f9, f10
}

# CEC2017: F2 is officially deprecated; if pkl has no f2, it's silently
# skipped.
CEC2017_GROUPS = {
    'Unimodal':           range(1, 4),     # f1-f3 (f2 deprecated)
    'Simple multimodal':  range(4, 11),    # f4-f10
    'Hybrid':             range(11, 21),   # f11-f20
    'Composition':        range(21, 31),   # f21-f30
}
CEC2014_GROUPS = {
    'Unimodal':           range(1, 4),     # f1-f3
    'Simple multimodal':  range(4, 17),    # f4-f16
    'Hybrid':             range(17, 23),   # f17-f22
    'Composition':        range(23, 31),   # f23-f30
}
CEC2022_GROUPS = {
    'All (f1–f12)': range(1, 13),
}


def suite_groups(suite):
    s = str(suite).lower()
    if '2017' in s:
        return CEC2017_GROUPS
    if '2014' in s:
        return CEC2014_GROUPS
    if '2022' in s:
        return CEC2022_GROUPS
    return CEC2020_GROUPS


# =====================================================================
# I/O — load per-algorithm pkls
# =====================================================================

def discover_algorithms(base_dir, maxevals):
    """Scan base_dir for algorithm subdirectories containing
    maxevals_<N>/ with at least one .pkl file.
    Returns {algo_name: algo_pkl_dir}.
    """
    algos = {}
    if not os.path.isdir(base_dir):
        return algos
    for name in sorted(os.listdir(base_dir)):
        mdir = os.path.join(base_dir, name, f'maxevals_{maxevals}')
        if os.path.isdir(mdir):
            pkls = [f for f in os.listdir(mdir) if f.endswith('.pkl')]
            if pkls:
                algos[name] = mdir
    return algos


def load_algo_pkls(pkl_dir):
    """Load all f*.pkl from one algorithm directory.
    Returns {func_name: pkl_dict}.
    """
    data = {}
    for fn in sorted(os.listdir(pkl_dir)):
        if not fn.endswith('.pkl'):
            continue
        path = os.path.join(pkl_dir, fn)
        try:
            with open(path, 'rb') as f:
                d = pickle.load(f)
        except Exception as e:
            print(f"  WARN: cannot load {path}: {e}", file=sys.stderr)
            continue
        func = d.get('func', fn[:-4])
        data[func] = d
    return data


# =====================================================================
# Reconstruct error curves from improvements
# =====================================================================

def improvements_to_curve(improvements, nfev_grid):
    """Convert a single seed's improvements array (N_i, 2) with columns
    [nfev, err] to a best-so-far error curve sampled on nfev_grid.

    Returns np.ndarray of shape (len(nfev_grid),).
    At grid points before the first improvement, error = +inf.
    """
    K = len(nfev_grid)
    curve = np.full(K, np.inf, dtype=np.float64)

    if improvements is None or len(improvements) == 0:
        return curve

    imp = np.asarray(improvements, dtype=np.float64)
    if imp.ndim != 2 or imp.shape[1] < 2:
        return curve

    nfevs = imp[:, 0]
    errs = imp[:, 1]

    imp_idx = 0
    best = np.inf
    for k in range(K):
        while imp_idx < len(nfevs) and nfevs[imp_idx] <= nfev_grid[k]:
            if errs[imp_idx] < best:
                best = errs[imp_idx]
            imp_idx += 1
        curve[k] = best

    return curve


def build_err_curves(algo_data, nfev_grid):
    """Build (n_runs, K) error curve matrix from pkl data.

    Uses 'improvements' list if present, otherwise falls back to
    'errors' at the final nfev only.
    """
    improvements = algo_data.get('improvements', [])
    n_runs = algo_data.get('n_runs', len(improvements))
    K = len(nfev_grid)

    if improvements and len(improvements) > 0:
        curves = np.full((n_runs, K), np.inf, dtype=np.float64)
        for r in range(min(n_runs, len(improvements))):
            curves[r] = improvements_to_curve(
                improvements[r], nfev_grid)
        return curves

    # Fallback: only final errors available
    errors = algo_data.get('errors', np.array([]))
    if len(errors) > 0:
        curves = np.full((n_runs, K), np.inf, dtype=np.float64)
        for r in range(min(n_runs, len(errors))):
            curves[r, -1] = errors[r]
        return curves

    return np.full((n_runs, K), np.inf, dtype=np.float64)


# =====================================================================
# Runtime extraction — first-hitting times per (run, target)
# =====================================================================

def first_hit_nfev(improvements, tau, maxevals):
    """Return NFEs at which best-so-far error first reached <= tau,
    or +inf if never reached within maxevals.
    """
    if improvements is None or len(improvements) == 0:
        return np.inf
    imp = np.asarray(improvements, dtype=np.float64)
    if imp.ndim != 2 or imp.shape[1] < 2 or imp.shape[0] == 0:
        return np.inf
    mask = imp[:, 1] <= tau
    if not mask.any():
        return np.inf
    first_idx = int(np.argmax(mask))
    nfev = float(imp[first_idx, 0])
    if nfev > maxevals:
        return np.inf
    return nfev


# =====================================================================
# ECDF computation on FIXED COCO grid
# =====================================================================

def compute_ecdf(func_data_by_algo, func_list, nfev_grid, algo,
                 targets=COCO_TARGETS):
    """Compute ECDF curve for one algorithm across selected functions.

    A "task" is (function, run, target).  Task is solved at grid
    point k iff err_curve[run, k] <= target.

    Returns (fraction_array of shape (K,), n_tasks).
    """
    K = len(nfev_grid)
    hits = []

    for fname in func_list:
        if fname not in func_data_by_algo:
            continue
        algo_d = func_data_by_algo[fname].get(algo)
        if algo_d is None:
            continue

        curves = build_err_curves(algo_d, nfev_grid)      # (R, K)

        for r in range(curves.shape[0]):
            ec = curves[r]
            for tau in targets:
                solved = (ec <= tau).astype(np.uint8)
                np.maximum.accumulate(solved, out=solved)
                hits.append(solved)

    if not hits:
        return None, 0

    stacked = np.array(hits, dtype=np.float64)
    ecdf = stacked.mean(axis=0)
    return ecdf, stacked.shape[0]


# =====================================================================
# SR + aRT computation for metrics.csv
# =====================================================================

def compute_sr_art(algo_data, tau, maxevals):
    """Return (SR, aRT, n_success, n_runs) for one (algo, func, tau).

    aRT uses Price's estimator:
        (T_max * N_unsucc + sum of RT_succ) / N_succ   if N_succ > 0
        +inf                                            otherwise
    with T_max = maxevals.
    """
    improvements = algo_data.get('improvements', []) or []
    n_runs = int(algo_data.get('n_runs', len(improvements)) or 0)
    if n_runs == 0:
        return 0.0, float('inf'), 0, 0

    runtimes = []
    n_success = 0
    for imp in improvements:
        rt = first_hit_nfev(imp, tau, maxevals)
        if np.isfinite(rt):
            runtimes.append(rt)
            n_success += 1

    # Some pkls may have fewer improvement records than n_runs (edge
    # case).  Treat missing runs as unsuccessful.
    n_unsucc = n_runs - n_success

    if n_success == 0:
        return 0.0, float('inf'), 0, n_runs

    sr = n_success / n_runs
    art = (maxevals * n_unsucc + sum(runtimes)) / n_success
    return float(sr), float(art), n_success, n_runs


def write_metrics_csv(csv_path, func_data, algos, targets, maxevals):
    """Write long-format metrics.csv with one row per (func, algo, tau)."""
    with open(csv_path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['func', 'algo', 'tau', 'SR', 'aRT',
                    'n_success', 'n_runs', 'maxevals'])
        for fname in sorted(func_data.keys(),
                            key=lambda s: int(s.lstrip('f'))):
            for algo in algos:
                algo_d = func_data[fname].get(algo)
                if algo_d is None:
                    continue
                for tau in targets:
                    sr, art, ns, nr = compute_sr_art(
                        algo_d, float(tau), maxevals)
                    art_str = 'inf' if not np.isfinite(art) \
                        else f'{art:.3e}'
                    w.writerow([
                        fname, algo, f'{tau:.3e}',
                        f'{sr:.4f}', art_str, ns, nr, maxevals,
                    ])


def write_targets_csv(csv_path, targets=COCO_TARGETS):
    """Write 51-row targets.csv: target_idx, tau."""
    with open(csv_path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['target_idx', 'tau'])
        for i, tau in enumerate(targets):
            w.writerow([i, f'{tau:.6e}'])


# =====================================================================
# Plotting helpers
# =====================================================================

def _coco_xtick_formatter(dim):
    """Formatter for ticks placed at D * 10^k positions.

    Used in conjunction with _coco_xtick_locator() which places ticks
    exactly at D, 10D, 100D, ....  This formatter then labels each such
    tick as 'D', '10D', '10^k·D', etc.
    """
    def fmt(x, pos):
        if x <= 0:
            return ''
        ratio = x / dim
        k = np.log10(ratio)
        k_round = int(round(k))
        if abs(k - k_round) > 0.05:
            return f'{int(x):,}'
        if k_round == 0:
            return 'D'
        if k_round == 1:
            return '10D'
        return rf'$10^{{{k_round}}}D$'
    return FuncFormatter(fmt)


def _coco_xticks(ax, dim, nfev_grid):
    """Place major ticks at D, 10D, 100D, ..., up to max nfev.

    Also sets the formatter so the ticks render in COCO 'D, 10D, ...'
    style.  Minor ticks use the default log locator so that the inner
    grid remains a visual scale cue.
    """
    from matplotlib.ticker import FixedLocator
    x_max = float(nfev_grid[-1])
    # Find the k values for which D * 10^k lies in [1, x_max].
    k_min = int(np.ceil(np.log10(1.0 / dim)))
    k_max = int(np.floor(np.log10(x_max / dim)))
    positions = [dim * 10**k for k in range(k_min, k_max + 1)]
    if not positions:
        return
    ax.xaxis.set_major_locator(FixedLocator(positions))
    ax.xaxis.set_major_formatter(_coco_xtick_formatter(dim))


def _annotate_final_values(ax, x, ecdf_by_algo):
    """Draw dotted horizontal line + '% at end' annotation for each curve.

    Placed to the right of the rightmost x, just outside the axes frame.
    """
    if not ecdf_by_algo:
        return
    x_end = x[-1]
    for algo, ecdf in ecdf_by_algo.items():
        if ecdf is None:
            continue
        y_final = float(ecdf[-1])
        style = ALGO_STYLES.get(algo, DEFAULT_STYLE)
        ax.axhline(y=y_final,
                   color=style['color'],
                   linestyle=':', linewidth=0.8, alpha=0.5)
        ax.annotate(f'{y_final*100:.0f}%',
                    xy=(x_end, y_final),
                    xytext=(4, 0), textcoords='offset points',
                    fontsize=7, color=style['color'],
                    va='center', ha='left')


def plot_ecdf(ax, nfev_grid, dim, ecdf_by_algo, title,
              show_legend=True):
    """Plot ECDF curves on axes.

    X-axis: FEvals (log scale) with COCO-style D, 10D, ... labels.
    Y-axis: proportion of (f, τ, run) tasks solved, in [0, 1].
    Dotted reference lines at final ECDF values with % labels.
    """
    x = nfev_grid   # absolute FEvals; formatter divides by D for labels

    for algo, ecdf in ecdf_by_algo.items():
        if ecdf is None:
            continue
        style = ALGO_STYLES.get(algo, DEFAULT_STYLE)
        ax.step(x, ecdf, where='post',
                color=style['color'], ls=style['ls'], lw=style['lw'],
                label=algo)

    ax.set_xscale('log')
    ax.set_xlabel('Function evaluations')
    ax.set_ylabel('Proportion of (f, target, run) solved')
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(title, fontsize=11)
    ax.grid(True, which='both', alpha=0.3, linewidth=0.5)
    _coco_xticks(ax, dim, nfev_grid)

    _annotate_final_values(ax, x, ecdf_by_algo)

    if show_legend:
        ax.legend(fontsize=8, loc='upper left', framealpha=0.9)


def plot_ecdf_zoom(ax, nfev_grid, dim, ecdf_by_algo, maxevals,
                   zoom_frac, show_legend=False):
    """Zoomed ECDF: linear x-axis over last zoom_frac of the budget.

    Reveals sharp transitions (e.g. MSC-CMA Phase-3 refinement cliff)
    that are compressed against the right edge on log-scale plots.
    """
    x = nfev_grid
    x_lo = maxevals * (1.0 - zoom_frac)
    mask = x >= x_lo
    if not mask.any():
        return

    for algo, ecdf in ecdf_by_algo.items():
        if ecdf is None:
            continue
        style = ALGO_STYLES.get(algo, DEFAULT_STYLE)
        ax.step(x[mask], ecdf[mask], where='post',
                color=style['color'], ls=style['ls'], lw=style['lw'],
                label=algo)

    ax.set_xlim(x_lo, maxevals)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel(f'Function evaluations  '
                  f'(last {zoom_frac*100:.0f}% of budget, linear)')
    ax.set_ylabel('Proportion solved')
    ax.grid(True, which='both', alpha=0.3, linewidth=0.5)

    # Thousands-separator formatter on linear axis.
    def fmt_linear(x, pos):
        if x >= 1e6:
            return f'{x/1e6:.1f}M'
        if x >= 1e3:
            return f'{x/1e3:.0f}K'
        return f'{int(x)}'
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_linear))

    _annotate_final_values(ax, x[mask], {
        a: (e[mask] if e is not None else None)
        for a, e in ecdf_by_algo.items()
    })

    if show_legend:
        ax.legend(fontsize=8, loc='upper left', framealpha=0.9)


def render_ecdf_figure(nfev_grid, dim, ecdf_by_algo, title, out_path,
                       maxevals=None, zoom_frac=None,
                       base_size=(7, 5)):
    """Render a single ECDF figure to disk.

    If zoom_frac is not None, adds a zoom panel below the main one.
    """
    w, h = base_size
    if zoom_frac is not None and maxevals is not None:
        fig, (ax_main, ax_zoom) = plt.subplots(
            2, 1, figsize=(w, h * 1.5),
            gridspec_kw={'height_ratios': [2.0, 1.0]})
        plot_ecdf(ax_main, nfev_grid, dim, ecdf_by_algo, title,
                  show_legend=True)
        plot_ecdf_zoom(ax_zoom, nfev_grid, dim, ecdf_by_algo,
                       maxevals, zoom_frac, show_legend=False)
    else:
        fig, ax = plt.subplots(figsize=(w, h))
        plot_ecdf(ax, nfev_grid, dim, ecdf_by_algo, title,
                  show_legend=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


# =====================================================================
# Main
# =====================================================================

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--base-dir', required=True,
                   help='e.g. experiments/cec2020/d5')
    p.add_argument('--maxevals', type=int, required=True)
    p.add_argument('--out', required=True,
                   help='Output directory for figures and CSVs')
    p.add_argument('--algos', default='',
                   help='Comma-separated algorithm names (default: all)')
    p.add_argument('--funcs', default='',
                   help='Per-function ECDF plots for these '
                        '(comma-separated, e.g. f5,f6,f7)')
    p.add_argument('--grid-size', type=int, default=GRID_SIZE,
                   help=f'NFEV grid resolution (default: {GRID_SIZE})')
    p.add_argument('--zoom', action='store_true',
                   help='Add a zoomed panel (linear x-axis) over the '
                        'last fraction of the budget to every plot.')
    p.add_argument('--zoom-frac', type=float, default=0.15,
                   help='Fraction of the budget shown in the zoom '
                        'panel (default: 0.15 = last 15%% of FEs).')
    args = p.parse_args()

    zoom_frac = args.zoom_frac if args.zoom else None
    if zoom_frac is not None and not (0 < zoom_frac < 1):
        print(f"ERROR: --zoom-frac must be in (0, 1), got {zoom_frac}",
              file=sys.stderr)
        sys.exit(1)

    # Discover algorithms
    algo_dirs = discover_algorithms(args.base_dir, args.maxevals)
    if not algo_dirs:
        print(f"No algorithms found in {args.base_dir} "
              f"for maxevals={args.maxevals}")
        sys.exit(1)

    if args.algos:
        keep = set(a.strip() for a in args.algos.split(','))
        algo_dirs = {k: v for k, v in algo_dirs.items() if k in keep}

    algos = list(algo_dirs.keys())
    print(f"Algorithms: {algos}")

    # Load pkls
    func_data = {}
    suite = dim = maxevals = None
    for algo, pdir in algo_dirs.items():
        pkls = load_algo_pkls(pdir)
        for fname, d in pkls.items():
            suite = suite or d.get('suite')
            dim = dim or d.get('dim')
            maxevals = maxevals or d.get('maxevals')
            if fname not in func_data:
                func_data[fname] = {}
            func_data[fname][algo] = d

    if maxevals is None:
        maxevals = args.maxevals

    all_funcs = sorted(func_data.keys(),
                       key=lambda s: int(s.lstrip('f')))
    print(f"Suite: {suite}  D={dim}  MaxFEs={maxevals}")
    print(f"Functions: {len(all_funcs)}  {all_funcs}")
    print(f"Targets: fixed COCO grid, {N_TARGETS} log-uniform in "
          f"[{TARGET_HI:.0e}, {TARGET_LO:.0e}]")

    # Build nfev grid
    nfev_grid = np.unique(np.logspace(
        0, np.log10(maxevals), num=args.grid_size).astype(np.int64))
    if nfev_grid[-1] != maxevals:
        nfev_grid = np.append(nfev_grid, maxevals)
    K = len(nfev_grid)
    print(f"NFEV grid: {K} points  [{nfev_grid[0]}..{nfev_grid[-1]}]")

    os.makedirs(args.out, exist_ok=True)

    # Write targets.csv (definition-only)
    targets_path = os.path.join(args.out, 'targets.csv')
    write_targets_csv(targets_path, COCO_TARGETS)
    print(f"\nTargets → {targets_path}")

    # Write metrics.csv (SR + aRT long format)
    metrics_path = os.path.join(args.out, 'metrics.csv')
    write_metrics_csv(metrics_path, func_data, algos, COCO_TARGETS,
                      maxevals)
    print(f"Metrics → {metrics_path}  "
          f"({len(all_funcs) * len(algos) * N_TARGETS} rows)")

    # ── Global ECDF ──────────────────────────────────────────────────
    print(f"\n[Global ECDF — {len(all_funcs)} functions]")
    ecdf_all = {}
    for algo in algos:
        ecdf, n_tasks = compute_ecdf(
            func_data, all_funcs, nfev_grid, algo)
        ecdf_all[algo] = ecdf
        if ecdf is not None:
            print(f"  {algo}: {n_tasks} tasks, "
                  f"final={ecdf[-1]:.4f}")

    path = os.path.join(args.out, 'ecdf_all.png')
    render_ecdf_figure(
        nfev_grid, dim, ecdf_all,
        f'{suite} D={dim} — All functions '
        f'({len(all_funcs)}, {N_TARGETS} targets each)',
        path, maxevals=maxevals, zoom_frac=zoom_frac)
    print(f"  → {path}")

    # ── Per-group ECDFs ──────────────────────────────────────────────
    groups = suite_groups(suite) if suite else {}
    if len(groups) > 1:
        n_groups = len(groups)
        ncols = min(n_groups, 2)
        nrows = (n_groups + ncols - 1) // ncols
        # With zoom, each group cell needs two stacked axes
        # (main on top, zoom below), so effective row count doubles.
        panel_rows = nrows * (2 if zoom_frac is not None else 1)
        fig_h = 5 * nrows * (1.5 if zoom_frac is not None else 1.0)
        fig, axs = plt.subplots(
            panel_rows, ncols,
            figsize=(7 * ncols, fig_h),
            squeeze=False,
            gridspec_kw=(
                {'height_ratios': [2.0, 1.0] * nrows}
                if zoom_frac is not None else None))

        for i, (glabel, frange) in enumerate(groups.items()):
            row_main = (i // ncols) * (2 if zoom_frac is not None else 1)
            col = i % ncols
            ax_main = axs[row_main][col]

            gfuncs = [f for f in all_funcs
                      if int(f.lstrip('f')) in frange]
            if not gfuncs:
                ax_main.set_visible(False)
                if zoom_frac is not None:
                    axs[row_main + 1][col].set_visible(False)
                continue

            ecdf_g = {}
            for algo in algos:
                ecdf, _ = compute_ecdf(
                    func_data, gfuncs, nfev_grid, algo)
                ecdf_g[algo] = ecdf

            plot_ecdf(ax_main, nfev_grid, dim, ecdf_g,
                      f'{glabel} ({len(gfuncs)} funcs)',
                      show_legend=(i == 0))
            if zoom_frac is not None:
                ax_zoom = axs[row_main + 1][col]
                plot_ecdf_zoom(ax_zoom, nfev_grid, dim, ecdf_g,
                               maxevals, zoom_frac,
                               show_legend=False)

        # Hide unused panels (when n_groups < nrows*ncols).
        used_cells = n_groups
        total_cells = nrows * ncols
        for j in range(used_cells, total_cells):
            row_main = (j // ncols) * (2 if zoom_frac is not None else 1)
            col = j % ncols
            axs[row_main][col].set_visible(False)
            if zoom_frac is not None:
                axs[row_main + 1][col].set_visible(False)

        fig.suptitle(f'{suite} D={dim} — ECDF per group',
                     fontsize=13)
        plt.tight_layout()
        path = os.path.join(args.out, 'ecdf_groups.png')
        plt.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  → {path}")

    # ── Per-function ECDFs (replaces old attain_*.png) ───────────────
    per_funcs = [f.strip() for f in args.funcs.split(',') if f.strip()]
    if per_funcs:
        print(f"\n[Per-function ECDF: {per_funcs}]")
        for fname in per_funcs:
            if fname not in func_data:
                print(f"  skip {fname}: not found")
                continue
            ecdf_f = {}
            for algo in algos:
                ecdf, _ = compute_ecdf(
                    func_data, [fname], nfev_grid, algo)
                ecdf_f[algo] = ecdf
            path = os.path.join(args.out, f'ecdf_{fname}.png')
            render_ecdf_figure(
                nfev_grid, dim, ecdf_f,
                f'{suite} {fname} D={dim} — ECDF '
                f'({N_TARGETS} targets × 51 seeds)',
                path, maxevals=maxevals, zoom_frac=zoom_frac)
            print(f"  → {path}")

    print("\nDone.")


if __name__ == '__main__':
    main()
