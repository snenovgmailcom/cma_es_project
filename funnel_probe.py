#!/usr/bin/env python3
"""
funnel_probe.py — funnel-detection метрики върху Phase-0 извадка.

За всяка функция взима LHS/Sobol извадка (както Phase-0), оценява я и смята
ELA funnel-сигналите, БЕЗ staircase (фиксирано φ), за да видим дали дадена
функция е фуния (един глобален trend + плитки локални минимуми) или
разделени басейни.

Дискриминатори (Lunacek-Whitley dispersion + Preuss/Kerschke NBC):
  disp_q{2,5,10}   mean pairwise dist(най-добрите q%) / mean pairwise dist(всички)
                     ниско (<~0.7) -> елитът се струпва -> ЕДНА фуния
                     високо (>~1)  -> елитът е разпръснат -> мулти/басейни
  nb_long          брой nb-ръбове > φ·mean(nb)  (φ по подразбиране 2.0)
                     ≈ брой мостове между фунии; +1 ≈ брой компоненти
                     малко (~0-1) -> една фуния; много -> разделени басейни
  nn_nb_mean       mean(nn)/mean(nb): ~1 -> по-добър съсед винаги наблизо (фуния)
  nbfit_cor        Spearman(F, indegree): силно отрицателна -> един атрактор

Употреба
--------
    # реален CEC ран (нужен е minionpy, на srv-01):
    python funnel_probe.py --suite cec2017 --dim 10 --functions $(seq -s, 1 30)

    # валидация върху известни пейзажи (без suite):
    python funnel_probe.py --selftest
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import qmc, spearmanr


# =========================================================================
# Метрики
# =========================================================================

def _mean_pairwise(Xn):
    """Средно двойно разстояние (върху нормирани [0,1] координати)."""
    m = len(Xn)
    if m < 2:
        return np.nan
    if m > 1200:                       # subsample за скорост
        idx = np.random.default_rng(0).choice(m, 1200, replace=False)
        Xn = Xn[idx]
        m = 1200
    D = cdist(Xn, Xn)
    iu = np.triu_indices(m, k=1)
    return float(D[iu].mean())


def persistence_metrics(Xn, F, k=20):
    """Morse-Smale merge-tree персистентност върху kNN граф.

    Обхожда точките във възходящ ред по F (water-filling). Нова точка без
    по-нисък съсед = нов минимум (раждане на басейн). Точка, чиито по-ниски
    съседи са в >=2 басейна = saddle: по-младият басейн (с по-висок min)
    умира, persistence = F(saddle) - min(умиращия). Глобалният басейн има
    +inf (не умира) и не влиза в статистиките.

    Връща: n_min (брой минимуми), max_pers_rel, mean_pers_top5_rel
    (персистентности, нормирани по обхвата на F => скейл-свободни).
    """
    from scipy.spatial import cKDTree
    N = len(F)
    kk = min(k + 1, N)
    tree = cKDTree(Xn)
    _, knn = tree.query(Xn, k=kk)
    order = np.argsort(F)

    uf = np.arange(N)
    best = np.full(N, np.inf)
    processed = np.zeros(N, bool)

    def find(a):
        while uf[a] != a:
            uf[a] = uf[uf[a]]
            a = uf[a]
        return a

    persist = []
    n_min = 0
    for idx in order:
        processed[idx] = True
        roots = {find(j) for j in knn[idx] if j != idx and processed[j]}
        if not roots:
            uf[idx] = idx
            best[idx] = F[idx]
            n_min += 1
            continue
        roots = sorted(roots, key=lambda r: best[r])
        survivor = roots[0]
        uf[idx] = survivor
        for r in roots[1:]:
            persist.append(F[idx] - best[r])   # r умира при saddle F[idx]
            uf[r] = survivor
        # best[survivor] вече е най-ниският; idx има по-висок F -> не го сваля

    frange = float(F.max() - F.min())
    if persist and frange > 0:
        pr = np.sort(np.array(persist) / frange)[::-1]
        return {'n_min': n_min, 'max_pers': float(pr[0]),
                'mean_pers5': float(pr[:5].mean())}
    return {'n_min': n_min, 'max_pers': 0.0, 'mean_pers5': 0.0}


def funnel_metrics(X, F, bounds, phi=2.0, compute_nbc=True, compute_persist=True):
    """X: (N,d) точки; F: (N,) стойности; bounds: (d,2)."""
    X = np.asarray(X, float)
    F = np.asarray(F, float)
    N, d = X.shape
    lb, ub = bounds[:, 0], bounds[:, 1]
    Xn = (X - lb) / (ub - lb)          # нормирани координати [0,1]

    # --- dispersion (Lunacek-Whitley) ---
    disp_all = _mean_pairwise(Xn)
    order = np.argsort(F)
    disp = {}
    for q in (2, 5, 10):
        m = max(2, int(np.ceil(q / 100.0 * N)))
        best = Xn[order[:m]]
        disp[q] = _mean_pairwise(best) / disp_all if disp_all else np.nan

    out = {'disp2': disp[2], 'disp5': disp[5], 'disp10': disp[10], 'N': N,
           'nb_long': -1, 'nn_nb_mean': np.nan, 'nbfit_cor': np.nan,
           'n_min': -1, 'max_pers': np.nan, 'mean_pers5': np.nan}

    # --- NBC (nearest-better) — само ако е поискано (скъпото cdist) ---
    if compute_nbc:
        D = cdist(Xn, Xn).astype(np.float32)
        np.fill_diagonal(D, np.inf)
        nn = D.min(axis=1)
        better = F[None, :] < F[:, None]
        Db = np.where(better, D, np.inf)
        nb = Db.min(axis=1)
        nb_arg = Db.argmin(axis=1)
        finite = np.isfinite(nb)
        nb_f = nb[finite]
        thr = phi * nb_f.mean()
        out['nb_long'] = int((nb_f > thr).sum())
        out['nn_nb_mean'] = (float(nn[finite].mean() / nb_f.mean())
                             if nb_f.mean() else np.nan)
        indeg = np.bincount(nb_arg[finite], minlength=N).astype(float)
        try:
            out['nbfit_cor'] = float(spearmanr(F, indeg).correlation)
        except Exception:
            out['nbfit_cor'] = np.nan

    # --- персистентност — само ако е поискано ---
    if compute_persist:
        pers = persistence_metrics(Xn, F)
        out['n_min'] = pers['n_min']
        out['max_pers'] = pers['max_pers']
        out['mean_pers5'] = pers['mean_pers5']

    return out


# =========================================================================
# Класификация на функциите (както pkl_stats)
# =========================================================================

CLASS_MAPS = {
    'cec2017': lambda f: ('hybrid' if 11 <= f <= 20 else
                          'composition' if 21 <= f <= 30 else
                          'basic' if f in (1, 3, 4, 5, 6, 7, 8, 9, 10) else 'other'),
    'cec2014': lambda f: ('hybrid' if 17 <= f <= 22 else
                          'composition' if 23 <= f <= 30 else
                          'basic' if 1 <= f <= 16 else 'other'),
    'cec2020': lambda f: ('hybrid' if 5 <= f <= 7 else
                          'composition' if 8 <= f <= 10 else
                          'basic' if 1 <= f <= 4 else 'other'),
    'cec2022': lambda f: ('hybrid' if 6 <= f <= 8 else
                          'composition' if 9 <= f <= 12 else
                          'basic' if 1 <= f <= 5 else 'other'),
}


def classify(suite, f):
    fn = CLASS_MAPS.get(suite)
    return fn(f) if fn else 'other'


# =========================================================================
# Sampling
# =========================================================================

def sample(bounds, n, sampler='sobol', seed=0):
    d = len(bounds)
    lb, ub = bounds[:, 0], bounds[:, 1]
    if sampler == 'sobol':
        eng = qmc.Sobol(d=d, scramble=True, seed=seed)
        U = eng.random(n)
    elif sampler == 'lhs':
        eng = qmc.LatinHypercube(d=d, seed=seed)
        U = eng.random(n)
    else:
        U = np.random.default_rng(seed).random((n, d))
    return lb + U * (ub - lb)


# =========================================================================
# Selftest landscapes (известна структура)
# =========================================================================

def _make_selftest(d=10):
    rng = np.random.default_rng(7)
    B = np.array([[-5.0, 5.0]] * d)

    def sphere(X):                     # чиста единична фуния
        return np.sum(X ** 2, axis=1)

    def rastrigin(X):                  # ЕДНА фуния + плитки локални минимуми
        return 10 * d + np.sum(X ** 2 - 10 * np.cos(2 * np.pi * X), axis=1)

    def lunacek(X):                    # ДВОЙНА фуния (deceptive)
        mu1 = 2.5
        s = 1 - 1 / (2 * np.sqrt(d + 20) - 8.2)
        mu2 = -np.sqrt((mu1 ** 2 - 1) / s)
        t1 = np.sum((X - mu1) ** 2, axis=1)
        t2 = d + s * np.sum((X - mu2) ** 2, axis=1)
        sph = np.minimum(t1, t2)
        rast = 10 * np.sum(1 - np.cos(2 * np.pi * (X - mu1)), axis=1)
        return sph + rast

    # 8 тесни, добре разделени кладенеца с РАЗЛИЧНИ дълбочини -> ЯСНИ басейни
    # (composition-подобно: един глобален + няколко дълбоки отделени локални).
    centers = rng.uniform(-4, 4, size=(8, d))
    depths = np.linspace(0.0, 7.0, 8)          # отчетлива наредба между басейните

    def wells(X):
        out = np.full(len(X), 80.0)            # висок фон между кладенците
        for c, dep in zip(centers, depths):
            r2 = np.sum((X - c) ** 2, axis=1)
            out = np.minimum(out, dep + 3.0 * r2)   # стръмни (тесни) кладенци
        return out

    return [('sphere(1-funnel)', sphere, B),
            ('rastrigin(1-funnel)', rastrigin, B),
            ('lunacek(2-funnel)', lunacek, B),
            ('8-wells(basins)', wells, B)]


# =========================================================================
# Печат
# =========================================================================

def print_rows(rows, title):
    print(f"\n# {title}\n")
    hdr = (f"{'func':>20} {'class':>11} {'disp2':>7} {'disp5':>7} "
           f"{'nb_long':>8} {'nn/nb':>7} {'n_min':>6} {'maxP':>6} {'mP5':>6}")
    print(hdr)
    print('-' * len(hdr))
    for name, cls, m in rows:
        print(f"{name:>20} {cls:>11} {m['disp2']:>7.3f} {m['disp5']:>7.3f} "
              f"{int(round(m['nb_long'])):>8d} {m['nn_nb_mean']:>7.3f} "
              f"{int(round(m['n_min'])):>6d} "
              f"{m['max_pers']:>6.3f} {m['mean_pers5']:>6.3f}")

    classes = {}
    for _, cls, m in rows:
        classes.setdefault(cls, []).append(m)
    if len(classes) > 1:
        print('\n   по клас (средно)\n')
        chdr = (f"{'class':>12} {'nF':>3} {'disp2':>7} {'disp5':>7} "
                f"{'nb_long':>8} {'n_min':>6} {'maxP':>6} {'mP5':>6}")
        print(chdr)
        print('-' * len(chdr))
        for cls in ['basic', 'hybrid', 'composition', 'other']:
            if cls not in classes:
                continue
            ms = classes[cls]
            def am(key):
                return float(np.nanmean([m[key] for m in ms]))
            print(f"{cls:>12} {len(ms):>3} {am('disp2'):>7.3f} "
                  f"{am('disp5'):>7.3f} {am('nb_long'):>8.1f} "
                  f"{am('n_min'):>6.1f} {am('max_pers'):>6.3f} "
                  f"{am('mean_pers5'):>6.3f}")
    print("\nФуния/плитко: ниско maxP/mP5 (басейните се сливат бързо). "
          "Ясни дълбоки басейни: високо maxP/mP5. n_min=брой минимуми, "
          "maxP/mP5=макс / ср.-топ5 персистентност (нормирана по обхвата на F).\n")


# =========================================================================
# main
# =========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--suite', default='cec2017')
    ap.add_argument('--dim', type=int, default=10)
    ap.add_argument('--functions', default='')
    ap.add_argument('--n', type=int, default=2000, help='брой точки в извадката')
    ap.add_argument('--phi', type=float, default=2.0)
    ap.add_argument('--sampler', choices=['sobol', 'lhs', 'uniform'], default='sobol')
    ap.add_argument('--seeds', type=int, default=3, help='усредни по толкова извадки')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()

    if args.selftest:
        rows = []
        for name, fn, B in _make_selftest(args.dim):
            accum = []
            for s in range(args.seeds):
                X = sample(B, args.n, args.sampler, seed=s)
                F = fn(X)
                accum.append(funnel_metrics(X, F, B, phi=args.phi))
            m = {k: float(np.nanmean([a[k] for a in accum])) for k in accum[0]}
            m['nb_long'] = int(round(m['nb_long']))
            m['n_min'] = int(round(m['n_min']))
            rows.append((name, 'selftest', m))
        print_rows(rows, f"SELFTEST  d={args.dim}  n={args.n}  sampler={args.sampler}")
        return

    # реален CEC ран
    _THIS = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(_THIS, 'benchmark'))
    from _common import suite_config

    funcs = [int(x.lstrip('fF')) for x in args.functions.split(',') if x.strip()]
    rows = []
    for fnum in funcs:
        cec_cls, bias, bounds = suite_config(args.suite, fnum, args.dim)
        cec = cec_cls(fnum, args.dim)
        accum = []
        for s in range(args.seeds):
            X = sample(bounds, args.n, args.sampler, seed=s)
            F = np.asarray(cec(X), float)
            accum.append(funnel_metrics(X, F, bounds, phi=args.phi))
        m = {k: float(np.nanmean([a[k] for a in accum])) for k in accum[0]}
        m['nb_long'] = int(round(m['nb_long']))
        rows.append((f"f{fnum}", classify(args.suite, fnum), m))
    print_rows(rows, f"{args.suite} d={args.dim} n={args.n} "
                     f"sampler={args.sampler} seeds={args.seeds}")


if __name__ == '__main__':
    main()
