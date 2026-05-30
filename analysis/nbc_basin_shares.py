#!/usr/bin/env python3
"""
nbc_basin_shares.py

For each (suite, fnum, seed), run the canonical NBC partition (Preuss phi-cut
+ Lin min-size + Lin max-share recursion) on a fresh LHS sample and extract
basin-dominance descriptors:

  top1_share        size(largest basin)  / N
  top2_share        size(2nd largest)    / N
  top3_share        size(3rd largest)    / N
  top1_minus_top2   primary dominance score:
                      ~ 1.0  -> single dominant basin (NBC saw nothing)
                      ~ 0.0  -> top-2 are evenly matched (real bi-modality)
  top1_div_top2     ratio variant (less sensitive to partition granularity)
  effective_n       exp(Shannon entropy of size distribution): soft basin count
  size_gini         Gini coefficient of basin sizes (0=uniform, 1=concentrated)
  n_basins          actual number of basins after Preuss+Lin

Reuses sbisection.nb_tree_indices and sbisection.nbc_partition_preuss_lin
verbatim. Default knobs match the v26 paper baseline.

Hypothesis to test:
  high (top1 - top2) -> Phase-0 has nothing to seed from -> MSC underperforms
  low  (top1 - top2) -> Phase-0 finds genuine basin centers -> MSC wins

Output CSV is intended to be merged with compare.py results to compute
Spearman corr( descriptor, log10(MSC_mean / ARRDE_mean) ).

Usage
-----
    python analysis/nbc_basin_shares.py \\
        --suite cec2017 --dim 10 --seeds 10 --jobs 20

    python analysis/nbc_basin_shares.py \\
        --suite cec2014,cec2017,cec2020,cec2022 --dim 10 --seeds 10
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

# Make sibling imports work regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sbisection import (SUITE_CONFIG, GROUND_TRUTH,
                        nb_tree_indices, nbc_partition_preuss_lin)


def compute_one(args):
    (suite, fnum, dim, seed, m_factor,
     phi, min_basin_size, max_share) = args

    from scipy.stats import qmc
    from minionpy import (CEC2014Functions, CEC2017Functions,
                          CEC2020Functions, CEC2022Functions)
    cls_map = {'cec2014': CEC2014Functions, 'cec2017': CEC2017Functions,
               'cec2020': CEC2020Functions, 'cec2022': CEC2022Functions}
    f = cls_map[suite](fnum, dim)

    out = {'suite': suite, 'fnum': fnum, 'seed': seed, 'dim': dim,
           'phi': phi, 'min_basin_size': min_basin_size,
           'max_share': max_share}

    try:
        # 1. LHS sample (identical to sbisection.py for direct comparability)
        n_points = m_factor * dim
        lhs = qmc.LatinHypercube(d=dim, seed=seed)
        unit = lhs.random(n_points)
        bounds_lo = np.full(dim, -100.0)
        bounds_hi = np.full(dim, 100.0)
        X = qmc.scale(unit, bounds_lo, bounds_hi)
        X_norm = (X - bounds_lo) / (bounds_hi - bounds_lo)

        y_native = np.asarray(f([row.tolist() for row in X]),
                              dtype=np.float64).ravel()
        # Normalize y to [0,1] (NBC ranking is invariant; this just keeps
        # things comparable across suites).
        y_range = float(y_native.max() - y_native.min())
        if y_range > 0:
            y = (y_native - y_native.min()) / y_range
        else:
            y = y_native - y_native.min()

        out['sample_n'] = int(n_points)
        out['f_range'] = y_range

        # 2. Exact NB tree (uses the prefix-KDTree implementation in
        # sbisection.py — NOT the v26 nb_tree.cpp module, which has a
        # k_cap=256 fallback that pollutes the longest-edge analysis).
        nb_idx, nb_dist = nb_tree_indices(X_norm, y)

        # 3. Canonical Preuss + Lin partition
        all_indices = np.arange(n_points)
        basins = nbc_partition_preuss_lin(
            all_indices, X_norm, y, nb_idx, nb_dist,
            phi=phi, min_size=min_basin_size, max_share=max_share)

        # 4. Basin-share descriptors
        sizes = np.array(sorted([len(b) for b in basins], reverse=True),
                         dtype=np.float64)
        n = float(sizes.sum())
        out['n_basins'] = int(len(sizes))
        out['max_basin_size'] = int(sizes[0])
        out['min_basin_size_actual'] = int(sizes[-1])
        out['size_list_json'] = json.dumps(sizes.astype(int).tolist())

        if n > 0:
            shares = sizes / n
            out['top1_share'] = float(shares[0])
            out['top2_share'] = float(shares[1]) if len(shares) > 1 else 0.0
            out['top3_share'] = float(shares[2]) if len(shares) > 2 else 0.0
            out['top1_minus_top2'] = out['top1_share'] - out['top2_share']
            if out['top2_share'] > 0:
                out['top1_div_top2'] = out['top1_share'] / out['top2_share']
            else:
                out['top1_div_top2'] = float('inf')

            # Effective number of basins via Shannon entropy
            #   H = -sum(p_i log p_i),   N_eff = exp(H)
            # H=0 (one basin) -> N_eff=1.  H=log(K) (uniform K basins) -> N_eff=K.
            p = shares[shares > 0]
            H = float(-(p * np.log(p)).sum())
            out['entropy'] = H
            out['effective_n'] = float(np.exp(H))

            # Gini coefficient on basin sizes (existing sbisection.py formula)
            if len(sizes) > 1:
                k = len(sizes)
                cum = np.cumsum(np.sort(sizes))
                gini = (2 * np.sum((np.arange(1, k + 1)) *
                                    np.sort(sizes))) / (k * cum[-1]) \
                       - (k + 1) / k
                out['size_gini'] = float(gini)
            else:
                out['size_gini'] = 0.0
        else:
            for k in ('top1_share', 'top2_share', 'top3_share',
                      'top1_minus_top2', 'top1_div_top2',
                      'entropy', 'effective_n', 'size_gini'):
                out[k] = float('nan')

    except Exception as exc:
        import traceback
        out['error'] = f'{type(exc).__name__}: {exc}'
        out['traceback'] = traceback.format_exc()[:500]

    out['ground_truth_label'] = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
    return out


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True,
                   help='Comma-separated: cec2014,cec2017,cec2020,cec2022')
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--seeds', type=int, default=10)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--functions', type=str, default=None,
                   help='Optional subset, e.g. "11-30". Default: all.')
    p.add_argument('--jobs', type=int, default=20)
    p.add_argument('--m-factor', type=int, default=850,
                   help='Sample size = m_factor * dim. Default 850 (v26).')
    p.add_argument('--phi', type=float, default=2.0,
                   help='Preuss phi-cut: edges > phi * mean_edge_length cut. '
                        'Default 2.0 (canonical Preuss).')
    p.add_argument('--min-basin-size', type=int, default=None,
                   help='Lin min-size constraint. Default: dim.')
    p.add_argument('--max-share', type=float, default=0.5,
                   help='Lin max-share recursion threshold. Default 0.5.')
    p.add_argument('--out', default=None)
    args = p.parse_args()

    if args.min_basin_size is None:
        args.min_basin_size = args.dim

    suite_list = [s.strip() for s in args.suite.split(',')]
    for s in suite_list:
        if s not in SUITE_CONFIG:
            print(f'Unknown suite: {s}. Choices: {list(SUITE_CONFIG.keys())}',
                  file=sys.stderr)
            sys.exit(1)

    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    tasks = []
    suite_funcs = {}
    for suite in suite_list:
        n_funcs, _ = SUITE_CONFIG[suite]
        if args.functions:
            func_list = []
            for part in args.functions.split(','):
                if '-' in part:
                    lo, hi = part.split('-')
                    func_list.extend(range(int(lo), int(hi) + 1))
                else:
                    func_list.append(int(part))
            func_list = [f for f in func_list if 1 <= f <= n_funcs]
        else:
            func_list = list(range(1, n_funcs + 1))
        suite_funcs[suite] = func_list
        for fnum in func_list:
            for seed in seeds:
                tasks.append((suite, fnum, args.dim, seed, args.m_factor,
                              args.phi, args.min_basin_size, args.max_share))

    out = args.out or (f'nbc_basin_shares_{"_".join(suite_list)}_d{args.dim}.csv')

    print('=== NBC basin-dominance descriptors ===')
    print(f'  Suites:       {", ".join(suite_list)}')
    for s in suite_list:
        fl = suite_funcs[s]
        print(f'    {s}: {len(fl)} funcs ({fl[0]}..{fl[-1]})')
    print(f'  Dim:          D={args.dim}')
    print(f'  Seeds:        {len(seeds)}  ({seeds[0]}..{seeds[-1]})')
    print(f'  Sample size:  {args.m_factor * args.dim} pts')
    print(f'  phi:          {args.phi}  (Preuss cut threshold)')
    print(f'  min_size:     {args.min_basin_size}')
    print(f'  max_share:    {args.max_share}')
    print(f'  Tasks:        {len(tasks)}  (jobs={args.jobs})')
    print(f'  Output:       {out}')
    print()

    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        fut = {ex.submit(compute_one, t): t for t in tasks}
        done = 0
        for f in as_completed(fut):
            try:
                results.append(f.result())
            except Exception as e:
                t = fut[f]
                print(f'  ERROR {t[0]}/f{t[1]}/seed{t[3]}: {e}',
                      file=sys.stderr)
            done += 1
            if done % 20 == 0 or done == len(tasks):
                print(f'  {done}/{len(tasks)}  ({time.time()-t0:.0f}s)')

    df = pd.DataFrame(results)
    df.to_csv(out, index=False)
    print(f'\nWrote {len(df)} rows to {out}\n')

    # Surface errors immediately so silent failures don't waste a run
    if 'error' in df.columns:
        n_err = int(df['error'].notna().sum())
        if n_err > 0:
            print(f'!! {n_err}/{len(df)} tasks failed. Top error types:')
            print(df['error'].dropna().value_counts().head(5).to_string())
            print()
            if 'traceback' in df.columns:
                tb = df['traceback'].dropna()
                if len(tb) > 0:
                    print('First traceback:')
                    print(tb.iloc[0])
                    print()

    if 'top1_share' not in df.columns:
        print('No successful runs to summarise.')
        return

    # ---------- Per-suite, per-function summary ----------
    for suite in suite_list:
        sd = df[df['suite'] == suite].dropna(subset=['top1_share'])
        if len(sd) == 0:
            continue
        print(f'\n--- {suite.upper()} D={args.dim} ---')
        print(f'{"fn":<5}{"gt":<14}{"#runs":>6}'
              f'{"#bas":>5}{"top1":>7}{"top2":>7}{"top3":>7}'
              f'{"t1-t2":>8}{"N_eff":>8}{"gini":>7}')
        print('-' * 75)
        for fn in sorted(sd['fnum'].unique()):
            d = sd[sd['fnum'] == fn]
            gt = d['ground_truth_label'].iloc[0]
            print(f'f{fn:<4}{gt:<14}{len(d):>6}'
                  f'{int(d["n_basins"].median()):>5}'
                  f'{d["top1_share"].median():>7.3f}'
                  f'{d["top2_share"].median():>7.3f}'
                  f'{d["top3_share"].median():>7.3f}'
                  f'{d["top1_minus_top2"].median():>8.3f}'
                  f'{d["effective_n"].median():>8.2f}'
                  f'{d["size_gini"].median():>7.3f}')

    # ---------- Aggregated by class ----------
    print()
    print('Aggregated by class (median across ALL suites):')
    print(f'{"class":<14}{"#runs":>6}{"#bas":>5}{"top1":>7}{"top2":>7}'
          f'{"top3":>7}{"t1-t2":>8}{"N_eff":>8}{"gini":>7}')
    print('-' * 65)
    for cls_name in ['unimodal', 'basic', 'hybrid', 'composition']:
        d = df[df['ground_truth_label'] == cls_name].dropna(
            subset=['top1_share'])
        if len(d) == 0:
            continue
        print(f'{cls_name:<14}{len(d):>6}'
              f'{int(d["n_basins"].median()):>5}'
              f'{d["top1_share"].median():>7.3f}'
              f'{d["top2_share"].median():>7.3f}'
              f'{d["top3_share"].median():>7.3f}'
              f'{d["top1_minus_top2"].median():>8.3f}'
              f'{d["effective_n"].median():>8.2f}'
              f'{d["size_gini"].median():>7.3f}')

    # ---------- Spearman correlation hint ----------
    print()
    print('Next: correlate with compare.py output.')
    print('  Snippet (paste perf dict from your compare.py CEC2017 D=10 100K run):')
    print('  ----------------------------------------------------------------')
    print('  import pandas as pd, numpy as np')
    print('  from scipy.stats import spearmanr')
    print(f'  d = pd.read_csv("{out}")')
    print('  agg = d.groupby(["suite","fnum"]).median(numeric_only=True).reset_index()')
    print('  agg = agg[agg["suite"]=="cec2017"]')
    print('  perf = {  # (MSC_mean, ARRDE_mean) per fnum from compare.py')
    print('      5:(2.263,1.873), 6:(0.02869,2.856e-7), 7:(9.295,12.16),')
    print('      8:(1.580,1.834), 9:(0.06779,0), 10:(86.08,92.54),')
    print('      11:(0.4292,0), 12:(120.1,20.89), 13:(2.701,3.997),')
    print('      14:(4.688,0.5264), 15:(1.279,0.2138), 16:(1.547,0.5760),')
    print('      17:(20.10,1.998), 18:(18.12,0.6503), 19:(3.100,0.02408),')
    print('      20:(16.09,1.334), 21:(84.57,100.3), 22:(24.00,72.22),')
    print('      23:(259.3,290.5), 24:(72.55,102.2), 25:(162.5,228.2),')
    print('      26:(166.7,117.3), 27:(381.8,389.1), 28:(176.5,252.9),')
    print('      29:(235.7,231.5), 30:(419.2,398.5),')
    print('  }')
    print('  floor=1e-8')
    print('  agg["log_gap"] = agg["fnum"].map(lambda fn:')
    print('      np.log10(max(perf[fn][0],floor)/max(perf[fn][1],floor))')
    print('      if fn in perf else np.nan)')
    print('  sub = agg.dropna(subset=["log_gap"])')
    print('  print(f"N={len(sub)}")')
    print('  for col in ["top1_share","top2_share","top1_minus_top2",')
    print('              "top1_div_top2","effective_n","size_gini"]:')
    print('      r,p = spearmanr(sub[col], sub["log_gap"])')
    print('      print(f"  {col:18s} rho={r:+.3f}  p={p:.3g}")')


if __name__ == '__main__':
    main()
