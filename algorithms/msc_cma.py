"""
msc_cma.py — MSC-CMA-ES main orchestrator.

Phases (per cycle):
    Phase-0  NBCDetector.discover()  → n_initial_basins sorted small→large
    Phase-1  topo CMA restarts       → small→large

End-game (after all cycles):
    If remaining ≥ 10·D → single refinement CMA from best_x

CMA stops (OR logic — first wins):
    es.stop()          CMA internal (tolfun, tolx, conditioncov, ...)
    std(F) < s_tol     absolute fitness convergence (bias-free)
    budget exhausted   global or per-restart

Scheduling:
    Single-cfg mode    pass `config` (default).  All cycles use that cfg.
    alt-CB mode        pass `mode_schedule=[cfg_0, cfg_1, ...]`.  Cycle i
                       uses mode_schedule[i % len(mode_schedule)] indefinitely.
                       No decision step.  The runner uses alt-CB in --auto:
                       mode_schedule=[cfg_C, cfg_B] (cycle 0=C, 1=B, 2=C, ...).

Sobol/Halton cross-cycle Phase-0 reuse (alt-CB only):
    When sampling_method ∈ {'sobol','halton'} and mode_schedule is set,
    odd cycles reuse the first N points (and their f-values) from the
    immediately preceding even cycle's Phase-0 sample.  Sobol/Halton
    sequences are nested: stream[0:N] ⊂ stream[0:M] for M > N, so the
    subset is a valid sample for the smaller n_phase0 needed by the
    odd cycle's config.  Zero new evaluations are spent on odd cycles'
    Phase-0.  NBC clustering is re-run with the odd cycle's own params
    (k, nbc_b, min_basin_size), giving a B-style basin geometry on the
    same points.
    No effect for LHS (no nesting), single-cfg mode (--conly), or when the
    previous cycle's sample is too small.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

import cma
import numpy as np

from basin_detector import BasinInfo, NBCDetector, _pow2_nearest
from basin_id import BasinId
from config import MSCConfig
from result import (BasinSnapshot, CycleStats, PhaseStats, RestartRecord,
                    RunResult)


# =========================================================================
# Helpers
# =========================================================================

def compute_popsize(basin_size: int, cfg: MSCConfig, D: int) -> int:
    """Adaptive CMA popsize with one tunable cap.

    Keeps the current behaviour:
        lower = Hansen default
        upper = cfg.cma_popsize
        value = clamp(ceil(basin_size * cfg.popsize_frac), lower, upper)
    """
    floor = 4 + int(3 * np.log(D))       # D=10 -> 10
    cap = max(floor, int(cfg.cma_popsize))
    n_elite = max(1, int(np.ceil(basin_size * cfg.popsize_frac)))
    return min(cap, max(floor, n_elite))


# =========================================================================
# MSC_CMA
# =========================================================================

class MSC_CMA:
    """MSC-CMA-ES solver.

    Usage:
        solver = MSC_CMA(func, bounds, maxevals, seed, config)
        result = solver.solve()
    """

    def __init__(self,
                 func,
                 bounds,
                 maxevals: int,
                 seed: int,
                 config: Optional[MSCConfig] = None,
                 disp: bool = False,
                 # alt-CB scheduler: when set, cycle i uses
                 # mode_schedule[i % len(mode_schedule)] for ALL cycles.
                 # Pass mode_schedule=[cfg_C, cfg_B] for the canonical alt-CB
                 # (cycle 0=C, 1=B, 2=C, ...).  None → single-cfg (C-only).
                 mode_schedule: Optional[List[MSCConfig]] = None):
        self.func = func
        self.bounds = np.asarray(bounds, dtype=float)
        self.dim = len(bounds)
        self.seed = seed
        self.disp = disp
        self.maxevals = maxevals

        # alt-CB schedule (None → single-cfg).  When set, cycle i uses
        # mode_schedule[i % len(mode_schedule)].
        self.mode_schedule = mode_schedule
        self.mode_label = 'default'

        # `config` is the cfg used for refine_budget reservation at solve()
        # entry (mode_schedule[0] in alt-CB; the C-class cfg for --conly).
        self.cfg = config or MSCConfig()
        self.rng = np.random.default_rng(seed)

        # Precompute CMA options (constant across restarts)
        self._bounds_list = [self.bounds[:, 0].tolist(),
                             self.bounds[:, 1].tolist()]
        self._tolfun = 10 ** (-self.cfg.tolfun_exp)
        self._tolx = 10 ** (-self.cfg.tolx_exp)

        # Global best tracking. nfev starts at 0; solve() runs entirely
        # within [0, maxevals].
        self.nfev = 0
        self.best_f = float('inf')
        self.best_x = np.zeros(self.dim)

        # Per-cycle local best tracker (min F over evals during current cycle).
        # Reset to inf at each cycle entry in solve(); read at cycle exit.
        self._cycle_local_min = float('inf')

        # Histogram of CMA-ES popsize values used across all restarts
        # (topo + refine).  Useful for diagnosing whether compute_popsize
        # is producing diverse adaptive λ or always hitting the cap.
        self.popsize_hist: Dict[int, int] = {}

        # Phase-0 cross-cycle reuse state (alt-CB + Sobol/Halton).  A fresh
        # Phase-0 sample is cached so the next (odd) cycle can reuse a prefix
        # of it instead of paying evals.  Single slot (overwritten on each
        # fresh sample).
        self._phase0_cached_cycle: Optional[int] = None
        self._phase0_cached_points: Optional[np.ndarray] = None
        self._phase0_cached_fvals: Optional[np.ndarray] = None
        # Diagnostic counters
        self.phase0_reuse_count: int = 0
        self.phase0_reuse_evals_saved: int = 0

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def _eval_batch(self, X):
        """Batch evaluate.  Updates global best.  Returns list of floats."""
        X_arr = np.asarray(X)
        F = self.func(X_arr)
        self.nfev += len(F)
        idx = int(np.argmin(F))
        if F[idx] < self.best_f:
            self.best_f = float(F[idx])
            self.best_x = X_arr[idx].copy()
        # Track min F over this cycle alone (reset at cycle entry in solve()).
        # Independent of self.best_f because best_f may carry over from a
        # previous cycle / hot-start.
        if F[idx] < self._cycle_local_min:
            self._cycle_local_min = float(F[idx])
        return F

    # ------------------------------------------------------------------
    # Single CMA restart
    # ------------------------------------------------------------------

    def _run_cma(self, x0, sigma0, popsize, budget, restart_idx,
                 phase='topo', cycle: int = -1):
        """Run one CMA-ES restart.

        Stops on: es.stop() | std(F) < s_tol | budget exhausted.
        For phase='refine': tolfun=tolx=0 — runs until budget exhaustion
        or CMA's internal conditioncov stop; s_tol disabled.
        `cycle` is stamped on the returned RestartRecord (-1 for refine).
        Returns RestartRecord.
        """
        # Track λ distribution across all restarts (topo/refine)
        self.popsize_hist[popsize] = self.popsize_hist.get(popsize, 0) + 1

        # Refinement: tolfun/tolx set to 0 here; the full stop-disable set
        # is applied below to the opts dict (after it's built).
        if phase == 'refine':
            tolfun = 0.0
            tolx = 0.0
            use_stol = False
            range_med = float(np.median(
                self.bounds[:, 1] - self.bounds[:, 0]))
            sigma0 = min(sigma0, range_med / 100)
        else:
            tolfun = self._tolfun
            tolx = self._tolx
            use_stol = self.cfg.s_tol > 0

        opts = {
            'seed':      self.seed + restart_idx * 1000,
            'maxfevals': budget,
            'tolfun':    tolfun,
            'tolx':      tolx,
            'bounds':    self._bounds_list,
            'verbose':   -9,
            'verb_disp': 0, 'verb_log': 0,
            'verb_plot': 0, 'verb_time': 0,
            'popsize':   popsize,
        }
        if phase == 'refine':
            # Refinement: disable ALL convergence/error stops so budget
            # (maxfevals) is the sole termination criterion.  Empirically
            # (cec2020 d5 f10): with default refinement stops, refinement
            # used only ~45% of reserved budget — converged seeds clustered
            # at exactly tolfun=1e-11 (the old floor).  This disables every
            # stop pycma exposes, letting refinement dig to float-epsilon.
            # See pycma cma_signals.in for full list.
            opts['tolfun']          = 0          # fitness tolerance (was 1e-11)
            opts['tolx']            = 0          # x tolerance (was 1e-12)
            opts['tolfunhist']      = 0          # long-term fitness change
            opts['tolflatfitness']  = 10**9          # flat fitness detector
            opts['tolstagnation']   = 0          # no-improvement counter
            opts['tolfacupx']       = 1e30       # step-size blowup (was 1e3)
            opts['tolupsigma']      = 1e30       # creeping detector (was 1e20)
            opts['tolconditioncov'] = 1e30       # ill-conditioning (was 1e14)
            opts['maxiter']         = 10**9      # iteration cap (was default)
            # Note: noeffectaxis / noeffectcoord are built-in float-precision
            # tripwires and cannot be disabled via options.  They fire only
            # at literal float-epsilon precision — the natural floor.

        if self.disp:
            print(f"    _run_cma R{restart_idx} phase={phase} "
                  f"cycle={cycle} "
                  f"budget={budget} popsize={popsize} "
                  f"sigma0={sigma0:.3f} "
                  f"tolfun={tolfun:.0e} tolx={tolx:.0e}")

        nfev_before = self.nfev
        best_f_run = float('inf')
        best_x_run = x0.copy()
        final_sigma = 0.0
        stop_reason = 'budget'
        history = []
        prev_best = self.best_f

        try:
            es = cma.CMAEvolutionStrategy(x0, sigma0, opts)

            while not es.stop() and self.nfev < self.maxevals:
                X = es.ask()
                F = self._eval_batch(X)
                es.tell(X, F)

                if self.best_f < prev_best:
                    history.append((self.nfev, self.best_f))
                    prev_best = self.best_f

                # Absolute fitness convergence (not during refinement)
                # ptp (max−min) ≥ std always; ptp < s_tol is slightly
                # stricter than std < s_tol — restarts converge a touch
                # later, which is fine.  Avoids numpy overhead on list.
                if use_stol:
                    f_min, f_max = F[0], F[0]
                    for f in F:
                        if f < f_min:
                            f_min = f
                        if f > f_max:
                            f_max = f
                    if f_max - f_min < self.cfg.s_tol:
                        stop_reason = 's_tol'
                        break

            if stop_reason == 'budget':
                stop_reason = _first_stop_key(es.stop())

            final_sigma = float(es.sigma)
            if float(es.result.fbest) < best_f_run:
                best_f_run = float(es.result.fbest)
                best_x_run = np.asarray(es.result.xbest, dtype=float)

        except Exception as exc:
            stop_reason = f'exception:{type(exc).__name__}'

        return RestartRecord(
            idx=restart_idx,
            phase=phase,
            seed_basin=None,
            conv_basin=None,
            nfev=self.nfev - nfev_before,
            best_f=best_f_run,
            best_x=best_x_run,
            final_sigma=final_sigma,
            sigma0=sigma0,
            popsize=popsize,
            stop_reason=stop_reason,
            history=history,
            cycle=cycle,
        )

    # ------------------------------------------------------------------
    # Phase helpers
    # ------------------------------------------------------------------

    def _make_detector_for_cycle(self, cycle: int,
                                 cfg: MSCConfig
                                 ) -> tuple:
        """Create the Phase-0 detector for a cycle.
        Returns (detector, sampling_method_used)."""
        cycle_seed = self.seed + cycle * 10000
        return (NBCDetector(self.dim, self.bounds, cfg, cycle_seed),
                cfg.sampling_method)

    def _phase0_snapshots(self, basins_sorted: List[BasinInfo],
                          detector: NBCDetector) -> List[BasinSnapshot]:
        """Create first-cycle basin snapshots for RunResult compatibility."""
        return [
            BasinSnapshot(
                basin_id=b.basin_id,
                size=b.size,
                best_val=b.best_val,
                diameter=b.diameter,
                centroid_norm=detector._normalize(
                    b.centroid.reshape(1, -1))[0],
            )
            for b in basins_sorted
        ]

    def _reuse_needed_n(self, cfg: MSCConfig) -> int:
        """Number of cached points the current cycle would consume on reuse.
        Sobol is rounded to a power of 2 to match sample_points."""
        n = cfg.n_phase0
        if cfg.sampling_method == 'sobol':
            n = _pow2_nearest(n)
        return n

    def _reuse_eligible(self, cycle: int, cfg: MSCConfig) -> bool:
        """True if this cycle can reuse the previous cycle's Phase-0 sample.

        All must hold:
          - alt-CB mode active (mode_schedule is not None)
          - cycle > 0
          - sampling_method ∈ {'sobol','halton'} (nested-sequence property)
          - cache holds the immediately preceding cycle (cycle - 1)
          - cached sample size ≥ N needed for this cycle
        """
        if self.mode_schedule is None:
            return False
        if cycle <= 0:
            return False
        if cfg.sampling_method not in ('sobol', 'halton'):
            return False
        if self._phase0_cached_cycle != cycle - 1:
            return False
        if self._phase0_cached_points is None:
            return False
        return len(self._phase0_cached_points) >= self._reuse_needed_n(cfg)

    def _try_reuse_phase0(self, cycle: int, cfg: MSCConfig
                          ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Return (points, fvals) prefix from the previous cycle's cache when
        reuse is eligible; otherwise None."""
        if not self._reuse_eligible(cycle, cfg):
            return None
        n = self._reuse_needed_n(cfg)
        return (self._phase0_cached_points[:n],
                self._phase0_cached_fvals[:n])

    def _run_phase0(self, cycle: int, cfg: MSCConfig,
                    phase_stats: PhaseStats):
        """Run Phase-0 for one cycle and update global best/stat counters.

        Returns: (detector, basins_sorted, phi_used, phi_history,
                  nfev_this_phase0, sampling_method)
        """
        detector, sampling_method = self._make_detector_for_cycle(cycle, cfg)

        # Try cross-cycle Sobol/Halton reuse (alt-CB only).  When successful,
        # detector skips sampling+evaluation and operates on the cached prefix.
        pre_sampled = self._try_reuse_phase0(cycle, cfg)

        if pre_sampled is not None:
            basins_sorted, phi_used, phi_history = detector.discover(
                self.func, pre_sampled=pre_sampled)
            # detector.nfev is 0 internally; MSC.nfev does NOT increment.
            nfev_this_phase0 = 0
            saved = len(pre_sampled[0])
            self.phase0_reuse_count += 1
            self.phase0_reuse_evals_saved += saved
            if self.disp:
                print(f"  Phase-0 cycle {cycle}: REUSE {saved} pts "
                      f"from cycle {cycle - 1} (0 new evals)")
        else:
            basins_sorted, phi_used, phi_history = detector.discover(self.func)
            self.nfev += detector.nfev
            nfev_this_phase0 = detector.nfev
            # Cache fresh sample for potential reuse by the next cycle.
            # Only cache when reuse could conceivably apply downstream
            # (alt-CB + Sobol/Halton).  Otherwise it would never be read.
            if (self.mode_schedule is not None
                    and sampling_method in ('sobol', 'halton')):
                self._phase0_cached_cycle = cycle
                self._phase0_cached_points = detector.points.copy()
                self._phase0_cached_fvals = detector.fvals.copy()

        # Update global best from Phase-0 (detector.fvals is populated).
        best_idx = int(np.argmin(detector.fvals))
        if detector.fvals[best_idx] < self.best_f:
            self.best_f = float(detector.fvals[best_idx])
            self.best_x = detector.points[best_idx].copy()

        # Update cycle-local min tracker from Phase-0 evals.  detector.discover
        # evaluates LHS points directly (not via _eval_batch), so we patch
        # _cycle_local_min here.  Without this, cycles whose Phase-0 found 0
        # basins (no Phase-1 restarts) would leave cycle_local_best = inf.
        if len(detector.fvals) > 0:
            phase0_min = float(np.min(detector.fvals))
            if phase0_min < self._cycle_local_min:
                self._cycle_local_min = phase0_min

        phase_stats.nfev += nfev_this_phase0
        phase_stats.best_f_end = self.best_f

        if self.disp:
            sizes = [b.size for b in basins_sorted]
            popsizes = [compute_popsize(b.size, cfg, self.dim)
                        for b in basins_sorted]
            print(f"  popsize check: sizes min/med/max="
                  f"{min(sizes)}/{int(np.median(sizes))}/{max(sizes)} | "
                  f"popsizes={popsizes}")
            print(f"  Phase-0: {nfev_this_phase0} evals, "
                  f"{len(basins_sorted)} basins, "
                  f"phi={phi_used:.3f}, best_err={self.best_f:.4e}")
            for i, b in enumerate(basins_sorted):
                print(f"    [{i}] bid={b.basin_id} size={b.size} "
                      f"sigma0={b.sigma0(cfg.sigma_divisor):.2f}")

        return (detector, basins_sorted, phi_used, phi_history,
                nfev_this_phase0, sampling_method)

    def _run_topo_phase(self,
                        detector: NBCDetector,
                        basins_sorted: List[BasinInfo],
                        cfg: MSCConfig,
                        main_budget: int,
                        restart_idx: int,
                        all_restarts: List[RestartRecord],
                        phase_stats: PhaseStats,
                        cycle: int,
                        ) -> int:
        """Run Phase-1 topo CMA restarts for a cycle."""
        D = self.dim
        topo_queue = [b.basin_id for b in basins_sorted]

        # Fresh within-cycle exclusion
        excluded_bids: set = set()
        converge_count: Counter = Counter()

        for bid in topo_queue:
            if self.nfev >= main_budget:
                break
            if bid not in detector.basins:
                continue

            basin = detector.basins[bid]

            # Pre-start probe: skip if x0 maps to excluded destination
            x0 = detector.jitter_x0(bid, self.rng)
            probe_bid = detector.identify_basin_knn(x0)
            if probe_bid in excluded_bids:
                if self.disp:
                    print(f"  SKIP bid={bid} "
                          f"(x0 maps to excluded {probe_bid})")
                continue

            remaining = main_budget - self.nfev
            sigma0 = basin.sigma0(cfg.sigma_divisor)
            if self.disp and sigma0 <= 1.0:
                print(f"  σ₀ safety net: computed→1.0 bid={bid}")
            popsize = compute_popsize(basin.size, cfg, D)

            rec = self._run_cma(x0, sigma0, popsize, remaining,
                                restart_idx, phase='topo', cycle=cycle)
            rec.seed_basin = bid

            # Convergence tracking — use restart's own best_x
            conv_bid = detector.identify_basin_knn(rec.best_x)
            rec.conv_basin = conv_bid

            if conv_bid is not None:
                converge_count[conv_bid] += 1
                if (converge_count[conv_bid] > 1
                        and conv_bid not in excluded_bids):
                    excluded_bids.add(conv_bid)
                    if self.disp:
                        print(f"  EXCLUDE bid={conv_bid} "
                              f"(2nd convergence)")

            all_restarts.append(rec)
            restart_idx += 1
            phase_stats.nfev += rec.nfev
            phase_stats.n_restarts += 1
            phase_stats.best_f_end = self.best_f

            if self.disp:
                print(f"  R{restart_idx-1} topo(bid={bid}) "
                      f"nfev={rec.nfev} best={rec.best_f:.4e} "
                      f"stop={rec.stop_reason} conv={conv_bid}")

        return restart_idx

    def _run_refinement(self,
                        cfg: MSCConfig,
                        refine_budget: int,
                        restart_idx: int,
                        all_restarts: List[RestartRecord],
                        phase_stats: PhaseStats) -> int:
        """Run the end-game single refinement restart, if budget allows.

        Refinement restarts are always tagged with cycle=-1.
        """
        D = self.dim
        lower = self.bounds[:, 0]
        upper = self.bounds[:, 1]
        remaining = self.maxevals - self.nfev

        if remaining >= D * 10:
            if self.disp:
                frac = 100.0 * remaining / self.maxevals
                print(f"\n  REFINE: {remaining} FEs "
                      f"({frac:.1f}% of budget, "
                      f"reserved={refine_budget}) "
                      f"tolfun=0 tolx=0")

            # σ₀: use final_sigma from the restart that found best
            sigma0_ref = 0.0
            if all_restarts:
                best_rec = min(all_restarts, key=lambda r: r.best_f)
                sigma0_ref = best_rec.final_sigma

            if sigma0_ref <= 0:
                sigma0_ref = float(
                    np.median(upper - lower) / cfg.sigma_divisor)

            popsize_ref = max(4 + int(3 * np.log(D)), 10)

            rec = self._run_cma(
                self.best_x.copy(), sigma0_ref, popsize_ref,
                remaining, restart_idx, phase='refine', cycle=-1)
            rec.seed_basin = None
            rec.conv_basin = None
            all_restarts.append(rec)
            restart_idx += 1

            phase_stats.nfev = rec.nfev
            phase_stats.n_restarts = 1
            phase_stats.best_f_end = self.best_f

        return restart_idx

    # ------------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------------

    def solve(self) -> RunResult:
        """Run full MSC-CMA-ES with cyclic restart.  Returns RunResult."""
        cfg = self.cfg
        D = self.dim

        # Budget reservation for refinement.  refine_frac is an explicit
        # fraction on every config (B and C), so the reservation is a direct
        # product; refinement later spends everything left down to maxevals,
        # so this is a floor, not a hard allocation.  For alt-CB, cfg here is
        # mode_schedule[0] (the C-class cfg passed at __init__).
        refine_budget = int(cfg.refine_frac * self.maxevals)
        main_budget = self.maxevals - refine_budget

        # Accumulate across all cycles
        all_restarts: List[RestartRecord] = []
        restart_idx = 0

        phase0_stats = PhaseStats()
        phase1_stats = PhaseStats()
        phase3_stats = PhaseStats()

        # Snapshots from the first cycle (for RunResult backward compat)
        first_phi_used = 0.0
        first_phi_history = []
        first_phase0_snapshots = []
        total_phase0_evals = 0

        # Per-cycle summary list
        cycles_list: List[CycleStats] = []

        # Main cycle loop
        cycle = 0
        active_cfg = cfg                          # default for single-cfg path
        while self.nfev < main_budget:

            # alt-CB per-cycle config selection.
            if self.mode_schedule is not None:
                n_modes = len(self.mode_schedule)
                active_cfg = self.mode_schedule[cycle % n_modes]
                # Label by index slot so PKL readers can identify which.
                self.mode_label = f'alt-{cycle % n_modes}'

            remaining_before_cycle = main_budget - self.nfev

            # Minimum budget to start a new cycle.  When this cycle is reuse-
            # eligible its Phase-0 costs 0 evals (it reuses the previous
            # cycle's sample), so only the Phase-1 restart budget is required;
            # otherwise Phase-0 needs n_phase0 evals up front.
            if self._reuse_eligible(cycle, active_cfg):
                min_cycle_budget = D * 50
            else:
                min_cycle_budget = active_cfg.n_phase0 + D * 50
            if remaining_before_cycle < min_cycle_budget:
                break

            if self.disp:
                print(f"\n  ══ CYCLE {cycle} ══  "
                      f"nfev={self.nfev}  "
                      f"remaining={remaining_before_cycle}  "
                      f"best={self.best_f:.4e}  "
                      f"mode={self.mode_label}")

            # Reset cycle-local min tracker (used by _eval_batch).
            self._cycle_local_min = float('inf')

            # Snapshot cycle entry state
            cs = CycleStats(
                cycle=cycle,
                nfev_start=self.nfev,
                nfev_end=0,                  # filled at cycle exit
                best_f_start=self.best_f,
                best_f_end=float('inf'),     # filled at cycle exit
                nfev_phase0=0,
                n_basins_phase0=0,
                phi_used=0.0,
                sampling_method='',
                cycle_local_best=float('inf'),  # filled at cycle exit
                mode=self.mode_label,
            )

            (detector, basins_sorted, phi_used, phi_history,
             nfev_phase0, sampling_method) = self._run_phase0(
                cycle, active_cfg, phase0_stats)
            total_phase0_evals += nfev_phase0

            cs.nfev_phase0 = nfev_phase0
            cs.n_basins_phase0 = len(basins_sorted)
            cs.phi_used = phi_used
            cs.sampling_method = sampling_method

            # Save first cycle's snapshots for RunResult
            if cycle == 0:
                first_phi_used = phi_used
                first_phi_history = phi_history
                first_phase0_snapshots = self._phase0_snapshots(
                    basins_sorted, detector)

            restart_idx = self._run_topo_phase(
                detector=detector,
                basins_sorted=basins_sorted,
                cfg=active_cfg,
                main_budget=main_budget,
                restart_idx=restart_idx,
                all_restarts=all_restarts,
                phase_stats=phase1_stats,
                cycle=cycle,
            )

            # Finalise cycle stats
            cs.nfev_end = self.nfev
            cs.best_f_end = self.best_f
            cs.cycle_local_best = self._cycle_local_min
            cycles_list.append(cs)

            if self.disp:
                print(f"  ── END CYCLE {cycle} ──  "
                      f"nfev: {cs.nfev_start}→{cs.nfev_end}  "
                      f"best: {cs.best_f_start:.4e}→{cs.best_f_end:.4e}  "
                      f"improvement={cs.improvement:+.4e}  "
                      f"cycle_local={cs.cycle_local_best:.4e}")

            cycle += 1

        # Snapshot pre-refinement best (refinement contribution = pre - fun)
        best_f_pre_refine = self.best_f

        # Refinement with active_cfg (last cycle's cfg).
        self._run_refinement(active_cfg, refine_budget, restart_idx,
                             all_restarts, phase3_stats)

        # Assemble RunResult
        if self.disp and self.popsize_hist:
            hist = " ".join(f"{k}:{v}"
                            for k, v in sorted(self.popsize_hist.items()))
            print(f"  popsize_hist: {hist}")

        if self.disp and self.phase0_reuse_count > 0:
            print(f"  phase0_reuse: {self.phase0_reuse_count} cycles, "
                  f"{self.phase0_reuse_evals_saved} evals saved")

        if self.disp:
            refine_gain = best_f_pre_refine - self.best_f
            print(f"  best_f_pre_refine={best_f_pre_refine:.4e}  "
                  f"fun={self.best_f:.4e}  "
                  f"refine_gain={refine_gain:+.4e}")

        return RunResult(
            seed=self.seed,
            fun=self.best_f,
            best_x=self.best_x.copy(),
            phi_used=first_phi_used,
            phi_history=first_phi_history,
            phase0_basins=first_phase0_snapshots,
            nfev_phase0=total_phase0_evals,
            restarts=all_restarts,
            phase0=phase0_stats,
            phase1=phase1_stats,
            phase3=phase3_stats,
            cycles=cycles_list,
            best_f_pre_refine=best_f_pre_refine,
        )


# =========================================================================
# Helpers
# =========================================================================

def _first_stop_key(stop_dict: dict) -> str:
    """Return the first key from es.stop() dict, or 'budget' if empty."""
    if not stop_dict:
        return 'budget'
    return next(iter(stop_dict))
