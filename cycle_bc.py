#!/usr/bin/env python3
"""
cycle_bc.py — B/C принос от per-cycle данните в MSC pkl-ите.

За всеки run чете cycles -> (cycle, mode->B/C, cycle_local_best) и определя
кой клас (alt-0 / alt-1) е произвел крайния best (цикълът с min cycle_local_best).
Агрегира по клас (basic/hybrid/composition), по размерност, и колко от
подобрението носи всеки клас.

Робустен към формата:
  * pkl може да е RunResult обект, списък от тях, dict по seed, или dict с
    ключ 'runs'/'results'.
  * per-cycle елементите може да са CycleStats обекти, .as_dict() или dict-ове.
  * dict-ове само с {func, errors} (агрегатни) се прескачат (нямат cycles).

    python cycle_bc.py --inspect                      # покажи схемата на 1-я pkl
    python cycle_bc.py --root experiments --algo MSC-CMA
    python cycle_bc.py --glob 'experiments/cec2017/d30/MSC-CMA/maxevals_300000/f*.pkl'
    python cycle_bc.py --schedule C,B                  # alt-0=C, alt-1=B (по подразбиране)

Ако pkl-ите са pickle-нати RunResult ОБЕКТИ (не dict-ове), подай --proj <път>,
за да се качи algorithms/ на sys.path (иначе unpickle гърми за липсващ клас).
"""
from __future__ import annotations
import argparse, glob, os, pickle, sys, math
from collections import defaultdict


def G(o, *keys, default=None):
    """Чете ключ от dict ИЛИ атрибут от обект — каквото е налично."""
    for k in keys:
        if isinstance(o, dict):
            if k in o:
                return o[k]
        elif hasattr(o, k):
            return getattr(o, k)
    return default


def looks_like_run(o):
    return (G(o, 'cycles') is not None or G(o, 'fun') is not None
            or G(o, 'restarts') is not None)


def iter_runs(obj):
    """Yield-ва run-подобни обекти от произволна вложеност."""
    if looks_like_run(obj):
        yield obj
        return
    if isinstance(obj, dict):
        for key in ('runs', 'results', 'records', 'per_seed', 'seeds'):
            if key in obj:
                yield from iter_runs(obj[key])
                return
        for v in obj.values():
            yield from iter_runs(v)
        return
    if isinstance(obj, (list, tuple)):
        for v in obj:
            yield from iter_runs(v)


def cycles_of(run):
    cs = G(run, 'cycles', default=None)
    if cs is None:
        return []
    out = []
    for c in cs:
        out.append({
            'cycle': G(c, 'cycle'),
            'mode': G(c, 'mode', default='default'),
            'clb': G(c, 'cycle_local_best', default=math.inf),
            'imp': G(c, 'improvement', default=None),
            'bf_start': G(c, 'best_f_start'),
            'bf_end': G(c, 'best_f_end'),
            'sampling': G(c, 'sampling_method', default='?'),
        })
    return out


def cls(suite, f):
    f = int(str(f).lstrip('fF'))
    if suite == 'cec2014': return 'hybrid' if 17<=f<=22 else 'composition' if 23<=f<=30 else 'basic'
    if suite == 'cec2017': return 'hybrid' if 11<=f<=20 else 'composition' if 21<=f<=30 else 'basic'
    if suite == 'cec2020': return 'hybrid' if 5<=f<=7 else 'composition' if 8<=f<=10 else 'basic'
    if suite == 'cec2022': return 'hybrid' if 6<=f<=8 else 'composition' if 9<=f<=12 else 'basic'
    return 'other'


def parse_path(p):
    """experiments/<suite>/d<dim>/<algo>/maxevals_<N>/f<fnum>.pkl"""
    parts = p.replace('\\', '/').split('/')
    suite = dim = fnum = None
    for i, x in enumerate(parts):
        if x.startswith('cec'): suite = x
        elif x.startswith('d') and x[1:].isdigit(): dim = int(x[1:])
    base = os.path.basename(p)
    if base.startswith('f'):
        digits = ''.join(ch for ch in base[1:] if ch.isdigit())
        fnum = int(digits) if digits else None
    return suite, dim, fnum


def load(path):
    with open(path, 'rb') as fh:
        return pickle.load(fh)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='experiments')
    ap.add_argument('--algo', default='MSC-CMA')
    ap.add_argument('--glob', default='', help='пряк glob; пренаписва --root/--algo')
    ap.add_argument('--proj', default='', help='път до проекта (за unpickle на RunResult обекти)')
    ap.add_argument('--schedule', default='C,B', help='ред на разписанието: alt-0,alt-1,... (по подразбиране C,B)')
    ap.add_argument('--inspect', action='store_true', help='покажи схемата на 1-я pkl и спри')
    args = ap.parse_args()

    if args.proj:
        sys.path.insert(0, args.proj)
        sys.path.insert(0, os.path.join(args.proj, 'algorithms'))

    labels = args.schedule.split(',')
    idx2lab = {f'alt-{i}': lab.strip() for i, lab in enumerate(labels)}
    idx2lab['default'] = '-'

    pattern = args.glob or os.path.join(args.root, '*', 'd*', args.algo,
                                        'maxevals_*', 'f*.pkl')
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"Няма pkl-ове по: {pattern}")

    if args.inspect:
        obj = load(files[0])
        print(f"pkl: {files[0]}\n top-level type: {type(obj).__name__}")
        if isinstance(obj, dict):
            print(f" dict keys: {list(obj.keys())}")
        runs = list(iter_runs(obj))
        print(f" намерени run-ове: {len(runs)}")
        if runs:
            cy = cycles_of(runs[0])
            print(f" cycles в 1-я run: {len(cy)}")
            if cy:
                print(f" пример cycle: {cy[0]}")
        else:
            print(" (няма cycles — вероятно агрегатен {func,errors} pkl)")
        return

    # win[(class)][label] += 1 ; imp[(class)][label] += подобрение
    win = defaultdict(lambda: defaultdict(int))
    imp = defaultdict(lambda: defaultdict(float))
    n_runs = defaultdict(int)
    no_cycle = 0
    perdim = defaultdict(lambda: defaultdict(int))

    for p in files:
        suite, dim, fnum = parse_path(p)
        c = cls(suite, fnum) if (suite and fnum) else 'other'
        try:
            obj = load(p)
        except Exception as e:
            print(f"  ! пропускам {p}: {type(e).__name__}: {e}")
            continue
        for run in iter_runs(obj):
            cy = cycles_of(run)
            if not cy:
                no_cycle += 1
                continue
            n_runs[c] += 1
            # принос по mode (подобрение)
            for r in cy:
                lab = idx2lab.get(r['mode'], r['mode'])
                d = r['imp']
                if d is None and r['bf_start'] is not None and r['bf_end'] is not None:
                    d = r['bf_start'] - r['bf_end']
                if d and d > 0:
                    imp[c][lab] += d
            # кой клас даде крайния best (цикъл с min cycle_local_best)
            fin = [r for r in cy if r['clb'] is not None and math.isfinite(r['clb'])]
            if fin:
                w = min(fin, key=lambda r: r['clb'])
                lab = idx2lab.get(w['mode'], w['mode'])
                win[c][lab] += 1
                perdim[(c, dim)][lab] += 1

    if not n_runs:
        print(f"Намерих {len(files)} pkl-а, но 0 с per-cycle данни "
              f"({no_cycle} без cycles). Това са агрегатни pkl-ове — "
              f"трябват RunResult (--save-pkl) pkl-ове. Пробвай --inspect.")
        return

    labs = labels + ['-']
    print(f"\nКраен best — от кой клас (цикъл с min cycle_local_best):\n")
    print(f"  {'клас':>12} {'runs':>5} " + " ".join(f"{l:>8}" for l in labs))
    for c in ['basic', 'hybrid', 'composition', 'other']:
        if not n_runs.get(c):
            continue
        tot = sum(win[c].values()) or 1
        cells = " ".join(f"{win[c].get(l,0)/tot:>7.0%}" for l in labs)
        print(f"  {c:>12} {n_runs[c]:>5} {cells}")

    print(f"\nПодобрение (сума best_f drop), дял по клас:\n")
    print(f"  {'клас':>12} " + " ".join(f"{l:>8}" for l in labs))
    for c in ['basic', 'hybrid', 'composition', 'other']:
        if not imp.get(c):
            continue
        tot = sum(imp[c].values()) or 1.0
        cells = " ".join(f"{imp[c].get(l,0.0)/tot:>7.0%}" for l in labs)
        print(f"  {c:>12} {cells}")

    if no_cycle:
        print(f"\n  ({no_cycle} pkl-а без per-cycle данни — прескочени.)")
    print()


if __name__ == '__main__':
    main()
