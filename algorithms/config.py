"""
config.py — MSC-CMA-ES configuration.
"""

from dataclasses import dataclass


@dataclass
class MSCConfig:
    """All algorithm parameters in one place.

    Refinement:
        refine_frac  -1.0 = auto (scales with maxevals/ref_budget ratio).
                     >=0  = explicit fraction.
        ref_budget   reference CEC competition budget (set by runner).
                     0 = not set; auto falls back to 0.05.
    """

    # ── Phase-0 ──────────────────────────────────────────────────────
    n_phase0: int = 4096             # direct N for Phase-0 sample (Sobol pow2)
    k: int = 1
    n_initial_basins: int = 33
    min_basin_size: int = 5
    sigma_elite_frac: float = 0.2    # top fraction defining basin elite center
    sampling_method: str = 'lhs'
    rotate_sampling: bool = False    # rotate lhs→sobol→halton per cycle
    sobol_n_policy: str = 'arbitrary'  # arbitrary | nearest_pow2 | floor_pow2 | ceil_pow2
                                       # Only used when sampling_method='sobol'.
                                       # With direct n_phase0 control, set to 'arbitrary'.

    # ── CMA ──────────────────────────────────────────────────────────
    sigma_divisor: float = 2.6714
    cma_popsize: int = 50
    popsize_frac: float = 0.2        # popsize = ceil(basin_size * popsize_frac)
    tolfun_exp: int = 1
    tolx_exp: int = 6
    s_tol: float = 6.208
    nearest_better_k: int = 5

    # ── Refinement ──────────────────────────────────────────────────
    refine_frac: float = -1.0    # -1.0 = auto; else explicit fraction
    ref_budget: int = 0          # CEC competition budget; 0 = unset

    # ── phi override ────────────────────────────────────────────────
    phi_override: float = 0.0

    # ── NBC internals ───────────────────────────────────────────────
    nbc_b: float = 2.0
    nbc_min_incoming: int = 3

    def summary(self) -> str:
        rf_str = 'auto' if self.refine_frac < 0 else f'{self.refine_frac:.3f}'
        rb_str = f' rb={self.ref_budget:,}' if self.ref_budget > 0 else ''
        rot_str = ' rot=ON' if self.rotate_sampling else ''
        np_str = ''
        if self.sampling_method == 'sobol' and self.sobol_n_policy != 'arbitrary':
            np_str = f' n={self.sobol_n_policy}'
        return (
            f"N0={self.n_phase0} k={self.k} nib={self.n_initial_basins} nbk={self.nearest_better_k} "
            f"sd={self.sigma_divisor} ef={self.sigma_elite_frac} pf={self.popsize_frac} "
            f"tf={self.tolfun_exp} "
            f"tx={self.tolx_exp} s_tol={self.s_tol} "
            f"rf={rf_str}{rb_str} cma={self.cma_popsize}{rot_str}{np_str}"
        )


def resolve_refine_frac(cfg: 'MSCConfig', maxevals: int) -> float:
    """Resolve refine_frac: explicit if >=0, else piecewise-linear from ratio.

    Knots: (1×,0.05), (5×,0.10), (10×,0.20), (15×,0.30 cap).
    Fallback (ref_budget == 0): 0.05.
    """
    if cfg.refine_frac >= 0:
        return cfg.refine_frac
    if cfg.ref_budget <= 0:
        return 0.05
    ratio = maxevals / cfg.ref_budget
    knots = [(1.0, 0.05), (5.0, 0.10), (10.0, 0.20), (15.0, 0.30)]
    if ratio <= knots[0][0]:
        return knots[0][1]
    if ratio >= knots[-1][0]:
        return knots[-1][1]
    for (r0, f0), (r1, f1) in zip(knots, knots[1:]):
        if r0 <= ratio <= r1:
            t = (ratio - r0) / (r1 - r0)
            return f0 + t * (f1 - f0)
    return 0.05
