"""Reconstruct phase_stats from existing PKL improvements arrays.

Phases:
  Phase 0: FE 0..M           (LHS sampling)
  Main:    FE M..main_end    (CMA cycles + topology)
  Endgame: FE main_end..max  (refine_frac * maxevals)
"""
import pickle
import numpy as np
import argparse
import os
import glob


def best_at_fe(improvements_arr, target_fe):
    """Return best error at FE <= target_fe. None if target before first improvement."""
    if len(improvements_arr) == 0:
        return None
    fes = improvements_arr[:, 0]
    errs = improvements_arr[:, 1]
    idx = np.searchsorted(fes, target_fe, side='right') - 1
    if idx < 0:
        return None
    return float(errs[idx])


def reconstruct_phase_stats(pkl_path):
    d = pickle.load(open(pkl_path, 'rb'))
    cfg = d['params']['msc_config']
    maxevals = d['maxevals']
    dim = d['dim']

    M = cfg['M_factor'] * dim
    refine_frac = float(cfg['refine_frac'])
    refine_budget = int(refine_frac * maxevals)
    main_end_fe = maxevals - refine_budget

    per_seed = []
    for seed_idx, imp in enumerate(d['improvements']):
        if len(imp) == 0:
            per_seed.append({
                'seed': seed_idx,
                'after_phase0': None,
                'before_endgame': None,
                'after_endgame': None,
                'phase0_to_main_delta': None,
                'main_to_endgame_delta': None,
            })
            continue

        e_p0 = best_at_fe(imp, M)
        e_be = best_at_fe(imp, main_end_fe)
        e_ae = float(imp[-1, 1])  # final best error

        per_seed.append({
            'seed': seed_idx,
            'after_phase0': e_p0,
            'before_endgame': e_be,
            'after_endgame': e_ae,
            'phase0_to_main_delta': (e_p0 - e_be) if (e_p0 and e_be) else None,
            'main_to_endgame_delta': (e_be - e_ae) if (e_be and e_ae is not None) else None,
        })

    return {
        'pkl': pkl_path,
        'func': d['func'],
        'M': M,
        'main_end_fe': main_end_fe,
        'maxevals': maxevals,
        'per_seed': per_seed,
    }


def aggregate(stats):
    """Aggregate across seeds → per-function summary."""
    valid = [s for s in stats['per_seed'] if s['after_endgame'] is not None]
    if not valid:
        return None

    p0 = np.array([s['after_phase0'] for s in valid if s['after_phase0'] is not None])
    be = np.array([s['before_endgame'] for s in valid if s['before_endgame'] is not None])
    ae = np.array([s['after_endgame'] for s in valid])

    # Improvement deltas (relative to before_endgame)
    main_imp = (p0 - be) / np.maximum(p0, 1e-12) if (len(p0) == len(be)) else None
    endgame_imp = (be - ae) / np.maximum(be, 1e-12) if (len(be) == len(ae)) else None

    # Diagnostic categorization
    # "right basin under-solved": before_endgame finite but after_endgame << before_endgame → endgame helped
    # "stuck": before_endgame finite, after_endgame ≈ before_endgame → no further improvement possible
    # "wrong basin": after_phase0 large, no recovery
    diag = []
    for s in valid:
        if s['after_phase0'] is None or s['before_endgame'] is None:
            continue
        p0_v = s['after_phase0']
        be_v = s['before_endgame']
        ae_v = s['after_endgame']
        eps = 1e-12

        if p0_v < 1e-8:
            diag.append('phase0_solved')
        elif (p0_v - be_v) / max(p0_v, eps) > 0.5:
            # Main phase improved a lot
            if (be_v - ae_v) / max(be_v, eps) > 0.1:
                diag.append('endgame_helped')
            elif ae_v < 1e-3:
                diag.append('main_solved')
            else:
                diag.append('main_progressed_endgame_stuck')
        else:
            # Main didn't improve much
            if (be_v - ae_v) / max(be_v, eps) > 0.5:
                diag.append('endgame_rescue')
            else:
                diag.append('wrong_basin_or_stuck')

    return {
        'func': stats['func'],
        'M': stats['M'],
        'main_end_fe': stats['main_end_fe'],
        'n_valid': len(valid),
        'p0_median': float(np.median(p0)) if len(p0) else None,
        'be_median': float(np.median(be)) if len(be) else None,
        'ae_median': float(np.median(ae)),
        'p0_to_be_relative': float(np.median(main_imp)) if main_imp is not None else None,
        'be_to_ae_relative': float(np.median(endgame_imp)) if endgame_imp is not None else None,
        'diag_counts': {d: diag.count(d) for d in set(diag)},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pkl-glob', required=True, help="Glob for f*.pkl files")
    ap.add_argument('--csv-out', default=None)
    args = ap.parse_args()

    paths = sorted(glob.glob(args.pkl_glob))
    if not paths:
        print(f"No PKLs found at {args.pkl_glob}")
        return

    print(f"{'func':<6} {'p0_med':>10} {'be_med':>10} {'ae_med':>10} "
          f"{'main_imp':>10} {'eg_imp':>10} {'diag (top 2)'}")
    print('-' * 110)

    rows = []
    for p in paths:
        st = reconstruct_phase_stats(p)
        agg = aggregate(st)
        if agg is None:
            continue
        diag_str = ', '.join(f"{k}:{v}" for k, v in
                            sorted(agg['diag_counts'].items(),
                                   key=lambda x: -x[1])[:2])
        print(f"{agg['func']:<6} "
              f"{agg['p0_median']:>10.3e} "
              f"{agg['be_median']:>10.3e} "
              f"{agg['ae_median']:>10.3e} "
              f"{(agg['p0_to_be_relative'] or 0)*100:>9.1f}% "
              f"{(agg['be_to_ae_relative'] or 0)*100:>9.1f}% "
              f"{diag_str}")
        rows.append(agg)

    if args.csv_out:
        import csv
        with open(args.csv_out, 'w') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"\nWrote CSV: {args.csv_out}")


if __name__ == '__main__':
    main()
