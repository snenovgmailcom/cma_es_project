#!/usr/bin/env python3
"""Regenerate by-category README.md for a CEC2020 cell from pkls.
Usage: python analysis/make_cell_readme.py --base-dir experiments/cec2020/d5 --maxevals 50000
"""
import argparse, os, glob, pickle, datetime
import numpy as np
from summary_grid import _floor, _std_from_final_errs, _fbtc_from_final_errs

CATS = [('Basic', ['f1','f2','f3','f4']),
        ('Hybrid', ['f5','f6','f7']),
        ('Composition', ['f8','f9','f10'])]
COL_ORDER = ['MSC-CMA', 'BIPOP-CMA', None,   # None = separator column
             'ARRDE', 'LSRTDE', 'NLSHADE-RSP', 'j2020', 'jSO']
DISPLAY = {'NLSHADE-RSP': 'NLSHADE'}
METRICS = ['mean', 'median', 'best', 'worst', 'std', 'FBTC']

def load(base, maxevals):
    algos = {}
    for d in sorted(glob.glob(os.path.join(base, '*', f'maxevals_{maxevals}'))):
        algo = d.split(os.sep)[-2]
        funcs = {}
        for p in sorted(glob.glob(os.path.join(d, 'f*.pkl'))):
            with open(p, 'rb') as f:
                rec = pickle.load(f)
            e = np.asarray(rec['errors'], float)
            ef = _floor(e)
            funcs[rec['func']] = {
                'mean': ef.mean(), 'median': float(np.median(ef)),
                'best': ef.min(), 'worst': ef.max(),
                'std': _std_from_final_errs(e), 'FBTC': _fbtc_from_final_errs(e)}
        if funcs:
            algos[algo] = funcs
    return algos

def fmt(v, metric):
    if metric == 'FBTC':
        return f'{v:.3f}'
    if v == 0:
        return '0'
    a = abs(v)
    if a < 1e-3:
        m, ex = f'{v:.1e}'.split('e')
        return f'{m}e{int(ex)}'          # 5.5e-7 style
    return f'{v:.0f}' if a >= 1000 else f'{v:.3g}'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-dir', required=True)
    ap.add_argument('--maxevals', type=int, required=True)
    ap.add_argument('-o', '--output', default=None)
    args = ap.parse_args()

    algos = load(args.base_dir, args.maxevals)
    cols = [c for c in COL_ORDER if c is None or c in algos]
    real = [c for c in cols if c]
    missing = [c for c in COL_ORDER if c and c not in algos]
    if missing:
        raise SystemExit(f'Missing cells for: {missing}')

    lines = []
    hdr = ['Category', 'Metric'] + [DISPLAY.get(c, c) if c else ' ' for c in cols]
    lines.append('| ' + ' | '.join(hdr) + ' |')
    lines.append('|:--|:--|' + '|'.join(
        ':-:' if c is None else '--:' for c in cols) + '|')

    def block(label, funcs_list, n):
        for i, metric in enumerate(METRICS):
            vals = {a: sum(algos[a][f][metric] for f in funcs_list) for a in real}
            tgt = max(vals.values()) if metric == 'FBTC' else min(vals.values())
            cells = []
            for c in cols:
                if c is None:
                    cells.append(' ')
                    continue
                s = fmt(vals[c], metric)
                cells.append(f'**{s}**' if np.isclose(vals[c], tgt, rtol=1e-12) else s)
            first = f'**{label}** (n={n})' if i == 0 else ''
            lines.append(f'| {first} | {metric} | ' + ' | '.join(cells) + ' |')

    for label, fl in CATS:
        block(label, fl, len(fl))
    block('SUM', [f for _, fl in CATS for f in fl], 10)

    today = datetime.date.today().isoformat()
    out = f"""# CEC2020 / D=5 — by-category summary

Sums of per-function metrics, grouped by function class. Categories: **Basic** = F1–F4 (1 unimodal + 3 basic multimodal), **Hybrid** = F5–F7, **Composition** = F8–F10. Total: 10 functions. Budget: {args.maxevals:,} evaluations. **Bold** = best in row.

{chr(10).join(lines)}

*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*

*Generated {today} by analysis/make_cell_readme.py from `{args.base_dir}/*/maxevals_{args.maxevals}/f*.pkl`.*

## Environment
Python 3.13.5 (anaconda3 env `intelpython`) · NumPy 2.3.1 · SciPy 1.15.3 · pycma 4.4.2 · minionpy 1.5.0.
Hardware: Intel Xeon Platinum 8160 @ 2.10 GHz, 192 threads, 251 GiB RAM.
"""
    dest = args.output or os.path.join(args.base_dir, 'README.md')
    with open(dest, 'w') as f:
        f.write(out)
    print(out)
    print(f'→ {dest}')

if __name__ == '__main__':
    main()
