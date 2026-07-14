#!/usr/bin/env python
"""Rebuild summary.csv files from f<k>.pkl ground truth.

Usage:
    python rebuild_summaries.py --check            # report only, no writes
    python rebuild_summaries.py --fix              # rewrite damaged summaries
    python rebuild_summaries.py --fix --root experiments/cec2020/d10

Logic per maxevals_* directory:
  1. Read every f<k>.pkl -> recompute mean/median/std/best/worst from
     pkl['errors'] (float64, no clipping).
  2. elapsed_sec: taken from the existing summary.csv row if present,
     else from pkl['params']['elapsed_sec'] (MSC runs), else empty.
  3. --check: report SUMMARY_MISSING_FUNC (pkl exists, row absent),
     ROW_WITHOUT_PKL (row exists, pkl absent), STAT_MISMATCH
     (|rel diff| > 1e-12 between summary row and pkl recomputation).
  4. --fix: rewrite summary.csv covering exactly the set of pkl files,
     sorted by function index. A row without pkl is DROPPED (reported).
     Nothing is written if the directory has no pkl files.

The pkl files are never modified.
"""

import argparse
import csv
import glob
import os
import pickle
import re
import sys

import numpy as np

FIELDS = ['func', 'n_runs', 'maxevals', 'mean', 'median', 'std',
          'best', 'worst', 'elapsed_sec']


def fnum(name):
    m = re.match(r'f(\d+)$', name)
    return int(m.group(1)) if m else 10**9


def read_summary(path):
    rows = {}
    if not os.path.exists(path):
        return rows
    with open(path, newline='') as fh:
        for r in csv.DictReader(fh):
            rows[r['func']] = r
    return rows


def pkl_row(pkl_path, old_row):
    with open(pkl_path, 'rb') as fh:
        d = pickle.load(fh)
    e = np.asarray(d['errors'], dtype=np.float64)
    elapsed = ''
    if old_row and old_row.get('elapsed_sec') not in (None, ''):
        elapsed = old_row['elapsed_sec']
    elif isinstance(d.get('params'), dict) and 'elapsed_sec' in d['params']:
        elapsed = round(float(d['params']['elapsed_sec']), 1)
    return {
        'func':        d['func'],
        'n_runs':      len(e),
        'maxevals':    d['maxevals'],
        'mean':        float(e.mean()),
        'median':      float(np.median(e)),
        'std':         float(e.std()),
        'best':        float(e.min()),
        'worst':       float(e.max()),
        'elapsed_sec': elapsed,
    }


def close(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if a == b:
        return True
    denom = max(abs(a), abs(b), 1e-300)
    return abs(a - b) / denom < 1e-12


def process_dir(mdir, fix):
    pkls = sorted(glob.glob(os.path.join(mdir, 'f*.pkl')),
                  key=lambda p: fnum(os.path.splitext(os.path.basename(p))[0]))
    spath = os.path.join(mdir, 'summary.csv')
    old = read_summary(spath)
    issues = []

    if not pkls:
        if old:
            issues.append(('NO_PKL_AT_ALL', mdir,
                           '%d summary rows, zero pkl files' % len(old)))
        return issues, False

    new_rows, pkl_funcs = [], set()
    for p in pkls:
        fn = os.path.splitext(os.path.basename(p))[0]
        pkl_funcs.add(fn)
        try:
            row = pkl_row(p, old.get(fn))
        except Exception as exc:
            issues.append(('PKL_READ_ERROR', p, repr(exc)))
            continue
        new_rows.append(row)
        if fn not in old:
            issues.append(('SUMMARY_MISSING_FUNC', mdir, fn))
        else:
            for k in ('mean', 'median', 'best', 'worst'):
                if not close(old[fn][k], row[k]):
                    issues.append(('STAT_MISMATCH', mdir,
                                   '%s.%s summary=%s pkl=%s'
                                   % (fn, k, old[fn][k], row[k])))
                    break

    for fn in old:
        if fn not in pkl_funcs:
            issues.append(('ROW_WITHOUT_PKL', mdir, fn))

    changed = False
    if fix and any(t in ('SUMMARY_MISSING_FUNC', 'STAT_MISMATCH',
                         'ROW_WITHOUT_PKL') for t, _, _ in issues):
        with open(spath, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(new_rows)
        changed = True
    return issues, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='experiments')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--check', action='store_true')
    g.add_argument('--fix', action='store_true')
    args = ap.parse_args()

    mdirs = sorted(set(
        os.path.dirname(p) for p in
        glob.glob(os.path.join(args.root, '**', 'maxevals_*'),
                  recursive=True)
        if os.path.isdir(p)) | set(
        p for p in glob.glob(os.path.join(args.root, '**', 'maxevals_*'),
                             recursive=True) if os.path.isdir(p)))
    mdirs = [d for d in mdirs if os.path.basename(d).startswith('maxevals_')]

    n_issues = n_fixed = 0
    for d in mdirs:
        issues, changed = process_dir(d, args.fix)
        n_fixed += changed
        for tag, where, detail in issues:
            n_issues += 1
            print('%-22s %s  %s' % (tag, where, detail))
        if changed:
            print('REWRITTEN              %s' % d)

    print('---')
    print('dirs scanned: %d   issues: %d   summaries rewritten: %d'
          % (len(mdirs), n_issues, n_fixed))
    return 0 if (args.fix or n_issues == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
