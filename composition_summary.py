#!/usr/bin/env python3
"""
composition_summary.py — cross-suite summary by dimension, for a single
function CLASS (composition by default).

Same layout as the overall table: a cell is the sum over every function of the
class at a given dimension (across suites, at each suite's STANDARD budget).
Rows = metric (best/mean/median/FBTC), columns = algorithm. Bold = best
(min for best/mean/median, max for FBTC). Output is markdown.

Reuses analysis/summary_grid_clean.aggregate (same best/mean/median/FBTC
definitions as the overall table) and benchmark/_common.suite_default_maxevals.

    python composition_summary.py                      # composition
    python composition_summary.py --class hybrid
    python composition_summary.py --class composition --out comp_summary.md
"""

from __future__ import annotations
import argparse
import os
import importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# CEC classes per suite (function-number ranges)
CLASS_RANGES = {
    'cec2014': {'basic': range(1, 17), 'hybrid': range(17, 23), 'composition': range(23, 31)},
    'cec2017': {'basic': range(1, 11), 'hybrid': range(11, 21), 'composition': range(21, 31)},
    'cec2020': {'basic': range(1, 5), 'hybrid': range(5, 8), 'composition': range(8, 11)},
    'cec2022': {'basic': range(1, 6), 'hybrid': range(6, 9), 'composition': range(9, 13)},
}

PREFERRED = ['MSC-CMA', 'BIPOP-CMA', 'ARRDE', 'LSRTDE',
             'NLSHADE-RSP', 'NLSHADE', 'j2020', 'jSO']


def _fnum(k):
    return int(str(k).lstrip('fF'))


def class_funcs(suite, cls):
    rng = CLASS_RANGES.get(suite, {}).get(cls)
    return set(rng) if rng else set()


def order_algos(present):
    ordered = []
    for p in PREFERRED:
        for a in present:
            if a == p and a not in ordered:
                ordered.append(a)
    for a in sorted(present):
        if a not in ordered:
            ordered.append(a)
    return ordered


def build(grid, common, cls):
    """by_dim[dim][algo] = {'best','mean','median','fbtc','nf'} (sums)."""
    by_dim = {}
    present = set()
    comp_per_dim = {}            # dim -> {suite: (nf, budget)} for the legend
    for (suite, dim, me), cell in grid.items():
        try:
            std = common.suite_default_maxevals(suite, dim)
        except Exception:
            continue
        if me != std:                       # standard budget only
            continue
        cf = class_funcs(suite, cls)
        if not cf:
            continue
        by_dim.setdefault(dim, {})
        for algo, funcs in cell.items():
            rel = [f for f in funcs if _fnum(f) in cf]
            if not rel:
                continue
            present.add(algo)
            e = by_dim[dim].setdefault(algo, {'best': 0.0, 'mean': 0.0,
                                              'median': 0.0, 'fbtc': 0.0,
                                              'nf': 0})
            e['best'] += sum(funcs[f]['best'] for f in rel)
            e['mean'] += sum(funcs[f]['mean'] for f in rel)
            e['median'] += sum(funcs[f]['median'] for f in rel)
            e['fbtc'] += sum(funcs[f]['fbtc'] for f in rel)
            e['nf'] += len(rel)
        # legend: take nf from the reference algo (MSC if present, else first)
        ref_algo = next((a for a in cell if a == 'MSC-CMA'), None) or \
            (next(iter(cell)) if cell else None)
        if ref_algo:
            nf = len([f for f in cell[ref_algo] if _fnum(f) in cf])
            if nf:
                comp_per_dim.setdefault(dim, {})[suite] = (nf, std)
    return by_dim, order_algos(present), comp_per_dim


def _fmt(v):
    if v == 0:
        return '0'
    a = abs(v)
    if a < 1e-3 or a >= 1e5:
        return f"{v:.3g}"
    if a < 1:
        return f"{v:.3g}"
    if a < 100:
        return f"{v:.1f}"
    return f"{v:.0f}"


def render_md(by_dim, algos, comp_per_dim, cls):
    lines = []
    lines.append(f"## Cross-suite summary — {cls} only, by dimension\n")
    lines.append(f"Sum over all **{cls}** functions at each dimension (across "
                 "suites, standard budget). CMA family first. **Bold** = best "
                 "(min for best/mean/median, max for FBTC).\n")
    head = "| D · nF | Metric | " + " | ".join(algos) + " |"
    sep = "|" + "---|" * (len(algos) + 2)
    lines.append(head)
    lines.append(sep)

    METRICS = [('best', 'min'), ('mean', 'min'), ('median', 'min'),
               ('fbtc', 'max')]
    MNAME = {'best': 'best', 'mean': 'mean', 'median': 'median', 'fbtc': 'FBTC'}

    for dim in sorted(by_dim):
        nf = max((by_dim[dim][a]['nf'] for a in by_dim[dim]), default=0)
        for mi, (metric, direction) in enumerate(METRICS):
            vals = {a: by_dim[dim][a][metric] for a in algos if a in by_dim[dim]}
            if not vals:
                continue
            best = (min if direction == 'min' else max)(vals.values())
            dcell = f"**{dim} · {nf}**" if mi == 0 else ""
            cells = []
            for a in algos:
                if a not in vals:
                    cells.append("—")
                    continue
                v = vals[a]
                s = _fmt(v)
                if abs(v - best) <= 1e-9 * max(1.0, abs(best)):
                    s = f"**{s}**"
                cells.append(s)
            lines.append(f"| {dcell} | {MNAME[metric]} | " +
                         " | ".join(cells) + " |")

    # composition-of-each-dimension legend
    lines.append(f"\n**Composition of each dimension** ({cls}, suite → nF, budget):\n")
    for dim in sorted(comp_per_dim):
        parts = [f"{s} ({nf}, {me:.0e})"
                 for s, (nf, me) in sorted(comp_per_dim[dim].items())]
        total = sum(nf for nf, _ in comp_per_dim[dim].values())
        lines.append(f"- **D={dim}** ({total}): " + " · ".join(parts))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='experiments')
    ap.add_argument('--class', dest='cls', default='composition',
                    choices=['composition', 'hybrid', 'basic'])
    ap.add_argument('--out', default='', help='write markdown to a file')
    args = ap.parse_args()

    THIS = os.path.dirname(os.path.abspath(__file__))
    sg = _load('summary_grid_clean',
               os.path.join(THIS, 'analysis', 'summary_grid_clean.py'))
    common = _load('_common', os.path.join(THIS, 'benchmark', '_common.py'))

    grid, _, _ = sg.aggregate(args.root)
    by_dim, algos, comp = build(grid, common, args.cls)
    md = render_md(by_dim, algos, comp, args.cls)
    print(md)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"\n(written to {args.out})")


if __name__ == '__main__':
    main()
