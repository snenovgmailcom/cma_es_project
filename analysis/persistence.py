#!/usr/bin/env python3
"""
collect_persistence.py

For each (suite, fnum, seed), run v26's Phase-0 (LHS + NBC clustering)
and compute basin persistence values. Output CSV with per-(function, seed)
persistence statistics for downstream regime-detection analysis.

Persistence formula (Morse-Smale water-filling merge tree):
    persistence(B) = saddle_height(B, neighbour) - best_val(B)
    The basin containing the global best gets persistence = +inf.

The intuition: basins that survive across a wide range of merge thresholds
are topologically robust (real features). Low-persistence basins are sample-
noise artefacts.

Workflow per (fnum, seed):
    1. Run NBCDetector.discover() exactly as MSC-CMA-ES would
    2. Build kNN index (k=20) over Phase-0 points
    3. Detect cross-basin saddle heights from kNN edges
    4. Compute per-basin persistence via union-find merge tree
    5. Record basin count + persistence statistics

Output CSV columns:
    suite, fnum, seed, dim, ground_truth_label, ground_truth_class,
    n_basins, n_basins_above_min_size,
    max_persistence,           # excludes +inf basin (global best)
    mean_persistence_top5,
    median_persistence,
    p_above_1, p_above_5, p_above_10, p_above_50, p_above_100,
    saddle_count, sample_f_min, sample_f_range

Usage
-----
    python collect_persistence.py --suite cec2017 --dim 10 --seeds 51 \
        --v26-path ~/cma_es_project_v26
    python collect_persistence.py --suite cec2017 --dim 10 \
        --functions 11-20 --seeds 11
    python collect_persistence.py --suite cec2020 --dim 10 \
        --out persistence_cec2020.csv

Notes
-----
* Uses v26's NBCDetector — the v29 version dropped persistence computation.
* Default config matches v26 defaults (M_factor=850, k=1, n_initial_basins=33).
  Override via CLI flags if needed.
* k_saddle=20 controls how many neighbours are scanned when detecting
  cross-basin saddles (v26's default).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict

import numpy as np
import pandas as pd


# Same SUITE_CONFIG and GROUND_TRUTH as collect_ela_predictions.py
SUITE_CONFIG = {
    'cec2014': (30, [5, 10, 20, 30, 50, 100]),
    'cec2017': (30, [5, 10, 20, 30, 50, 100]),
    'cec2020': (10, [5, 10, 15, 20]),
    'cec2022': (12, [10, 20]),
}
GROUND_TRUTH = {
    'cec2014': {**{i: 'unimodal' for i in [1, 2, 3]},
                **{i: 'basic' for i in range(4, 17)},
                **{i: 'hybrid' for i in range(17, 23)},
                **{i: 'composition' for i in range(23, 31)}},
    'cec2017': {**{i: 'unimodal' for i in [1, 2, 3]},
                **{i: 'basic' for i in range(4, 11)},
                **{i: 'hybrid' for i in range(11, 21)},
                **{i: 'composition' for i in range(21, 31)}},
    'cec2020': {1: 'unimodal',
                2: 'basic', 3: 'basic', 4: 'basic',
                5: 'hybrid', 6: 'hybrid', 7: 'hybrid',
                8: 'composition', 9: 'composition', 10: 'composition'},
    'cec2022': {1: 'unimodal', 2: 'basic', 3: 'basic', 4: 'basic', 5: 'basic',
                6: 'hybrid', 7: 'hybrid', 8: 'hybrid',
                9: 'composition', 10: 'composition',
                11: 'composition', 12: 'composition'},
}
CLASS_MAP = {'unimodal': 0, 'basic': 0, 'hybrid': 1, 'composition': 2}


def compute_one(args):
    """Worker: returns dict with persistence stats for one (suite, fnum, seed)."""
    (suite, fnum, dim, seed, v26_path,
     m_factor, k_nbc, n_init_basins, k_saddle, min_basin_size) = args

    # Make v26's algorithms importable
    algo_path = os.path.join(v26_path, 'algorithms')
    if algo_path not in sys.path:
        sys.path.insert(0, algo_path)

    from scipy.spatial import cKDTree as KDTree
    from minionpy import (CEC2014Functions, CEC2017Functions,
                          CEC2020Functions, CEC2022Functions)

    # Use v26 modules
    from config import MSCConfig
    from basin_detector import NBCDetector
    # Use v26's persistence helpers — they exist in v26 even though
    # discover() no longer calls them
    from basin_detector import _boundary_saddles, _compute_persistence

    cls_map = {'cec2014': CEC2014Functions, 'cec2017': CEC2017Functions,
               'cec2020': CEC2020Functions, 'cec2022': CEC2022Functions}
    f = cls_map[suite](fnum, dim)
    bounds = np.tile(np.array([-100.0, 100.0]), (dim, 1))

    cfg = MSCConfig(
        M_factor=m_factor,
        k=k_nbc,
        n_initial_basins=n_init_basins,
        min_basin_size=min_basin_size,
        sigma_divisor=2.6714,
        sampling_method='lhs',
    )

    out = {
        'suite': suite, 'fnum': fnum, 'seed': seed, 'dim': dim,
    }

    try:
        # Run Phase 0 exactly as MSC would
        detector = NBCDetector(dim, bounds, cfg, seed)
        basins_sorted, phi_used, _ = detector.discover(f)

        # Sample stats
        out['phi_used'] = float(phi_used)
        out['sample_f_min'] = float(np.min(detector.fvals))
        out['sample_f_range'] = float(
            np.max(detector.fvals) - np.min(detector.fvals))

        if not basins_sorted:
            out['n_basins'] = 0
            out['n_basins_above_min_size'] = 0
            out['max_persistence'] = 0.0
            out['mean_persistence_top5'] = 0.0
            out['median_persistence'] = 0.0
            out['max_persistence_rel'] = 0.0
            out['mean_persistence_rel_top5'] = 0.0
            out['saddle_count'] = 0
            for thr_pct in (1, 2, 5, 10, 25):
                out[f'p_above_{thr_pct}pct'] = 0
            for thr in (1.0, 10.0, 100.0):
                out[f'p_above_{int(thr)}_abs'] = 0
        else:
            # Build kNN index for saddle detection
            knn_idx = detector._build_knn(k=k_saddle)

            # Compute saddles + persistence.
            # NB: _boundary_saddles uses raw labels which include components
            # that extract_basins filtered out (size < min_basin_size).
            # Filter saddles to only the surviving basin ids before passing
            # to _compute_persistence — otherwise it raises KeyError on the
            # filtered components. (Latent bug in v26: function was disabled
            # in discover(), so this never surfaced in production.)
            basins_dict = {b.basin_id: b for b in basins_sorted}
            surviving_ids = set(basins_dict.keys())
            saddles_filtered = {
                (a, b): h for (a, b), h in
                _boundary_saddles(detector.labels, detector.fvals, knn_idx).items()
                if a in surviving_ids and b in surviving_ids
            }
            persistence_dict = _compute_persistence(basins_dict, saddles_filtered)
            saddles = saddles_filtered

            out['saddle_count'] = len(saddles)

            # Per-basin persistence values, excluding +inf (global best)
            persistences = [v for v in persistence_dict.values()
                            if np.isfinite(v)]
            out['n_basins'] = len(basins_sorted)
            out['n_basins_above_min_size'] = sum(
                1 for b in basins_sorted if b.size >= min_basin_size)

            if persistences:
                arr = np.array(persistences, dtype=np.float64)
                f_range = float(np.max(detector.fvals) - np.min(detector.fvals))
                out['max_persistence'] = float(arr.max())
                arr_sorted_desc = np.sort(arr)[::-1]
                out['mean_persistence_top5'] = float(
                    arr_sorted_desc[:5].mean())
                out['median_persistence'] = float(np.median(arr))
                # Normalised: persistence as fraction of sample f-range.
                # Makes thresholds comparable across functions with very
                # different f-scales (unimodal e.g. ~1, composition ~3000).
                if f_range > 0:
                    rel = arr / f_range
                    out['max_persistence_rel'] = float(rel.max())
                    out['mean_persistence_rel_top5'] = float(
                        np.sort(rel)[::-1][:5].mean())
                    for thr_pct in (1, 2, 5, 10, 25):
                        out[f'p_above_{thr_pct}pct'] = int(
                            (rel > thr_pct / 100.0).sum())
                else:
                    out['max_persistence_rel'] = 0.0
                    out['mean_persistence_rel_top5'] = 0.0
                    for thr_pct in (1, 2, 5, 10, 25):
                        out[f'p_above_{thr_pct}pct'] = 0
                # Keep absolute thresholds too (legacy)
                for thr in (1.0, 10.0, 100.0):
                    out[f'p_above_{int(thr)}_abs'] = int((arr > thr).sum())
            else:
                out['max_persistence'] = 0.0
                out['mean_persistence_top5'] = 0.0
                out['median_persistence'] = 0.0
                out['max_persistence_rel'] = 0.0
                out['mean_persistence_rel_top5'] = 0.0
                for thr_pct in (1, 2, 5, 10, 25):
                    out[f'p_above_{thr_pct}pct'] = 0
                for thr in (1.0, 10.0, 100.0):
                    out[f'p_above_{int(thr)}_abs'] = 0

    except Exception as exc:
        out['error'] = str(exc)

    # Ground truth lookup
    gt_label = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
    out['ground_truth_label'] = gt_label
    out['ground_truth_class'] = CLASS_MAP.get(gt_label, -1)

    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True,
                   choices=list(SUITE_CONFIG.keys()))
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--seeds', type=int, default=51)
    p.add_argument('--seed-start', type=int, default=0)
    p.add_argument('--functions', type=str, default=None,
                   help='Subset, e.g. "11-20" or "1,5,12". Default: all.')
    p.add_argument('--jobs', type=int, default=51)
    p.add_argument('--v26-path', default=os.path.expanduser('~/cma_es_project_v26'),
                   help='Path to v26 project (default: ~/cma_es_project_v26)')
    p.add_argument('--m-factor', type=int, default=850,
                   help='Phase 0 LHS sample = M_factor * dim (default 850)')
    p.add_argument('--k-nbc', type=int, default=1,
                   help='kNN voting k for basin membership (default 1)')
    p.add_argument('--n-init-basins', type=int, default=33,
                   help='Phase 0 staircase target basin count (default 33)')
    p.add_argument('--k-saddle', type=int, default=20,
                   help='kNN scan size for saddle detection (default 20)')
    p.add_argument('--min-basin-size', type=int, default=5)
    p.add_argument('--out', default=None,
                   help='Output CSV; default: persistence_<suite>_d<dim>.csv')
    p.add_argument('--append', action='store_true')
    args = p.parse_args()

    # Validate v26 path
    if not os.path.exists(os.path.join(args.v26_path, 'algorithms', 'basin_detector.py')):
        print(f'ERROR: v26 algorithms not found at {args.v26_path}',
              file=sys.stderr)
        sys.exit(1)

    n_funcs, supported_dims = SUITE_CONFIG[args.suite]
    if args.dim not in supported_dims:
        print(f'WARNING: dim={args.dim} not standard for {args.suite}. '
              f'Standard: {supported_dims}', file=sys.stderr)

    # Function selection
    if args.functions:
        func_list = []
        for part in args.functions.split(','):
            if '-' in part:
                lo, hi = part.split('-')
                func_list.extend(range(int(lo), int(hi) + 1))
            else:
                func_list.append(int(part))
    else:
        func_list = list(range(1, n_funcs + 1))

    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    out = args.out or f'persistence_{args.suite}_d{args.dim}.csv'

    tasks = [(args.suite, fnum, args.dim, seed, args.v26_path,
              args.m_factor, args.k_nbc, args.n_init_basins,
              args.k_saddle, args.min_basin_size)
             for fnum in func_list for seed in seeds]

    print(f'=== Persistence collection: {args.suite} D={args.dim} ===')
    print(f'  Functions:  {len(func_list)}  ({func_list[0]}..{func_list[-1]})')
    print(f'  Seeds:      {len(seeds)}  ({seeds[0]}..{seeds[-1]})')
    print(f'  M*D points per Phase 0:  {args.m_factor * args.dim}')
    print(f'  Phase 0 cost (FE/seed):  {args.m_factor * args.dim}')
    print(f'  Tasks:      {len(tasks)}  (jobs={args.jobs})')
    print(f'  Output:     {out}  ({"append" if args.append else "overwrite"})')
    print()

    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        fut_to_task = {ex.submit(compute_one, t): t for t in tasks}
        done = 0
        for fut in as_completed(fut_to_task):
            try:
                results.append(fut.result())
            except Exception as exc:
                t = fut_to_task[fut]
                print(f'  ERROR {t[0]}/f{t[1]}/seed{t[3]}: {exc}',
                      file=sys.stderr)
            done += 1
            if done % 50 == 0 or done == len(tasks):
                elapsed = time.time() - t0
                rate = done / elapsed if elapsed > 0 else 0
                eta = (len(tasks) - done) / rate if rate > 0 else 0
                print(f'  {done}/{len(tasks)}  ({elapsed:.0f}s, ETA {eta:.0f}s)')

    df = pd.DataFrame(results)

    # Reorder columns
    id_cols = ['suite', 'fnum', 'seed', 'dim',
               'ground_truth_label', 'ground_truth_class']
    stats_cols = ['n_basins', 'n_basins_above_min_size', 'saddle_count',
                  'phi_used', 'sample_f_min', 'sample_f_range',
                  'max_persistence', 'mean_persistence_top5',
                  'median_persistence',
                  'max_persistence_rel', 'mean_persistence_rel_top5',
                  'p_above_1pct', 'p_above_2pct', 'p_above_5pct',
                  'p_above_10pct', 'p_above_25pct',
                  'p_above_1_abs', 'p_above_10_abs', 'p_above_100_abs']
    err_cols = [c for c in df.columns if c == 'error']
    other_cols = [c for c in df.columns
                  if c not in id_cols + stats_cols + err_cols]
    final_cols = ([c for c in id_cols if c in df.columns]
                  + [c for c in stats_cols if c in df.columns]
                  + sorted(other_cols)
                  + err_cols)
    df = df[final_cols]

    if args.append and os.path.exists(out):
        existing = pd.read_csv(out)
        df = pd.concat([existing, df], ignore_index=True, sort=False)
    df.to_csv(out, index=False)
    print(f'\nWrote {len(df)} rows to {out}')

    # Quick per-function summary by ground truth class
    print('\nQuick check — median persistence stats per function '
          '(NaN-tolerant):')
    print(f'{"fn":<5}{"gt":<14}{"#runs":>6}{"#bas":>6}'
          f'{"max_p":>10}{"top5":>10}{"max_rel":>9}{"top5_rel":>10}'
          f'{"#>1%":>6}{"#>5%":>6}{"#>10%":>7}')
    print('-' * 95)
    for fn in sorted(df['fnum'].unique()):
        d = df[df['fnum'] == fn].dropna(subset=['n_basins'])
        if len(d) == 0:
            gt = df[df['fnum']==fn]['ground_truth_label'].iloc[0]
            print(f'f{fn:<4}{gt:<14}{0:>6}  (all NaN)')
            continue
        gt = d['ground_truth_label'].iloc[0]
        n = len(d)
        n_basins_med = int(d['n_basins'].median())
        max_p_med = d['max_persistence'].median()
        top5_med = d['mean_persistence_top5'].median()
        max_rel_med = d['max_persistence_rel'].median()
        top5_rel_med = d['mean_persistence_rel_top5'].median()
        above1pct = int(d['p_above_1pct'].median())
        above5pct = int(d['p_above_5pct'].median())
        above10pct = int(d['p_above_10pct'].median())
        print(f'f{fn:<4}{gt:<14}{n:>6}{n_basins_med:>6}'
              f'{max_p_med:>10.2f}{top5_med:>10.2f}'
              f'{max_rel_med:>9.4f}{top5_rel_med:>10.4f}'
              f'{above1pct:>6}{above5pct:>6}{above10pct:>7}')


if __name__ == '__main__':
    main()
