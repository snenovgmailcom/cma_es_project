#!/usr/bin/env python3
"""
msc_vs_funnel.py — по ВСИЧКИ suite-ове и размерности една таблица:

    [ MSC побеждава ли другите по медиана | disp2-предсказание | вид CEC ]

За всяка клетка experiments/<suite>/d<dim>:
  * чете pkl-ите (чрез analysis/compare.discover_algorithms), смята медианата
    на всеки алгоритъм за всяка функция; MSC_wins = MSC median <= най-добрата
    чужда медиана (общ бюджет = най-големият maxevals_* на MSC в клетката).
  * смята disp2 (бързо — само dispersion, без NBC/persistence) и предсказва
    MSC-HARD (disp2 > 0.835) / MSC-OK.
  * взима вида CEC функция (basic/hybrid/composition).
Накрая: точност на правилото (disp2-OK <=> MSC печели) по клетка и общо,
плюс TPR (MSC-губи, уловени като HARD) и specificity (MSC-печели като OK).

Зарежда compare.py / funnel_probe.py / benchmark/_common.py ПО ПЪТ (работи и
при PYTHONSAFEPATH). Нужен е minionpy за disp2.

    python msc_vs_funnel.py                 # root = experiments/
    python msc_vs_funnel.py --root experiments --seeds 2
"""

from __future__ import annotations
import argparse
import glob
import os
import pickle
import importlib.util

import numpy as np

DISP2_THR = 0.835


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _by_budget(alg_path):
    """{maxevals:int -> {fn_key -> errors}} за един алгоритъм."""
    out = {}
    for me_dir in sorted(glob.glob(os.path.join(alg_path, 'maxevals_*'))):
        try:
            me = int(os.path.basename(me_dir).split('_')[1])
        except (IndexError, ValueError):
            continue
        funcs = {}
        for p in glob.glob(os.path.join(me_dir, 'f*.pkl')):
            try:
                with open(p, 'rb') as fh:
                    d = pickle.load(fh)
            except Exception:
                continue
            funcs[d['func']] = np.asarray(d['errors'], float)
        if funcs:
            out[me] = funcs
    return out


def collect(root, ref, vs, n, seeds, tol, cmp, fp, common):
    suite_config = common.suite_config
    cells = sorted(glob.glob(os.path.join(root, '*', 'd*')))
    rows = []
    skipped = []
    for base in cells:
        if not os.path.isdir(base):
            continue
        suite = os.path.basename(os.path.dirname(base)).lower()
        try:
            dim = int(os.path.basename(base).lstrip('dD'))
        except ValueError:
            continue
        if suite not in fp.CLASS_MAPS:
            continue

        # стандартен бюджет за тази (suite, dim) от benchmark/_common.py
        try:
            target = common.suite_default_maxevals(suite, dim)
        except (ValueError, KeyError):
            continue

        msc_b = _by_budget(os.path.join(base, ref))
        bip_b = _by_budget(os.path.join(base, vs))
        if target not in msc_b or target not in bip_b:
            skipped.append((suite, dim, target,
                            target in msc_b, target in bip_b))
            continue
        mf, bf = msc_b[target], bip_b[target]

        def _fnum(k):
            return int(str(k).lstrip('fF'))

        common_fns = sorted(set(mf) & set(bf), key=_fnum)
        for fn in common_fns:
            fnum = _fnum(fn)
            msc_med = float(np.median(cmp._floor(mf[fn])))
            vs_med = float(np.median(cmp._floor(bf[fn])))
            msc_wins = msc_med <= vs_med + tol

            cec_cls, bias, bounds = suite_config(suite, fnum, dim)
            cec = cec_cls(fnum, dim)
            d2 = []
            for sd in range(seeds):
                X = fp.sample(bounds, n, 'sobol', seed=sd)
                F = np.asarray(cec(X), float)
                d2.append(fp.funnel_metrics(X, F, bounds, compute_nbc=False,
                                            compute_persist=False)['disp2'])
            disp2 = float(np.mean(d2))
            pred_hard = disp2 > DISP2_THR
            agree = (pred_hard != msc_wins)

            rows.append((suite, dim, fnum, fp.classify(suite, fnum), msc_wins,
                         msc_med, vs_med, disp2, pred_hard, agree, target))
    return rows, skipped


def report(rows, vs='BIPOP-CMA', skipped=None):
    if not rows:
        print("Няма намерени клетки/данни под root.")
        if skipped:
            print(f"Пропуснати клетки (липсва стандартен бюджет): {skipped}")
        return
    vcol = (vs[:9] + '_med')
    hdr = (f"{'suite':>8} {'dim':>4} {'func':>5} {'type':>11} {'MSC<BIP':>8} "
           f"{'MSC_med':>11} {vcol:>13} {'disp2':>7} {'предсказ':>9} "
           f"{'съгл':>5}")
    print(hdr)
    print('-' * len(hdr))
    cur = None
    for r in rows:
        (suite, dim, fn, typ, wins, mm, bo, d2, hard, agree, budget) = r
        if (suite, dim) != cur:
            cur = (suite, dim)
            ncell = sum(1 for x in rows if (x[0], x[1]) == cur)
            print(f"{'·' * 20} {suite} d{dim} @ {budget:.0e}  "
                  f"({ncell} функции) {'·' * 10}")
        pred = 'MSC-HARD' if hard else 'MSC-OK'
        print(f"{suite:>8} {dim:>4} {'f' + str(fn):>5} {typ:>11} "
              f"{'да' if wins else 'не':>8} {mm:>11.3e} {bo:>13.3e} "
              f"{d2:>7.3f} {pred:>9} {'✓' if agree else '✗':>5}")

    # --- обобщения ---
    A = np.array([r[9] for r in rows])
    wins = np.array([r[4] for r in rows])
    hard = np.array([r[8] for r in rows])
    print("\n" + "=" * 64)
    print(f"ОБОБЩЕНИЕ: 'disp2 > {DISP2_THR} => MSC няма да бие {vs}'")
    print("=" * 64)
    print(f"  обща точност:                 {A.sum()}/{len(A)} = {A.mean():.0%}")
    nlose = (~wins).sum()
    nwin = wins.sum()
    tpr = (hard & ~wins).sum() / nlose if nlose else float('nan')
    spec = (~hard & wins).sum() / nwin if nwin else float('nan')
    print(f"  MSC губи от {vs[:9]}, HARD:  {(hard & ~wins).sum()}/{nlose} "
          f"= {tpr:.0%}  (TPR)")
    print(f"  MSC бие {vs[:9]}, дадено OK: {(~hard & wins).sum()}/{nwin} "
          f"= {spec:.0%}  (specificity)")

    print("\n  По клетка:")
    print(f"    {'suite':>8} {'dim':>4} {'n':>3} {'точност':>8}")
    cells = {}
    for r in rows:
        cells.setdefault((r[0], r[1]), []).append(r[9])
    for (suite, dim), a in sorted(cells.items()):
        a = np.array(a)
        print(f"    {suite:>8} {dim:>4} {len(a):>3} {a.mean():>7.0%}")

    print("\n  По вид CEC функция:")
    print(f"    {'type':>11} {'n':>3} {'MSC-печели':>11} {'disp2-OK':>9} "
          f"{'точност':>8}")
    types = {}
    for r in rows:
        types.setdefault(r[3], []).append(r)
    for typ in ['basic', 'hybrid', 'composition', 'other']:
        if typ not in types:
            continue
        rs = types[typ]
        w = np.mean([r[4] for r in rs])
        ok = np.mean([not r[8] for r in rs])
        acc = np.mean([r[9] for r in rs])
        print(f"    {typ:>11} {len(rs):>3} {w:>10.0%} {ok:>9.0%} {acc:>7.0%}")

    if skipped:
        print("\n  Пропуснати клетки (липсва стандартният бюджет):")
        for (suite, dim, target, in_msc, in_bip) in skipped:
            miss = []
            if not in_msc:
                miss.append('MSC')
            if not in_bip:
                miss.append(vs[:9])
            print(f"    {suite} d{dim} @ {target:.0e} — липсва: {', '.join(miss)}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='experiments')
    ap.add_argument('--ref', default='MSC-CMA')
    ap.add_argument('--vs', default='BIPOP-CMA', help='срещу кого (по подразбиране BIPOP-CMA)')
    ap.add_argument('--n', type=int, default=4096)
    ap.add_argument('--seeds', type=int, default=2)
    ap.add_argument('--tol', type=float, default=1e-9)
    args = ap.parse_args()

    THIS = os.path.dirname(os.path.abspath(__file__))
    cmp = _load('compare', os.path.join(THIS, 'analysis', 'compare.py'))
    fp = _load('funnel_probe', os.path.join(THIS, 'funnel_probe.py'))
    common = _load('_common', os.path.join(THIS, 'benchmark', '_common.py'))

    rows, skipped = collect(args.root, args.ref, args.vs, args.n, args.seeds,
                            args.tol, cmp, fp, common)
    report(rows, vs=args.vs, skipped=skipped)


if __name__ == '__main__':
    main()
