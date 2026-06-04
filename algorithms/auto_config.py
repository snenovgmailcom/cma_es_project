"""
auto_config.py — the two MSC-CMA configurations (B and C) for alt-CB.

Two MSCConfig instances (_B_BASE, _C_BASE) define both regimes.  The only
dimension-dependent law is the universal sigma scaling anchored at D=10:

        sigma_divisor(class, D) = SIGMA_DIVISOR_REF_{B,C} * sqrt(10 / D)

(standard CMA sigma0 ~ sqrt(D) box-scaling).  All other parameters are
universal across (dim, maxevals).
"""

from __future__ import annotations

import dataclasses as _dc
import math

from config import MSCConfig


# ──────────────────────────────────────────────────────────────────────────────
# Sigma divisor reference values (anchored at D=10).
# Optuna v3 dual-metric champions (cec2017 D=10 100k).
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
# Base configurations (Optuna v3 dual-metric champions, cec2017 D=10 100k).
# The sigma_divisor field is overwritten per-dim by get_B/get_C using
# _scale_sigma_divisor; the placeholder here is the D=10 value.
# ──────────────────────────────────────────────────────────────────────────────

_B_BASE = MSCConfig(
    n_phase0=4096,
    sampling_method='sobol',
    sigma_divisor=SIGMA_DIVISOR_REF_B,
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
    n_phase0=4096,
    sampling_method='sobol',
    sigma_divisor=SIGMA_DIVISOR_REF_C,
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

def get_B(dim: int) -> MSCConfig:
    """Return the B-class config for the given dim (sqrt(10/D) sigma scaling)."""
    return _dc.replace(_B_BASE,
                       sigma_divisor=_scale_sigma_divisor(SIGMA_DIVISOR_REF_B, dim))


def get_C(dim: int) -> MSCConfig:
    """Return the C-class config for the given dim (sqrt(10/D) sigma scaling)."""
    return _dc.replace(_C_BASE,
                       sigma_divisor=_scale_sigma_divisor(SIGMA_DIVISOR_REF_C, dim))


__all__ = [
    "D_REF",
    "SIGMA_DIVISOR_REF_B",
    "SIGMA_DIVISOR_REF_C",
    "get_B",
    "get_C",
]
