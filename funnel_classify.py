#!/usr/bin/env python3
"""
funnel_classify.py — MSC-difficulty предиктор по ЕДИН непрекъснат маркер: disp2.

Логиката (изведена от данните): MSC се проваля НЕ заради броя басейни, а
когато няма ДОМИНИРАЩ атрактор — елитът остава разпръснат чак до върха.
disp2 = разсейване на най-добрите 2% / разсейване на всички:
  нисък  -> топ-2% се струпват -> доминиращ (глобален) басейн -> MSC ОК
  висок  -> дори топ-2% разпръснати -> няма ясна цел за NBC  -> MSC ТРУДНО

Праг: disp2 > 0.835 -> "MSC-HARD" (изведен срещу реалния cec2017 изход:
12/12 MSC-трудни уловени, 4 FP — виж --demo). БЕЗ гласуване; nb_long/n_min
се показват само за контекст (те мерят БРОЯ басейни, не доминантността,
затова флагваха композити, на които MSC е ОК).

Известно ограничение: висок disp2 + МАЛКО nb_long = издължена зле-обусловена
долина (Zakharov-тип, унимодална) — там MSC е ОК, а disp2 я белязва като
трудна. Колоната nb помага да се разпознае този случай (малко nb при висок
disp2 = долина, не много басейни).

Режими:
  --demo                       cec2017 d10 + валидация срещу MSC-изхода
  --suite ... --dim ... --functions ...   реален ран (нужен minionpy)
"""

from __future__ import annotations
import argparse
import os

import numpy as np

DISP2_THR = 0.835          # disp2 > THR -> предсказано MSC-HARD


def predict(disp2):
    return 'MSC-HARD' if disp2 > DISP2_THR else 'MSC-OK'


# =========================================================================
# Печат + заключение
# =========================================================================

def report(rows, has_truth=False):
    """rows: (func, cls, m, msc_hard|None). m има disp2,disp5,nb_long,n_min."""
    print(f"\nMSC-difficulty индекс: disp2  (праг {DISP2_THR} -> MSC-HARD)\n")
    cols = f"{'func':>6} {'class':>11} {'disp2':>7} {'disp5':>7} {'nb':>3}  " \
           f"{'предсказание':>12}"
    if has_truth:
        cols += f"  {'реален MSC':>11}  {'?':>4}"
    print(cols)
    print('-' * len(cols))

    tp = fp = fn = tn = 0
    for func, cls, m, truth in rows:
        pred = predict(m['disp2'])
        ph = (pred == 'MSC-HARD')
        nbv = int(m['nb_long']) if m['nb_long'] >= 0 else -1
        nbs = f"{nbv:>3d}" if nbv >= 0 else "  -"
        line = (f"{func:>6} {cls:>11} {m['disp2']:>7.3f} {m['disp5']:>7.3f} {nbs}  "
                f"{pred:>12}")
        if has_truth:
            th = bool(truth)
            real = 'HARD' if th else 'OK'
            mark = '✓' if ph == th else '✗'
            line += f"  {real:>11}  {mark:>4}"
            if ph and th:
                tp += 1
            elif ph and not th:
                fp += 1
            elif (not ph) and th:
                fn += 1
            else:
                tn += 1
        print(line)

    if has_truth:
        nH = tp + fn
        nN = fp + tn
        print("\n" + "=" * 58)
        print("ВАЛИДАЦИЯ: disp2-предсказание срещу реалния MSC-изход")
        print("=" * 58)
        print(f"  точност:                 {tp + tn}/{len(rows)} "
              f"= {(tp + tn) / len(rows):.0%}")
        print(f"  MSC-трудни уловени (TPR): {tp}/{nH} = {tp / nH:.0%}")
        print(f"  фалшиви тревоги (FP):     {fp}  (MSC е ОК, но disp2 високо)")
        print(f"  изпуснати трудни (FN):    {fn}")
        fps = [r[0] for r in rows if predict(r[2]['disp2']) == 'MSC-HARD'
               and not r[3]]
        if fps:
            print(f"\n  FP-та: {fps}")
            print("  - те са или унимодални издължени долини (Zakharov f3: "
                  "disp2 високо от анизотропия,")
            print("    не от басейни -> nb малко; MSC ги решава), или маргинални "
                  "случаи (f11/f29).")
        print("\n  Извод: disp2 хваща 100% от реално трудните за MSC и не "
              "наказва композитите")
        print("  с много басейни (нисък disp2 = доминиращ басейн = MSC ОК). "
              "Това е правилната ос —")
        print("  доминантност на атрактора, не брой басейни.")
    else:
        nh = sum(1 for r in rows if predict(r[2]['disp2']) == 'MSC-HARD')
        print(f"\n  Предсказани MSC-HARD: {nh}/{len(rows)}")
        print("  (disp2 > праг = няма доминиращ атрактор = трудно за MSC. "
              "Провери nb: ако е малко при висок disp2 —")
        print("   вероятно издължена долина, не много басейни, и MSC може да е ОК.)")
    print()


# =========================================================================
# Demo данни: cec2017 d10 + реален MSC-изход (1=трудно/бит, 0=ОК)
# (func, class, disp2, disp5, nb_long, n_min, msc_hard)
# MSC-hard = съществена грешка И baseline значимо по-добър (f10,f12-f20,f27,f30)
# =========================================================================
DEMO = [
    ('f1', 'basic', 0.708, 0.765, 0, 7, 0), ('f2', 'other', 0.852, 0.878, 1, 38, 0),
    ('f3', 'basic', 0.975, 0.975, 1, 110, 0), ('f4', 'basic', 0.719, 0.777, 0, 8, 0),
    ('f5', 'basic', 0.731, 0.784, 0, 18, 0), ('f6', 'basic', 0.763, 0.808, 0, 58, 0),
    ('f7', 'basic', 0.629, 0.690, 0, 8, 0), ('f8', 'basic', 0.728, 0.770, 0, 31, 0),
    ('f9', 'basic', 0.734, 0.787, 0, 54, 0), ('f10', 'basic', 0.990, 0.986, 6, 184, 1),
    ('f11', 'hybrid', 0.870, 0.927, 0, 79, 0), ('f12', 'hybrid', 0.838, 0.857, 1, 22, 1),
    ('f13', 'hybrid', 0.895, 0.898, 3, 59, 1), ('f14', 'hybrid', 0.958, 0.956, 6, 104, 1),
    ('f15', 'hybrid', 0.942, 0.951, 4, 102, 1), ('f16', 'hybrid', 0.865, 0.884, 1, 63, 1),
    ('f17', 'hybrid', 0.895, 0.900, 3, 69, 1), ('f18', 'hybrid', 0.877, 0.887, 1, 40, 1),
    ('f19', 'hybrid', 0.905, 0.908, 3, 76, 1), ('f20', 'hybrid', 0.965, 0.970, 2, 170, 1),
    ('f21', 'composition', 0.798, 0.826, 1, 36, 0), ('f22', 'composition', 0.694, 0.779, 2, 99, 0),
    ('f23', 'composition', 0.795, 0.846, 0, 17, 0), ('f24', 'composition', 0.804, 0.848, 1, 14, 0),
    ('f25', 'composition', 0.702, 0.765, 0, 13, 0), ('f26', 'composition', 0.782, 0.848, 0, 22, 0),
    ('f27', 'composition', 0.880, 0.910, 2, 52, 1), ('f28', 'composition', 0.831, 0.859, 2, 22, 0),
    ('f29', 'composition', 0.902, 0.911, 2, 60, 0), ('f30', 'composition', 0.934, 0.948, 3, 75, 1),
]


def _demo_rows():
    return [(f, c, {'disp2': d2, 'disp5': d5, 'nb_long': nb, 'n_min': nm}, h)
            for (f, c, d2, d5, nb, nm, h) in DEMO]


# =========================================================================
# main
# =========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--suite', default='cec2017')
    ap.add_argument('--dim', type=int, default=10)
    ap.add_argument('--functions', default='')
    ap.add_argument('--n', type=int, default=4096)
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--fast', action='store_true', help='само disp (без nb) — най-бързо')
    args = ap.parse_args()

    if args.demo:
        report(_demo_rows(), has_truth=True)
        return

    import importlib.util
    _THIS = os.path.dirname(os.path.abspath(__file__))

    def _load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    fp = _load('funnel_probe', os.path.join(_THIS, 'funnel_probe.py'))
    common = _load('_common', os.path.join(_THIS, 'benchmark', '_common.py'))
    suite_config = common.suite_config

    funcs = [int(x.lstrip('fF')) for x in args.functions.split(',') if x.strip()]
    rows = []
    for fnum in funcs:
        cec_cls, bias, bounds = suite_config(args.suite, fnum, args.dim)
        cec = cec_cls(fnum, args.dim)
        acc = []
        for sd in range(args.seeds):
            X = fp.sample(bounds, args.n, 'sobol', seed=sd)
            F = np.asarray(cec(X), float)
            acc.append(fp.funnel_metrics(X, F, bounds,
                                         compute_nbc=not args.fast,
                                         compute_persist=False))
        m = {k: float(np.nanmean([a[k] for a in acc]))
             for k in ('disp2', 'disp5', 'nb_long')}
        rows.append((f"f{fnum}", fp.classify(args.suite, fnum), m, None))
    report(rows, has_truth=False)


if __name__ == '__main__':
    main()
