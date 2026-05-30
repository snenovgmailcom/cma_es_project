#!/usr/bin/env python3
"""Driver: run all non-MSC minionpy (C++) baselines across a grid of cells.

Lays results in experiments/<suite>/d<dim>/<ALGO>/maxevals_<N>/ via the runners'
own build_outdir, so naming stays canonical ('-minionpy' suffix).

Resumable: per (cell, algo) computes which functions are still TODO (pkl absent,
or present-but-corrupt: <runs seeds / NaN / inf) and passes only those. Completed
functions are never touched. Each cell-algo is a fresh subprocess -> memory fully
released between runs (kills loky/minionpy worker-accumulation across the grid).

BIPOP (pycma, slow) and MSC-CMA are NOT here -- run separately.
"""
import argparse, os, pickle, subprocess, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (suite_config, suite_default_maxevals, build_outdir,
                     ALGO_ARRDE, ALGO_JSO, ALGO_J2020,
                     ALGO_NLSHADE_RSP, ALGO_LSRTDE)

MINION_ALGOS = [
    ('benchmark.arrde',       ALGO_ARRDE),
    ('benchmark.jso',         ALGO_JSO),
    ('benchmark.j2020',       ALGO_J2020),
    ('benchmark.nlshade_rsp', ALGO_NLSHADE_RSP),
    ('benchmark.lsrtde',      ALGO_LSRTDE),
    # Dropped per agreed set (redundant/dominated for D<=30); uncomment if needed:
    # ('benchmark.lshade',         'LSHADE-minionpy'),
    # ('benchmark.lshade_cnepsin', 'LSHADE-cnEpSin-minionpy'),
    ('benchmark.bipop',       'BIPOP-CMA-pycma'),
]

SUITE_MAXF = {'cec2014': 30, 'cec2017': 30, 'cec2019': 10,
              'cec2020': 10, 'cec2022': 12}

# === EDIT: grid of cells. (suite, dim, maxevals)  maxevals=0 -> suite default ===
CELLS = [
    ('cec2017',  2,   20000),
    ('cec2017',  2,   40000),
    ('cec2017', 10,       0),
    ('cec2017', 30,       0),
    ('cec2017', 30,  600000),
    ('cec2014', 10,       0),
    ('cec2014', 30,       0),
    ('cec2019',  9,       0),   # F1 only (auto-detected)
    ('cec2019', 10,       0),   # F4-F10
    ('cec2019', 16,       0),   # F2 only
    ('cec2019', 18,       0),   # F3 only
    ('cec2020',  5,   50000),
    ('cec2020',  5,  100000),
    ('cec2020', 10, 1000000),
    ('cec2020', 15, 3000000),
    ('cec2022', 10,  200000),
    ('cec2022', 20, 1000000),
]


def valid_functions(suite, dim):
    ok = []
    center = [[0.0] * dim]
    for k in range(1, SUITE_MAXF[suite] + 1):
        try:
            cls, _b, _bb = suite_config(suite, k, dim)
            f = cls(k, dim); _ = f(center)
            ok.append(k)
        except Exception:
            pass
    return ok


def func_status(outdir, k, runs):
    p = os.path.join(outdir, f'f{k}.pkl')
    if not os.path.exists(p):
        return 'missing'
    try:
        e = np.asarray(pickle.load(open(p, 'rb'))['errors'], dtype=float)
    except Exception:
        return 'bad'
    if len(e) < runs or np.isnan(e).any() or np.isinf(e).any():
        return 'bad'
    return 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=int, default=51)
    ap.add_argument('--jobs', type=int, default=51)
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--algos', type=str, default='')
    ap.add_argument('--logdir', type=str, default='logs')
    args = ap.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    restrict = {a.strip().lower() for a in args.algos.split(',') if a.strip()}

    plan, skipped = [], []
    for suite, dim, mx in CELLS:
        mx = mx or suite_default_maxevals(suite, dim)
        funcs = valid_functions(suite, dim)
        for mod, algo in MINION_ALGOS:
            if restrict and algo.split('-')[0].lower() not in restrict:
                continue
            outdir = build_outdir(suite, dim, algo, mx)
            if args.force:
                todo, force_needed = funcs, True
            else:
                st = {k: func_status(outdir, k, args.runs) for k in funcs}
                todo = [k for k in funcs if st[k] != 'ok']
                force_needed = any(st[k] == 'bad' for k in todo)
            if not todo:
                skipped.append((suite, dim, mx, algo))
            else:
                plan.append((suite, dim, mx, todo, mod, algo, outdir, force_needed))

    print(f'=== PLAN: {len(plan)} run(s), {len(skipped)} complete (skip) ===')
    for s, d, m, a in skipped:
        print(f'  SKIP {a:24s} {s} D={d:<2d} {m}')
    for s, d, m, todo, mod, a, od, fn in plan:
        print(f'  RUN  {a:24s} {s} D={d:<2d} {m}  {len(todo)}f'
              f'{" (force: corrupt)" if fn else ""}')
    if args.dry_run:
        return

    t_all = time.time()
    for i, (suite, dim, mx, todo, mod, algo, outdir, fn) in enumerate(plan, 1):
        cmd = [sys.executable, '-m', mod, '--suite', suite, '--dim', str(dim),
               '--functions', ','.join(map(str, todo)),
               '--runs', str(args.runs), '--jobs', str(args.jobs),
               '--maxevals', str(mx), '--outdir', outdir]
        if fn:
            cmd.append('--force')
        log = os.path.join(args.logdir, f'{algo}_{suite}_d{dim}_{mx}.log')
        print(f'[{i}/{len(plan)}] {algo} {suite} D={dim} {mx} '
              f'({len(todo)}f) -> {log}', flush=True)
        t0 = time.time()
        with open(log, 'w') as lf:
            rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT).returncode
        print(f'      {"ok" if rc == 0 else f"FAIL rc={rc}"} in {time.time()-t0:.0f}s',
              flush=True)
    print(f'=== done in {time.time()-t_all:.0f}s ===')


if __name__ == '__main__':
    main()
