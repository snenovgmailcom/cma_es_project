"""
result.py — MSC-CMA-ES result dataclasses.

Hierarchy:
    RestartRecord   — one CMA restart (topo / refine)
    PhaseStats      — budget summary per phase (aggregated across cycles)
    CycleStats      — per-cycle summary (Phase-0 + Phase-1)
    RunResult       — one full run (51 per function) → goes into PKL
    BenchmarkResult — aggregated over all runs → goes into summary.csv
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np

from basin_id import BasinId


# =========================================================================
# Basin snapshot (frozen at Phase-0, for PKL reference)
# =========================================================================

@dataclass
class BasinSnapshot:
    """Lightweight basin record stored in PKL."""
    basin_id: BasinId
    size: int
    best_val: float
    diameter: float
    centroid_norm: np.ndarray   # normalized centroid (for reference)


# =========================================================================
# One CMA restart
# =========================================================================

@dataclass
class RestartRecord:
    """Full record of one CMA restart.

    phase: 'topo' | 'refine'
    cycle: 0-indexed cycle number for topo restarts.
           -1 for refinement (refinement is end-game, not part of a cycle).
    """
    idx: int                        # restart index (0-based, global)
    phase: str                      # 'topo' | 'refine'
    seed_basin: Optional[BasinId]   # basin we started from (None = refine)
    conv_basin: Optional[BasinId]   # basin CMA converged to (kNN vote)
    nfev: int                       # evaluations used in this restart
    best_f: float                   # best f found in this restart
    best_x: Optional[np.ndarray]    # best x found in this restart
    final_sigma: float              # CMA σ at termination
    sigma0: float                   # σ₀ used
    popsize: int                    # CMA popsize used
    stop_reason: str                # es.stop() key (e.g. 'tolfun', 'maxfevals')
    history: List[Tuple[int, float]] = field(default_factory=list)
    cycle: int = -1                 # cycle index (-1 = refinement)


# =========================================================================
# Per-phase budget summary (aggregated across cycles)
# =========================================================================

@dataclass
class PhaseStats:
    """Budget and outcome summary for one phase, aggregated across cycles."""
    nfev: int = 0
    n_restarts: int = 0
    best_f_end: float = float('inf')


# =========================================================================
# Per-cycle summary
# =========================================================================

@dataclass
class CycleStats:
    """Summary of one MSC cycle (Phase-0 + Phase-1).

    All counters are local to the cycle (NOT cumulative). Use the
    `restarts` list on RunResult with `.cycle == c` filter for per-cycle
    restart-level breakdown.
    """
    cycle: int
    nfev_start: int            # self.nfev at cycle entry
    nfev_end: int              # self.nfev at cycle exit (before next cycle / refine)
    best_f_start: float        # global best at cycle entry
    best_f_end: float          # global best at cycle exit
    nfev_phase0: int           # this cycle's Phase-0 evals (not aggregated)
    n_basins_phase0: int       # len(basins_sorted) at this cycle's Phase-0
    phi_used: float            # NBCDetector φ resolved this cycle
    sampling_method: str       # 'lhs'/'sobol'/'halton' (or cfg.sampling_method)
    cycle_local_best: float = float('inf')  # min F over evals DURING this cycle
    mode: str = 'default'      # 'alt-0'/'alt-1' for alt-CB schedule; else 'default'

    @property
    def improvement(self) -> float:
        return self.best_f_start - self.best_f_end

    def as_dict(self) -> dict:
        """Plain-dict snapshot for PKL persistence (no class dependency).

        Includes the derived `improvement` field as a stored scalar so
        readers don't need to recompute.
        """
        return {
            'cycle':            self.cycle,
            'nfev_start':       self.nfev_start,
            'nfev_end':         self.nfev_end,
            'best_f_start':     self.best_f_start,
            'best_f_end':       self.best_f_end,
            'improvement':      self.improvement,
            'nfev_phase0':      self.nfev_phase0,
            'n_basins_phase0':  self.n_basins_phase0,
            'phi_used':         self.phi_used,
            'sampling_method':  self.sampling_method,
            'cycle_local_best': self.cycle_local_best,
            'mode':             self.mode,
        }


# =========================================================================
# One full run
# =========================================================================

@dataclass
class RunResult:
    """Complete record of one MSC-CMA run. Stored in PKL when --save-pkl."""
    seed: int
    fun: float                          # best f found (raw, not error)
    best_x: np.ndarray

    # Phase-0 (first cycle's snapshots, retained for back-compat)
    phi_used: float
    phi_history: List[Tuple[float, int]]
    phase0_basins: List[BasinSnapshot]  # sorted small→large
    nfev_phase0: int                    # total Phase-0 evals across all cycles

    # Restarts (all cycles + refinement, each tagged with .cycle)
    restarts: List[RestartRecord]

    # Phase budget (aggregated across cycles)
    phase0: PhaseStats = field(default_factory=PhaseStats)
    phase1: PhaseStats = field(default_factory=PhaseStats)
    phase3: PhaseStats = field(default_factory=PhaseStats)  # end-game refine

    # Per-cycle summary (length = number of cycles actually started)
    cycles: List[CycleStats] = field(default_factory=list)

    # Best f right before end-game refinement starts. If refinement did not
    # run (remaining < 10·D), this equals `fun`. Useful for measuring the
    # refinement contribution: refine_gain = best_f_pre_refine - fun.
    best_f_pre_refine: float = float('inf')

    @property
    def nfev_total(self):
        return self.nfev_phase0 + sum(r.nfev for r in self.restarts)

    @property
    def n_cycles(self):
        return len(self.cycles)


# =========================================================================
# Aggregated benchmark result
# =========================================================================

@dataclass
class BenchmarkResult:
    """Aggregated over all runs for one function. → summary.csv row."""
    suite: str
    dim: int
    func: str
    bias: float
    n_runs: int

    errors: List[float] = field(default_factory=list)   # raw - bias
    elapsed_sec: float = 0.0

    @property
    def mean(self):
        return float(np.mean(self.errors))

    @property
    def median(self):
        return float(np.median(self.errors))

    @property
    def std(self):
        return float(np.std(self.errors))

    @property
    def best(self):
        return float(np.min(self.errors))

    @property
    def worst(self):
        return float(np.max(self.errors))

    def csv_row(self) -> dict:
        return {
            'suite': self.suite,
            'dim': self.dim,
            'func': self.func,
            'mean': f'{self.mean:.4f}',
            'median': f'{self.median:.4f}',
            'std': f'{self.std:.4f}',
            'best': f'{self.best:.4f}',
            'worst': f'{self.worst:.4f}',
            'elapsed_sec': f'{self.elapsed_sec:.1f}',
        }
