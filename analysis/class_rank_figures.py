#!/usr/bin/env python3
"""Two publication figures from the experiments grid, restricted to the
OFFICIAL CEC budgets (one cell per suite x dim), split by function class.

Figure 1 (class_ranks.png)    : mean Friedman-style rank per algorithm,
                                one panel per class (basic / hybrid /
                                composition) + ALL. Rank is computed PER
                                FUNCTION across algorithms (ties = average
                                rank), then averaged within the class over
                                all standard cells. Lower = better.
                                Scale-free, so cells with wildly different
                                error magnitudes are comparable.

Figure 2 (class_heatmap.png)  : where the profile holds. One panel per
                                class; rows = suite/dim cells, columns =
                                algorithms, color + annotation = mean rank
                                inside that cell.

Within every cell, only the COMMON function set (functions present for all
plotted algorithms) is used, so partially-populated cells cannot distort
the ranks. Cells where an algorithm is missing entirely are skipped for
Figure 1 only if --strict, otherwise the algorithm is ranked among those
present (and the panel notes n).

Usage
-----
    python analysis/class_rank_figures.py
    python analysis/class_rank_figures.py --metric median
    python analysis/class_rank_figures.py --metric fbtc
    python analysis/class_rank_figures.py --root experiments --out figs/
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summary_grid_clean import aggregate, FUNC_CLASSES  # noqa: E402

# =========================================================================
# Official CEC MaxFES per (suite, dim) — the competition-defined budgets.
# CEC2014 / CEC2017 : 10^4 * D
# CEC2020           : 50K (D5), 1M (D10), 3M (D15), 10M (D20)
# CEC2022           : 200K (D10), 1M (D20)
# =========================================================================

STANDARD_BUDGET = {
    ('cec2014', 10):    100_000,
    ('cec2014', 30):    300_000,
    ('cec2014', 50):    500_000,
    ('cec2014', 100): 1_000_000,
    ('cec2017',  2):     20_000,
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

CLASSES = ['basic', 'hybrid', 'composition']
DISPLAY = {
    'MSC-CMA':     'MSC-CMA-ES',
    'BIPOP-CMA':   'BIPOP-CMA-ES',
    'LSRTDE':      'L-SRTDE',
    'NLSHADE-RSP': 'NL-SHADE-RSP',
}
CLASS_LABEL = {'basic': 'USM', 'hybrid': 'Hybrid',
               'composition': 'Composition', 'ALL': 'All functions'}

ALGO_ORDER = ['MSC-CMA', 'BIPOP-CMA',
              'ARRDE', 'j2020', 'jSO', 'LSRTDE', 'NLSHADE-RSP']

MSC_COLOR = '#c0392b'
OTHER_COLOR = '#34495e'


def _avg_ranks(values, higher_better=False):
    """Average ranks (1 = best) with ties = mean rank.

    values : 1-D array, NaN not allowed here.
    """
    v = np.asarray(values, dtype=np.float64)
    if higher_better:
        v = -v
    order = np.argsort(v, kind='mergesort')
    ranks = np.empty(len(v), dtype=np.float64)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def collect_ranks(grid, algos, metric, strict=False):
    """Per-function ranks restricted to standard cells & common functions.

    Returns
    -------
    per_class : {class_name: {algo: [rank, rank, ...]}}   ('ALL' included)
    per_cell  : {(suite, dim): {class_name: {algo: mean_rank}}}
    skipped   : list of human-readable notes
    """
    higher_better = (metric == 'fbtc')
    per_class = {c: {a: [] for a in algos} for c in CLASSES + ['ALL']}
    per_cell = {}
    skipped = []

    for (suite, dim), budget in sorted(STANDARD_BUDGET.items()):
        cell = grid.get((suite, dim, budget))
        if not cell:
            continue
        present = [a for a in algos if a in cell]
        if len(present) < 2:
            skipped.append(f"{suite}/d{dim}/{budget}: <2 algorithms, skipped")
            continue
        missing = [a for a in algos if a not in cell]
        if missing:
            if strict:
                skipped.append(f"{suite}/d{dim}/{budget}: missing "
                               f"{','.join(missing)} — SKIPPED (--strict)")
                continue
            skipped.append(f"{suite}/d{dim}/{budget}: missing "
                           f"{','.join(missing)} (ranked among "
                           f"{len(present)} — NOT comparable to 7-algo "
                           f"cells, consider --strict)")

        # Common function set across the plotted algorithms.
        common = set.intersection(*(set(cell[a]) for a in present))
        if not common:
            skipped.append(f"{suite}/d{dim}/{budget}: no common functions")
            continue
        dropped = {f for a in present for f in cell[a]} - common
        if dropped:
            skipped.append(f"{suite}/d{dim}/{budget}: non-common funcs "
                           f"dropped: {','.join(sorted(dropped))}")

        classes = FUNC_CLASSES.get(suite, {})
        cell_acc = {c: {a: [] for a in present} for c in CLASSES + ['ALL']}

        for fname in sorted(common):
            try:
                fnum = int(fname.lstrip('f'))
            except ValueError:
                continue
            fclass = next((c for c in CLASSES
                           if fnum in classes.get(c, ())), None)
            vals = np.array([cell[a][fname][metric] for a in present])
            ranks = _avg_ranks(vals, higher_better=higher_better)
            for a, r in zip(present, ranks):
                cell_acc['ALL'][a].append(r)
                per_class['ALL'][a].append(r)
                if fclass is not None:
                    cell_acc[fclass][a].append(r)
                    per_class[fclass][a].append(r)

        per_cell[(suite, dim)] = {
            c: {a: float(np.mean(rs)) for a, rs in cell_acc[c].items() if rs}
            for c in CLASSES + ['ALL']
        }
    return per_class, per_cell, skipped


def fig_class_ranks(per_class, algos, metric, n_algos, path):
    """Figure 1: mean rank per class, dot plot, one panel per class."""
    panels = CLASSES + ['ALL']
    fig, axes = plt.subplots(1, len(panels), figsize=(13, 3.6),
                             sharey=True)
    order = algos  # keep canonical order top-to-bottom
    ypos = np.arange(len(order))[::-1]

    for ax, cname in zip(axes, panels):
        means, counts = [], []
        for a in order:
            rs = per_class[cname][a]
            means.append(np.mean(rs) if rs else np.nan)
            counts.append(len(rs))
        means = np.array(means)
        colors = [MSC_COLOR if a == 'MSC-CMA' else OTHER_COLOR
                  for a in order]
        ax.hlines(ypos, 1, means, color=colors, lw=1.2, alpha=0.6)
        ax.scatter(means, ypos, c=colors, s=45, zorder=3)
        nz = [c for c in counts if c > 0]
        if nz and min(nz) != max(nz):
            n_lbl = f"n={min(nz)}\u2013{max(nz)} per algo!"
        else:
            n_lbl = f"n={max(counts) if counts else 0}"
        ax.set_title(f"{CLASS_LABEL[cname]}  ({n_lbl})", fontsize=10)
        ax.set_xlim(0.5, n_algos + 0.5)
        ax.set_xlabel('mean rank (1 = best)', fontsize=9)
        ax.grid(axis='x', ls=':', alpha=0.5)
        ax.set_yticks(ypos)
        ax.set_yticklabels([DISPLAY.get(a, a) for a in order], fontsize=9)
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)

    fig.suptitle(f"Per-function mean rank by CEC function class "
                 f"(official budgets, metric: {metric})", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fig_heatmap(per_cell, algos, metric, n_algos, path):
    """Figure 2: per-cell mean rank heatmap, one panel per class."""
    cells = sorted(per_cell.keys())
    labels = [f"{s} D{d}" for s, d in cells]
    fig, axes = plt.subplots(1, len(CLASSES),
                             figsize=(11.5, 0.42 * len(cells) + 1.8),
                             sharey=True)

    for ax, cname in zip(axes, CLASSES):
        M = np.full((len(cells), len(algos)), np.nan)
        for i, ck in enumerate(cells):
            row = per_cell[ck].get(cname, {})
            for j, a in enumerate(algos):
                if a in row:
                    M[i, j] = row[a]
        im = ax.imshow(M, cmap='RdYlGn_r', vmin=1, vmax=n_algos,
                       aspect='auto')
        for i in range(len(cells)):
            for j in range(len(algos)):
                if not np.isnan(M[i, j]):
                    ax.text(j, i, f"{M[i, j]:.1f}", ha='center',
                            va='center', fontsize=7)
        ax.set_title(CLASS_LABEL[cname], fontsize=10)
        ax.set_xticks(range(len(algos)))
        ax.set_xticklabels([DISPLAY.get(a, a) for a in algos],
                           rotation=45, ha='right', fontsize=8)
        ax.set_yticks(range(len(cells)))
        ax.set_yticklabels(labels, fontsize=8)

    cbar = fig.colorbar(im, ax=axes, fraction=0.02, pad=0.01)
    cbar.set_label('mean rank (1 = best)', fontsize=9)
    fig.suptitle(f"Mean rank inside every standard cell "
                 f"(metric: {metric})", fontsize=11)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='experiments')
    p.add_argument('--metric', default='mean',
                   choices=['mean', 'median', 'best', 'worst', 'fbtc'])
    p.add_argument('--out', default='figs')
    p.add_argument('--strict', action='store_true',
                   help='Use only cells where ALL requested algorithms '
                        'are present (ranks always among the same k).')
    p.add_argument('--algos', default=','.join(ALGO_ORDER),
                   help='Comma-separated canonical algo names to plot.')
    args = p.parse_args()

    algos = [a.strip() for a in args.algos.split(',') if a.strip()]
    grid, _, _ = aggregate(args.root)
    if not grid:
        sys.exit(f"No experiments found under {args.root}/")

    per_class, per_cell, skipped = collect_ranks(grid, algos, args.metric,
                                                  strict=args.strict)
    if not per_cell:
        sys.exit("No standard-budget cells found.")

    os.makedirs(args.out, exist_ok=True)
    f1 = os.path.join(args.out, f"class_ranks_{args.metric}.png")
    f2 = os.path.join(args.out, f"class_heatmap_{args.metric}.png")
    fig_class_ranks(per_class, algos, args.metric, len(algos), f1)
    fig_heatmap(per_cell, algos, args.metric, len(algos), f2)

    print(f"Standard cells used: {len(per_cell)}")
    for (s, d) in sorted(per_cell):
        print(f"  {s} d{d} @ {STANDARD_BUDGET[(s, d)]}")
    if skipped:
        print("Notes:")
        for n in skipped:
            print(f"  - {n}")
    print(f"Figure 1 -> {f1}")
    print(f"Figure 2 -> {f2}")


if __name__ == '__main__':
    main()
