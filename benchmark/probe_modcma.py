#!/usr/bin/env python3
"""
Probe modcma API to discover correct attribute names for RR-CMA-ES.

Run this once on srv-01 and paste the output back. Then I can finalize
benchmark/rrcma.py without defensive guesses.

Usage:
    python probe_modcma.py
"""
import modcma
from modcma import c_maes

print(f"modcma version: {getattr(modcma, '__version__', 'unknown (no __version__ attr)')}")
print(f"modcma path: {getattr(modcma, '__file__', 'unknown')}")
print(f"c_maes path: {getattr(c_maes, '__file__', 'unknown')}")
print()

# === Top-level c_maes attributes ===
print("=== c_maes top-level (excluding dunder) ===")
for attr in sorted(a for a in dir(c_maes) if not a.startswith('_')):
    print(f"  {attr}")
print()

# === parameters submodule ===
print("=== c_maes.parameters ===")
for attr in sorted(a for a in dir(c_maes.parameters) if not a.startswith('_')):
    print(f"  {attr}")
print()

# === Modules class — instance attrs ===
print("=== c_maes.parameters.Modules() instance attributes ===")
m = c_maes.parameters.Modules()
for attr in sorted(a for a in dir(m) if not a.startswith('_')):
    try:
        val = getattr(m, attr)
        if callable(val):
            print(f"  {attr}() [callable]")
        else:
            print(f"  {attr} = {val!r}")
    except Exception as e:
        print(f"  {attr} = <error: {e}>")
print()

# === Settings class — try different constructor signatures ===
print("=== c_maes.parameters.Settings ===")
print("  Constructor signature attempts:")
try:
    import inspect
    sig = inspect.signature(c_maes.parameters.Settings.__init__)
    print(f"  signature: {sig}")
except (TypeError, ValueError):
    print("  (signature introspection not available — C++ binding)")

# Try a minimal construction to inspect attributes
import numpy as np
modules = c_maes.parameters.Modules()
attempts = [
    ("dim only", lambda: c_maes.parameters.Settings(2)),
    ("dim, modules", lambda: c_maes.parameters.Settings(2, modules)),
    ("dim, modules, sigma0", lambda: c_maes.parameters.Settings(2, modules, 1.0)),
    ("kwargs", lambda: c_maes.parameters.Settings(
        dim=2, modules=modules,
        lb=np.array([-1.0, -1.0]), ub=np.array([1.0, 1.0]),
        sigma0=0.5)),
]
settings_obj = None
for name, fn in attempts:
    try:
        settings_obj = fn()
        print(f"  ✓ {name} works")
        break
    except Exception as e:
        print(f"  ✗ {name}: {type(e).__name__}: {e}")

if settings_obj is not None:
    print()
    print("  Settings instance attributes:")
    for attr in sorted(a for a in dir(settings_obj) if not a.startswith('_')):
        try:
            val = getattr(settings_obj, attr)
            if callable(val):
                continue
            preview = repr(val)
            if len(preview) > 60:
                preview = preview[:57] + '...'
            print(f"    {attr} = {preview}")
        except Exception as e:
            print(f"    {attr} = <error: {e}>")
print()

# === Parameters class ===
print("=== c_maes.parameters.Parameters ===")
try:
    sig = inspect.signature(c_maes.parameters.Parameters.__init__)
    print(f"  signature: {sig}")
except (TypeError, ValueError):
    print("  (signature introspection not available)")

if settings_obj is not None:
    try:
        params = c_maes.parameters.Parameters(settings_obj)
        print(f"  ✓ Parameters(settings) works")
        print(f"  Parameters instance attributes (top 30):")
        attrs = sorted(a for a in dir(params) if not a.startswith('_'))
        for attr in attrs[:30]:
            try:
                val = getattr(params, attr)
                if callable(val):
                    continue
                preview = repr(val)
                if len(preview) > 60:
                    preview = preview[:57] + '...'
                print(f"    {attr} = {preview}")
            except Exception:
                print(f"    {attr} = <error>")
        if len(attrs) > 30:
            print(f"    ... and {len(attrs)-30} more")
    except Exception as e:
        print(f"  ✗ Parameters(settings): {type(e).__name__}: {e}")
print()

# === ModularCMAES class ===
print("=== c_maes.ModularCMAES ===")
try:
    sig = inspect.signature(c_maes.ModularCMAES.__init__)
    print(f"  signature: {sig}")
except (TypeError, ValueError):
    print("  (signature introspection not available)")

print("  Class methods/attributes (non-dunder):")
for attr in sorted(a for a in dir(c_maes.ModularCMAES) if not a.startswith('_')):
    print(f"    {attr}")
print()

# === Quick functional test: minimal RR-CMA-ES on sphere ===
print("=== Functional smoke test: tiny sphere optimization ===")
def sphere(x):
    x = np.asarray(x, dtype=float).ravel()
    return float(np.dot(x, x))

# Find repelling attr name
repelling_attr = None
for cand in ('repelling_restart', 'repelling', 'tabu',
             'tabu_restart', 'rr', 'tabu_archive'):
    if hasattr(c_maes.parameters.Modules(), cand):
        repelling_attr = cand
        break

if repelling_attr is None:
    print("  ✗ No repelling attribute found on Modules.")
    print("    Searched: repelling_restart, repelling, tabu, tabu_restart,"
          " rr, tabu_archive")
else:
    print(f"  ✓ Repelling attribute: {repelling_attr!r}")

# Find restart_strategy enum
print()
print("=== Restart strategy enum search ===")
for attr_name in dir(c_maes.parameters):
    if 'restart' in attr_name.lower() or 'strategy' in attr_name.lower():
        attr = getattr(c_maes.parameters, attr_name)
        print(f"  {attr_name}: {attr!r}")
        if hasattr(attr, '__members__'):
            print(f"    members: {list(attr.__members__)}")
        elif hasattr(attr, 'BIPOP'):
            print(f"    has .BIPOP = {attr.BIPOP!r}")

# Inspect Modules attributes related to restart
print()
print("=== Modules attributes related to restart ===")
m = c_maes.parameters.Modules()
for attr in dir(m):
    if attr.startswith('_'):
        continue
    if 'restart' in attr.lower() or 'strategy' in attr.lower() or 'bipop' in attr.lower() or 'ipop' in attr.lower():
        try:
            val = getattr(m, attr)
            print(f"  m.{attr} = {val!r} (type {type(val).__name__})")
        except Exception as e:
            print(f"  m.{attr} = <error: {e}>")

print()
print("=" * 60)
print("DONE. Paste the output back so I can finalize rrcma.py.")
print("=" * 60)
