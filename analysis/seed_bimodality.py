"""Detect bimodal seed distributions and check if phase0 predicts final outcome."""
import pickle
import numpy as np
import argparse
import glob


def best_at_fe(improvements_arr, target_fe):
    if len(improvements_arr) == 0:
        return None
    fes = improvements_arr[:, 0]
    errs = improvements_arr[:, 1]
    idx = np.searchsorted(fes, target_fe, side='right') - 1
    if idx < 0:
        return None
    return float(errs[idx])


def analyze(pkl_path):
    d = pickle.load(open(pkl_path, 'rb'))
    cfg = d['params']['msc_config']
    M = cfg['M_factor'] * d['dim']
    refine_frac = float(cfg['refine_frac'])
    main_end_fe = d['maxevals'] - int(refine_frac * d['maxevals'])

    rows = []
    for seed_idx, imp in enumerate(d['improvements']):
        if len(imp) == 0:
            continue
        rows.append({
            'seed': seed_idx,
            'p0': best_at_fe(imp, M),
            'be': best_at_fe(imp, main_end_fe),
            'ae': float(imp[-1, 1]),
        })
    return d['func'], d['maxevals'], rows


def classify_seed(ae, success_threshold=1e-3):
    return 'success' if ae <= success_threshold else 'fail'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pkl-glob', required=True)
    ap.add_argument('--success-thresh', type=float, default=1e-3,
                    help="Final error below this = success")
    args = ap.parse_args()

    print(f"{'func':<6} {'N_succ':>6} {'N_fail':>6} {'p0_med_succ':>12} {'p0_med_fail':>12} "
          f"{'p0_pred?':>8}  Diagnosis")
    print('-' * 100)

    for path in sorted(glob.glob(args.pkl_glob)):
        func, mxev, rows = analyze(path)

        success = [r for r in rows if r['ae'] <= args.success_thresh]
        fail = [r for r in rows if r['ae'] > args.success_thresh]

        # Skip uniform cases
        if len(success) == 0 or len(fail) == 0:
            uniform = 'all_succ' if len(fail) == 0 else 'all_fail'
            print(f"{func:<6} {len(success):>6} {len(fail):>6} "
                  f"{'-':>12} {'-':>12} {'-':>8}  {uniform}")
            continue

        # Compare phase0 outcomes
        p0_succ = [r['p0'] for r in success if r['p0'] is not None]
        p0_fail = [r['p0'] for r in fail if r['p0'] is not None]

        if not p0_succ or not p0_fail:
            continue

        p0_succ_med = np.median(p0_succ)
        p0_fail_med = np.median(p0_fail)

        # Mann-Whitney U test (non-parametric: do success seeds have lower p0?)
        from scipy.stats import mannwhitneyu
        try:
            stat, pval = mannwhitneyu(p0_succ, p0_fail, alternative='less')
            predictor = "YES" if pval < 0.05 else "NO"
        except Exception:
            pval = 1.0
            predictor = "?"

        # Diagnosis
        ratio = p0_fail_med / max(p0_succ_med, 1e-12)
        if ratio > 10 and predictor == "YES":
            diag = f"TOPOLOGY LOTTERY (p0_fail/succ={ratio:.1f}×, p={pval:.3f})"
        elif predictor == "YES":
            diag = f"phase0 weakly predicts (p={pval:.3f})"
        else:
            diag = f"ENDGAME LOTTERY (phase0 doesn't predict, p={pval:.3f})"

        print(f"{func:<6} {len(success):>6} {len(fail):>6} "
              f"{p0_succ_med:>12.3e} {p0_fail_med:>12.3e} {predictor:>8}  {diag}")


if __name__ == '__main__':
    main()
