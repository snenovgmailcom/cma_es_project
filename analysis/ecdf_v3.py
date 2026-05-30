#!/usr/bin/env python3
"""
ecdf_v3.py — COCO-compliant runtime ECDF + SR/aRT, with v33 HIGH/LOW partition.

Differences from ecdf_v2.py
---------------------------
* The basic / hybrid / composition CEC group classification is REPLACED by the
  v33 LOW/HIGH LHS partition rule (cls_v1):

      LHS at seed=0, M_factor=500, N=M_factor*D (per-function sampler seed = seed+fnum).
      range < 1500   OR  range > 1e10        →  HIGH
      mean_q ∈ {Q3, Q4}                       →  HIGH
      otherwise                               →  LOW

* THREE main figures produced per (suite, dim):

      ecdf_all.png    — global ECDF over every function present in the dir
      ecdf_high.png   — ECDF over HIGH-bucket functions only
      ecdf_low.png    — ECDF over LOW-bucket functions only

* Per-function ECDF figures (ecdf_f<k>.png) are still emitted for any function
  named via --funcs (unchanged from v2).

* Auto-discovers every algorithm subdirectory under base-dir/<algo>/maxevals_<N>/.

* Partition can be overridden manually via --high / --low (skips minionpy).
  Without overrides, the rule is computed at runtime — minionpy must be
  importable (same dependency as analysis/lhs_range_saddles.py).

Usage
-----
    # All algorithms in experiments/cec2020/d10, classify automatically:
    python analysis/ecdf_v3.py \\
        --base-dir experiments/cec2020/d10 \\
        --maxevals 1000000 \\
        --out plots/cec2020_d10

    # Manual partition (no minionpy needed):
    python analysis/ecdf_v3.py \\
        --base-dir experiments/cec2017/d10 \\
        --maxevals 100000 \\
        --high 1,2,3,5,6,8,10,11,12,13,14,15,18,19,22,30 \\
        --low  4,7,9,16,17,20,21,23,24,25,26,27,28,29 \\
        --out plots/cec2017_d10

    # Per-function plots in addition to the three buckets, with refinement zoom:
    python analysis/ecdf_v3.py \\
        --base-dir experiments/cec2020/d10 \\
        --maxevals 1000000 \\
        --funcs f8,f10 --zoom \\
        --out plots/cec2020_d10
"""

import argparse
import csv
import os
import pickle
import sys

import numpy as np

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.family']        = 'DejaVu Sans'
matplotlib.rcParams['font.sans-serif']    = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# =====================================================================
# COCO target grid
# =====================================================================

N_TARGETS = 51
TARGET_HI = 1e+2
TARGET_LO = 1e-8

COCO_TARGETS = np.logspace(np.log10(TARGET_HI), np.log10(TARGET_LO),
                           num=N_TARGETS, dtype=np.float64)

GRID_SIZE = 500


# =====================================================================
# Algorithm display
# =====================================================================

ALGO_STYLES = {
    'MSC-CMA':            {'color': '#d62728', 'ls': '-',  'lw': 2.0},
    'ARRDE-minionpy':     {'color': '#2ca02c', 'ls': '-',  'lw': 2.0},
    'BIPOP-CMA-pycma':    {'color': '#1f77b4', 'ls': '--', 'lw': 2.0},
    'LSRTDE-minionpy':    {'color': '#ff7f0e', 'ls': '-',  'lw': 2.0},
}
DEFAULT_STYLE = {'color': '#7f7f7f', 'ls': '-.', 'lw': 1.5}


# =====================================================================
# v33 LOW/HIGH classification rule (cls_v1)
# =====================================================================

RULE_RANGE_LO = 1500.0
RULE_RANGE_HI = 1e10


def _suite_funcs(suite):
    s = str(suite).lower()
    if '2017' in s or '2014' in s:  return list(range(1, 31))
    if '2020' in s:                 return list(range(1, 11))
    if '2022' in s:                 return list(range(1, 13))
    if '2019' in s:                 return list(range(1, 11))
    return []


def _suite_bounds(suite, fnum, dim):
    s = str(suite).lower()
    if '2019' in s:
        b2019 = {1: (-8192, 8192), 2: (-16384, 16384), 3: (-4, 4)}
        lb, ub = b2019.get(fnum, (-100, 100))
    else:
        lb, ub = -100, 100
    return (np.full(dim, lb, dtype=np.float64),
            np.full(dim, ub, dtype=np.float64))


def _suite_evaluator(suite, fnum, dim):
    """Return f(X)->errors using minionpy. Imported lazily."""
    import minionpy
    cls_map = {
        'cec2014': 'CEC2014Functions', 'cec2017': 'CEC2017Functions',
        'cec2019': 'CEC2019Functions', 'cec2020': 'CEC2020Functions',
        'cec2022': 'CEC2022Functions',
    }
    s = str(suite).lower()
    key = next((k for k in cls_map if k in s), None)
    if key is None:
        raise ValueError(f"Cannot find minionpy class for suite={suite!r}")
    ev = getattr(minionpy, cls_map[key])(fnum, dim)
    return lambda X: np.asarray(ev(X), dtype=np.float64)


def _quartile_label(value, fmin, fmax):
    if fmax == fmin:
        return '—'
    pos = (value - fmin) / (fmax - fmin)
    pos = max(0.0, min(1.0, pos))
    if pos < 0.25: return 'Q1'
    if pos < 0.50: return 'Q2'
    if pos < 0.75: return 'Q3'
    return 'Q4'


def classify_lhs_v1(suite, dim, fnums, m_factor=500, seed=0):
    """Compute LOW/HIGH partition for fnums via the canonical v1 rule.

    Returns (high_set, low_set) as sorted Python lists of int.
    Requires minionpy. Per-function sampler seed = seed + fnum, mirroring
    analysis/lhs_range_saddles.py exactly.
    """
    from scipy.stats import qmc
    n = m_factor * dim
    high, low = [], []
    for fnum in fnums:
        lb, ub = _suite_bounds(suite, fnum, dim)
        sampler = qmc.LatinHypercube(d=dim, seed=seed + fnum)
        unit = sampler.random(n=n)
        X = lb + (ub - lb) * unit
        F = _suite_evaluator(suite, fnum, dim)(X)
        fmin = float(np.min(F)); fmax = float(np.max(F))
        frange = fmax - fmin
        mean_q = _quartile_label(float(np.mean(F)), fmin, fmax)
        if frange < RULE_RANGE_LO or frange > RULE_RANGE_HI:
            high.append(fnum)
        elif mean_q in ('Q3', 'Q4'):
            high.append(fnum)
        else:
            low.append(fnum)
    return sorted(high), sorted(low)


def parse_func_list(s):
    """Accepts '1,2,3' or 'f1,f2,f3'; returns list[int] sorted."""
    out = []
    for tok in (t.strip() for t in s.split(',') if t.strip()):
        out.append(int(tok.lstrip('f')))
    return sorted(out)


# =====================================================================
# I/O — load per-algorithm pkls
# =====================================================================

def discover_algorithms(base_dir, maxevals):
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
    K = len(nfev_grid)
    curve = np.full(K, np.inf, dtype=np.float64)
    if improvements is None or len(improvements) == 0:
        return curve
    imp = np.asarray(improvements, dtype=np.float64)
    if imp.ndim != 2 or imp.shape[1] < 2:
        return curve
    nfevs = imp[:, 0]
    errs  = imp[:, 1]
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
    improvements = algo_data.get('improvements', [])
    n_runs = algo_data.get('n_runs', len(improvements))
    K = len(nfev_grid)
    if improvements and len(improvements) > 0:
        curves = np.full((n_runs, K), np.inf, dtype=np.float64)
        for r in range(min(n_runs, len(improvements))):
            curves[r] = improvements_to_curve(improvements[r], nfev_grid)
        return curves
    errors = algo_data.get('errors', np.array([]))
    if len(errors) > 0:
        curves = np.full((n_runs, K), np.inf, dtype=np.float64)
        for r in range(min(n_runs, len(errors))):
            curves[r, -1] = errors[r]
        return curves
    return np.full((n_runs, K), np.inf, dtype=np.float64)


# =====================================================================
# Runtime extraction
# =====================================================================

def first_hit_nfev(improvements, tau, maxevals):
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
# ECDF computation
# =====================================================================

def compute_ecdf(func_data_by_algo, func_list, nfev_grid, algo,
                 targets=COCO_TARGETS):
    K = len(nfev_grid)
    hits = []
    for fname in func_list:
        if fname not in func_data_by_algo:
            continue
        algo_d = func_data_by_algo[fname].get(algo)
        if algo_d is None:
            continue
        curves = build_err_curves(algo_d, nfev_grid)
        for r in range(curves.shape[0]):
            ec = curves[r]
            for tau in targets:
                solved = (ec <= tau).astype(np.uint8)
                np.maximum.accumulate(solved, out=solved)
                hits.append(solved)
    if not hits:
        return None, 0
    stacked = np.array(hits, dtype=np.float64)
    return stacked.mean(axis=0), stacked.shape[0]


# =====================================================================
# SR + aRT for metrics.csv
# =====================================================================

def compute_sr_art(algo_data, tau, maxevals):
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
    n_unsucc = n_runs - n_success
    if n_success == 0:
        return 0.0, float('inf'), 0, n_runs
    sr  = n_success / n_runs
    art = (maxevals * n_unsucc + sum(runtimes)) / n_success
    return float(sr), float(art), n_success, n_runs


def write_metrics_csv(csv_path, func_data, algos, targets, maxevals):
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
                    art_str = 'inf' if not np.isfinite(art) else f'{art:.3e}'
                    w.writerow([fname, algo, f'{tau:.3e}',
                                f'{sr:.4f}', art_str, ns, nr, maxevals])


def write_targets_csv(csv_path, targets=COCO_TARGETS):
    with open(csv_path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['target_idx', 'tau'])
        for i, tau in enumerate(targets):
            w.writerow([i, f'{tau:.6e}'])


def write_partition_txt(path, suite, dim, m_factor, seed, high, low):
    """Persist the partition next to the figures so it's reproducible."""
    with open(path, 'w') as fh:
        fh.write(f"# v33 LOW/HIGH partition (cls_v1)\n")
        fh.write(f"# suite={suite}  dim={dim}  M_factor={m_factor}  seed={seed}\n")
        fh.write(f"# rule: range<{int(RULE_RANGE_LO)} OR range>{RULE_RANGE_HI:.0e} "
                 f"OR mean_q ∈ {{Q3,Q4}} → HIGH\n")
        fh.write(f"HIGH ({len(high)}): {high}\n")
        fh.write(f"LOW  ({len(low)}): {low}\n")


# =====================================================================
# Plotting helpers
# =====================================================================

def _coco_xtick_formatter(dim):
    def fmt(x, pos):
        if x <= 0:
            return ''
        ratio = x / dim
        k = np.log10(ratio)
        k_round = int(round(k))
        if abs(k - k_round) > 0.05:
            return f'{int(x):,}'
        if k_round == 0: return 'D'
        if k_round == 1: return '10D'
        return rf'$10^{{{k_round}}}D$'
    return FuncFormatter(fmt)


def _coco_xticks(ax, dim, nfev_grid):
    from matplotlib.ticker import FixedLocator
    x_max = float(nfev_grid[-1])
    k_min = int(np.ceil(np.log10(1.0 / dim)))
    k_max = int(np.floor(np.log10(x_max / dim)))
    positions = [dim * 10**k for k in range(k_min, k_max + 1)]
    if not positions:
        return
    ax.xaxis.set_major_locator(FixedLocator(positions))
    ax.xaxis.set_major_formatter(_coco_xtick_formatter(dim))


def _annotate_final_values(ax, x, ecdf_by_algo):
    if not ecdf_by_algo:
        return
    x_end = x[-1]
    for algo, ecdf in ecdf_by_algo.items():
        if ecdf is None:
            continue
        y_final = float(ecdf[-1])
        style = ALGO_STYLES.get(algo, DEFAULT_STYLE)
        ax.axhline(y=y_final, color=style['color'],
                   linestyle=':', linewidth=0.8, alpha=0.5)
        ax.annotate(f'{y_final*100:.0f}%',
                    xy=(x_end, y_final),
                    xytext=(4, 0), textcoords='offset points',
                    fontsize=7, color=style['color'],
                    va='center', ha='left')


def plot_ecdf(ax, nfev_grid, dim, ecdf_by_algo, title, show_legend=True):
    x = nfev_grid
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

    def fmt_linear(x, pos):
        if x >= 1e6: return f'{x/1e6:.1f}M'
        if x >= 1e3: return f'{x/1e3:.0f}K'
        return f'{int(x)}'
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_linear))

    _annotate_final_values(ax, x[mask], {
        a: (e[mask] if e is not None else None)
        for a, e in ecdf_by_algo.items()
    })
    if show_legend:
        ax.legend(fontsize=8, loc='upper left', framealpha=0.9)


def render_ecdf_figure(nfev_grid, dim, ecdf_by_algo, title, out_path,
                       maxevals=None, zoom_frac=None, base_size=(7, 5)):
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
        plot_ecdf(ax, nfev_grid, dim, ecdf_by_algo, title, show_legend=True)
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
                   help='e.g. experiments/cec2020/d10')
    p.add_argument('--maxevals', type=int, required=True)
    p.add_argument('--out', required=True,
                   help='Output directory for figures and CSVs')
    p.add_argument('--algos', default='',
                   help='Comma-separated algorithm names (default: all discovered)')
    p.add_argument('--funcs', default='',
                   help='Per-function ECDF plots for these (e.g. f5,f6,f7)')
    p.add_argument('--grid-size', type=int, default=GRID_SIZE)
    p.add_argument('--zoom', action='store_true',
                   help='Add a zoomed panel over the last fraction of the budget')
    p.add_argument('--zoom-frac', type=float, default=0.15)

    # Partition controls
    p.add_argument('--high', default='',
                   help='Manual HIGH list (e.g. 1,2,5,7). Skips LHS classification.')
    p.add_argument('--low', default='',
                   help='Manual LOW list (e.g. 3,4,6,8,9,10). Skips LHS classification.')
    p.add_argument('--rule-mfactor', type=int, default=500,
                   help='M_factor for the LHS rule (canonical: 500)')
    p.add_argument('--rule-seed', type=int, default=0,
                   help='Seed base for the LHS rule (canonical: 0)')
    p.add_argument('--no-bucket-plots', action='store_true',
                   help='Skip ecdf_high.png and ecdf_low.png')
    args = p.parse_args()

    zoom_frac = args.zoom_frac if args.zoom else None
    if zoom_frac is not None and not (0 < zoom_frac < 1):
        sys.exit(f"ERROR: --zoom-frac must be in (0, 1), got {zoom_frac}")

    # Discover algorithms
    algo_dirs = discover_algorithms(args.base_dir, args.maxevals)
    if not algo_dirs:
        sys.exit(f"No algorithms found in {args.base_dir} "
                 f"for maxevals={args.maxevals}")
    if args.algos:
        keep = set(a.strip() for a in args.algos.split(','))
        algo_dirs = {k: v for k, v in algo_dirs.items() if k in keep}
    algos = list(algo_dirs.keys())
    print(f"Algorithms: {algos}")

    # Load pkls
    func_data = {}
    suite = dim = maxevals = None
    for algo, pdir in algo_dirs.items():
        for fname, d in load_algo_pkls(pdir).items():
            suite    = suite    or d.get('suite')
            dim      = dim      or d.get('dim')
            maxevals = maxevals or d.get('maxevals')
            func_data.setdefault(fname, {})[algo] = d
    if maxevals is None:
        maxevals = args.maxevals

    all_funcs = sorted(func_data.keys(), key=lambda s: int(s.lstrip('f')))
    all_fnums = [int(f.lstrip('f')) for f in all_funcs]
    print(f"Suite: {suite}  D={dim}  MaxFEs={maxevals}")
    print(f"Functions: {len(all_funcs)}  {all_funcs}")
    print(f"Targets: fixed COCO grid, {N_TARGETS} log-uniform in "
          f"[{TARGET_HI:.0e}, {TARGET_LO:.0e}]")

    # NFEV grid
    nfev_grid = np.unique(np.logspace(
        0, np.log10(maxevals), num=args.grid_size).astype(np.int64))
    if nfev_grid[-1] != maxevals:
        nfev_grid = np.append(nfev_grid, maxevals)
    print(f"NFEV grid: {len(nfev_grid)} points  [{nfev_grid[0]}..{nfev_grid[-1]}]")

    os.makedirs(args.out, exist_ok=True)

    # ── Partition (LOW / HIGH) ───────────────────────────────────────────
    high_fnums, low_fnums = [], []
    skip_buckets = args.no_bucket_plots

    if args.high or args.low:
        if args.high:
            high_fnums = parse_func_list(args.high)
        if args.low:
            low_fnums = parse_func_list(args.low)
        # Cross-check against present funcs
        unknown_h = [f for f in high_fnums if f not in all_fnums]
        unknown_l = [f for f in low_fnums  if f not in all_fnums]
        if unknown_h or unknown_l:
            print(f"  WARN: HIGH override missing pkls for {unknown_h}, "
                  f"LOW override missing pkls for {unknown_l}", file=sys.stderr)
        # If only one bucket given, infer the other as complement of present funcs
        if high_fnums and not low_fnums:
            low_fnums = [f for f in all_fnums if f not in high_fnums]
        elif low_fnums and not high_fnums:
            high_fnums = [f for f in all_fnums if f not in low_fnums]
        print(f"Partition (manual override):  HIGH={high_fnums}  LOW={low_fnums}")
    elif not skip_buckets:
        if suite is None or dim is None:
            print("  WARN: cannot auto-classify (suite/dim missing from pkls); "
                  "skipping HIGH/LOW plots.", file=sys.stderr)
            skip_buckets = True
        else:
            try:
                high_fnums, low_fnums = classify_lhs_v1(
                    suite, dim, all_fnums,
                    m_factor=args.rule_mfactor, seed=args.rule_seed)
                print(f"Partition (LHS v1, M={args.rule_mfactor}, "
                      f"seed={args.rule_seed}):")
                print(f"  HIGH ({len(high_fnums)}): {high_fnums}")
                print(f"  LOW  ({len(low_fnums)}): {low_fnums}")
                write_partition_txt(
                    os.path.join(args.out, 'partition.txt'),
                    suite, dim, args.rule_mfactor, args.rule_seed,
                    high_fnums, low_fnums)
            except Exception as e:
                print(f"  WARN: LHS classification failed ({type(e).__name__}: {e}); "
                      f"skipping HIGH/LOW plots. Use --high/--low to override.",
                      file=sys.stderr)
                skip_buckets = True

    # ── CSV outputs ─────────────────────────────────────────────────────
    targets_path = os.path.join(args.out, 'targets.csv')
    write_targets_csv(targets_path, COCO_TARGETS)
    print(f"\nTargets → {targets_path}")

    metrics_path = os.path.join(args.out, 'metrics.csv')
    write_metrics_csv(metrics_path, func_data, algos, COCO_TARGETS, maxevals)
    print(f"Metrics → {metrics_path}  "
          f"({len(all_funcs) * len(algos) * N_TARGETS} rows)")

    # ── Global ECDF (ecdf_all.png) ──────────────────────────────────────
    print(f"\n[Global ECDF — {len(all_funcs)} functions]")
    ecdf_all = {}
    for algo in algos:
        ecdf, n_tasks = compute_ecdf(func_data, all_funcs, nfev_grid, algo)
        ecdf_all[algo] = ecdf
        if ecdf is not None:
            print(f"  {algo}: {n_tasks} tasks, final={ecdf[-1]:.4f}")
    path = os.path.join(args.out, 'ecdf_all.png')
    render_ecdf_figure(
        nfev_grid, dim, ecdf_all,
        f'{suite} D={dim} — All functions '
        f'({len(all_funcs)}, {N_TARGETS} targets each)',
        path, maxevals=maxevals, zoom_frac=zoom_frac)
    print(f"  → {path}")

    # ── HIGH / LOW bucket figures ────────────────────────────────────────
    if not skip_buckets:
        for label, fnums, fname_out in (
                ('HIGH', high_fnums, 'ecdf_high.png'),
                ('LOW',  low_fnums,  'ecdf_low.png')):
            funcs_in_bucket = [f'f{n}' for n in fnums if f'f{n}' in func_data]
            if not funcs_in_bucket:
                print(f"\n[{label} bucket] empty — no pkls match; skipping figure")
                continue
            print(f"\n[{label} bucket — {len(funcs_in_bucket)} functions]")
            ecdf_b = {}
            for algo in algos:
                ecdf, n_tasks = compute_ecdf(
                    func_data, funcs_in_bucket, nfev_grid, algo)
                ecdf_b[algo] = ecdf
                if ecdf is not None:
                    print(f"  {algo}: {n_tasks} tasks, final={ecdf[-1]:.4f}")
            path = os.path.join(args.out, fname_out)
            title = (f'{suite} D={dim} — {label} bucket '
                     f'({len(funcs_in_bucket)} funcs, {N_TARGETS} targets each)')
            render_ecdf_figure(
                nfev_grid, dim, ecdf_b, title, path,
                maxevals=maxevals, zoom_frac=zoom_frac)
            print(f"  → {path}")

    # ── Per-function ECDFs ──────────────────────────────────────────────
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
