"""
auto_config.py — two global MSC-CMA configurations (B and C) for alt-CB.

Drastic simplification of the prior MATRIX-based design:
  * No (dim, maxevals) lookup.
  * No nearest-cell fallback warnings.
  * No per-cell tunable dict.
  * Two MSCConfig instances (_B_BASE, _C_BASE) define both regimes.

The single dimension-dependent law preserved is the universal sigma scaling
anchored at D=10:

        sigma_divisor(class, D) = SIGMA_DIVISOR_REF_{B,C} * sqrt(10 / D)

This corresponds to the standard CMA sigma0 ~ sqrt(D) box-scaling.

All other parameters are universal across (dim, maxevals).  Tune them via
experiments/optuna_v3.py at a chosen anchor cell (currently D=10, 100k) and
paste the winners into _B_BASE / _C_BASE.

Refinement multiplier
---------------------
get_B(dim, refine_mult=k) and get_C(dim, refine_mult=k) optionally scale
refine_frac by k.  Default 1.0 → unmodified base config.  Use refine_mult
on non-anchor budgets where the absolute refinement budget would otherwise
get unreasonably long (large maxevals) or short (small maxevals).
"""

from __future__ import annotations

import math
import dataclasses as _dc

try:
    from .config import MSCConfig
except ImportError:  # compatibility for scripts that put algorithms/ on sys.path
    from config import MSCConfig


# ──────────────────────────────────────────────────────────────────────────────
# Sigma divisor reference values (anchored at D=10).
# Updated from Optuna v3 dual-metric champions (cec2017 D=10 100k).
# ──────────────────────────────────────────────────────────────────────────────

D_REF: int = 10

SIGMA_DIVISOR_REF_B: float = 1.6608948569080033  # B-study T322 (cec2017 D=10 100k)
SIGMA_DIVISOR_REF_C: float = 5.989240613667311   # C-study T264 (cec2017 D=10 100k)


def _scale_sigma_divisor(base: float, dim: int) -> float:
    """Universal sigma scaling law anchored at D=10."""
    dim = int(dim)
    if dim <= 0:
        raise ValueError(f"auto_config: dim must be positive, got {dim!r}.")
    return base * math.sqrt(D_REF / float(dim))


# ──────────────────────────────────────────────────────────────────────────────
# Base configurations.
# Updated to Optuna v3 dual-metric champions (cec2017 D=10 100k):
#   B-study T322: sum_mean=69.35 (#8), mean_ECDF=0.2974 (#2)
#   C-study T264: sum_mean=1779.32 (#1), mean_ECDF=0.2276 (#1)
#
# The sigma_divisor field is overwritten per-dim by get_B/get_C using
# _scale_sigma_divisor; the placeholder here is the D=10 value.
# ──────────────────────────────────────────────────────────────────────────────

_B_BASE = MSCConfig(
    # --- frozen structural ---
    n_phase0=4096,
    sampling_method='sobol',
    sobol_n_policy='nearest_pow2',
    ref_budget=100_000,
    # --- tuned: Optuna v3 B-study T322 (sum_mean=69.35, mean_ECDF=0.2974) ---
    sigma_divisor=SIGMA_DIVISOR_REF_B,    # 1.6608948569080033
    s_tol=11.547494511750605,
    tolfun_exp=6,
    tolx_exp=5,
    refine_frac=0.08965495538898643,
    n_initial_basins=5,
    cma_popsize=236,
    k=6,
    min_basin_size=155,
    nbc_b=3.0289994886574108,
    sigma_elite_frac=0.06492838126699994,
    popsize_frac=0.4343402198177367,
)


_C_BASE = MSCConfig(
    # --- frozen structural ---
    n_phase0=4096,
    sampling_method='sobol',
    sobol_n_policy='nearest_pow2',
    ref_budget=100_000,
    # --- tuned: Optuna v3 C-study T264 (mean_ECDF=0.2276 #1, sum_mean=1779.32 #1) ---
    sigma_divisor=SIGMA_DIVISOR_REF_C,    # 5.989240613667311
    s_tol=13.817541999859726,
    tolfun_exp=4,
    tolx_exp=8,
    refine_frac=0.03981005009689487,
    n_initial_basins=25,
    cma_popsize=12,
    k=5,
    min_basin_size=7,
    nbc_b=2.4982136680659166,
    sigma_elite_frac=0.41136439781745526,
    popsize_frac=0.12928936480761777,
)


# ──────────────────────────────────────────────────────────────────────────────
# Accessors.
# ──────────────────────────────────────────────────────────────────────────────

def get_B(dim: int, refine_mult: float = 1.0) -> MSCConfig:
    """Return the B-class config for the given dim.

    Applies the universal sqrt(10/D) sigma scaling.  Optionally scales
    refine_frac by refine_mult (default 1.0 = no scaling).
    """
    sigma = _scale_sigma_divisor(SIGMA_DIVISOR_REF_B, dim)
    if refine_mult == 1.0:
        return _dc.replace(_B_BASE, sigma_divisor=sigma)
    return _dc.replace(
        _B_BASE,
        sigma_divisor=sigma,
        refine_frac=_B_BASE.refine_frac * float(refine_mult),
    )


def get_C(dim: int, refine_mult: float = 1.0) -> MSCConfig:
    """Return the C-class config for the given dim.

    Applies the universal sqrt(10/D) sigma scaling.  Optionally scales
    refine_frac by refine_mult (default 1.0 = no scaling).
    """
    sigma = _scale_sigma_divisor(SIGMA_DIVISOR_REF_C, dim)
    if refine_mult == 1.0:
        return _dc.replace(_C_BASE, sigma_divisor=sigma)
    return _dc.replace(
        _C_BASE,
        sigma_divisor=sigma,
        refine_frac=_C_BASE.refine_frac * float(refine_mult),
    )


__all__ = [
    "D_REF",
    "SIGMA_DIVISOR_REF_B",
    "SIGMA_DIVISOR_REF_C",
    "get_B",
    "get_C",
]
