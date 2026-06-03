import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np, pandas as pd, importlib.util

SUITE, DIM, SEEDS, N = 'cec2017', 10, 3, 2048      # DIM=30 за другата клетка

def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
fp = load('funnel_probe', 'funnel_probe.py')
common = load('_common', os.path.join('benchmark', '_common.py'))
from pflacco.classical_ela_features import calculate_ela_meta, calculate_information_content

def cls(s, f):
    if s == 'cec2017': return 'hybrid' if 11<=f<=20 else 'composition' if 21<=f<=30 else 'basic'
    if s == 'cec2014': return 'hybrid' if 17<=f<=22 else 'composition' if 23<=f<=30 else 'basic'
    if s == 'cec2020': return 'hybrid' if 5<=f<=7 else 'composition' if 8<=f<=10 else 'basic'
    if s == 'cec2022': return 'hybrid' if 6<=f<=8 else 'composition' if 9<=f<=12 else 'basic'
    return 'other'
RNG = {'cec2017': range(11, 31), 'cec2014': range(17, 31),
       'cec2020': range(5, 11), 'cec2022': range(6, 13)}

rows = []
for fnum in RNG[SUITE]:
    cec_cls, bias, bounds = common.suite_config(SUITE, fnum, DIM); cec = cec_cls(fnum, DIM)
    cond, mbm, eps = [], [], []
    for sd in range(SEEDS):
        X = fp.sample(bounds, N, 'sobol', sd); F = np.asarray(cec(X), float)
        Xd, ys = pd.DataFrame(X), pd.Series(F)
        m = calculate_ela_meta(Xd, ys); ic = calculate_information_content(Xd, ys, seed=sd)
        cond.append(m['ela_meta.quad_simple.cond'])
        mbm.append(m['ela_meta.lin_simple.coef.max_by_min'])
        eps.append(ic['ic.eps_s'])
    rows.append((fnum, cls(SUITE, fnum), np.nanmean(cond), np.nanmean(mbm), np.nanmean(eps)))

print(f"\n{SUITE} d{DIM}   (sobol n={N}, seeds={SEEDS})\n")
print(f"{'func':>5} {'class':>11} {'cond':>11} {'max_by_min':>11} {'eps_s':>8}")
for fn, c, cd, mb, ep in rows:
    print(f"f{fn:<4} {c:>11} {cd:>11.3g} {mb:>11.3g} {ep:>8.3f}")

H = [r for r in rows if r[1] == 'hybrid']; C = [r for r in rows if r[1] == 'composition']
def stats(i, name):
    x = np.array([r[i] for r in H + C]); y = np.array([1]*len(H) + [0]*len(C))
    best = (0, 0)
    for t in np.unique(x):
        for a in (x > t, x >= t):
            acc = float(np.mean(a == y))
            if acc > best[0]: best = (acc, t)
    print(f"  {name:11} hybrid_mean={np.nanmean([r[i] for r in H]):.3g}  "
          f"comp_mean={np.nanmean([r[i] for r in C]):.3g}  "
          f"best-thr acc={best[0]:.0%} (>{best[1]:.3g})")
print(f"\nразделяне hybrid vs composition (n_h={len(H)}, n_c={len(C)}):")
stats(2, 'cond'); stats(3, 'max_by_min'); stats(4, 'eps_s')