#!/usr/bin/env python3
"""Per-function budget-slope figure: low budget vs high budget, one panel
per algorithm, lines coloured by what the extra budget achieved.

For a chosen (suite, dim, function-class) it reads the per-function metric
at a LOW budget and a HIGH budget from the experiments grid and draws, for
each algorithm, one line segment per function between the two budgets on a
log y-axis. Lines are categorised exactly as in the published figure:

    red    : reaches the 1e-8 floor at the high budget
    blue   : drops >= 10x but stays above the floor
    grey   : plateau (less than 10x change), still above the floor
    d.grey : already at the floor at the low budget

By default three panels are shown: MSC-CMA, BIPOP-CMA, and the BEST OTHER
algorithm (lowest summed metric on the class at the high budget). Only the
function set common to all plotted algorithms at BOTH budgets is used, so
the panels are strictly comparable.

Usage
-----
    # the "good" case (the composition figure):
    python analysis/budget_slopes.py --suite cec2017 --dim 10 \
        --func-class composition --low 100000 --high 1000000

    # an "opposite" case (hybrid: MSC drops but stays behind the leaders):
    python analysis/budget_slopes.py --suite cec2017 --dim 10 \
        --func-class hybrid --low 100000 --high 1000000

    # an "opposite" case at D=30 (budget reduces error, ordering unchanged):
    python analysis/budget_slopes.py --suite cec2014 --dim 30 \
        --func-class composition --low 300000 --high 1000000

    # force the third panel to a specific algorithm instead of "best other":
    python analysis/budget_slopes.py --suite cec2017 --dim 10 \
        --func-class composition --low 100000 --high 1000000 --other LSRTDE
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

ALGO_ORDER = ['MSC-CMA', 'BIPOP-CMA',
              'ARRDE', 'j2020', 'jSO', 'LSRTDE', 'NLSHADE-RSP']

# Categorisation colours (match the published figure legend).
C_REACH = '#c0392b'   # reaches the 1e-8 floor at high budget
C_DROP = '#2980b9'    # drops >= 10x, still above floor
C_FLAT = '#bdc3c7'    # plateau (little change)
C_ATFLOOR = '#7f8c8d'  # already at floor at low budget

FLOOR = 1e-8          # "target reached" threshold
PLOT_FLOOR = 1e-12    # clamp for the log axis (0 / sub-floor values)
DROP_FACTOR = 10.0    # "drops >= 10x"


def _clamp(v):
    """Clamp a (possibly zero/negative-rounding) error to the plot floor."""
    return max(float(v), PLOT_FLOOR)


def _category(lo, hi):
    """Return (colour, label-key) for a low->high pair of raw errors."""
    if lo <= FLOOR:
        return C_ATFLOOR, 'atfloor'
    if hi <= FLOOR:
        return C_REACH, 'reach'
    if lo / max(hi, PLOT_FLOOR) >= DROP_FACTOR:
        return C_DROP, 'drop'
    return C_FLAT, 'flat'


def _class_funcs(suite, fclass):
    """Sorted f-names for a class, or all funcs if fclass == 'all'."""
    classes = FUNC_CLASSES.get(suite, {})
    if fclass == 'all':
        nums = sorted({n for s in classes.values() for n in s})
    else:
        nums = sorted(classes.get(fclass, ()))
    return [f'f{n}' for n in nums]


def _common(cell_lo, cell_hi, algos, want):
    """Functions present for every plotted algo at BOTH budgets."""
    sets = []
    for a in algos:
        sets.append(set(cell_lo.get(a, {})))
        sets.append(set(cell_hi.get(a, {})))
    have = set.intersection(*sets) if sets else set()
    return [f for f in want if f in have]


def _best_other(cell_hi, funcs, metric, exclude):
    """Algo (not in `exclude`) with the lowest summed metric on `funcs`."""
    best, best_sum = None, np.inf
    for a in ALGO_ORDER:
        if a in exclude or a not in cell_hi:
            continue
        try:
            s = sum(cell_hi[a][f][metric] for f in funcs)
        except KeyError:
            continue
        if s < best_sum:
            best, best_sum = a, s
    return best


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='experiments')
    p.add_argument('--suite', required=True)
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--low', type=int, required=True, help='low budget (FEs)')
    p.add_argument('--high', type=int, required=True, help='high budget (FEs)')
    p.add_argument('--metric', default='median',
                   choices=['mean', 'median', 'best', 'worst'])
    p.add_argument('--func-class', default='composition',
                   choices=['basic', 'hybrid', 'composition', 'all'])
    p.add_argument('--other', default=None,
                   help='force the third panel algo (default: best other)')
    p.add_argument('--out', default='figs')
    args = p.parse_args()

    grid, _, _ = aggregate(args.root)
    if not grid:
        sys.exit(f"No experiments found under {args.root}/")

    cell_lo = grid.get((args.suite, args.dim, args.low))
    cell_hi = grid.get((args.suite, args.dim, args.high))
    if not cell_lo or not cell_hi:
        have = sorted({b for (s, d, b) in grid
                       if s == args.suite and d == args.dim})
        sys.exit(f"Missing budget cell for {args.suite} d{args.dim}. "
                 f"Budgets present: {have}")

    panels = ['MSC-CMA', 'BIPOP-CMA']
    third = args.other
    want = _class_funcs(args.suite, args.func_class)
    if third is None:
        third = _best_other(cell_hi, want, args.metric, exclude=set(panels))
    if third is None:
        sys.exit("No third (other) algorithm available in the high cell.")
    panels.append(third)

    funcs = _common(cell_lo, cell_hi, panels, want)
    if not funcs:
        sys.exit(f"No common {args.func_class} functions across "
                 f"{panels} at both budgets.")

    def _blab(b):
        return (f"{b // 1_000_000}M" if b >= 1_000_000
                else f"{b // 1000}k")

    fig, axes = plt.subplots(1, len(panels), figsize=(15, 5),
                             sharey=True)
    if len(panels) == 1:
        axes = [axes]
    seen = {}  # legend-key -> handle

    for ax, algo in zip(axes, panels):
        lo_d, hi_d = cell_lo[algo], cell_hi[algo]
        for f in funcs:
            lo = lo_d[f][args.metric]
            hi = hi_d[f][args.metric]
            colour, key = _category(lo, hi)
            ln, = ax.plot([0, 1], [_clamp(lo), _clamp(hi)],
                          color=colour, lw=2.2, marker='o', ms=4,
                          alpha=0.9, zorder=3 if key == 'reach' else 2)
            seen.setdefault(key, ln)
            if key == 'reach':
                ax.annotate(f, (1, _clamp(hi)), fontsize=8,
                            color=colour, weight='bold',
                            xytext=(4, 0), textcoords='offset points',
                            va='center')

        title = algo if algo not in ('ARRDE', 'j2020', 'jSO',
                                      'LSRTDE', 'NLSHADE-RSP') \
            else f"{algo} (best other)"
        ax.set_title(title, fontsize=12, weight='bold')
        ax.set_yscale('log')
        ax.set_ylim(PLOT_FLOOR * 0.3, None)
        ax.set_xlim(-0.15, 1.25)
        ax.set_xticks([0, 1])
        ax.set_xticklabels([f"{_blab(args.low)}\n(1x)",
                            f"{_blab(args.high)}\n({args.high // args.low}x)"])
        ax.axhspan(PLOT_FLOOR * 0.3, FLOOR, color='#2ecc71', alpha=0.07)
        ax.axhline(FLOOR, color='#27ae60', ls='--', lw=1, alpha=0.7)
        ax.grid(axis='y', ls=':', alpha=0.4)
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)

    axes[0].set_ylabel(f"{args.metric} error  (log)", fontsize=11)
    axes[0].text(0.02, FLOOR * 1.6, 'target reached (err < 1e-08)',
                 fontsize=9, color='#27ae60')

    legend_text = {
        'reach': 'reaches the 1e-8 floor at high budget',
        'drop': 'drops >= 10x (still above floor)',
        'flat': 'plateau (little change)',
        'atfloor': 'already at floor at low budget',
    }
    order = ['reach', 'drop', 'flat', 'atfloor']
    handles = [seen[k] for k in order if k in seen]
    labels = [legend_text[k] for k in order if k in seen]
    if handles:
        axes[0].legend(handles, labels, fontsize=8, loc='upper right',
                       framealpha=0.9)

    cl = {'all': 'all'}.get(args.func_class, args.func_class)
    fig.suptitle(f"{args.suite.upper()} | D={args.dim} | {cl} functions | "
                 f"per-function {args.metric}, "
                 f"{_blab(args.low)} vs {_blab(args.high)}",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    os.makedirs(args.out, exist_ok=True)
    fname = (f"slopes_{args.suite}_d{args.dim}_{args.func_class}_"
             f"{args.metric}.png")
    path = os.path.join(args.out, fname)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)

    print(f"panels      : {', '.join(panels)}")
    print(f"functions   : {len(funcs)} common ({', '.join(funcs)})")
    print(f"budgets     : {args.low} -> {args.high} "
          f"({args.high // args.low}x)")
    print(f"figure      -> {path}")


if __name__ == '__main__':
    main()
