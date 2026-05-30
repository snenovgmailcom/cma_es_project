"""Compare per-seed final outcomes across sampling methods."""
import pickle
import numpy as np
import argparse
import os
import glob


def load_per_seed(pkl_path):
    """Return dict: seed_idx -> final_error."""
    if not os.path.exists(pkl_path):
        return None
    d = pickle.load(open(pkl_path, 'rb'))
    out = {}
    for seed_idx, imp in enumerate(d['improvements']):
        if len(imp) > 0:
            out[seed_idx] = float(imp[-1, 1])
        else:
            out[seed_idx] = None
    return out


def compare_funcs(funcs, lhs_dir, halton_dir, sobol_dir):
    print(f"{'seed':>4} | {'func':>5} | {'LHS':>12} | {'Halton':>12} | {'Sobol':>12} | identical?")
    print('-' * 80)

    for f in funcs:
        lhs = load_per_seed(f'{lhs_dir}/f{f}.pkl')
        hal = load_per_seed(f'{halton_dir}/f{f}.pkl')
        sob = load_per_seed(f'{sobol_dir}/f{f}.pkl')

        if not lhs:
            continue

        n_identical = 0
        n_diff = 0
        max_diff_seed = None
        max_diff_val = 0.0

        for seed in sorted(lhs.keys()):
            l = lhs.get(seed)
            h = hal.get(seed)
            s = sob.get(seed)
            if l is None or h is None or s is None:
                continue

            # Compare with relative tolerance
            vals = [l, h, s]
            mn, mx = min(vals), max(vals)
            rel_diff = (mx - mn) / max(mx, 1e-12)
            if rel_diff < 0.01:
                n_identical += 1
            else:
                n_diff += 1
                if rel_diff > max_diff_val:
                    max_diff_val = rel_diff
                    max_diff_seed = seed

        print(f"\nf{f}: identical_seeds={n_identical}/{len(lhs)} "
              f"different_seeds={n_diff}/{len(lhs)} "
              f"(max diff: seed {max_diff_seed}, rel={max_diff_val:.1%})")

        # Show first 10 different seeds (если има)
        diff_seeds = []
        for seed in sorted(lhs.keys()):
            l, h, s = lhs.get(seed), hal.get(seed), sob.get(seed)
            if all(x is not None for x in (l, h, s)):
                vals = [l, h, s]
                mn, mx = min(vals), max(vals)
                if (mx - mn) / max(mx, 1e-12) > 0.01:
                    diff_seeds.append((seed, l, h, s))

        for seed, l, h, s in diff_seeds[:10]:
            print(f"   seed {seed:>2}:  L={l:.3e}  H={h:.3e}  S={s:.3e}")
        if len(diff_seeds) > 10:
            print(f"   ... and {len(diff_seeds) - 10} more different seeds")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--lhs-dir', default='/tmp/sampling_test_lhs')
    ap.add_argument('--halton-dir', default='/tmp/sampling_test_halton')
    ap.add_argument('--sobol-dir', default='/tmp/sampling_test_sobol')
    ap.add_argument('--funcs', default='21,23,27,29')
    args = ap.parse_args()

    funcs = [int(x) for x in args.funcs.split(',')]
    compare_funcs(funcs, args.lhs_dir, args.halton_dir, args.sobol_dir)
