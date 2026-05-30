#!/usr/bin/env python3
"""
analysis/compare.py — multi-algorithm comparison for v26 (extended).

Adds two new metrics:
  --metric ecdf   : COCO ECDF area (51 log-spaced targets in [1e-8, 1e2]),
                    per-function scalar in [0,1]. HIGHER is better.
  --metric hits   : Per-CEC-display-target hit counts (7 targets) — shown as
                    a separate per-function block. Not a scalar; aggregation
                    is per-target totals + per-target win counts. No Wilcoxon
                    table for this metric (use 'mean' or 'ecdf' for stats).

Usage
-----
    python analysis/compare.py \
        --base-dir experiments/cec2020/d10 \
        --metric median --ref MSC-CMA --correction bh

    # COCO ECDF table
    python analysis/compare.py \
        --base-dir experiments/cec2020/d10 \
        --metric ecdf --ref MSC-CMA --correction bh

    # CEC hits-per-target table
    python analysis/compare.py \
        --base-dir experiments/cec2020/d10 \
        --metric hits --ref MSC-CMA

    # ARRDE Appendix-A style LaTeX output
    python analysis/compare.py \
        --base-dir experiments/cec2020/d10 \
        --ref MSC-CMA --maxevals 1000000 \
        --latex
"""

import argparse
import glob
import os
import pickle
import sys
import warnings

import numpy as np
from scipy import stats


# =========================================================================
# COCO / CEC numerical-zero convention
# =========================================================================

COCO_ZERO = 1e-8


def _floor(arr: np.ndarray, eps: float = COCO_ZERO) -> np.ndarray:
    out = np.asarray(arr, dtype=np.float64).copy()
    out[np.abs(out) <= eps] = 0.0
    return out


# =========================================================================
# COCO ECDF helpers
# =========================================================================

# 51 log-spaced targets in [1e-8, 1e2] — matches BBOB convention.
COCO_TAUS = 10.0 ** np.linspace(2.0, -8.0, 51)

# 7 CEC display targets (Suganthan-style)
CEC_TAUS = [1e1, 1e0, 1e-1, 1e-2, 1e-3, 1e-5, 1e-8]


def ecdf_area(errs: np.ndarray, taus=COCO_TAUS) -> float:
    """COCO-style ECDF area: mean attainment rate over targets.

    For each target tau, fraction of seeds with err <= tau.
    Mean across all targets in [0, 1]. Higher is better.
    """
    a = np.asarray(errs, dtype=np.float64)
    n = len(a)
    if n == 0:
        return 0.0
    return float(np.mean([np.sum(a <= t) / n for t in taus]))


def per_seed_ecdf(errs: np.ndarray, taus=COCO_TAUS) -> np.ndarray:
    """Per-seed ECDF: for each seed, fraction of targets it reaches.

    Returns array of length len(errs), each value in [0, 1].
    Used for paired Wilcoxon on ECDF metric.
    """
    a = np.asarray(errs, dtype=np.float64)
    if len(a) == 0:
        return np.array([])
    # For each seed err, count how many targets it satisfies.
    # err <= tau means seed reaches that target.
    counts = np.array([np.sum(a[i] <= taus) for i in range(len(a))])
    return counts.astype(np.float64) / len(taus)


def hits_per_target(errs: np.ndarray, taus=CEC_TAUS) -> list:
    """For each target in taus, how many seeds reach err <= tau.

    Returns list of int, same length as taus.
    """
    a = np.asarray(errs, dtype=np.float64)
    return [int(np.sum(a <= t)) for t in taus]


# =========================================================================
# Function categories (Basic / Hybrid / Composition)
# =========================================================================

# Per-suite function-index ranges. Unimodal functions are folded into
# "Basic", consistent with the CEC2014/2017 grouping supplied for this tool.
#   CEC2020 (10 funcs): F1 unimodal + F2-F4 basic; F5-F7 hybrid; F8-F10 comp.
#   CEC2022 (12 funcs): F1 unimodal + F2-F5 basic; F6-F8 hybrid; F9-F12 comp.
CATEGORY_ORDER = ['Basic', 'Hybrid', 'Composition']

CATEGORIES = {
    'CEC2014': {'Basic':       range(1, 17),
                'Hybrid':      range(17, 23),
                'Composition': range(23, 31)},
    'CEC2017': {'Basic':       range(1, 11),
                'Hybrid':      range(11, 21),
                'Composition': range(21, 31)},
    'CEC2020': {'Basic':       range(1, 5),
                'Hybrid':      range(5, 8),
                'Composition': range(8, 11)},
    'CEC2022': {'Basic':       range(1, 6),
                'Hybrid':      range(6, 9),
                'Composition': range(9, 13)},
}


def _detect_suite(base_dir: str) -> str:
    """Infer the suite tag (e.g. 'CEC2020') from a base_dir of the form
    experiments/<suite>/d<dim>."""
    suite_tag = os.path.basename(os.path.dirname(base_dir.rstrip('/')))
    return suite_tag.upper()


# =========================================================================
# BH correction
# =========================================================================

def bh_correction(p_values: list) -> list:
    n = len(p_values)
    if n == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * n
    prev = 1.0
    for rank_minus_1 in range(n - 1, -1, -1):
        orig_idx, p = indexed[rank_minus_1]
        rank = rank_minus_1 + 1
        adj = min(prev, p * n / rank, 1.0)
        adjusted[orig_idx] = adj
        prev = adj
    return adjusted


def bonferroni_correction(p_values: list) -> list:
    n = len(p_values)
    return [min(p * n, 1.0) for p in p_values]


# =========================================================================
# Wilcoxon
# =========================================================================

def paired_wilcoxon(errors_a: np.ndarray, errors_b: np.ndarray,
                    higher_better: bool = False):
    """Wilcoxon signed-rank test (two-sided), COCO/CEC-conformant.

    For higher_better=True (e.g. per-seed ECDF), test for a > b.
    For higher_better=False (default, errors), test for a < b.
    """
    a = np.asarray(errors_a, dtype=np.float64)
    b = np.asarray(errors_b, dtype=np.float64)

    if np.all(a == b):
        return 0.0, 1.0, len(a)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            result = stats.wilcoxon(
                a, b,
                zero_method='pratt',
                alternative='two-sided',
                method='auto',
            )
        except ValueError:
            return 0.0, 1.0, len(a)

    return float(result.statistic), float(result.pvalue), len(a)


# =========================================================================
# Auto-discovery
# =========================================================================

def discover_algorithms(base_dir: str, maxevals: int = None) -> dict:
    algorithms = {}

    for alg_dir in sorted(os.listdir(base_dir)):
        alg_path = os.path.join(base_dir, alg_dir)
        if not os.path.isdir(alg_path):
            continue

        me_dirs = sorted(glob.glob(os.path.join(alg_path, 'maxevals_*')))
        if not me_dirs:
            continue

        if maxevals is not None:
            target = os.path.join(alg_path, f'maxevals_{maxevals}')
            if not os.path.isdir(target):
                continue
            me_dir = target
        elif len(me_dirs) == 1:
            me_dir = me_dirs[0]
        else:
            me_dir = me_dirs[-1]

        pkls = sorted(
            glob.glob(os.path.join(me_dir, 'f*.pkl')),
            key=lambda p: int(
                os.path.basename(p).replace('f', '').replace('.pkl', '')))

        if not pkls:
            continue

        funcs = {}
        for p in pkls:
            with open(p, 'rb') as f:
                d = pickle.load(f)
            fn = d['func']
            funcs[fn] = d

        # Use directory name as the algorithm key, not the pkl's `algorithm`
        # field. The pkl field is hardcoded to a canonical name (e.g. all MSC
        # variants stamp 'MSC-CMA'), which causes silent collisions and
        # overwrites when multiple version subdirs (MSC-CMA, MSC-CMA-v34, ...)
        # coexist under the same suite/dim cell.
        alg_name = alg_dir

        if alg_name and funcs:
            algorithms[alg_name] = funcs

    return algorithms


# =========================================================================
# Compare (scalar metrics including 'ecdf')
# =========================================================================

def run_comparison(base_dir, ref, metric, correction, alpha,
                   maxevals=None):
    """Run scalar-metric comparison. metric is one of
    {median, mean, best, worst, std, ecdf}."""
    algorithms = discover_algorithms(base_dir, maxevals)

    if not algorithms:
        raise FileNotFoundError(
            f"No algorithm directories found in {base_dir}")

    alg_names = sorted(algorithms.keys())

    if ref not in algorithms:
        available = ', '.join(alg_names)
        raise ValueError(
            f"Reference '{ref}' not found. Available: {available}")

    func_sets = [set(algorithms[a].keys()) for a in alg_names]
    common = sorted(
        set.intersection(*func_sets),
        key=lambda fn: int(fn.replace('f', '')))

    if not common:
        raise ValueError("No common functions across all algorithms")

    higher_better = (metric == 'ecdf')
    ref_data = algorithms[ref]

    metric_table = {a: {} for a in alg_names}
    sig_table = {a: {} for a in alg_names}
    raw_p = {a: [] for a in alg_names if a != ref}

    for fn in common:
        ref_errors = _floor(ref_data[fn]['errors'])
        ref_per_seed_ecdf = per_seed_ecdf(ref_errors) if metric == 'ecdf' else None

        for alg in alg_names:
            errs = _floor(algorithms[alg][fn]['errors'])

            if metric == 'median':
                metric_table[alg][fn] = float(np.median(errs))
            elif metric == 'mean':
                metric_table[alg][fn] = float(np.mean(errs))
            elif metric == 'best':
                metric_table[alg][fn] = float(np.min(errs))
            elif metric == 'worst':
                metric_table[alg][fn] = float(np.max(errs))
            elif metric == 'std':
                metric_table[alg][fn] = float(np.std(errs))
            elif metric == 'ecdf':
                metric_table[alg][fn] = ecdf_area(errs)

            if alg != ref:
                if metric == 'ecdf':
                    # Wilcoxon on per-seed ECDF vectors
                    alg_seed_ecdf = per_seed_ecdf(errs)
                    _, p, _ = paired_wilcoxon(
                        alg_seed_ecdf, ref_per_seed_ecdf,
                        higher_better=True)
                else:
                    _, p, _ = paired_wilcoxon(errs, ref_errors)
                raw_p[alg].append((fn, p))

    for fn in common:
        sig_table[ref][fn] = False

    for alg in raw_p:
        p_list = [x[1] for x in raw_p[alg]]
        if correction == 'bh':
            adj = bh_correction(p_list)
        elif correction == 'bonferroni':
            adj = bonferroni_correction(p_list)
        else:
            adj = p_list

        for i, (fn, _) in enumerate(raw_p[alg]):
            alg_val = metric_table[alg][fn]
            ref_val = metric_table[ref][fn]
            if higher_better:
                better = alg_val > ref_val
            else:
                better = alg_val < ref_val
            sig_table[alg][fn] = (adj[i] < alpha) and better

    return common, alg_names, metric_table, sig_table


# =========================================================================
# Print scalar table (median/mean/best/worst/std/ecdf)
# =========================================================================

def print_table(common, alg_names, metric_table, sig_table,
                ref, metric, base_dir, correction, alpha):
    """Print scalar metric table."""

    corr_label = {'bh': 'Benjamini-Hochberg (FDR)',
                  'bonferroni': 'Bonferroni',
                  'none': 'none'}
    corr_str = corr_label.get(correction, correction)
    higher_better = (metric == 'ecdf')
    direction_note = ('higher is better' if higher_better
                      else 'lower is better')

    print(f"Loaded {len(alg_names)} algorithms from {base_dir}")
    print(f"Wilcoxon vs {ref}  ({corr_str}, \u03b1={alpha})")
    print(f"  * = significantly better than {ref} on this function "
          f"({direction_note})")
    print(f"{base_dir}  metric={metric}")

    col_w = max(len(a) for a in alg_names)
    col_w = max(col_w, 15)

    header = f"{'func':>4s}"
    for alg in alg_names:
        header += f"  {alg:>{col_w}s}"
    print(header)
    print("-" * len(header))

    wins = {a: 0 for a in alg_names}
    per_func_vals = {a: [] for a in alg_names}

    for fn in common:
        row = f"{fn:>4s}"
        for alg in alg_names:
            val = metric_table[alg][fn]
            # Floor only applies to error metrics, not ECDF
            if metric == 'ecdf':
                val_disp = val
                val_str = f"{val_disp:.3f}"
            else:
                val_disp = 0.0 if abs(val) <= COCO_ZERO else val
                val_str = ("0.000e+00" if val_disp == 0.0
                           else f"{val_disp:.3e}")
            per_func_vals[alg].append(val_disp)

            if sig_table[alg][fn]:
                val_str += "*"
                wins[alg] += 1

            row += f"  {val_str:>{col_w}s}"
        print(row)

    print("-" * len(header))

    # Aggregation
    if metric == 'ecdf':
        agg_label, agg_fn = 'SUM', np.sum
    elif metric in ('median', 'mean', 'std'):
        agg_label, agg_fn = 'SUM', np.sum
    elif metric == 'worst':
        agg_label, agg_fn = 'SUM', np.sum
    elif metric == 'best':
        agg_label, agg_fn = 'SUM', np.sum
    else:
        agg_label, agg_fn = 'SUM', np.sum

    row = f"{agg_label:>4s}"
    for alg in alg_names:
        v = agg_fn(np.asarray(per_func_vals[alg], dtype=np.float64))
        if metric == 'ecdf':
            v_str = f"{v:.3f}"
        else:
            v = 0.0 if abs(v) <= COCO_ZERO else v
            v_str = "0.000e+00" if v == 0.0 else f"{v:.3e}"
        row += f"  {v_str:>{col_w}s}"
    print(row)

    n_funcs = len(common)
    row = f"{'wins':>4s}"
    for alg in alg_names:
        if alg == ref:
            val_str = "(ref)"
        else:
            val_str = f"{wins[alg]}/{n_funcs}"
        row += f"  {val_str:>{col_w}s}"
    print(row)
    print("  (wins = funcs where algo is significantly better than ref)")

    # Aggregate stats block
    print()
    print(f"Aggregate statistics of per-function {metric} across "
          f"{len(common)} functions:")
    print(f"{'algo':>30s}  {'sum':>10s}  {'mean':>10s}  {'median':>10s}  "
          f"{'best':>10s}  {'worst':>10s}  {'std':>10s}")
    print("-" * 102)

    def _fmt(v):
        if metric == 'ecdf':
            return f"{v:10.3f}"
        return "0.000e+00" if abs(v) <= COCO_ZERO else f"{v:10.3e}"

    for alg in alg_names:
        vec = np.asarray(per_func_vals[alg], dtype=np.float64)
        print(f"{alg:>30s}  {_fmt(vec.sum())}  {_fmt(vec.mean())}  "
              f"{_fmt(np.median(vec))}  {_fmt(vec.min())}  "
              f"{_fmt(vec.max())}  {_fmt(vec.std())}")


# =========================================================================
# Hits-per-target display (--metric hits)
# =========================================================================

def print_hits_table(base_dir, alg_names, algorithms,
                     ref, taus=CEC_TAUS):
    """Print per-CEC-target hits for each algorithm and function."""
    func_sets = [set(algorithms[a].keys()) for a in alg_names]
    common = sorted(
        set.intersection(*func_sets),
        key=lambda fn: int(fn.replace('f', '')))
    if not common:
        raise ValueError("No common functions across all algorithms")

    n_seeds_max = 0
    for alg in alg_names:
        for fn in common:
            n = len(algorithms[alg][fn]['errors'])
            n_seeds_max = max(n_seeds_max, n)

    print(f"Loaded {len(alg_names)} algorithms from {base_dir}")
    print(f"CEC display-target hits (out of {n_seeds_max} seeds per function)")
    print(f"{base_dir}  metric=hits")
    print()

    # Header
    tau_hdr = ' | '.join([f'{t:>5.0e}' for t in taus])
    alg_w = max(max(len(a) for a in alg_names), 5)
    print(f'{"":>4} {"algo":>{alg_w}} | {tau_hdr}')
    sep = '-' * (4 + 1 + alg_w + 3 + len(tau_hdr))
    print(sep)

    # Per-function block
    totals = {a: [0]*len(taus) for a in alg_names}
    win_counts = {a: [0]*len(taus) for a in alg_names}
    tie_counts = [0]*len(taus)

    for fn in common:
        for alg in alg_names:
            errs = _floor(algorithms[alg][fn]['errors'])
            hits = hits_per_target(errs, taus)
            row = f'{fn:>4} {alg:>{alg_w}} | ' + ' | '.join(
                [f'{h:>5}' for h in hits])
            print(row)
            for i, h in enumerate(hits):
                totals[alg][i] += h

        # Per-target winner among algos for this function
        for i in range(len(taus)):
            vals = {a: 0 for a in alg_names}
            for alg in alg_names:
                errs = _floor(algorithms[alg][fn]['errors'])
                vals[alg] = int(np.sum(errs <= taus[i]))
            mx = max(vals.values())
            winners = [a for a, v in vals.items() if v == mx]
            if len(winners) == 1:
                win_counts[winners[0]][i] += 1
            else:
                tie_counts[i] += 1
        print()

    # Per-target totals
    print(sep)
    print(f"Per-target totals across {len(common)} functions "
          f"(max possible per target: {n_seeds_max * len(common)}):")
    print(sep)
    for alg in alg_names:
        row = f'{"TOT":>4} {alg:>{alg_w}} | ' + ' | '.join(
            [f'{t:>5}' for t in totals[alg]])
        print(row)
    print()

    # Per-target wins
    print(f"Per-target win counts (out of {len(common)} functions):")
    print(sep)
    for alg in alg_names:
        row = f'{"":>4} {alg:>{alg_w}} | ' + ' | '.join(
            [f'{w:>5}' for w in win_counts[alg]])
        print(row)
    row = f'{"":>4} {"ties":>{alg_w}} | ' + ' | '.join(
        [f'{t:>5}' for t in tie_counts])
    print(row)


# =========================================================================
# LaTeX (unchanged from v26)
# =========================================================================

def print_latex_errstats(base_dir, alg_names, algorithms,
                         maxevals=None, caption=None, label=None):
    func_sets = [set(algorithms[a].keys()) for a in alg_names]
    common = sorted(
        set.intersection(*func_sets),
        key=lambda fn: int(fn.replace('f', '')))
    if not common:
        raise ValueError("No common functions across all algorithms")

    stats_tbl = {a: {fn: {} for fn in common} for a in alg_names}
    for fn in common:
        for alg in alg_names:
            errs = _floor(algorithms[alg][fn]['errors'])
            stats_tbl[alg][fn]['best'] = float(np.min(errs))
            stats_tbl[alg][fn]['mean'] = float(np.mean(errs))
            stats_tbl[alg][fn]['std']  = float(np.std(errs))

    TIE_ATOL = 1e-12
    TIE_RTOL = 1e-9

    def _is_tied(a, b):
        return abs(a - b) <= max(TIE_ATOL, TIE_RTOL * max(abs(a), abs(b)))

    def _winner_value(fn, stat):
        return min(stats_tbl[a][fn][stat] for a in alg_names)

    def _fmt(v):
        return f"{v:.3e}"

    if caption is None:
        suite_tag = os.path.basename(os.path.dirname(base_dir.rstrip('/')))
        dim_tag   = os.path.basename(base_dir.rstrip('/'))
        caption = (f"Error statistics (best, mean, and standard "
                   f"deviation) for all algorithms on the "
                   f"{suite_tag.upper()} benchmark suite at "
                   f"{dim_tag}. Each value is computed over 51 "
                   f"independent runs. Boldface denotes the best "
                   f"result for each statistic.")
    if label is None:
        label = f"tab:errstats-{os.path.basename(base_dir.rstrip('/'))}"

    print(r"\begin{table}[htbp]")
    print(r"\centering")
    print(r"\caption{" + caption + r"}")
    print(r"\label{" + label + r"}")
    print(r"\small")
    print(r"\setlength{\tabcolsep}{4pt}")
    cols = "l l" + " r" * len(alg_names)
    print(r"\begin{tabular}{" + cols + "}")
    print(r"\toprule")

    header = "Function & Statistic"
    for alg in alg_names:
        alg_tex = alg.replace('_', r'\_')
        header += f" & {alg_tex}"
    header += r" \\"
    print(header)
    print(r"\midrule")

    sum_stats = {a: {'best': 0.0, 'mean': 0.0, 'std': 0.0}
                 for a in alg_names}
    for i, fn in enumerate(common):
        for stat in ('best', 'mean', 'std'):
            win_val = _winner_value(fn, stat)
            row = fn.upper() if stat == 'best' else ""
            row += f" & {stat}"
            for alg in alg_names:
                v = stats_tbl[alg][fn][stat]
                sum_stats[alg][stat] += v
                cell = _fmt(v)
                if _is_tied(v, win_val):
                    cell = r"\textbf{" + cell + "}"
                row += f" & {cell}"
            row += r" \\"
            print(row)
        if i < len(common) - 1:
            print(r"\addlinespace[2pt]")

    print(r"\midrule")
    for j, stat in enumerate(('best', 'mean', 'std')):
        sum_vals = {a: sum_stats[a][stat] for a in alg_names}
        sum_min = min(sum_vals.values())
        row = r"$\Sigma$" if stat == 'best' else ""
        row += f" & {stat}"
        for alg in alg_names:
            v = sum_vals[alg]
            cell = _fmt(v)
            if _is_tied(v, sum_min):
                cell = r"\textbf{" + cell + "}"
            row += f" & {cell}"
        row += r" \\"
        print(row)

    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


# =========================================================================
# Per-category sums (--by-category)
# =========================================================================

def print_category_table(common, alg_names, metric_table, ref, metric,
                         base_dir):
    """Print per-category (Basic/Hybrid/Composition) sums of the scalar
    metric, using the same algorithms as the per-function table but with
    the reference (MSC-CMA) column first.

    Sanity-checks that Basic+Hybrid+Composition equals the overall SUM row
    from the per-function table; warns to stderr otherwise. For an unknown
    suite (no entry in CATEGORIES) it warns and prints nothing.
    """
    suite = _detect_suite(base_dir)
    mapping = CATEGORIES.get(suite)
    if mapping is None:
        print(f"\nWARNING: --by-category: no category mapping for suite "
              f"'{suite}'; skipping category table. "
              f"Known suites: {', '.join(sorted(CATEGORIES))}.",
              file=sys.stderr)
        return

    higher_better = (metric == 'ecdf')

    # Columns: reference first, then the remaining algorithms in the same
    # relative order as the per-function table.
    col_order = [ref] + [a for a in alg_names if a != ref]

    # Per-function value, floored exactly as print_table's SUM row does, so
    # the category sums and the overall SUM stay consistent.
    def _disp(alg, fn):
        v = metric_table[alg][fn]
        if metric == 'ecdf':
            return v
        return 0.0 if abs(v) <= COCO_ZERO else v

    # Partition the common functions into categories; track any that fall
    # outside every category range.
    cat_funcs = {cat: [] for cat in CATEGORY_ORDER}
    uncategorized = []
    for fn in common:
        idx = int(fn.replace('f', ''))
        for cat in CATEGORY_ORDER:
            if idx in mapping[cat]:
                cat_funcs[cat].append(fn)
                break
        else:
            uncategorized.append(fn)

    cat_sums = {cat: {} for cat in CATEGORY_ORDER}
    total_cat = {a: 0.0 for a in col_order}
    for cat in CATEGORY_ORDER:
        for alg in col_order:
            s = float(np.sum([_disp(alg, fn) for fn in cat_funcs[cat]])) \
                if cat_funcs[cat] else 0.0
            cat_sums[cat][alg] = s
            total_cat[alg] += s

    # Overall SUM over all common functions (== per-function table SUM row).
    total_all = {alg: float(np.sum([_disp(alg, fn) for fn in common]))
                 for alg in col_order}

    def _fmt(v):
        if metric == 'ecdf':
            return f"{v:.3f}"
        v = 0.0 if abs(v) <= COCO_ZERO else v
        return "0.000e+00" if v == 0.0 else f"{v:.3e}"

    print()
    print(f"By-category sums  (suite={suite}, metric={metric}, "
          f"{'higher is better' if higher_better else 'lower is better'})")

    col_w = max(max(len(a) for a in col_order), 15)
    header = f"{'category':>12s}"
    for alg in col_order:
        header += f"  {alg:>{col_w}s}"
    print(header)
    print("-" * len(header))

    for cat in CATEGORY_ORDER:
        row = f"{cat:>12s}"
        for alg in col_order:
            row += f"  {_fmt(cat_sums[cat][alg]):>{col_w}s}"
        row += f"   (n={len(cat_funcs[cat])})"
        print(row)

    print("-" * len(header))
    row = f"{'SUM':>12s}"
    for alg in col_order:
        row += f"  {_fmt(total_cat[alg]):>{col_w}s}"
    print(row)

    # Sanity check: the three category sums must reconstitute the SUM row.
    mismatched = [(alg, total_cat[alg], total_all[alg]) for alg in col_order
                  if not np.isclose(total_cat[alg], total_all[alg],
                                    rtol=1e-9, atol=1e-12)]
    if uncategorized or mismatched:
        print("\nWARNING: --by-category: Basic+Hybrid+Composition does not "
              "match the overall SUM row.", file=sys.stderr)
        if uncategorized:
            print(f"  Functions outside every {suite} category range: "
                  f"{', '.join(uncategorized)}", file=sys.stderr)
        for alg, tc, ta in mismatched:
            print(f"  {alg}: categories sum to {tc:.6e} but SUM is {ta:.6e}",
                  file=sys.stderr)


# =========================================================================
# Consolidated all-metrics category table (--all-metrics)
# =========================================================================

# Scalar metrics iterated by --all-metrics (excludes 'hits', which is not a
# scalar). 'ecdf' is higher-is-better; the rest are lower-is-better.
ALL_METRICS = ['mean', 'median', 'best', 'worst', 'std', 'ecdf']


def _fmt_metric(v, metric):
    """Format a per-category scalar consistently with print_table's SUM row:
    ecdf as a [0,1] fraction, error metrics as %.3e with a COCO_ZERO floor."""
    if metric == 'ecdf':
        return f"{v:.3f}"
    v = 0.0 if abs(v) <= COCO_ZERO else v
    return "0.000e+00" if v == 0.0 else f"{v:.3e}"


def print_all_metrics_category_table(base_dir, ref, correction, alpha,
                                     maxevals):
    """Consolidated category x metric x algorithm table.

    Runs every scalar metric in ALL_METRICS and prints one table whose rows
    are (category, metric) pairs and whose columns are algorithms (reference
    first), instead of six separate per-metric runs. The per-category sums
    match what each individual --metric ... --by-category run would print.
    """
    suite = _detect_suite(base_dir)
    mapping = CATEGORIES.get(suite)
    if mapping is None:
        print(f"WARNING: --all-metrics: no category mapping for suite "
              f"'{suite}'; cannot build consolidated table. "
              f"Known suites: {', '.join(sorted(CATEGORIES))}.",
              file=sys.stderr)
        return

    # Compute the per-metric scalar tables once. correction/alpha only affect
    # the significance table (unused here), but we thread them through so the
    # underlying run_comparison call is identical to the per-metric path.
    metric_tables = {}
    common = None
    alg_names = None
    for metric in ALL_METRICS:
        c, a, mt, _ = run_comparison(base_dir, ref, metric, correction,
                                     alpha, maxevals)
        metric_tables[metric] = mt
        common, alg_names = c, a

    col_order = [ref] + [a for a in alg_names if a != ref]

    # Partition the common functions into categories.
    cat_funcs = {cat: [] for cat in CATEGORY_ORDER}
    uncategorized = []
    for fn in common:
        idx = int(fn.replace('f', ''))
        for cat in CATEGORY_ORDER:
            if idx in mapping[cat]:
                cat_funcs[cat].append(fn)
                break
        else:
            uncategorized.append(fn)

    def _disp(metric, alg, fn):
        v = metric_tables[metric][alg][fn]
        if metric == 'ecdf':
            return v
        return 0.0 if abs(v) <= COCO_ZERO else v

    def _cat_sum(metric, alg, fns):
        return (float(np.sum([_disp(metric, alg, fn) for fn in fns]))
                if fns else 0.0)

    print()
    print(f"By-category sums — all metrics  (suite={suite})")
    print("  (ecdf: higher is better; all others: lower is better)")

    col_w = max(max(len(a) for a in col_order), 15)
    header = f"{'category':>12s}  {'metric':>7s}"
    for alg in col_order:
        header += f"  {alg:>{col_w}s}"
    print(header)
    print("-" * len(header))

    # One block per category; each metric is a row.
    for cat in CATEGORY_ORDER:
        for metric in ALL_METRICS:
            row = f"{cat:>12s}  {metric:>7s}"
            for alg in col_order:
                v = _cat_sum(metric, alg, cat_funcs[cat])
                row += f"  {_fmt_metric(v, metric):>{col_w}s}"
            if metric == ALL_METRICS[0]:
                row += f"   (n={len(cat_funcs[cat])})"
            print(row)
        print()

    # Overall SUM block (over all common functions).
    print("-" * len(header))
    for metric in ALL_METRICS:
        row = f"{'SUM':>12s}  {metric:>7s}"
        for alg in col_order:
            v = _cat_sum(metric, alg, common)
            row += f"  {_fmt_metric(v, metric):>{col_w}s}"
        print(row)

    if uncategorized:
        print(f"\nWARNING: --all-metrics: functions outside every {suite} "
              f"category range: {', '.join(uncategorized)}", file=sys.stderr)


# =========================================================================
# CLI
# =========================================================================

def main():
    ap = argparse.ArgumentParser(
        description='Multi-algorithm comparison (extended). New metrics: '
                    'ecdf (COCO area), hits (CEC per-target counts).')
    ap.add_argument('--base-dir', required=True)
    ap.add_argument('--ref', required=True)
    ap.add_argument('--metric',
                    choices=['median', 'mean', 'best', 'worst', 'std',
                             'ecdf', 'hits'],
                    default='median')
    ap.add_argument('--correction',
                    choices=['bh', 'bonferroni', 'none'], default='bh')
    ap.add_argument('--alpha', type=float, default=0.05)
    ap.add_argument('--maxevals', type=int, default=None)
    ap.add_argument('--latex', action='store_true')
    ap.add_argument('--caption', type=str, default=None)
    ap.add_argument('--label', type=str, default=None)
    ap.add_argument('--by-category', action='store_true',
                    help='After the per-function table, also print sums '
                         'grouped by {Basic, Hybrid, Composition}.')
    ap.add_argument('--quiet', '--by-category-only', action='store_true',
                    dest='quiet',
                    help='With --by-category, suppress the per-function table '
                         'and the aggregate-statistics block; print only the '
                         'By-category sums table.')
    ap.add_argument('--all-metrics', action='store_true',
                    help='Iterate over [mean, median, best, worst, std, ecdf] '
                         'and print one consolidated category x metric x '
                         'algorithm table instead of six separate runs. '
                         'Overrides --metric.')
    args = ap.parse_args()

    if args.all_metrics:
        # Consolidated path: iterate all scalar metrics, one category table.
        # Overrides --metric (incl. 'hits') and --by-category.
        print_all_metrics_category_table(
            args.base_dir, args.ref, args.correction, args.alpha,
            args.maxevals)

        if args.latex:
            print()
            algorithms = discover_algorithms(args.base_dir, args.maxevals)
            alg_names = sorted(algorithms.keys())
            print_latex_errstats(args.base_dir, alg_names, algorithms,
                                 maxevals=args.maxevals,
                                 caption=args.caption, label=args.label)
        return

    if args.metric == 'hits':
        # Special path: no Wilcoxon, custom display
        algorithms = discover_algorithms(args.base_dir, args.maxevals)
        if not algorithms:
            raise FileNotFoundError(
                f"No algorithm directories found in {args.base_dir}")
        if args.ref not in algorithms:
            raise ValueError(
                f"Reference '{args.ref}' not found. "
                f"Available: {', '.join(sorted(algorithms.keys()))}")
        alg_names = sorted(algorithms.keys())
        print_hits_table(args.base_dir, alg_names, algorithms, args.ref)

        if args.by_category:
            print("\nWARNING: --by-category is not supported for "
                  "--metric hits; ignoring.", file=sys.stderr)

        if args.latex:
            print()
            print_latex_errstats(args.base_dir, alg_names, algorithms,
                                 maxevals=args.maxevals,
                                 caption=args.caption, label=args.label)
        return

    # Scalar metrics (including 'ecdf')
    common, alg_names, metric_table, sig_table = \
        run_comparison(args.base_dir, args.ref, args.metric,
                       args.correction, args.alpha, args.maxevals)

    quiet = args.quiet and args.by_category
    if args.quiet and not args.by_category:
        print("WARNING: --quiet/--by-category-only has no effect without "
              "--by-category; printing the full table.", file=sys.stderr)

    if not quiet:
        print_table(common, alg_names, metric_table, sig_table,
                    args.ref, args.metric,
                    args.base_dir, args.correction, args.alpha)

    if args.by_category:
        print_category_table(common, alg_names, metric_table,
                             args.ref, args.metric, args.base_dir)

    if args.latex:
        print()
        algorithms = discover_algorithms(args.base_dir, args.maxevals)
        print_latex_errstats(args.base_dir, alg_names, algorithms,
                             maxevals=args.maxevals,
                             caption=args.caption,
                             label=args.label)


if __name__ == '__main__':
    main()
