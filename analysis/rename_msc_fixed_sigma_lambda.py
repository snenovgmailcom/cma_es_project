#!/usr/bin/env python3
"""Rename NEA2-INIT results to MSC-fixed_sigma_lambda without rerunning them.

Defaults to a read-only preview; pass --apply to publish the changes.
Only the project's experiments/, ablations/experiments/, and
ablations/comparisons/ suite/dimension algorithm entries are examined.
Original result directories are retained in ablations/rename_backups/.
Run this script only on your own trusted benchmark PKLs.
"""

import argparse
from datetime import datetime, timezone
import math
import os
from pathlib import Path
import pickle
import re
import shutil
import sys
import uuid

import numpy as np

OLD = 'NEA2-INIT'
NEW = 'MSC-fixed_sigma_lambda'
ROOT = Path(__file__).resolve().parents[1]


def present(path):
    return os.path.lexists(path)


def renamed_path(path):
    return Path(*(NEW if part == OLD else part for part in Path(path).parts))


def equal_value(a, b):
    """Check serialization preserved all numerical values, including NaNs."""
    if type(a) is not type(b):
        return False
    if isinstance(a, np.ndarray):
        if a.dtype != b.dtype or a.shape != b.shape:
            return False
        if a.dtype.hasobject:
            return all(equal_value(x, y) for x, y in zip(a.flat, b.flat))
        return a.tobytes() == b.tobytes()
    if isinstance(a, np.generic):
        return a.dtype == b.dtype and a.tobytes() == b.tobytes()
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal_value(v, b[k]) for k, v in a.items())
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(equal_value(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and math.isnan(a):
        return math.isnan(b)
    return a == b


def read_result(path, expected):
    with path.open('rb') as handle:
        data = pickle.load(handle)
    if not isinstance(data, dict) or data.get('algorithm') != expected:
        raise ValueError(f'{path}: expected algorithm={expected!r}')
    params = data.get('params', {})
    if not isinstance(params, dict):
        raise ValueError(f'{path}: params must be a dictionary')
    variant = params.get('variant')
    if variant not in (None, 'nea2-init', 'fixed_sigma_lambda'):
        raise ValueError(f'{path}: unexpected variant={variant!r}')
    return data


def rename_metadata(data):
    data['algorithm'] = NEW
    params = data.get('params', {})
    if params.get('variant') == 'nea2-init':
        params['variant'] = 'fixed_sigma_lambda'
    # An explicitly supplied output path is metadata, not benchmark data.
    cli = params.get('cli_args', {})
    if isinstance(cli, dict) and isinstance(cli.get('outdir'), str) and cli['outdir']:
        cli['outdir'] = str(renamed_path(cli['outdir']))
    return data


def result_files(directory):
    files = []
    for current, dirs, names in os.walk(directory, followlinks=False):
        for name in dirs + names:
            if (Path(current) / name).is_symlink():
                raise ValueError(f'Symlink inside a real result directory: {Path(current) / name}')
        for name in names:
            if name.endswith('.pkl'):
                if not re.fullmatch(r'f\d+\.pkl', name):
                    raise ValueError(f'Unexpected PKL filename: {Path(current) / name}')
                files.append(Path(current) / name)
    if not files:
        raise ValueError(f'No function PKLs in {directory}')
    return sorted(files)


def dimension_dirs(base):
    if not base.exists():
        return
    if base.is_symlink():
        raise ValueError(f'Result root must be a real directory: {base}')
    for suite in sorted(base.iterdir()):
        if not re.fullmatch(r'cec\d{4}', suite.name):
            continue
        if suite.is_symlink():
            raise ValueError(f'Suite must be a real directory: {suite}')
        if not suite.is_dir():
            continue
        for dim in sorted(suite.iterdir()):
            if not re.fullmatch(r'd\d+', dim.name):
                continue
            if dim.is_symlink():
                raise ValueError(f'Dimension must be a real directory: {dim}')
            if dim.is_dir():
                yield dim


def preflight(root):
    moves, links, known = [], [], set()
    bases = (root / 'ablations/experiments', root / 'experiments',
             root / 'ablations/comparisons')
    for base in bases:
        for dim in dimension_dirs(base):
            old, new = dim / OLD, dim / NEW
            if present(old) and present(new):
                raise ValueError(f'Both names exist; resolve this collision first: {old}, {new}')
            path = old if present(old) else new
            if not present(path):
                continue
            if path.is_symlink():
                target = Path(os.readlink(path))
                absolute = Path(os.path.abspath(path.parent / target))
                updated = renamed_path(absolute)
                links.append((path, new, updated))
            else:
                if base == bases[2] or not path.is_dir():
                    raise ValueError(f'Expected an algorithm symlink here: {path}')
                files = result_files(path)
                for pkl in files:
                    data = read_result(pkl, OLD if path == old else NEW)
                    if path == new and not equal_value(data, rename_metadata(pickle.loads(pickle.dumps(data)))):
                        raise ValueError(f'New-named PKL has stale metadata: {pkl}')
                known.add(new)
                if path == old:
                    moves.append((old, new, files))
    # Every alias must resolve to a known result tree, possibly through another alias.
    aliases = {new: target for _, new, target in links}
    for old, new, target in links:
        seen = {new}
        final = target
        while final in aliases:
            if final in seen:
                raise ValueError(f'Algorithm symlink cycle: {old}')
            seen.add(final)
            final = aliases[final]
        if final not in known:
            raise ValueError(f'{old}: target is outside the recognized result directories: {target}')
    return moves, links


def apply(root, moves, links):
    changing_links = [(old, new, target) for old, new, target in links
                      if old != new or Path(os.readlink(old)) != target]
    if not moves and not changing_links:
        print('Already migrated; no changes needed.')
        return
    backup = None
    staged = []
    if moves:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = root / 'ablations/rename_backups' / f'{stamp}-{uuid.uuid4().hex[:8]}'
        # Stage and verify every output before publishing the first directory.
        for source, destination, files in moves:
            stage = backup / 'staged' / source.relative_to(root)
            shutil.copytree(source, stage)
            for source_pkl in files:
                expected = rename_metadata(read_result(source_pkl, OLD))
                staged_pkl = stage / source_pkl.relative_to(source)
                with staged_pkl.open('wb') as handle:
                    pickle.dump(expected, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    handle.flush()
                    os.fsync(handle.fileno())
                actual = read_result(staged_pkl, NEW)
                if not equal_value(expected, actual):
                    raise ValueError(f'Staged verification failed: {staged_pkl}')
            staged.append((source, destination, stage))
        for source, destination, stage in staged:
            original = backup / 'original' / source.relative_to(root)
            original.parent.mkdir(parents=True, exist_ok=True)
            if present(destination):
                raise ValueError(f'Destination appeared during migration: {destination}')
            os.rename(source, original)
            try:
                os.rename(stage, destination)
            except BaseException:
                os.rename(original, source)
                raise
    for old, new, target in changing_links:
        if old != new:
            if present(new):
                raise ValueError(f'Destination appeared during migration: {new}')
            os.rename(old, new)
        temporary = new.with_name(f'.{NEW}-{uuid.uuid4().hex}.tmp')
        try:
            temporary.symlink_to(target, target_is_directory=True)
            os.replace(temporary, new)
        finally:
            if temporary.is_symlink():
                temporary.unlink()
    # Validate the published data and aliases, including absence of old entries.
    remaining, checked_links = preflight(root)
    if remaining or any(old != new or not new.is_dir() for old, new, _ in checked_links):
        raise ValueError('Post-migration verification failed')
    print(f'DONE: {sum(len(files) for _, _, files in moves)} PKLs; '
          f'{len(moves)} result directories; {len(changing_links)} symlinks.')
    if backup:
        print(f'Original result directories: {backup / "original"}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        moves, links = preflight(root)
        for old, new, files in moves:
            print(f'{old.relative_to(root)} -> {new.name}: {len(files)} PKLs')
        for old, new, target in links:
            if old != new or Path(os.readlink(old)) != target:
                print(f'Link {old.relative_to(root)} -> {new.name} -> {target}')
        if args.apply:
            apply(root, moves, links)
        else:
            print(f'DRY RUN: {sum(len(files) for _, _, files in moves)} PKLs, '
                  f'{len(moves)} result directories. Use --apply to rename.')
    except (OSError, ValueError, pickle.UnpicklingError, EOFError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
