"""
fig_budget_slopes.py — per-function budget-scaling slope chart.

For one (suite, dim) and two REAL budgets from the experiments tree,
plot the per-function median error (log y) at budget_lo vs budget_hi,
one panel per algorithm.  Functions are classified by what happens
between the two budgets:

    escaped   (red)   above 1e-8 at lo, below 1e-8 at hi
    improved  (blue)  above 1e-8 at both, dropped by >= --drop-factor
    stuck     (light) above 1e-8 at both, dropped by <  --drop-factor
    at-floor  (grey)  already below 1e-8 at lo

Every composition function is drawn — including the stuck ones — so
the figure cannot overstate the escape story.

Usage (from project root):
    python analysis/fig_budget_slopes.py \
        --suite cec2017 --dim 10 --b-lo 100000 --b-hi 1000000 \
        --algos MSC-CMA,BIPOP-CMA --func-class composition \
        --out figures/slopes_cec2017_d10.png
"""

import argparse
import os
import pickle
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summary_grid_clean import FUNC_CLASSES, DEPRECATED_FUNCS  # noqa: E402

FLOOR = 1e-8          # accuracy floor (same convention as summary script)
DISP_CLIP = 1e-12     # display clip for exact zeros on log axis

C_ESCAPED = '#c8405a'
C_IMPROVED = '#3b6ea5'
C_STUCK = '#b9b9b9'
C_FLOOR = '#9aa5a0'


def _fmt_budget(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        return f'{v:g}M'
    return f'{n // 1000}k'


def load_median(root, suite, dim, algo, budget, fnum):
    path = os.path.join(root, suite, f'd{dim}', algo,
                        f'maxevals_{budget}', f'f{fnum}.pkl')
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        d = pickle.load(f)
    errs = np.asarray(d['errors'], dtype=float)
    errs = np.where(np.abs(errs) <= FLOOR, 0.0, errs)
    return float(np.median(errs))


def classify(lo, hi, drop_factor):
    if lo <= FLOOR:
        return 'floor'
    if hi <= FLOOR:
        return 'escaped'
    if lo / max(hi, DISP_CLIP) >= drop_factor:
        return 'improved'
    return 'stuck'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='experiments')
    p.add_argument('--suite', required=True)
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--b-lo', type=int, required=True)
    p.add_argument('--b-hi', type=int, required=True)
    p.add_argument('--algos', default='MSC-CMA,BIPOP-CMA',
                   help='Comma-separated algo directory names, one panel each')
    p.add_argument('--func-class', default='composition',
                   choices=['basic', 'hybrid', 'composition'])
    p.add_argument('--official', type=int, default=0,
                   help='Official budget for the multiplier annotation '
                        '(default: b-lo).')
    p.add_argument('--drop-factor', type=float, default=10.0,
                   help='Min lo/hi ratio to count as "improved" (default 10)')
    p.add_argument('--add-best-other', action='store_true',
                   help='Append a panel: the algo (not already in --algos) '
                        'with the lowest summed median at b-hi over the '
                        'selected function class.')
    p.add_argument('--out', default='')
    args = p.parse_args()

    funcs = sorted(FUNC_CLASSES[args.suite][args.func_class])
    deprecated = {int(f[1:]) for f in DEPRECATED_FUNCS.get(args.suite, set())}
    funcs = [f for f in funcs if f not in deprecated]

    algos = [a.strip() for a in args.algos.split(',') if a.strip()]
    official = args.official or args.b_lo

    best_other = None
    if args.add_best_other:
        base = os.path.join(args.root, args.suite, f'd{args.dim}')
        candidates = sorted(a for a in os.listdir(base)
                            if a not in algos
                            and os.path.isdir(os.path.join(base, a)))
        scores = {}
        for cand in candidates:
            meds = [load_median(args.root, args.suite, args.dim,
                                cand, args.b_hi, f) for f in funcs]
            if any(m is None for m in meds):
                continue            # incomplete at b-hi -> not eligible
            scores[cand] = sum(meds)
        if scores:
            best_other = min(scores, key=scores.get)
            algos.append(best_other)
            ranked = ', '.join(f'{k}={v:.2f}' for k, v in
                               sorted(scores.items(), key=lambda x: x[1]))
            print(f'best-other panel: {best_other} ({ranked})')
        else:
            print('!! --add-best-other: no complete candidate found')

    fig, axes = plt.subplots(1, len(algos),
                             figsize=(7.0 * len(algos), 6.2),
                             sharey=True)
    if len(algos) == 1:
        axes = [axes]

    missing = []
    for ax, algo in zip(axes, algos):
        n_escaped = 0
        for fnum in funcs:
            lo = load_median(args.root, args.suite, args.dim,
                             algo, args.b_lo, fnum)
            hi = load_median(args.root, args.suite, args.dim,
                             algo, args.b_hi, fnum)
            if lo is None or hi is None:
                missing.append((algo, fnum))
                continue
            kind = classify(lo, hi, args.drop_factor)
            y = [max(lo, DISP_CLIP), max(hi, DISP_CLIP)]
            color = {'escaped': C_ESCAPED, 'improved': C_IMPROVED,
                     'stuck': C_STUCK, 'floor': C_FLOOR}[kind]
            lw = {'escaped': 2.6, 'improved': 2.0,
                  'stuck': 1.4, 'floor': 1.0}[kind]
            z = {'escaped': 5, 'improved': 4, 'stuck': 3, 'floor': 2}[kind]
            ax.plot([0, 1], y, '-o', color=color, lw=lw, ms=5, zorder=z)
            if kind in ('escaped', 'improved'):
                ax.annotate(f'f{fnum}', (1, y[1]),
                            xytext=(8, 0), textcoords='offset points',
                            va='center', fontsize=10, color=color,
                            fontweight='bold')
                n_escaped += kind == 'escaped'

        ax.set_yscale('log')
        ax.axhline(FLOOR, color='seagreen', ls='--', lw=0.8, alpha=0.7)
        ax.axhspan(DISP_CLIP / 3, FLOOR, color='seagreen', alpha=0.07)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(
            [f'{_fmt_budget(args.b_lo)}\n({args.b_lo / official:g}x)',
             f'{_fmt_budget(args.b_hi)}\n({args.b_hi / official:g}x)'],
            fontsize=11)
        ax.set_xlim(-0.15, 1.30)
        title = algo + (' (best other)' if algo == best_other else '')
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.25)

    axes[0].set_ylabel('median error  (log)', fontsize=11)
    axes[0].text(0.02, FLOOR * 2.2, f'target reached (err < {FLOOR:g})',
                 color='seagreen', fontsize=9, transform=axes[0].transData)

    handles = [
        plt.Line2D([], [], color=C_ESCAPED, lw=2.6, marker='o',
                   label='reaches the 1e-8 floor at high budget'),
        plt.Line2D([], [], color=C_IMPROVED, lw=2.0, marker='o',
                   label=f'drops >= {args.drop_factor:g}x (still above floor)'),
        plt.Line2D([], [], color=C_STUCK, lw=1.4, marker='o',
                   label='plateau (little change)'),
        plt.Line2D([], [], color=C_FLOOR, lw=1.0, marker='o',
                   label='already at floor at low budget'),
    ]
    axes[0].legend(handles=handles, loc='upper right', fontsize=9,
                   framealpha=0.9)

    fig.suptitle(f'{args.suite.upper()} | D={args.dim} | '
                 f'{args.func_class} functions | per-function median, '
                 f'{_fmt_budget(args.b_lo)} vs {_fmt_budget(args.b_hi)}',
                 fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    out = args.out or (f'figures/slopes_{args.suite}_d{args.dim}_'
                       f'{args.func_class}.png')
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    fig.savefig(out, dpi=160)
    print(f'-> {out}')
    if missing:
        print(f'!! missing pkls (skipped): {missing}')


if __name__ == '__main__':
    main()
