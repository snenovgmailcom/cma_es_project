#!/usr/bin/env python3
"""analysis/cell_report.py — one-shot per-cell report (figures + README).

For a single (suite, dimension) cell this script regenerates, in a fixed and
reproducible style shared across every cell:

  1. Ranking figures  (rank_basic.png, rank_hybrid.png, rank_composition.png)
     Parallel-coordinate ranking of all algorithms on four aggregate metrics
     (worst-SUM, median-SUM, FBTC, best-SUM) at the OFFICIAL CEC budget.
     One line per algorithm; per axis the best value sits at the top.

  2. Budget-scaling figures (budget_basic.png, budget_hybrid.png,
     budget_composition.png) — FBTC vs budget, MONOTONE ENVELOPE
     (running maximum over budgets; see paper, sec:budget).
     PER-CLASS budget axis: a budget B is included for class C only if ALL
     plotted algorithms have the ENTIRE class C present at B. Classes with
     fewer than two such budgets get no panel.

  With --extended <budget>, also emits rank_<class>_<label>.png at that higher
  budget (e.g. rank_composition_1M.png) and adds a second ranking section.

  3. README.md with sections in fixed order (Ranking @official, Budget scaling,
     optional Ranking @extended, Summary table):
        Ranking across metrics  ->  Budget scaling  ->  Summary table
     followed by an Environment block.

All FBTC / floor / class logic is reused from summary_grid_clean to stay
consistent with the rest of the analysis package.

Usage
-----
    # official budget is required (the cell's competition MaxFES)
    python analysis/cell_report.py --base-dir experiments/cec2014/d10 \
        --official 100000

    # only (re)build figures, leave README untouched
    python analysis/cell_report.py --base-dir experiments/cec2014/d10 \
        --official 100000 --no-readme

    # restrict plotted algorithms
    python analysis/cell_report.py --base-dir experiments/cec2017/d30 \
        --official 300000 --algos MSC-CMA,BIPOP-CMA,ARRDE,jSO
"""

import argparse
import datetime
import glob
import os
import pickle
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summary_grid_clean import (  # noqa: E402
    FUNC_CLASSES, _floor, _fbtc_from_final_errs, _std_from_final_errs,
)

# ---------------------------------------------------------------------------
# Fixed presentation constants (shared by every cell -> identical style).
# ---------------------------------------------------------------------------

ALGO_ORDER = ['MSC-CMA', 'BIPOP-CMA', 'ARRDE', 'LSRTDE',
              'NLSHADE-RSP', 'j2020', 'jSO']

# Table column order keeps the CMA pair, then a separator, then the DE block,
# matching the existing per-cell READMEs.
TABLE_COLS = ['MSC-CMA', 'BIPOP-CMA', None,
              'ARRDE', 'LSRTDE', 'NLSHADE-RSP', 'j2020', 'jSO']
DISPLAY = {'NLSHADE-RSP': 'NLSHADE'}

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
CLASS_LABEL = {'basic': 'Basic', 'hybrid': 'Hybrid', 'composition': 'Composition'}

# Ranking axes: (display label, metric key, higher_is_better).
RANK_AXES = [('worst-SUM', 'worst', False),
             ('median-SUM', 'median', False),
             ('FBTC', 'FBTC', True),
             ('best-SUM', 'best', False)]

METRICS = ['mean', 'median', 'best', 'worst', 'std', 'FBTC']
DEPRECATED = {'cec2017': {'f2'}}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def suite_of(base_dir):
    # experiments/cec2014/d10 -> cec2014
    return os.path.basename(os.path.dirname(base_dir.rstrip('/'))).lower()


def list_budgets(base_dir, algo):
    d = os.path.join(base_dir, algo)
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


def load_budget(base_dir, algo, budget, drop):
    """Return {func_name: metric_dict} for one (algo, budget), or {}."""
    d = os.path.join(base_dir, algo, f'maxevals_{budget}')
    funcs = {}
    for p in sorted(glob.glob(os.path.join(d, 'f*.pkl'))):
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


def class_members(suite, cls):
    return {f'f{n}' for n in FUNC_CLASSES.get(suite, {}).get(cls, set())}


# ---------------------------------------------------------------------------
# Ranking figures
# ---------------------------------------------------------------------------

def _fmt(v):
    if v >= 100:
        return f'{v:.0f}'
    if v >= 10:
        return f'{v:.0f}'
    if v >= 1:
        return f'{v:.3g}'
    return f'{v:.3f}'


def class_sums(data, algos, members, key):
    """SUM over the common members present for all algos."""
    common = sorted(set.intersection(*(set(data[a]) for a in algos)) & members,
                    key=lambda s: int(s[1:]))
    return {a: sum(data[a][f][key] for f in common) for a in algos}, common


def _tie_groups(ranked, s, rtol=1e-9, atol=1e-9):
    """Split a value-sorted algo list into consecutive near-equal groups.

    Given the COCO_ZERO=1e-8 floor already applied upstream (per run, per
    function, before summing), genuine ties at the SUM level are expected to
    land bit-identical or within float summation noise. rtol/atol are kept
    tight on purpose: values that only agree after _fmt()'s display rounding
    (e.g. 100.001 vs 100.008, both printed "100") must NOT be merged — that
    would misrepresent the data. Only real ties collapse.
    """
    groups, i, n = [], 0, len(ranked)
    while i < n:
        j = i
        while j + 1 < n and np.isclose(s[ranked[j + 1]], s[ranked[i]],
                                        rtol=rtol, atol=atol):
            j += 1
        groups.append(ranked[i:j + 1])
        i = j + 1
    return groups


def fig_ranking(data, algos, suite, cls, out_path, tie_rtol=1e-9, tie_atol=1e-9):
    members = class_members(suite, cls)
    sums = {}
    for label, key, hb in RANK_AXES:
        s, common = class_sums(data, algos, members, key)
        sums[label] = (s, hb)
    if not common:
        return False

    nax = len(RANK_AXES)
    ypos = {}
    axis_groups = {}
    for ai, (label, key, hb) in enumerate(RANK_AXES):
        s, _ = sums[label]
        ranked = sorted(algos, key=lambda a: (-s[a] if hb else s[a]))
        groups = _tie_groups(ranked, s, rtol=tie_rtol, atol=tie_atol)
        axis_groups[ai] = groups
        ng = len(groups)
        for gi, grp in enumerate(groups):
            if ng == 1:
                # Everyone ties on this axis (e.g. all seven hit the target
                # to floor precision). No ranking info at all here -- but
                # "top = best" is a promise made for every axis, so the one
                # group still anchors at the top rather than falling out of
                # the generic formula's 0/0-ish bottom default.
                y = len(algos) - 1
            else:
                # Rescaled (not raw ng-1-gi): stretches the surviving groups
                # across the FULL 0..len(algos)-1 span, so the best group on
                # an axis still sits at the visual top even when ties
                # compress it to fewer rows than there are algorithms.
                y = (ng - 1 - gi) * (len(algos) - 1) / (ng - 1)
            for a in grp:
                ypos[(ai, a)] = y

    fig, ax = plt.subplots(figsize=(13, 6.5))
    xs = np.arange(nax)
    for a in algos:
        ys = [ypos[(ai, a)] for ai in range(nax)]
        st = STYLE[a]
        # Use the algorithm's OWN style (lw/ls/zorder) instead of a bare
        # "is it MSC-CMA?" check. STYLE already encodes the CMA-vs-DE
        # visual hierarchy (BIPOP-CMA: lw=2.4, ls='--' vs DE: lw=1.6,
        # solid) -- it just wasn't being read here, so BIPOP-CMA rendered
        # identically to any DE line and the CMA-vs-CMA comparison (the
        # actual headline result) was invisible at a glance.
        ax.plot(xs, ys, color=st['color'], lw=st['lw'], ls=st['ls'],
                zorder=st['zorder'], alpha=0.95, solid_capstyle='round',
                dash_capstyle='round')

    # Endpoint markers: singleton -> the algo's own marker shape+size, as
    # defined in STYLE (also previously ignored -- every algo rendered as
    # a plain circle regardless of its 'marker' entry).
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

    for ai, (label, key, hb) in enumerate(RANK_AXES):
        s, _ = sums[label]
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
                        ax.text(-0.06, yk, f'{a} {_fmt(v)}', ha='right',
                                va='center', color=STYLE[a]['color'],
                                fontweight=bold, fontsize=fs)
                    else:
                        ax.text(nax - 1 + 0.06, yk, f'{_fmt(v)} {a}',
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
    ax.set_xticklabels([a[0] for a in RANK_AXES], fontsize=13)
    ax.set_xlim(-1.9, nax - 1 + 1.9)
    ax.set_ylim(-0.8, len(algos) - 0.2)
    ax.set_yticks([])
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_position(('data', -0.6))
    ax.set_title(f'{suite.upper()}  {dimlabel}  —  {CLASS_LABEL[cls]} '
                 f'({len(common)} funcs)', fontsize=14, pad=15)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return True


# ---------------------------------------------------------------------------
# Budget-scaling figures (monotone envelope, per-class budget axis)
# ---------------------------------------------------------------------------

def _envelope(vals):
    out, m = [], -np.inf
    for v in vals:
        m = max(m, v)
        out.append(m)
    return out


def _fmt_budget(b):
    if b >= 1_000_000:
        return f'{b // 1_000_000}M' if b % 1_000_000 == 0 else f'{b/1e6:g}M'
    if b >= 1000:
        return f'{b // 1000}k' if b % 1000 == 0 else f'{b/1e3:g}k'
    return str(b)


def class_budgets(base_dir, algos, suite, cls, drop):
    """Budgets where ALL algos have the ENTIRE class present.

    Returns (sorted_budgets, {budget: {algo: classFBTC_sum}}).
    """
    members = class_members(suite, cls)
    if not members:
        return [], {}
    # candidate = budgets common to every algo's directory
    cand = None
    for a in algos:
        b = list_budgets(base_dir, a)
        cand = b if cand is None else (cand & b)
    cand = sorted(cand or [])

    valid = []
    fbtc = {}
    for b in cand:
        ok = True
        per_algo = {}
        for a in algos:
            d = load_budget(base_dir, a, b, drop)
            if not members.issubset(set(d)):   # whole class required
                ok = False
                break
            per_algo[a] = sum(d[f]['FBTC'] for f in members)
        if ok:
            valid.append(b)
            fbtc[b] = per_algo
    return valid, fbtc


def fig_budget(base_dir, algos, suite, cls, out_path):
    budgets, fbtc = class_budgets(base_dir, algos, suite, cls, DEPRECATED.get(suite, set()))
    if len(budgets) < 2:
        return False, budgets
    members = class_members(suite, cls)
    nmax = len(members)

    x = np.arange(len(budgets))
    fig, ax = plt.subplots(figsize=(7, 5.0))
    for a in algos:
        raw = [fbtc[b][a] for b in budgets]
        ax.plot(x, _envelope(raw), label=a, **STYLE[a])
    if cls != 'composition':
        ax.axhline(nmax, ls=':', color='gray', lw=1)
        ax.text(x[-1], nmax, f' max={nmax}', va='center', ha='left',
                color='gray', fontsize=9)
        ax.set_ylim(0, nmax * 1.06)
    else:
        ax.set_ylim(0, None)
    ax.set_xticks(x)
    ax.set_xticklabels([_fmt_budget(b) for b in budgets])
    ax.set_xlabel('Budget (MaxFES)', fontsize=11)
    ax.set_ylabel(f'FBTC (sum over {nmax} functions)', fontsize=11)
    ax.set_title(f'{suite.upper()}  {dimlabel} — {cls} class', fontsize=12)
    ax.grid(axis='y', ls=':', alpha=0.5)
    loc = 'best'
    ax.legend(ncol=2, fontsize=8.5, loc=loc)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return True, budgets


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------

def fmt_cell(v, metric):
    if metric == 'FBTC':
        return f'{v:.3f}'
    if v == 0:
        return '0'
    a = abs(v)
    if a < 1e-3:
        m, ex = f'{v:.1e}'.split('e')
        return f'{m}e{int(ex)}'
    if a < 1:
        return f'{v:.3g}'
    if a < 1000:
        return f'{v:.3g}'
    return f'{v:.0f}'


def build_table(data, suite):
    algos = [a for a in TABLE_COLS if a]
    rows = []
    header_algos = [DISPLAY.get(a, a) if a else '' for a in TABLE_COLS]
    rows.append('| Category | Metric | ' + ' | '.join(header_algos) + ' |')
    rows.append('|:--|:--|' + '|'.join(['--:' if a else ':-:'
                                        for a in TABLE_COLS]) + '|')

    higher = {'FBTC'}
    class_groups = [(CLASS_LABEL[c], class_members(suite, c)) for c in CLASSES]
    all_members = set.union(*(m for _, m in class_groups))
    sum_label = ('SUM', all_members)

    def emit(label, members):
        common = sorted(set.intersection(*(set(data[a]) for a in algos)) & members,
                        key=lambda s: int(s[1:]))
        n = len(common)
        first = True
        for metric in METRICS:
            vals = {a: sum(data[a][f][metric] for f in common) for a in algos}
            if metric in higher:
                best = max(vals.values())
            else:
                best = min(vals.values())
            cells = []
            for a in TABLE_COLS:
                if a is None:
                    cells.append('  ')
                    continue
                v = vals[a]
                s = fmt_cell(v, metric)
                if abs(v - best) < 1e-9:
                    s = f'**{s}**'
                cells.append(s)
            cat = f'**{label}** (n={n})' if first else ''
            rows.append(f'| {cat} | {metric} | ' + ' | '.join(cells) + ' |')
            first = False

    for label, members in class_groups:
        emit(label, members)
    emit(*sum_label)
    return '\n'.join(rows)


# ---------------------------------------------------------------------------
# README assembly
# ---------------------------------------------------------------------------

def fig_table(prefix, made, suffix=''):
    cells = []
    labels = []
    for c in CLASSES:
        if made.get(c):
            cells.append(f'<td><img src="{prefix}_{c}{suffix}.png" width="320" '
                         f'alt="{CLASS_LABEL[c]}"></td>')
            labels.append(f'<td align="center">{CLASS_LABEL[c]}</td>')
    if not cells:
        return ''
    return ('<table>\n<tr>\n' + '\n'.join(cells) + '\n</tr>\n<tr>\n'
            + '\n'.join(labels) + '\n</tr>\n</table>')


def build_readme(suite, dimlbl, official, data, rank_made, budget_made,
                 class_def_note, ext_sections=None):
    o = []
    o.append(f'# {suite.upper()} / {dimlbl} — by-category summary')
    o.append('')
    o.append(f'Sums of per-function metrics, grouped by function class. '
             f'Budget: {official:,} evaluations. **Bold** = best in row.')
    o.append('')

    o.append(f'## Ranking across metrics (budget {_fmt_budget(official).upper()})')
    o.append('')
    o.append('Parallel-coordinate rank of all seven algorithms on four '
             'aggregate metrics (worst-SUM, median-SUM, FBTC, best-SUM), per '
             'function class. Each line is one algorithm; for every axis the '
             'best value is at the top. MSC-CMA in red.')
    o.append('')
    rt = fig_table('rank', rank_made)
    if rt:
        o.append(rt)
        o.append('')
    o.append(f'*{class_def_note}*')
    o.append('')

    bt = fig_table('budget', budget_made)
    if bt:
        o.append('## Budget scaling')
        o.append('')
        o.append('FBTC by budget, monotone envelope (running maximum over '
                 'budgets). Higher is better. The budget axis is per class: a '
                 'budget is shown only where all seven algorithms cover the '
                 'whole class. MSC-CMA in red.')
        o.append('')
        o.append(bt)
        o.append('')

    for eb, elabel, made in (ext_sections or []):
        et = fig_table('rank', made, suffix=f'_{elabel}')
        if not et:
            continue
        o.append(f'## Ranking across metrics (budget {elabel.upper()})')
        o.append('')
        o.append(f'Same parallel-coordinate rank, recomputed at {eb:,} '
                 f'evaluations. Only classes with full seven-algorithm coverage '
                 f'at {elabel.upper()} are shown. MSC-CMA in red.')
        o.append('')
        o.append(et)
        o.append('')

    o.append('## Summary table')
    o.append('')
    o.append(build_table(data, suite))
    o.append('')
    o.append('*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform '
             'targets in [10²…10⁻⁸] per function); fixed-budget analogue of '
             'the COCO/BBOB ECDF. Higher is better.*')
    o.append('')
    o.append('## Environment')
    o.append('Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · '
             'SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.')
    o.append('Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, '
             '251 GiB RAM.')
    o.append('')
    today = datetime.date.today().isoformat()
    o.append(f'*Generated {today} by analysis/cell_report.py from '
             f'`*/maxevals_{official}/f*.pkl` (table) and all common budgets '
             f'(budget scaling).*')
    return '\n'.join(o)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

dimlabel = ''  # set in main, used by figure titles


def main():
    global dimlabel
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-dir', required=True,
                    help='e.g. experiments/cec2014/d10')
    ap.add_argument('--official', type=int, required=True,
                    help='official CEC budget (MaxFES) for the table/ranking')
    ap.add_argument('--algos', default=','.join(ALGO_ORDER))
    ap.add_argument('--extended', type=str, default=None,
                    help='optional higher budget(s), comma-separated; each '
                         'generates rank_<class>_<label>.png (e.g. '
                         'rank_composition_1M.png) and adds a ranking section. '
                         'Classes without full 7-algorithm coverage at a given '
                         'budget are skipped. Example: --extended 1000000,10000000')
    ap.add_argument('--no-readme', action='store_true')
    ap.add_argument('--no-figures', action='store_true')
    args = ap.parse_args()

    base = args.base_dir.rstrip('/')
    suite = suite_of(base)
    dimlbl = os.path.basename(base)            # 'd10'
    dimlabel = 'D=' + dimlbl.lstrip('d')
    drop = DEPRECATED.get(suite, set())
    algos = [a.strip() for a in args.algos.split(',') if a.strip()]

    if suite not in FUNC_CLASSES:
        sys.exit(f"No FUNC_CLASSES entry for suite '{suite}'.")

    # Official-budget data for ranking + table.
    data = {}
    for a in algos:
        d = load_budget(base, a, args.official, drop)
        if d:
            data[a] = d
    missing = [a for a in algos if a not in data]
    if missing:
        sys.exit(f"Missing official-budget ({args.official}) data for: "
                 f"{', '.join(missing)}")

    note = ('Basic = unimodal + simple multimodal, per the '
            f'{suite.upper()} definition.')

    rank_made = {}
    budget_made = {}
    if not args.no_figures:
        for c in CLASSES:
            rp = os.path.join(base, f'rank_{c}.png')
            rank_made[c] = fig_ranking(data, algos, suite, c, rp)
            print(f"  rank {c:<12} {'ok' if rank_made[c] else 'skip'}")
        for c in CLASSES:
            bp = os.path.join(base, f'budget_{c}.png')
            ok, budgets = fig_budget(base, algos, suite, c, bp)
            budget_made[c] = ok
            blist = ','.join(_fmt_budget(b) for b in budgets)
            print(f"  budget {c:<12} {'ok' if ok else 'skip'}  [{blist}]")
    else:
        # still need the made-maps for README; infer from existing files
        for c in CLASSES:
            rank_made[c] = os.path.exists(os.path.join(base, f'rank_{c}.png'))
            budget_made[c] = os.path.exists(os.path.join(base, f'budget_{c}.png'))

    # Extended-budget ranking (optional): one or more higher budgets, each shown
    # as rank_<class>_<label>.png next to the official one, without overwriting
    # it. Given as a comma list, e.g. --extended 1000000,10000000. For each
    # budget, only the classes with full seven-algorithm coverage are rendered
    # (so a 10M budget with composition-only data yields just that panel).
    ext_budgets = [int(b) for b in str(args.extended).split(',') if b.strip()] \
        if args.extended else []
    ext_sections = []  # list of (budget, label, rank_ext_made) in given order
    for eb in ext_budgets:
        elabel = _fmt_budget(eb)
        made = {}
        for c in CLASSES:
            members = class_members(suite, c)
            # class covered iff every algo has the whole class at this budget
            covered = bool(members) and all(
                members.issubset(set(load_budget(base, a, eb, drop)))
                for a in algos)
            rp = os.path.join(base, f'rank_{c}_{elabel}.png')
            if not covered:
                if not args.no_figures:
                    print(f"  rank {c:<12} @{elabel:<5} skip (incomplete)")
                    made[c] = False
                else:
                    made[c] = os.path.exists(rp)
                continue
            if not args.no_figures:
                edata = {a: load_budget(base, a, eb, drop) for a in algos}
                made[c] = fig_ranking(edata, algos, suite, c, rp)
                print(f"  rank {c:<12} @{elabel:<5} "
                      f"{'ok' if made[c] else 'skip'}")
            else:
                made[c] = os.path.exists(rp)
        ext_sections.append((eb, elabel, made))

    if not args.no_readme:
        md = build_readme(suite, dimlabel, args.official, data,
                          rank_made, budget_made, note,
                          ext_sections=ext_sections)
        with open(os.path.join(base, 'README.md'), 'w') as fh:
            fh.write(md + '\n')
        print(f"  README.md written ({base}/README.md)")


if __name__ == '__main__':
    main()
