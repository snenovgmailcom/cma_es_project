#!/usr/bin/env python3
"""
ablations/analysis/fbtc_diff.py -- per-function FBTC: FULL vs an ablation.

FBTC per the manuscript (par. 3.1): 51 log-uniformly spaced targets tau
in [1e-8, 1e2]; FBTC = fraction of (target, run) pairs with e <= tau.
Reads per-run final errors from the pkl files (key 'errors'); prints to
stdout, writes nothing.
"""

import argparse
import os
import pickle
import sys

import numpy as np

_ABL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_ABL_DIR)

N_TARGETS = 51
TARGETS = np.logspace(-8.0, 2.0, N_TARGETS)


def load_errors(path):
    with open(path, 'rb') as fh:
        d = pickle.load(fh)
    if 'errors' not in d:
        sys.exit(f"ERROR: no 'errors' key in {path}; keys: {sorted(d)}")
    return np.asarray(d['errors'], dtype=np.float64)


def fbtc(errors):
    """Fraction of (target, run) pairs with e <= tau."""
    hits = errors[:, None] <= TARGETS[None, :]
    return float(np.mean(hits))


def main():
    p = argparse.ArgumentParser(description='FBTC diff: FULL vs ablation.')
    p.add_argument('--suite', required=True)
    p.add_argument('--dim', type=int, required=True)
    p.add_argument('--maxevals', type=int, required=True)
    p.add_argument('--functions', type=str, required=True)
    p.add_argument('--ablation', type=str, default='NO-NBC')
    p.add_argument('--full-algo', type=str, default='MSC-CMA')
    args = p.parse_args()

    fnums = [int(x.strip().lstrip('f')) for x in args.functions.split(',')]
    cell = os.path.join(args.suite, f'd{args.dim}')
    dir_full = os.path.join(_ROOT, 'experiments', cell, args.full_algo,
                            f'maxevals_{args.maxevals}')
    dir_abl = os.path.join(_ABL_DIR, 'experiments', cell, args.ablation,
                           f'maxevals_{args.maxevals}')

    print(f'FBTC ({N_TARGETS} targets, [1e-8, 1e2]), '
          f'{args.suite} d{args.dim} maxevals={args.maxevals}')
    print(f'FULL: {dir_full}')
    print(f'ABL : {dir_abl}')
    print(f'{"func":>5s} {"FULL":>8s} {args.ablation:>10s} {"diff":>8s}')

    s_full = s_abl = 0.0
    for fnum in fnums:
        e_full = load_errors(os.path.join(dir_full, f'f{fnum}.pkl'))
        e_abl = load_errors(os.path.join(dir_abl, f'f{fnum}.pkl'))
        v_full, v_abl = fbtc(e_full), fbtc(e_abl)
        s_full += v_full
        s_abl += v_abl
        print(f'{"f" + str(fnum):>5s} {v_full:8.3f} {v_abl:10.3f} '
              f'{v_full - v_abl:+8.3f}')

    print(f'{"SUM":>5s} {s_full:8.3f} {s_abl:10.3f} {s_full - s_abl:+8.3f}')


if __name__ == '__main__':
    main()
