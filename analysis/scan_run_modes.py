#!/usr/bin/env python3
"""
scan_run_modes.py — audit how each MSC-CMA result directory was launched.

Walks experiments/<suite>/d<dim>/MSC-CMA/maxevals_<N>/ and, for every
f<k>.pkl, recovers the run mode from three independent signals stored in
the payload, cross-checks them, and reports per directory.

Signals (in payload):
    params['cli_args']        full argparse namespace at launch (authoritative)
    params['auto']            bool
    params['msc_config']      None when auto, dict when single-config
    cycles_per_seed[*][*]['mode']
                              'alt-0'/'alt-1' (alt-CB) | 'default' (single OR anchor)

Mode resolution:
    alt-CB        auto and not anchor and not tune_class
    alt-CB(tuned) auto and tune_class set
    anchor        auto and anchor          (cycle mode is 'default', like single)
    single-config not auto                 (msc_config is a dict)

Anchor and single-config share cycle mode 'default', so they are told apart
only by cli_args['anchor'].  When the cli_args, msc_config and cycle-mode
signals disagree, the row is flagged CONFLICT and all three are printed.

Output:
    - grouped console report
    - run_mode_audit.csv next to the scanned root (--csv to relocate)

Usage:
    python analysis/scan_run_modes.py [ROOT]
    python analysis/scan_run_modes.py experiments --csv /tmp/audit.csv
    python analysis/scan_run_modes.py experiments --first-only   # 1 pkl/dir
"""

from __future__ import annotations

import argparse
import csv
import os
import pickle
import sys
from collections import defaultdict


# ----------------------------------------------------------------------
# Signal extraction
# ----------------------------------------------------------------------

def _load(path):
    """Unpickle one payload; return dict or None on failure."""
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as exc:                       # corrupt / foreign / old
        return {'__load_error__': f'{type(exc).__name__}: {exc}'}


def _cycle_modes(payload):
    """Collect the set of cycle 'mode' labels across all seeds/cycles."""
    modes = set()
    for per_seed in payload.get('cycles_per_seed') or []:
        for cyc in per_seed or []:
            m = cyc.get('mode') if isinstance(cyc, dict) else None
            if m is not None:
                modes.add(m)
    return modes


def _mode_from_cli(cli, auto_flag):
    """Authoritative mode from cli_args (falls back to top-level auto)."""
    if not isinstance(cli, dict):
        cli = {}
    auto = cli.get('auto', auto_flag)
    anchor = bool(cli.get('anchor', False))
    tune = cli.get('tune_class', None)
    if auto is None:
        return None
    if not auto:
        return 'single-config'
    if anchor:
        return 'anchor'
    if tune:
        return f'alt-CB(tuned-{tune})'
    return 'alt-CB'


def _mode_from_cycles(modes):
    """Mode inferred from cycle labels alone."""
    if not modes:
        return None
    if any(m.startswith('alt-') for m in modes):
        return 'alt-CB'
    if modes <= {'default'}:
        return 'default-or-anchor'    # cannot separate single vs anchor here
    return None


def classify(payload):
    """Return a per-pkl record: mode, conflict flag, evidence, key params."""
    if '__load_error__' in payload:
        return {'mode': 'UNREADABLE', 'conflict': True,
                'evidence': payload['__load_error__']}

    params = payload.get('params') or {}
    cli = params.get('cli_args')
    auto_flag = params.get('auto')
    msc_cfg = params.get('msc_config', '__absent__')

    m_cli = _mode_from_cli(cli, auto_flag)
    m_cyc = _mode_from_cycles(_cycle_modes(payload))
    cfg_is_dict = isinstance(msc_cfg, dict)
    cfg_is_none = msc_cfg is None

    # Resolve: cli_args wins when present.
    mode = m_cli
    if mode is None:
        # No cli_args/auto — fall back to weaker signals.
        if m_cyc == 'alt-CB':
            mode = 'alt-CB'
        elif cfg_is_dict:
            mode = 'single-config'
        elif cfg_is_none:
            mode = 'auto(unspecified)'
        else:
            mode = 'UNKNOWN'

    # Cross-check for conflicts.
    conflict = False
    notes = []
    base = mode.split('(')[0]
    if m_cyc == 'alt-CB' and base not in ('alt-CB',):
        conflict = True
        notes.append("cycles say alt-CB")
    if m_cyc == 'default-or-anchor' and base == 'alt-CB':
        conflict = True
        notes.append("cycles say default (not alt-CB)")
    if base == 'single-config' and not cfg_is_dict:
        conflict = True
        notes.append("single-config but msc_config not a dict")
    if base in ('alt-CB', 'anchor') and cfg_is_dict:
        conflict = True
        notes.append("auto-mode but msc_config is a dict")

    # Distinguishing params (single-config) and reuse flag (alt-CB).
    sampling = nib = sdiv = reuse = None
    if cfg_is_dict:
        sampling = msc_cfg.get('sampling_method')
        nib = msc_cfg.get('n_initial_basins')
        sdiv = msc_cfg.get('sigma_divisor')
    if isinstance(cli, dict):
        reuse = (not cli.get('no_phase0_reuse', False))

    meta = payload.get('meta') or {}
    return {
        'mode': mode,
        'conflict': conflict,
        'evidence': '; '.join(notes) if notes else 'consistent',
        'sig_cli': m_cli, 'sig_cycles': m_cyc,
        'msc_config': 'dict' if cfg_is_dict else ('None' if cfg_is_none else 'absent'),
        'sampling': sampling, 'n_initial_basins': nib, 'sigma_divisor': sdiv,
        'phase0_reuse': reuse,
        'timestamp': meta.get('timestamp'), 'hostname': meta.get('hostname'),
        'cma_version': meta.get('cma_version'),
        'cmd': _rebuild_cmd(cli) if isinstance(cli, dict) else None,
    }


def _rebuild_cmd(cli):
    """Approximate command line from cli_args (for the audit trail)."""
    parts = ['python benchmark/msc.py']
    for key in ('suite', 'dim', 'functions', 'runs', 'jobs', 'maxevals'):
        v = cli.get(key)
        if v not in (None, ''):
            parts.append(f'--{key.replace("_", "-")} {v}')
    for flag in ('auto', 'anchor', 'force', 'rotate_sampling'):
        if cli.get(flag):
            parts.append(f'--{flag.replace("_", "-")}')
    if cli.get('no_phase0_reuse'):
        parts.append('--no-phase0-reuse')
    for key in ('sampling_method', 'sobol_n_policy', 'tune_class',
                'refine_frac', 'refine_mult'):
        v = cli.get(key)
        if v not in (None, ''):
            parts.append(f'--{key.replace("_", "-")} {v}')
    return ' '.join(parts)


# ----------------------------------------------------------------------
# Directory walk
# ----------------------------------------------------------------------

def _parse_dir(path):
    """Pull (suite, dim, maxevals) from .../<suite>/d<dim>/MSC-CMA/maxevals_<N>."""
    parts = path.replace('\\', '/').split('/')
    suite = dim = mx = None
    for i, p in enumerate(parts):
        if p.startswith('maxevals_'):
            mx = p[len('maxevals_'):]
        elif p.startswith('d') and p[1:].isdigit():
            dim = p[1:]
            if i >= 1:
                suite = parts[i - 1]
    return suite, dim, mx


def scan(root, first_only=False):
    rows = []
    for dirpath, _, files in os.walk(root):
        if os.path.basename(os.path.dirname(dirpath + '/.')) and \
           'MSC-CMA' not in dirpath:
            continue
        if not os.path.basename(dirpath).startswith('maxevals_'):
            continue
        if 'MSC-CMA' not in dirpath:
            continue

        pkls = sorted(f for f in files
                      if f.startswith('f') and f.endswith('.pkl'))
        suite, dim, mx = _parse_dir(dirpath)

        if not pkls:
            rows.append({'suite': suite, 'dim': dim, 'maxevals': mx,
                         'dir': dirpath, 'funcs': '', 'func_count': 0,
                         'mode': 'NO-PKL', 'conflict': False,
                         'evidence': 'no f*.pkl (e.g. _nopkl export)'})
            continue

        scanned = pkls[:1] if first_only else pkls
        per_pkl = {}
        for fn in scanned:
            rec = classify(_load(os.path.join(dirpath, fn)))
            per_pkl[fn] = rec

        # Group functions by detected mode within this directory.
        by_mode = defaultdict(list)
        for fn, rec in per_pkl.items():
            by_mode[rec['mode']].append(fn[:-4])     # strip .pkl

        mixed = len(by_mode) > 1
        for mode, fns in sorted(by_mode.items()):
            sample = next(r for f, r in per_pkl.items() if f[:-4] in fns)
            rows.append({
                'suite': suite, 'dim': dim, 'maxevals': mx, 'dir': dirpath,
                'func_count': len(fns),
                'funcs': ','.join(sorted(fns, key=_fkey)),
                'mode': mode,
                'conflict': sample['conflict'] or mixed,
                'evidence': (('MIXED dir; ' if mixed else '')
                             + sample.get('evidence', '')),
                'sig_cli': sample.get('sig_cli'),
                'sig_cycles': sample.get('sig_cycles'),
                'msc_config': sample.get('msc_config'),
                'sampling': sample.get('sampling'),
                'n_initial_basins': sample.get('n_initial_basins'),
                'sigma_divisor': sample.get('sigma_divisor'),
                'phase0_reuse': sample.get('phase0_reuse'),
                'timestamp': sample.get('timestamp'),
                'hostname': sample.get('hostname'),
                'cma_version': sample.get('cma_version'),
                'cmd': sample.get('cmd'),
            })
    return rows


def _fkey(name):
    digits = ''.join(c for c in name if c.isdigit())
    return int(digits) if digits else 0


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------

_CSV_FIELDS = ['suite', 'dim', 'maxevals', 'mode', 'conflict', 'func_count',
               'funcs', 'evidence', 'sig_cli', 'sig_cycles', 'msc_config',
               'sampling', 'n_initial_basins', 'sigma_divisor', 'phase0_reuse',
               'timestamp', 'hostname', 'cma_version', 'cmd', 'dir']


def report(rows, csv_path):
    rows.sort(key=lambda r: (str(r.get('suite')), int(r.get('dim') or 0),
                             int(r.get('maxevals') or 0), str(r.get('mode'))))
    flagged = [r for r in rows if r.get('conflict')]

    print(f"\n{'SUITE':<9}{'DIM':>4}{'MAXEVALS':>11}  {'MODE':<20}"
          f"{'#fn':>4}  FUNCS")
    print('-' * 88)
    for r in rows:
        flag = ' ⚠' if r.get('conflict') else ''
        print(f"{str(r.get('suite')):<9}{str(r.get('dim')):>4}"
              f"{str(r.get('maxevals')):>11}  {str(r.get('mode')):<20}"
              f"{r.get('func_count', 0):>4}  {r.get('funcs', '')}{flag}")

    if flagged:
        print(f"\n⚠ {len(flagged)} row(s) need a look "
              f"(conflict or mixed directory):")
        for r in flagged:
            print(f"  {r.get('suite')} d{r.get('dim')} "
                  f"{r.get('maxevals')} → {r.get('mode')}  "
                  f"[{r.get('evidence')}]")
            print(f"      cli={r.get('sig_cli')} cycles={r.get('sig_cycles')} "
                  f"msc_config={r.get('msc_config')}")
    else:
        print("\nNo conflicts — every directory's signals agree.")

    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=_CSV_FIELDS, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    print(f"\nFull audit → {csv_path}  ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('root', nargs='?', default='experiments',
                    help='results root (default: experiments)')
    ap.add_argument('--csv', default=None,
                    help='audit CSV path (default: <root>/run_mode_audit.csv)')
    ap.add_argument('--first-only', action='store_true',
                    help='read only the first pkl per dir (fast, assumes '
                         'the whole dir was one launch)')
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"ERROR: not a directory: {args.root}", file=sys.stderr)
        sys.exit(1)

    csv_path = args.csv or os.path.join(args.root, 'run_mode_audit.csv')
    rows = scan(args.root, first_only=args.first_only)
    if not rows:
        print("No MSC-CMA maxevals_* directories found under "
              f"{args.root!r}.")
        return
    report(rows, csv_path)


if __name__ == '__main__':
    main()
