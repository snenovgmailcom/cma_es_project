"""
config.py — MSC-CMA-ES configuration.

MSCConfig is a plain container for one parameter set.  In production it is
only ever instantiated by auto_config.get_B / get_C (the B and C classes);
there is no standalone default-config run mode.
"""

from dataclasses import dataclass


@dataclass
class MSCConfig:
    """All algorithm parameters in one place."""

    # ── Phase-0 ──────────────────────────────────────────────────────
    n_phase0: int = 4096             # direct N for Phase-0 sample (Sobol pow2)
    k: int = 1
    n_initial_basins: int = 33
    min_basin_size: int = 5
    sigma_elite_frac: float = 0.2    # top fraction defining basin elite center
    sampling_method: str = 'sobol'   # 'lhs' | 'sobol' | 'halton'

    # ── CMA ──────────────────────────────────────────────────────────
    sigma_divisor: float = 2.6714
    cma_popsize: int = 50
    popsize_frac: float = 0.2        # popsize = ceil(basin_size * popsize_frac)
    tolfun_exp: int = 1
    tolx_exp: int = 6
    s_tol: float = 6.208
    nearest_better_k: int = 5

    # ── Refinement ──────────────────────────────────────────────────
    refine_frac: float = 0.05        # explicit fraction of maxevals reserved

    # ── NBC internals ───────────────────────────────────────────────
    nbc_b: float = 2.0
    nbc_min_incoming: int = 3

    def summary(self) -> str:
        return (
            f"N0={self.n_phase0} k={self.k} nib={self.n_initial_basins} "
            f"nbk={self.nearest_better_k} sd={self.sigma_divisor} "
            f"ef={self.sigma_elite_frac} pf={self.popsize_frac} "
            f"tf={self.tolfun_exp} tx={self.tolx_exp} s_tol={self.s_tol} "
            f"rf={self.refine_frac:.3f} cma={self.cma_popsize} "
            f"sampling={self.sampling_method}"
        )
