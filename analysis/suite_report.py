#!/usr/bin/env python3
"""analysis/suite_report.py — one-shot per-SUITE report (figures + README).

For one CEC suite this builds, in the same fixed style as cell_report.py,
a cross-dimension summary: for each requested dimension a row of three
ranking figures and (where >=2 budgets exist) a row of budget-scaling
figures, followed by the per-metric summary tables.

Rules (agreed):
  * Ranking axes per (dim, class): worst-SUM, median-SUM, <cov>, best-SUM,
    where <cov> = FBTC if ANY algorithm has FBTC>0 for that (dim,class) at
    the official budget, else mean-SUM.
  * Budget axis: auto-discovered from the directories — the budgets common
    to ALL plotted algorithms, restricted (per class) to budgets where every
    algorithm has the WHOLE class present.
  * Budget metric per class: FBTC (monotone envelope) if any algorithm has
    FBTC>0 at any budget; else median-SUM (lower-better, no envelope).
  * Legend: matplotlib loc='best' (internal), consistent with cell_report.
  * Dimensions are passed explicitly via --dims (controls e.g. D=2 inclusion).
  * Reads *.pkl; run where the data lives.

Usage
-----
    python analysis/suite_report.py --suite cec2017 --dims 10,30 \
        --official 10,100000 --official 30,300000

If --official is omitted for a dim, suite_default_maxevals is used.
"""

import argparse
import datetime
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summary_grid_clean import (  # noqa: E402
    FUNC_CLASSES, _floor, _fbtc_from_final_errs, _std_from_final_errs,
)
from cell_report import _tie_groups  # noqa: E402 -- single source of truth,
                                       # shared with cell_report.py's own
                                       # fig_ranking() so the tie-merge rule
                                       # can't drift out of sync between the
                                       # two report generators again.
try:
    from _common import suite_default_maxevals  # type: ignore
except Exception:                                # pragma: no cover
    sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'benchmark'))
    from _common import suite_default_maxevals

# --- shared presentation constants (identical to cell_report) --------------
ALGO_ORDER = ['MSC-CMA', 'BIPOP-CMA', 'ARRDE', 'LSRTDE',
              'NLSHADE-RSP', 'j2020', 'jSO']
TABLE_COLS = ['MSC-CMA', 'BIPOP-CMA', None,
              'ARRDE', 'LSRTDE', 'NLSHADE-RSP', 'j2020', 'jSO']
DISPLAY = {
    'MSC-CMA':     'MSC-CMA-ES',
    'BIPOP-CMA':   'BIPOP-CMA-ES',
    'LSRTDE':      'L-SRTDE',
    'NLSHADE-RSP': 'NL-SHADE-RSP',
}
STYLE = {
    'MSC-CMA':     dict(color='#d62728', lw=3.2, marker='o', ms=8, ls='-',  zorder=5),
    'BIPOP-CMA':   dict(color='#7b2d8e', lw=2.4, marker='s', ms=7, ls='--', zorder=4),
    'ARRDE':       dict(color='#7fb3d5', lw=1.6, marker='^', ms=6, ls='-',  zorder=3),
    'LSRTDE':      dict(color='#90ee90', lw=1.6, marker='v', ms=6, ls='-',  zorder=3),
    'NLSHADE-RSP': dict(color='#f4a460', lw=1.6, marker='D', ms=5, ls='-',  zorder=3),
    'j2020':       dict(color='#b09a90', lw=1.6, marker='P', ms=6, ls='-',  zorder=3),
    'jSO':         dict(color='#b0b0b0', lw=1.6, marker='s', ms=5, ls='-',  zorder=3),
}
CLASSES = ['basic', 'hybrid', 'composition']
CLASS_LABEL = {'basic': 'USM', 'hybrid': 'Hybrid', 'composition': 'Composition'}
METRICS = ['mean', 'median', 'best', 'worst', 'std', 'FBTC']
DEPRECATED = {'cec2017': {'f2'}}


# --- loading ---------------------------------------------------------------

def list_budgets(base, algo):
    d = os.path.join(base, algo)
    if not os.path.isdir(d):
        return set()
    out = set()
    for x in os.listdir(d):
        if x.startswith('maxevals_'):
            try:
                out.add(int(x.split('_')[1]))
            except ValueError:
                pass
    return out


def load_budget(base, algo, budget, drop):
    d = os.path.join(base, algo, f'maxevals_{budget}')
    funcs = {}
    for p in sorted(glob.glob(os.path.join(d, 'f*.pkl'))):
        import pickle
        with open(p, 'rb') as fh:
            rec = pickle.load(fh)
        fn = rec['func']
        if fn in drop:
            continue
        e = np.asarray(rec['errors'], float)
        ef = _floor(e)
        funcs[fn] = {
            'mean': float(ef.mean()), 'median': float(np.median(ef)),
            'best': float(ef.min()), 'worst': float(ef.max()),
            'std': _std_from_final_errs(e), 'FBTC': _fbtc_from_final_errs(e),
        }
    return funcs


def members(suite, cls):
    drop = DEPRECATED.get(suite, set())
    return {f'f{n}' for n in FUNC_CLASSES[suite][cls]} - drop


# --- ranking figure --------------------------------------------------------

def _fmt(v):
    if v >= 10:
        return f'{v:.0f}'
    if v >= 1:
        return f'{v:.3g}'
    return f'{v:.3f}'


def class_common(data, algos, mem):
    return sorted(set.intersection(*(set(data[a]) for a in algos)) & mem,
                  key=lambda s: int(s[1:]))


def fig_ranking(data, algos, suite, dim, cls, out):
    mem = members(suite, cls)
    common = class_common(data, algos, mem)
    if not common:
        return False
    # decide coverage axis: FBTC unless all algos have FBTC==0
    fbtc_sum = {a: sum(data[a][f]['FBTC'] for f in common) for a in algos}
    use_fbtc = any(v > 1e-12 for v in fbtc_sum.values())
    cov_label, cov_key = ('FBTC', 'FBTC') if use_fbtc else ('mean-SUM', 'mean')
    axes = [('worst-SUM', 'worst', False), ('median-SUM', 'median', False),
            (cov_label, cov_key, use_fbtc), ('best-SUM', 'best', False)]

    nax = len(axes)
    ypos = {}
    axis_groups = {}
    for ai, (label, key, hb) in enumerate(axes):
        s = {a: sum(data[a][f][key] for f in common) for a in algos}
        ranked = sorted(algos, key=lambda a: (-s[a] if hb else s[a]))
        groups = _tie_groups(ranked, s)
        axis_groups[ai] = groups
        ng = len(groups)
        for gi, grp in enumerate(groups):
            if ng == 1:
                v = s[grp[0]]
                is_zero = abs(v) < 1e-9
                if hb:
                    max_possible = len(common)
                    frac = min(max((v / max_possible) if max_possible else 0.0,
                                   0.0), 1.0)
                    y = frac * (len(algos) - 1)
                elif is_zero:
                    y = len(algos) - 1
                else:
                    y = (len(algos) - 1) / 2.0
            else:
                y = (ng - 1 - gi) * (len(algos) - 1) / (ng - 1)
            for a in grp:
                ypos[(ai, a)] = y

    fig, ax = plt.subplots(figsize=(13, 6.5))
    xs = np.arange(nax)
    for a in algos:
        ys = [ypos[(ai, a)] for ai in range(nax)]
        st = STYLE[a]
        # Use the algorithm's OWN style (lw/ls/zorder), not a bare
        # "is it MSC-CMA?" check -- STYLE already encodes the CMA-vs-DE
        # hierarchy (BIPOP-CMA: lw=2.4, ls='--' vs DE: lw=1.6, solid), it
        # just wasn't being read here.
        ax.plot(xs, ys, color=st['color'], lw=st['lw'], ls=st['ls'],
                zorder=st['zorder'], alpha=0.95, solid_capstyle='round',
                dash_capstyle='round')

    # Endpoint markers: singleton -> the algo's own marker shape+size from
    # STYLE (also previously ignored). Merged group -> one neutral "hub"
    # marker (stacking N colored dots on the same pixel just hides all but
    # the last-drawn one).
    for ai in (0, nax - 1):
        for grp in axis_groups[ai]:
            y = ypos[(ai, grp[0])]
            if len(grp) == 1:
                a0 = grp[0]
                st = STYLE[a0]
                ax.scatter([xs[ai]], [y], color=st['color'],
                           marker=st['marker'], s=st['ms'] ** 2 * 2.2,
                           zorder=st['zorder'] + 1)
            else:
                ax.scatter([xs[ai]], [y], facecolor='white',
                           edgecolor='#2c3e50', linewidth=1.6,
                           s=150, zorder=7)

    for ai, (label, key, hb) in enumerate(axes):
        s = {a: sum(data[a][f][key] for f in common) for a in algos}
        groups = axis_groups[ai]
        for grp in groups:
            y = ypos[(ai, grp[0])]
            v = s[grp[0]]  # tied group shares one (near-)identical value
            if ai in (0, nax - 1):
                m = len(grp)
                step = 0.16
                y0 = y + step * (m - 1) / 2.0
                for k, a in enumerate(grp):
                    bold = 'bold' if a == 'MSC-CMA' else 'normal'
                    yk = y0 - k * step
                    fs = 11 if m == 1 else 9
                    if ai == 0:
                        ax.text(-0.06, yk, f'{DISPLAY.get(a, a)} {_fmt(v)}', ha='right',
                                va='center', color=STYLE[a]['color'],
                                fontweight=bold, fontsize=fs)
                    else:
                        ax.text(nax - 1 + 0.06, yk, f'{_fmt(v)} {DISPLAY.get(a, a)}',
                                ha='left', va='center',
                                color=STYLE[a]['color'], fontweight=bold,
                                fontsize=fs)
            else:
                if len(grp) == 1:
                    color = STYLE[grp[0]]['color']
                    bold = 'bold' if grp[0] == 'MSC-CMA' else 'normal'
                else:
                    color = '#555555'
                    bold = 'bold' if 'MSC-CMA' in grp else 'normal'
                ax.text(ai, y + 0.18, _fmt(v), ha='center', va='bottom',
                        color=color, fontweight=bold, fontsize=10)
    ax.set_xticks(xs)
    ax.set_xticklabels([a[0] for a in axes], fontsize=13)
    ax.set_xlim(-1.9, nax - 1 + 1.9)
    ax.set_ylim(-0.8, len(algos) - 0.2)
    ax.set_yticks([])
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_position(('data', -0.6))
    ax.set_title(f'{suite.upper()}  D={dim}  —  {CLASS_LABEL[cls]} '
                 f'({len(common)} funcs)', fontsize=14, pad=15)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return True


# --- budget figure ---------------------------------------------------------

def _env(v):
    o, m = [], -np.inf
    for x in v:
        m = max(m, x)
        o.append(m)
    return o


def _bl(b):
    if b >= 1_000_000:
        return f'{b // 1_000_000}M' if b % 1_000_000 == 0 else f'{b/1e6:g}M'
    if b >= 1000:
        return f'{b // 1000}k' if b % 1000 == 0 else f'{b/1e3:g}k'
    return str(b)


def class_budget_series(base, algos, suite, cls, drop):
    mem = members(suite, cls)
    cand = None
    for a in algos:
        b = list_budgets(base, a)
        cand = b if cand is None else (cand & b)
    cand = sorted(cand or [])
    budgets, data = [], {}
    for b in cand:
        ok = True
        per = {}
        for a in algos:
            d = load_budget(base, a, b, drop)
            if not mem.issubset(set(d)):
                ok = False
                break
            per[a] = {'FBTC': sum(d[f]['FBTC'] for f in mem),
                      'median': sum(d[f]['median'] for f in mem)}
        if ok:
            budgets.append(b)
            data[b] = per
    return budgets, data, mem


def fig_budget(base, algos, suite, dim, cls, out):
    budgets, series, mem = class_budget_series(base, algos, suite, cls,
                                               DEPRECATED.get(suite, set()))
    if len(budgets) < 2:
        return False, budgets, None
    nmax = len(mem)
    # FBTC unless all-zero at every budget -> median
    any_fbtc = any(series[b][a]['FBTC'] > 1e-12
                   for b in budgets for a in algos)
    metric = 'FBTC' if any_fbtc else 'median'

    x = np.arange(len(budgets))
    fig, ax = plt.subplots(figsize=(7, 5.0))
    for a in algos:
        raw = [series[b][a][metric] for b in budgets]
        y = _env(raw) if metric == 'FBTC' else raw
        ax.plot(x, y, label=DISPLAY.get(a, a), **STYLE[a])
    if metric == 'FBTC':
        if cls != 'composition':
            ax.axhline(nmax, ls=':', color='gray', lw=1)
            ax.text(x[-1], nmax, f' max={nmax}', va='center', ha='left',
                    color='gray', fontsize=9)
            ax.set_ylim(0, nmax * 1.06)
        else:
            ax.set_ylim(0, None)
        ylab = f'FBTC (sum over {nmax} functions)'
        title = f'{suite.upper()}  D={dim} — {cls} class'
    else:
        ylab = f'Median error, summed over {nmax} functions (lower is better)'
        title = f'{suite.upper()}  D={dim} — {cls} class (median error)'
    ax.set_xticks(x)
    ax.set_xticklabels([_bl(b) for b in budgets])
    ax.set_xlabel('Budget (MaxFES)', fontsize=11)
    ax.set_ylabel(ylab, fontsize=10.5)
    ax.set_title(title, fontsize=12)
    ax.grid(axis='y', ls=':', alpha=0.5)
    ax.legend(ncol=2, fontsize=8.5, loc='best')
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return True, budgets, metric


# --- tables ----------------------------------------------------------------

def fmt_cell(v, metric):
    if metric == 'FBTC':
        return f'{v:.3f}'
    if v == 0:
        return '0'
    a = abs(v)
    if a < 1e-3:
        m, ex = f'{v:.1e}'.split('e')
        return f'{m}e{int(ex)}'
    if a < 1000:
        return f'{v:.3g}'
    return f'{v:.0f}'


def metric_table(per_dim, suite, dims, metric):
    higher = metric == 'FBTC'
    rows = []
    header = [DISPLAY.get(a, a) if a else '' for a in TABLE_COLS]
    rows.append('| Category | Dim | ' + ' | '.join(header) + ' |')
    rows.append('|:--|:--:|' + '|'.join(['--:' if a else ':-:'
                                         for a in TABLE_COLS]) + '|')
    algos = [a for a in TABLE_COLS if a]
    for cls in CLASSES:
        for dim in dims:
            data = per_dim[dim]
            mem = members(suite, cls)
            common = class_common(data, algos, mem)
            if not common:
                continue
            vals = {a: sum(data[a][f][metric] for f in common) for a in algos}
            best = max(vals.values()) if higher else min(vals.values())
            cells = []
            for a in TABLE_COLS:
                if a is None:
                    cells.append('  ')
                    continue
                s = fmt_cell(vals[a], metric)
                if abs(vals[a] - best) < 1e-9:
                    s = f'**{s}**'
                cells.append(s)
            rows.append(f'| {CLASS_LABEL[cls]} | {dim} | '
                        + ' | '.join(cells) + ' |')
    return '\n'.join(rows)


# --- README assembly -------------------------------------------------------

def fig_row(prefix, dim, made):
    cells, labels = [], []
    for c in CLASSES:
        if made.get((dim, c)):
            cells.append(f'<td><img src="{prefix}_d{dim}_{c}.png" width="300" '
                         f'alt="{CLASS_LABEL[c]}"></td>')
            labels.append(f'<td align="center">{CLASS_LABEL[c]}</td>')
    if not cells:
        return ''
    return ('<table>\n<tr>\n' + '\n'.join(cells) + '\n</tr>\n<tr>\n'
            + '\n'.join(labels) + '\n</tr>\n</table>')


def build_readme(suite, dims, per_dim, rank_made, budget_made,
                 budget_metric, officials):
    o = [f'# {suite.upper()} — cross-dimension summary', '']
    o.append('Aggregated sums by function category, across dimensions. '
             '**Bold** = best in row. For simplicity the suite is presented '
             'per dimension.')
    o.append('')
    bud = ', '.join(f'{d}D: {officials[d]:,}' for d in dims)
    o.append(f'Official budgets — {bud}.')
    o.append('')
    for dim in dims:
        o.append(f'## Ranking — D={dim}')
        o.append('')
        o.append('Parallel-coordinate rank on four aggregate metrics '
                 '(worst-SUM, median-SUM, coverage, best-SUM). Best value at '
                 'the top of each axis; MSC-CMA in red.')
        o.append('')
        r = fig_row('rank', dim, rank_made)
        if r:
            o.append(r)
            o.append('')
        b = fig_row('budget', dim, budget_made)
        if b:
            o.append(f'## Budget scaling — D={dim}')
            o.append('')
            note = ('FBTC by budget, monotone envelope; higher is better.')
            # composition may be median
            if budget_metric.get((dim, 'composition')) == 'median':
                note += (' Composition is shown as *median error* '
                         '(lower is better): no algorithm reaches even the '
                         'easiest target, so FBTC is zero for all.')
            o.append(note)
            o.append('')
            o.append(b)
            o.append('')

    o.append('## Median error (lower is better)')
    o.append('')
    o.append(metric_table(per_dim, suite, dims, 'median'))
    o.append('')
    o.append('## Best error (lower is better)')
    o.append('')
    o.append(metric_table(per_dim, suite, dims, 'best'))
    o.append('')
    o.append('## Worst error (lower is better)')
    o.append('')
    o.append(metric_table(per_dim, suite, dims, 'worst'))
    o.append('')
    o.append('## FBTC — Fixed-Budget Target Coverage (higher is better)')
    o.append('')
    o.append(metric_table(per_dim, suite, dims, 'FBTC'))
    o.append('')
    o.append('*FBTC = Fixed-Budget Target Coverage (per-function sum across '
             '51 log-uniform targets in [10²…10⁻⁸]); fixed-budget analogue of '
             'the COCO/BBOB ECDF. Higher is better.*')
    o.append('')
    o.append('## Environment')
    o.append('Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · '
             'SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.')
    o.append('Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, '
             '251 GiB RAM.')
    today = datetime.date.today().isoformat()
    o.append('')
    o.append(f'*Generated {today} by analysis/suite_report.py.*')
    return '\n'.join(o)


# --- driver ----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--suite', required=True)
    ap.add_argument('--dims', required=True,
                    help='comma list, e.g. 10,30')
    ap.add_argument('--official', action='append', default=[],
                    help='dim,budget  (repeatable). Missing -> suite default.')
    ap.add_argument('--algos', default=','.join(ALGO_ORDER))
    ap.add_argument('--root', default='experiments')
    ap.add_argument('--no-readme', action='store_true')
    ap.add_argument('--no-figures', action='store_true')
    args = ap.parse_args()

    suite = args.suite.lower()
    if suite not in FUNC_CLASSES:
        sys.exit(f"No FUNC_CLASSES for suite '{suite}'.")
    dims = [int(d) for d in args.dims.split(',')]
    algos = [a.strip() for a in args.algos.split(',') if a.strip()]
    drop = DEPRECATED.get(suite, set())

    officials = {}
    for spec in args.official:
        d, b = spec.split(',')
        officials[int(d)] = int(b)
    for d in dims:
        officials.setdefault(d, suite_default_maxevals(suite, d))

    per_dim, rank_made, budget_made, budget_metric = {}, {}, {}, {}
    for dim in dims:
        base = os.path.join(args.root, suite, f'd{dim}')
        data = {}
        for a in algos:
            dd = load_budget(base, a, officials[dim], drop)
            if dd:
                data[a] = dd
        miss = [a for a in algos if a not in data]
        if miss:
            sys.exit(f"D={dim}: missing official-budget data for "
                     f"{', '.join(miss)} at {officials[dim]}")
        per_dim[dim] = data

        if not args.no_figures:
            for c in CLASSES:
                rp = os.path.join(base, f'rank_d{dim}_{c}.png')
                rank_made[(dim, c)] = fig_ranking(data, algos, suite, dim, c, rp)
                bp = os.path.join(base, f'budget_d{dim}_{c}.png')
                ok, budgets, met = fig_budget(base, algos, suite, dim, c, bp)
                budget_made[(dim, c)] = ok
                budget_metric[(dim, c)] = met
                tag = (f"{met}, [{','.join(_bl(b) for b in budgets)}]"
                       if ok else 'skip')
                print(f"  D={dim} {c:<12} rank "
                      f"{'ok' if rank_made[(dim,c)] else 'skip'}  budget {tag}")
        else:
            for c in CLASSES:
                rank_made[(dim, c)] = os.path.exists(
                    os.path.join(base, f'rank_d{dim}_{c}.png'))
                budget_made[(dim, c)] = os.path.exists(
                    os.path.join(base, f'budget_d{dim}_{c}.png'))
                budget_metric[(dim, c)] = None

    if not args.no_readme:
        # figures live in experiments/<suite>/d<dim>/ but README is at suite
        # root; copy paths are relative as d<dim>/rank_... -> adjust prefix.
        md = build_readme(suite, dims, per_dim, rank_made, budget_made,
                          budget_metric, officials)
        # fix figure src to include the d<dim>/ subdir
        for dim in dims:
            md = md.replace(f'src="rank_d{dim}_',
                            f'src="d{dim}/rank_d{dim}_')
            md = md.replace(f'src="budget_d{dim}_',
                            f'src="d{dim}/budget_d{dim}_')
        out = os.path.join(args.root, suite, 'README.md')
        with open(out, 'w') as fh:
            fh.write(md + '\n')
        print(f"  wrote {out}")


if __name__ == '__main__':
    main()
