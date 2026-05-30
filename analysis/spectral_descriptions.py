#!/usr/bin/env python3
"""
spectral_descriptors.py

Per (suite, fnum, seed): build the same critical-weighted 8-NN graph as
sbisection.py (same LHS, same w = 0.01 on crit-crit edges, 1.0 elsewhere),
then compute the K smallest eigenvalues of the SYMMETRIC NORMALIZED
Laplacian L_sym = I - D^{-1/2} A D^{-1/2} and derive:

  - lambda_1 .. lambda_K      first K eigenvalues (ascending)
  - gap_i = lambda_{i+1} - lambda_i  (consecutive gaps)
  - k_star  = argmax_i gap_i  (von Luxburg eigengap heuristic)
  - delta_star = gap_{k_star}  (size of the chosen gap)
  - delta_star_norm = delta_star / lambda_K  (scale-invariant variant)
  - phi_cheeger from sign(Fiedler) split  (graph conductance, scalar)

Why these specific knobs:

  * which='SA' (smallest algebraic) for eigsh on a symmetric PSD matrix is
    the canonical reliable mode. We avoid 'SM' (which is what sbisection.py
    currently uses and which silently fails on near-degenerate spectra) and
    we avoid shift-invert at sigma=0 (the matrix is singular there).

  * L_sym, not unnormalized L. von Luxburg's eigengap heuristic is illustrated
    on L_rw / L_sym, and degree-normalized Laplacians are more robust under
    non-uniform sample density (Path-based spectral clustering, JMLR 2020).

  * Cheeger phi is a scalar interpretation of lambda_2 grounded in
    Cheeger's inequality phi^2/2 <= lambda_2(L_sym) <= 2 phi.
    Computed directly from the cut, no eigsh dependency once we have the
    Fiedler sign vector.

Output CSV is intended to be merged with compare.py SUM/per-fn results to
compute Spearman correlation between (k_star, delta_star, lambda_2, phi)
and log(MSC_mean / ARRDE_mean) — i.e. is the spectrum a-priori predictive
of MSC-CMA-ES applicability.

Usage
-----
    python analysis/spectral_descriptors.py \\
        --suite cec2017 --dim 10 --seeds 10 --K 10
    python analysis/spectral_descriptors.py \\
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


SUITE_CONFIG = {
    'cec2014': (30, [5, 10, 20, 30, 50, 100]),
    'cec2017': (30, [5, 10, 20, 30, 50, 100]),
    'cec2020': (10, [5, 10, 15, 20]),
    'cec2022': (12, [10, 20]),
}
GROUND_TRUTH = {
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
    'cec2014': {**{i: 'unimodal' for i in [1, 2, 3]},
                **{i: 'basic' for i in range(4, 17)},
                **{i: 'hybrid' for i in range(17, 23)},
                **{i: 'composition' for i in range(23, 31)}},
}


# ----------------------------------------------------------------------
# Worker: spectrum + Cheeger for one (suite, fnum, seed)
# ----------------------------------------------------------------------

def compute_one(args):
    (suite, fnum, dim, seed, m_factor, k_nn, K, beta, weighting) = args

    from scipy.stats import qmc
    from scipy.spatial import cKDTree
    from scipy.sparse import csr_matrix, diags, eye as speye
    from scipy.sparse.linalg import eigsh
    from minionpy import (CEC2014Functions, CEC2017Functions,
                          CEC2020Functions, CEC2022Functions)
    cls_map = {'cec2014': CEC2014Functions, 'cec2017': CEC2017Functions,
               'cec2020': CEC2020Functions, 'cec2022': CEC2022Functions}
    f = cls_map[suite](fnum, dim)

    out = {'suite': suite, 'fnum': fnum, 'seed': seed, 'dim': dim,
           'k_nn': k_nn, 'K': K, 'beta': beta, 'weighting': weighting}

    try:
        # ===== 1. LHS sample (identical to sbisection.py for comparability) =====
        n = m_factor * dim
        lhs = qmc.LatinHypercube(d=dim, seed=seed)
        unit = lhs.random(n)
        bounds_lo = np.full(dim, -100.0)
        bounds_hi = np.full(dim, 100.0)
        X = qmc.scale(unit, bounds_lo, bounds_hi)
        X_norm = (X - bounds_lo) / (bounds_hi - bounds_lo)

        y = np.asarray(f([row.tolist() for row in X]),
                       dtype=np.float64).ravel()
        out['sample_n'] = int(n)
        out['f_min'] = float(y.min())
        out['f_range'] = float(y.max() - y.min())

        # ===== 2. f-based edge weights: w_ij = exp(-beta * f_edge) =====
        # f_edge is the mid-f along the edge in y-normalized [0,1] space.
        # Low-f edges (in valley) -> w near 1.
        # High-f edges (on ridge) -> w near exp(-beta).
        # This is the standard Gaussian-similarity scheme adapted to fitness:
        # the graph topology now actually depends on f, not just on uniform
        # geometry like the old binary critical-tag scheme.
        f_range = float(y.max() - y.min())
        if f_range <= 0.0:
            out['error'] = f'f is constant on sample (range={f_range})'
            out['ground_truth_label'] = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
            return out
        y_norm = (y - y.min()) / f_range            # in [0, 1]
        out['f_range'] = f_range

        # ===== 3. Build symmetric weighted 8-NN graph =====
        tree = cKDTree(X_norm)
        _, knn = tree.query(X_norm, k=k_nn + 1)
        knn = knn[:, 1:]                                  # drop self

        src = np.repeat(np.arange(n), k_nn)
        tgt = knn.ravel().astype(np.int64)
        valid = src != tgt
        src, tgt = src[valid], tgt[valid]

        # Edge weights from f. weighting='exp' gives standard Gaussian-similarity
        # form; 'minmax' gives an alternative w = max(eps, 1 - f_edge).
        f_edge = 0.5 * (y_norm[src] + y_norm[tgt])
        if weighting == 'exp':
            w = np.exp(-beta * f_edge)
        elif weighting == 'minmax':
            w = np.maximum(1.0 - f_edge, 1e-6)
        else:
            raise ValueError(f'unknown weighting: {weighting}')
        out['w_min'] = float(w.min())
        out['w_max'] = float(w.max())
        out['w_mean'] = float(w.mean())

        rows = np.concatenate([src, tgt])
        cols = np.concatenate([tgt, src])
        data = np.concatenate([w, w])
        A = csr_matrix((data, (rows, cols)), shape=(n, n))
        A.sum_duplicates()

        # ===== 4. Symmetric normalized Laplacian L_sym = I - D^{-1/2} A D^{-1/2} =====
        d = np.asarray(A.sum(axis=1)).ravel()
        out['min_degree'] = float(d.min())
        out['max_degree'] = float(d.max())
        out['mean_degree'] = float(d.mean())

        # Numerical floor on degree to avoid 1/0 (shouldn't happen for k_nn>=1
        # but guard anyway)
        d_safe = np.maximum(d, 1e-300)
        d_inv_sqrt = 1.0 / np.sqrt(d_safe)
        D_inv_sqrt = diags(d_inv_sqrt)
        L_sym = speye(n) - D_inv_sqrt @ A @ D_inv_sqrt

        # ===== 5. K smallest eigenvalues via which='SA' (canonical for PSD) =====
        # We need eigenvectors only for k=2 (Fiedler -> Cheeger), so two calls:
        # one cheap eigvals-only call for the spectrum, one with vectors for k=2.
        try:
            eigvals = eigsh(L_sym, k=K, which='SA',
                            maxiter=30000, tol=1e-9,
                            return_eigenvectors=False)
        except Exception as e:
            # Fallback: shift-invert at small positive sigma. Some L_sym have
            # ARPACK convergence issues at the lower end with 'SA'.
            try:
                eigvals = eigsh(L_sym, k=K, sigma=1e-8, which='LM',
                                mode='normal',
                                maxiter=30000, tol=1e-9,
                                return_eigenvectors=False)
                out['eigsh_fallback'] = 'shift_invert'
            except Exception as e2:
                out['eigsh_error'] = f'{type(e2).__name__}: {e2}'
                gt = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
                out['ground_truth_label'] = gt
                return out

        eigvals = np.sort(eigvals)
        for i in range(K):
            out[f'lambda_{i+1}'] = float(eigvals[i])

        # ===== 6. von Luxburg eigengap heuristic =====
        # gaps[i] = lambda_{i+2} - lambda_{i+1}  for i = 0..K-2
        # k_star = number of "small" eigenvalues before the largest gap
        #        = argmax(gaps) + 1
        gaps = np.diff(eigvals)
        for i in range(len(gaps)):
            out[f'gap_{i+1}'] = float(gaps[i])

        k_star = int(np.argmax(gaps)) + 1
        delta_star = float(gaps[k_star - 1])
        out['k_star'] = k_star
        out['delta_star'] = delta_star
        # Normalized variant — useful when comparing across functions whose
        # absolute spectrum scales differ.
        lam_top = float(eigvals[-1])
        out['delta_star_norm'] = (delta_star / lam_top) if lam_top > 0 else 0.0

        # ===== 7. Fiedler vector + Cheeger conductance =====
        try:
            ev2, vec2 = eigsh(L_sym, k=2, which='SA',
                              maxiter=30000, tol=1e-9)
            order = np.argsort(ev2)
            fiedler_sym = vec2[:, order[1]]
            # In L_sym basis the cluster indicator for L_rw is u = D^{-1/2} v.
            # For sign-based bipartition the sign pattern of u and v can differ
            # only on near-zero entries; we use D^{-1/2} v which is the standard
            # Ng-Jordan-Weiss prescription.
            fiedler = d_inv_sqrt * fiedler_sym

            left_mask = fiedler > 0
            right_mask = ~left_mask
            n_left = int(left_mask.sum())
            n_right = int(right_mask.sum())
            out['fiedler_n_left'] = n_left
            out['fiedler_n_right'] = n_right

            if n_left > 0 and n_right > 0:
                left_idx = np.where(left_mask)[0]
                right_idx = np.where(right_mask)[0]
                vol_left = float(d[left_mask].sum())
                vol_right = float(d[right_mask].sum())
                cut = float(A[left_idx][:, right_idx].sum())
                phi = cut / min(vol_left, vol_right)
                out['cut_weight'] = cut
                out['vol_left'] = vol_left
                out['vol_right'] = vol_right
                out['phi_cheeger'] = float(phi)
            else:
                out['phi_cheeger'] = float('nan')
        except Exception as e:
            out['fiedler_error'] = f'{type(e).__name__}: {e}'
            out['phi_cheeger'] = float('nan')

    except Exception as exc:
        import traceback
        out['error'] = f'{type(exc).__name__}: {exc}'
        out['traceback'] = traceback.format_exc()[:500]

    out['ground_truth_label'] = GROUND_TRUTH.get(suite, {}).get(fnum, '?')
    return out


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

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
                   help='Sample size = m_factor * dim. Default 850 to match '
                        'sbisection.py.')
    p.add_argument('--k-nn', type=int, default=8)
    p.add_argument('--K', type=int, default=10,
                   help='Number of smallest eigenvalues to compute.')
    p.add_argument('--beta', type=float, default=10.0,
                   help='Edge weight bandwidth: w = exp(-beta * f_edge) for '
                        'f_edge in [0,1]. beta=10 -> high-f edges get '
                        'w ~ exp(-10) ~ 4.5e-5, low-f edges get w ~ 1. '
                        'Larger beta = more contrast = more sensitive to f.')
    p.add_argument('--weighting', choices=['exp', 'minmax'], default='exp',
                   help='Edge weighting scheme. exp: w=exp(-beta*f_edge). '
                        'minmax: w=max(eps, 1-f_edge), beta-free.')
    p.add_argument('--out', default=None)
    args = p.parse_args()

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
                              args.k_nn, args.K, args.beta, args.weighting))

    out = args.out or (f'spectral_desc_{"_".join(suite_list)}_d{args.dim}.csv')

    print(f'=== Spectral descriptors (von Luxburg eigengap + Cheeger) ===')
    print(f'  Suites:       {", ".join(suite_list)}')
    for s in suite_list:
        fl = suite_funcs[s]
        print(f'    {s}: {len(fl)} funcs ({fl[0]}..{fl[-1]})')
    print(f'  Dim:          D={args.dim}')
    print(f'  Seeds:        {len(seeds)}  ({seeds[0]}..{seeds[-1]})')
    print(f'  Sample size:  {args.m_factor * args.dim} pts')
    print(f'  k_NN:         {args.k_nn}')
    print(f'  K:            {args.K}  (eigenvalues to compute)')
    print(f'  weighting:    {args.weighting}  (edge weight scheme)')
    print(f'  beta:         {args.beta}  (only used for weighting=exp)')
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

    # Surface errors immediately. Previously these went silent because the
    # 'k_star not in columns' branch fired before printing anything useful.
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

    if 'k_star' not in df.columns:
        print('No successful runs to summarise.')
        return

    # ---------- Per-suite, per-function summary ----------
    for suite in suite_list:
        sd = df[df['suite'] == suite].dropna(subset=['k_star'])
        if len(sd) == 0:
            continue
        print(f'\n--- {suite.upper()} D={args.dim} ---')
        print(f'{"fn":<5}{"gt":<14}{"#runs":>6}'
              f'{"lam_2":>11}{"lam_3":>11}{"k*":>5}{"d*":>11}{"d*_n":>9}'
              f'{"phi":>9}')
        print('-' * 85)
        for fn in sorted(sd['fnum'].unique()):
            d = sd[sd['fnum'] == fn]
            gt = d['ground_truth_label'].iloc[0]
            print(f'f{fn:<4}{gt:<14}{len(d):>6}'
                  f'{d["lambda_2"].median():>11.3e}'
                  f'{d["lambda_3"].median():>11.3e}'
                  f'{int(d["k_star"].median()):>5}'
                  f'{d["delta_star"].median():>11.3e}'
                  f'{d["delta_star_norm"].median():>9.3f}'
                  f'{d["phi_cheeger"].median():>9.4f}')

    # ---------- Aggregated by class ----------
    print()
    print('Aggregated by class (median across ALL suites):')
    print(f'{"class":<14}{"#runs":>6}{"lam_2":>11}{"lam_3":>11}'
          f'{"k*":>5}{"d*":>11}{"d*_n":>9}{"phi":>9}')
    print('-' * 75)
    for cls_name in ['unimodal', 'basic', 'hybrid', 'composition']:
        d = df[df['ground_truth_label'] == cls_name].dropna(subset=['k_star'])
        if len(d) == 0:
            continue
        print(f'{cls_name:<14}{len(d):>6}'
              f'{d["lambda_2"].median():>11.3e}'
              f'{d["lambda_3"].median():>11.3e}'
              f'{int(d["k_star"].median()):>5}'
              f'{d["delta_star"].median():>11.3e}'
              f'{d["delta_star_norm"].median():>9.3f}'
              f'{d["phi_cheeger"].median():>9.4f}')

    # ---------- Hint for next step ----------
    print()
    print('Next step: merge with compare.py results and compute Spearman:')
    print('  import pandas as pd, numpy as np')
    print('  from scipy.stats import spearmanr')
    print(f'  spec = pd.read_csv("{out}")')
    print('  perf = pd.read_csv("compare_cec2017_d10_mean.csv")  # from compare.py')
    print('  agg = spec.groupby(["suite","fnum"]).median(numeric_only=True)')
    print('  for col in ["lambda_2","k_star","delta_star","phi_cheeger"]:')
    print('      r, p = spearmanr(agg[col], '
          'np.log10(perf["MSC-CMA"]/perf["ARRDE-minionpy"]))')
    print('      print(f"{col:20s} rho={r:+.3f} p={p:.3g}")')


if __name__ == '__main__':
    main()
