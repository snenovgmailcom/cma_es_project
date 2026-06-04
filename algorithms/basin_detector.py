"""
basin_detector.py — MSC-CMA-ES Phase-0 basin detection.

Pipeline:
    LHS/Sobol/Halton sampling  →  NB tree  →  NBC (Rule 1 + Rule 2)
    →  staircase φ for n_initial_basins
    →  BasinInfo list sorted small→large

Basin membership (Phase-1):
    identify_basin_knn(x)  →  kNN majority vote

References:
    Preuss (2010): Niching the CMA-ES via nearest-better clustering
    Preuss (2012): Improved Topological Niching (Rule 2)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from scipy.spatial import cKDTree as KDTree
from scipy.stats import qmc

from config import MSCConfig
from basin_id import BasinId

# --- C++ acceleration (optional, ~20× faster NB tree) ---
try:
    from cpp.nb_tree import (nearest_better_tree as _nb_tree_cpp,
                             nbc_clustering as _nbc_clustering_cpp)
    _HAS_CPP = True
except ImportError:
    _HAS_CPP = False


# σ₀ anchor: top-fraction of basin points by f-value defines the "elite center"
# from which per-axis Q75 distances are measured.  Now read from MSCConfig.sigma_elite_frac.
SIGMA_ELITE_FRAC_DEFAULT = 0.2


# =========================================================================
# BasinInfo
# =========================================================================

@dataclass
class BasinInfo:
    """All information about one detected basin."""
    basin_id: BasinId
    member_indices: np.ndarray   # indices into detector.points
    size: int
    best_val: float              # best f in LHS sample (not true optimum)
    best_idx: int                # index of best point
    centroid: np.ndarray         # mean of member points (original scale)
    diameter: float              # 2 × max distance from centroid

    # Per-coord Q75 distances from elite center — used for σ₀ computation
    # coord_sigma[j] = Q75_i( |x_ij - center_j| ) for axis j
    coord_sigma: Optional[np.ndarray] = None  # shape (D,)

    def sigma0(self, divisor: float) -> float:
        """σ₀ = median_j( Q75_i(|x_ij - center_j|) ) / divisor

        center   = mean of top-elite_frac points by f
        d_ij     = |x_ij - center_j|  per axis j, per point i
        σ₀       = median_j( Q75_i(d_ij) ) / divisor
        σ₀       = max(σ₀, 1.0)  [hardcoded safety net]
        """
        if self.coord_sigma is None or len(self.coord_sigma) == 0:
            sigma = self.diameter / divisor
        else:
            sigma = float(np.median(self.coord_sigma)) / divisor
        return max(sigma, 1.0)  # safety net


# =========================================================================
# Phase-0 sampling
# =========================================================================

def _pow2_floor(n: int) -> int:
    """Largest 2^m <= n. n >= 1."""
    return 1 << (n.bit_length() - 1) if n > 0 else 1


def _pow2_ceil(n: int) -> int:
    """Smallest 2^m >= n. n >= 1."""
    return 1 << ((n - 1).bit_length()) if n > 1 else 1


def _pow2_nearest(n: int) -> int:
    """Nearest 2^m to n (ties → ceil)."""
    if n <= 1:
        return 1
    lo = _pow2_floor(n)
    hi = lo << 1
    return lo if (n - lo) < (hi - n) else hi


def sample_points(dim: int, n: int, bounds: np.ndarray, seed: int,
                  method: str = 'sobol') -> np.ndarray:
    """Sample n points in [lb, ub]^D using the given method.

    Methods:
        'lhs'    — Latin Hypercube (randomized, seed-dependent)
        'sobol'  — Sobol sequence; n is rounded to the nearest 2^m for
                   proper balance (Sobol requires a power-of-2 sample size)
        'halton' — Halton sequence

    The returned array length is the actual sample size, which for 'sobol'
    may differ from n. Callers must use len() on the returned array for
    budget tracking, not the requested n.

    Returns (n_eff, D) array.
    """
    import math

    lb = bounds[:, 0]
    ub = bounds[:, 1]

    if method == 'lhs':
        sampler = qmc.LatinHypercube(d=dim, seed=seed)
        unit = sampler.random(n)
    elif method == 'sobol':
        n_eff = _pow2_nearest(n)
        sampler = qmc.Sobol(d=dim, scramble=True, seed=seed)
        unit = sampler.random_base2(int(math.log2(n_eff)))
    elif method == 'halton':
        sampler = qmc.Halton(d=dim, scramble=True, seed=seed)
        unit = sampler.random(n)
    else:
        raise ValueError(f"Unknown sampling method: {method!r}. "
                         f"Use 'lhs', 'sobol', or 'halton'.")

    return qmc.scale(unit, lb, ub)


# =========================================================================
# NB tree
# =========================================================================

def nearest_better_tree(points_norm: np.ndarray,
                        fvals: np.ndarray,
                        k: int) -> Tuple[np.ndarray, np.ndarray]:
    """Build nearest-better (NB) tree.

    For each point i, parent[i] = nearest point j with f(j) < f(i).
    Edge length = normalized Euclidean distance to parent.
    Root (global best) has parent = -1, edge_len = 0.

    Returns:
        parent   (M,) int   — parent index, -1 for root
        edge_len (M,) float — distance to parent, 0 for root
    """
    M = len(fvals)
    best = int(np.argmin(fvals))
    tree = KDTree(points_norm)

    parent = -np.ones(M, dtype=int)
    edge_len = np.zeros(M, dtype=float)

    k0 = max(2, min(k, M - 1))
    k_cap = min(M - 1, max(k0, 8 * k0, 256))

    for i in range(M):
        if i == best:
            continue
        fi = float(fvals[i])
        k_try = k0

        while True:
            kk = min(M, k_try + 1)
            dists, nbrs = tree.query(points_norm[i], k=kk)
            nbrs = np.atleast_1d(nbrs).astype(int)
            dists = np.atleast_1d(dists).astype(float)

            # exclude self
            mask = nbrs != i
            nbrs, dists = nbrs[mask], dists[mask]

            better = fvals[nbrs] < fi
            if np.any(better):
                idx = int(np.argmin(dists[better]))
                parent[i] = int(nbrs[better][idx])
                edge_len[i] = float(dists[better][idx])
                break

            if k_try >= k_cap:
                # fallback: connect to global best
                parent[i] = best
                edge_len[i] = float(
                    np.linalg.norm(points_norm[i] - points_norm[best]))
                break

            k_try = min(k_cap, 2 * k_try)

    return parent, edge_len


# =========================================================================
# NBC clustering
# =========================================================================

def nbc_clustering(points_norm: np.ndarray,
                   fvals: np.ndarray,
                   k: int,
                   phi: float,
                   nbc_b: float,
                   nbc_min_incoming: int
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """NBC with Rule 1 + Rule 2.

    Returns:
        labels       (M,) int  — component label (= root index)
        parent_raw   (M,) int  — NB parent BEFORE any cuts
        edge_len_raw (M,) float — NB edge lengths BEFORE any cuts
        mu           float     — mean edge length (for staircase)
    """
    M = len(fvals)
    if M == 0:
        return (np.array([], dtype=int),
                np.array([], dtype=int),
                np.array([], dtype=float),
                0.0)

    parent, edge_len = nearest_better_tree(points_norm, fvals, k)

    # Save raw tree before any cuts
    parent_raw = parent.copy()
    edge_len_raw = edge_len.copy()

    # μ = mean edge length of valid edges
    valid = parent >= 0
    mu = float(np.mean(edge_len[valid])) if np.any(valid) else 0.0

    # Rule 1: cut edges longer than φ × μ
    if mu > 0:
        cut = (edge_len > phi * mu) & valid
        parent[cut] = -1

    # Rule 2: hub detection
    # A hub j has high in-degree AND its own edge to parent is long
    # relative to its incoming edges.
    indeg = np.zeros(M, dtype=int)
    sum_incoming = np.zeros(M, dtype=float)

    for i in range(M):
        p = parent[i]
        if p >= 0:
            indeg[p] += 1
            sum_incoming[p] += edge_len[i]

    if nbc_min_incoming > 0:
        hubs = np.where(indeg >= nbc_min_incoming)[0]
        for j in hubs:
            if parent[j] < 0:
                continue
            mean_in = sum_incoming[j] / indeg[j]
            if mean_in > 0 and edge_len[j] / mean_in > nbc_b:
                parent[j] = -1

    # Pointer jumping → labels (component = root)
    roots = parent.copy()
    for i in range(M):
        if roots[i] < 0:
            roots[i] = i

    n_iter = int(np.ceil(np.log2(max(M, 2)))) + 5
    for _ in range(n_iter):
        r2 = roots[roots]
        if np.array_equal(r2, roots):
            break
        roots = r2

    return roots, parent_raw, edge_len_raw, mu


# =========================================================================
# Basin extraction from labels
# =========================================================================

def _compute_coord_sigma(pts: np.ndarray, fv: np.ndarray,
                          elite_frac: float = SIGMA_ELITE_FRAC_DEFAULT) -> np.ndarray:
    """Compute coord_sigma for BasinInfo.sigma0().

    center   = mean of top elite_frac points by f-value
    d_ij     = |x_ij - center_j|
    returns  Q75_i(d_ij) per axis, shape (D,)
    """
    n_elite = max(1, int(len(fv) * elite_frac))
    elite_order = np.argsort(fv)[:n_elite]
    elite_center = pts[elite_order].mean(axis=0)
    d_ij = np.abs(pts - elite_center)
    return np.quantile(d_ij, 0.75, axis=0)


def extract_basins(points: np.ndarray,
                   fvals: np.ndarray,
                   labels: np.ndarray,
                   min_size: int = 5,
                   elite_frac: float = SIGMA_ELITE_FRAC_DEFAULT) -> Dict[BasinId, BasinInfo]:
    """Build BasinInfo dict from label array.

    Basins with fewer than min_size members are discarded (noise).
    """
    basins = {}
    for bid in np.unique(labels):
        bid = int(bid)
        if bid < 0:
            continue
        mask = labels == bid
        indices = np.where(mask)[0]
        size = len(indices)
        if size < min_size:
            continue

        pts = points[indices]
        fv = fvals[indices]
        best_local = int(np.argmin(fv))
        best_idx = int(indices[best_local])
        best_val = float(fv[best_local])
        centroid = pts.mean(axis=0)

        dists = np.linalg.norm(pts - centroid, axis=1)
        diameter = float(2.0 * np.max(dists)) if size > 1 else 0.0

        coord_sigma = _compute_coord_sigma(pts, fv, elite_frac)

        basins[bid] = BasinInfo(
            basin_id=bid,
            member_indices=indices,
            size=size,
            best_val=best_val,
            best_idx=best_idx,
            centroid=centroid,
            diameter=diameter,
            coord_sigma=coord_sigma,
        )

    return basins


# =========================================================================
# Main detector
# =========================================================================

class NBCDetector:
    """Phase-0 basin detector: LHS → NB tree → NBC → staircase → basins.

    Usage:
        det = NBCDetector(dim, bounds, config, seed)
        basins, phi_used, phi_history = det.discover(func)
        # det.basins  — sorted small→large (topo queue order)
    """

    def __init__(self, dim: int, bounds: np.ndarray,
                 config: MSCConfig, seed: int = 42):
        self.dim = dim
        self.bounds = np.asarray(bounds, dtype=float)
        self.config = config
        self.seed = seed

        # Filled by discover()
        self.points: Optional[np.ndarray] = None
        self.fvals: Optional[np.ndarray] = None
        self.points_norm: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.basins: Dict[BasinId, BasinInfo] = {}
        self.nfev: int = 0

        # Raw NB tree (before cuts) — used by staircase _cluster_at_phi
        self.nb_parent_raw: Optional[np.ndarray] = None
        self.nb_edge_len_raw: Optional[np.ndarray] = None
        self.nb_mu: float = 0.0

        # kNN structure for basin membership queries
        self._basin_tree: Optional[KDTree] = None
        self._basin_tree_labels: Optional[np.ndarray] = None
        self._basin_tree_norm: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self, pts: np.ndarray) -> np.ndarray:
        lb = self.bounds[:, 0]
        span = self.bounds[:, 1] - lb
        span[span == 0] = 1.0
        return (pts - lb) / span

    # ------------------------------------------------------------------
    # discover()
    # ------------------------------------------------------------------

    def discover(self, func, *,
                 pre_sampled: Optional[Tuple[np.ndarray, np.ndarray]] = None
                 ) -> Tuple[List[BasinInfo],
                            float,
                            List[Tuple[float, int]]]:
        """Run Phase-0.

        func: minionpy-style callable — func([x1, x2, ...]) → [f1, f2, ...]

        pre_sampled : (points, fvals), optional
            If given, skip the internal sampling+evaluation step. `points`
            must be a (N, D) array in raw (un-normalized) coordinates and
            `fvals` a (N,) array of evaluated F values. `self.nfev` is set
            to 0 in this case — the caller is responsible for accounting
            those evaluations against its own budget. Used by MSC_CMA's
            cross-cycle Sobol/Halton reuse mechanism in alt-CB mode.

        Returns:
            basins_sorted  — list of BasinInfo sorted small→large
            phi_used       — φ chosen from staircase
            phi_history    — [(phi, n_basins)] walk
        """
        cfg = self.config
        D = self.dim

        # 1. Sample + evaluate (or accept pre-sampled inputs)
        if pre_sampled is not None:
            points, fvals = pre_sampled
            self.points = np.asarray(points, dtype=float)
            self.fvals = np.asarray(fvals, dtype=float)
            # Caller already incremented its own nfev counter when it
            # evaluated these points; detector contributes 0 here.
            self.nfev = 0
        else:
            M = cfg.n_phase0
            self.points = sample_points(D, M, self.bounds, self.seed,
                                        method=cfg.sampling_method)
            # Actual sample size may differ from M for Sobol (rounded to a
            # power of 2). Use the array length as the source of truth for
            # budget tracking.
            M = len(self.points)
            self.fvals = np.array(
                func([x.tolist() for x in self.points]), dtype=float)
            self.nfev = M

        # 2. Normalize
        self.points_norm = self._normalize(self.points)

        # 3. NBC clustering (initial φ=2.0 — will be replaced by staircase)
        if _HAS_CPP:
            labels, parent_raw, edge_len_raw, mu = _nbc_clustering_cpp(
                self.points_norm, self.fvals,
                cfg.k, 2.0, cfg.nbc_b, cfg.nbc_min_incoming)
        else:
            labels, parent_raw, edge_len_raw, mu = nbc_clustering(
                self.points_norm, self.fvals,
                cfg.k, phi=2.0,
                nbc_b=cfg.nbc_b,
                nbc_min_incoming=cfg.nbc_min_incoming)

        self.nb_parent_raw = parent_raw
        self.nb_edge_len_raw = edge_len_raw
        self.nb_mu = mu

        # 4. Staircase: find φ for n_initial_basins
        phi_used, phi_history = self._staircase_phi(cfg.n_initial_basins)

        # 5. Re-cluster at chosen φ
        labels = self._cluster_at_phi(phi_used)
        self.labels = labels

        # 6. Extract basins
        raw_basins = extract_basins(
            self.points, self.fvals, labels, cfg.min_basin_size,
            elite_frac=cfg.sigma_elite_frac)

        # 7. Sort small→large
        basins_sorted = sorted(raw_basins.values(), key=lambda b: b.size)
        self.basins = {b.basin_id: b for b in basins_sorted}

        # 8. Build kNN membership tree
        self._build_basin_tree()

        return basins_sorted, phi_used, phi_history

    # ------------------------------------------------------------------
    # Staircase
    # ------------------------------------------------------------------

    def _staircase_phi(self, n_target: int
                       ) -> Tuple[float, List[Tuple[float, int]]]:
        """Find largest φ giving ≥ n_target useful basins.

        Useful = size ≥ min_basin_size.
        Returns (phi_used, phi_history) where
        phi_history = [(phi, n_basins)] at each staircase step.
        """
        mu = self.nb_mu
        if mu <= 0:
            return 2.0, [(2.0, 1)]

        valid = self.nb_parent_raw >= 0
        phi_stars = np.sort(
            self.nb_edge_len_raw[valid] / mu)[::-1]  # descending

        phi_history = []
        min_sz = self.config.min_basin_size

        for n_cut in range(1, len(phi_stars)):
            phi_above = float(phi_stars[n_cut - 1])
            phi_below = float(phi_stars[n_cut]) if n_cut < len(phi_stars) else 0.0
            phi = (phi_above + phi_below) / 2.0

            labels = self._cluster_at_phi(phi)
            _, counts = np.unique(labels[labels >= 0], return_counts=True)
            n_useful = int(np.sum(counts >= min_sz))

            phi_history.append((phi, n_useful))

            if n_useful >= n_target:
                return phi, phi_history

        # Could not reach n_target — return current best
        phi_fallback = float(phi_stars[-1]) / 2.0 if len(phi_stars) > 0 else 2.0
        return phi_fallback, phi_history

    def _cluster_at_phi(self, phi: float) -> np.ndarray:
        """Apply Rule-1 + Rule-2 cuts at φ to stored raw NB tree.
        Returns labels array (pointer-jumping). No new evaluations.

        Rule 1: cut edges longer than φ·μ.
        Rule 2: cut hub edges — vertices with high indegree whose
                own edge to parent is long relative to incoming edges.
                Hub j is cut if indeg(j) ≥ nbc_min_incoming AND
                edge_len[j] / mean_incoming[j] > nbc_b.
        Rule 2 runs AFTER Rule 1 so that indegree counts reflect
        the already-pruned graph.

        Fully vectorized — no Python loops. Safe to call thousands
        of times from the staircase.
        """
        mu = self.nb_mu
        M = len(self.fvals)
        edge_len = self.nb_edge_len_raw   # read-only reference

        parent = self.nb_parent_raw.copy()

        # Rule 1: cut long edges
        if mu > 0:
            cut = (edge_len > phi * mu) & (parent >= 0)
            parent[cut] = -1

        # Rule 2: hub detection (vectorized)
        if self.config.nbc_min_incoming > 0:
            valid = parent >= 0
            if np.any(valid):
                indeg = np.zeros(M, dtype=int)
                sum_incoming = np.zeros(M, dtype=float)
                parents_valid = parent[valid]
                np.add.at(indeg, parents_valid, 1)
                np.add.at(sum_incoming, parents_valid, edge_len[valid])

                hubs = np.where(
                    (indeg >= self.config.nbc_min_incoming) &
                    (parent >= 0)
                )[0]
                if len(hubs) > 0:
                    mean_in = sum_incoming[hubs] / indeg[hubs]
                    ratio = np.where(mean_in > 0,
                                     edge_len[hubs] / mean_in, 0.0)
                    cut_mask = (mean_in > 0) & (ratio > self.config.nbc_b)
                    parent[hubs[cut_mask]] = -1

        # Pointer jumping → labels (vectorized)
        roots = np.where(parent >= 0, parent, np.arange(M))

        n_iter = int(np.ceil(np.log2(max(M, 2)))) + 5
        for _ in range(n_iter):
            r2 = roots[roots]
            if np.array_equal(r2, roots):
                break
            roots = r2

        return roots

    # ------------------------------------------------------------------
    # Basin membership (for converge_count)
    # ------------------------------------------------------------------

    def _build_basin_tree(self):
        """Build kNN tree from labeled Phase-0 points for membership queries."""
        if self.labels is None or not self.basins:
            self._basin_tree = None
            return

        valid_bids = set(self.basins.keys())
        mask = np.isin(self.labels, list(valid_bids))

        if not np.any(mask):
            self._basin_tree = None
            return

        self._basin_tree = KDTree(self.points_norm[mask])
        self._basin_tree_labels = self.labels[mask].copy()
        self._basin_tree_norm = self.points_norm[mask]

    def identify_basin_knn(self, x: np.ndarray,
                           k: Optional[int] = None) -> Optional[int]:
        """kNN majority vote: assign x to basin with most neighbors.

        Returns basin_id of the winning component.
        """
        if self._basin_tree is None:
            return None

        if k is None:
            k = self.config.nearest_better_k
        k = min(k, len(self._basin_tree_labels))
        if k == 0:
            return None

        x_norm = self._normalize(np.atleast_2d(x))[0]
        _, idxs = self._basin_tree.query(x_norm, k=k)
        idxs = np.atleast_1d(idxs)

        unique, counts = np.unique(
            self._basin_tree_labels[idxs], return_counts=True)
        best = int(np.argmax(counts))
        return int(unique[best])

    # ------------------------------------------------------------------
    # x₀ initialization
    # ------------------------------------------------------------------

    def jitter_x0(self, basin_id: BasinId, rng: np.random.Generator) -> np.ndarray:
        """x₀ = best point in basin (deterministic).

        CMA-ES starts from the strongest initial f-value, removing cold-start
        randomness from the elite pool. The `rng` argument is retained for
        the unlikely fallback when basin_id is not registered.
        """
        if basin_id not in self.basins:
            lb, ub = self.bounds[:, 0], self.bounds[:, 1]
            return rng.uniform(lb, ub)

        basin = self.basins[basin_id]
        return self.points[int(basin.best_idx)].copy()
