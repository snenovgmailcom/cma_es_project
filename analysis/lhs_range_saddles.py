#!/usr/bin/env python3
"""
lhs_range_saddles.py — Extended landscape classification.

EXTENSION over original:

  1. log_ratio = log10(max/min) when min > 0
       Distinguishes uniform-high from long-tailed distributions.

  2. basin_density = n_basins / N  (only when --saddle)
       Direct basin-count proxy via Morse-Smale flooding.

  3. cls_v1: original rule (range + mean quartile)
       range < 1500  OR  range > 1e10  →  HIGH
       mean_q ∈ {Q3, Q4}                →  HIGH
       otherwise                         →  LOW

  4. cls_v2: extended rule (only when --saddle)
       Splits HIGH into HIGH-narrow / HIGH-comp using log_ratio
       and basin_density thresholds.

  5. cls_abc: A/B/C partition (only when --cls-abc)
       Derived from empirical Optuna tuning study partitions.

         A: narrow flat       (range < 1500)
         B: cliff/few-basin   (range > 1e10  OR  mq >= 0.5)
         C: strict-LOW        (else)

SAMPLERS:
  --sampler {lhs,sobol}   Default: lhs (backward compat).
                          Sobol gives lower-discrepancy samples;
                          may reduce mq variance on borderline functions.
                          Sobol works with any N, but power-of-2 N gives
                          best balance properties.

Usage:
    # Original behavior (LHS, cls_v1 only)
    python lhs_range_saddles.py --suite cec2017 --dim 10

    # With saddle analysis + cls_v2
    python lhs_range_saddles.py --suite cec2017 --dim 10 --saddle

    # With A/B/C classification
    python lhs_range_saddles.py --suite cec2017 --dim 10 --cls-abc

    # Sobol sampler
    python lhs_range_saddles.py --suite cec2017 --dim 10 --sampler sobol

    # Full kit
    python lhs_range_saddles.py --suite cec2017 --dim 10 \\
        --sampler sobol --saddle --cls-abc
"""

import argparse
import sys as _sys
import warnings

import numpy as np
from scipy.stats import qmc
from scipy.spatial import cKDTree


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

LOG_RATIO_THRESH_DEFAULT = 4.0
BASIN_DENS_THRESH_DEFAULT = 0.01

# A/B/C v2 (scale-free) defaults. log_ratio replaces absolute range thresholds.
L_LOW_DEFAULT = 0.5    # log_ratio < L_LOW  -> A (narrow / nearly flat in log)
L_HIGH_DEFAULT = 4.0   # log_ratio > L_HIGH -> B (cliff / many-decade spread)

# Multi-seed mode sweeps exactly this many seeds (CEC/COCO convention: 51).
N_SEEDS = 51


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", default="cec2017",
                   choices=["cec2014", "cec2017", "cec2019", "cec2020", "cec2022"])
    p.add_argument("--dim", type=int, default=10)
    p.add_argument("--M-factor", type=int, default=500)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--functions", default=None,
                   help="Comma-separated list (default: all)")
    p.add_argument("--sampler", choices=["lhs", "sobol"], default="lhs",
                   help="Sampling method (default: lhs)")
    p.add_argument("--sobol-no-scramble", action="store_true",
                   help="Disable Sobol scrambling (default: scrambled)")
    p.add_argument("--saddle", action="store_true",
                   help="Compute basin persistence + cls_v2 extended class")
    p.add_argument("--k-saddle", type=int, default=10)
    p.add_argument("--log-ratio-thresh", type=float,
                   default=LOG_RATIO_THRESH_DEFAULT)
    p.add_argument("--basin-dens-thresh", type=float,
                   default=BASIN_DENS_THRESH_DEFAULT)
    p.add_argument("--cls-abc", action="store_true",
                   help="Compute A/B/C partition (range + mq based)")
    p.add_argument("--l-low", type=float, default=L_LOW_DEFAULT,
                   help=f"v2 log_ratio threshold for A class "
                        f"(default {L_LOW_DEFAULT})")
    p.add_argument("--l-high", type=float, default=L_HIGH_DEFAULT,
                   help=f"v2 log_ratio threshold for B class "
                        f"(default {L_HIGH_DEFAULT})")
    p.add_argument("--show-diff-only", action="store_true",
                   help="Only show functions where cls_v1 differs from cls_v2")
    p.add_argument("--start-seed", type=int, default=None,
                   help=f"Multi-seed mode: classify over {N_SEEDS} seeds "
                        f"[start-seed, start-seed+{N_SEEDS}). Reports "
                        "per-function A/B/C frequency + STABLE/BORDERLINE "
                        "flag. Implies --cls-abc. Mutually exclusive with "
                        "--seed.")
    args = p.parse_args()
    if args.start_seed is not None and "--seed" in _sys.argv:
        p.error("--seed and --start-seed are mutually exclusive: "
                "use --seed for a single classification, --start-seed for "
                f"the {N_SEEDS}-seed sweep.")
    return args


def get_suite_funcs(suite):
    if suite == "cec2017":  return list(range(1, 31))
    if suite == "cec2014":  return list(range(1, 31))
    if suite == "cec2020":  return list(range(1, 11))
    if suite == "cec2022":  return list(range(1, 13))
    if suite == "cec2019":  return list(range(1, 11))
    raise ValueError(f"Unknown suite: {suite}")


def get_bounds(suite, fnum, dim):
    if suite == "cec2019":
        bounds_2019 = {1: (-8192, 8192), 2: (-16384, 16384), 3: (-4, 4)}
        lb, ub = bounds_2019.get(fnum, (-100, 100))
    else:
        lb, ub = -100, 100
    return np.full(dim, lb, dtype=np.float64), np.full(dim, ub, dtype=np.float64)


def get_evaluator(suite, fnum, dim):
    import minionpy
    cls_map = {
        "cec2014": "CEC2014Functions",
        "cec2017": "CEC2017Functions",
        "cec2019": "CEC2019Functions",
        "cec2020": "CEC2020Functions",
        "cec2022": "CEC2022Functions",
    }
    cls = getattr(minionpy, cls_map[suite])
    # CEC2019Functions is 1-arg API (fnum only); dim is implicit per fnum.
    if suite == "cec2019":
        evaluator = cls(fnum)
    else:
        evaluator = cls(fnum, dim)
    return lambda X: np.asarray(evaluator(X), dtype=np.float64)


def quartile_label(value, fmin, fmax):
    if fmax == fmin:
        return "—", 0.0
    pos = max(0.0, min(1.0, (value - fmin) / (fmax - fmin)))
    label = ("Q1" if pos < 0.25 else
             "Q2" if pos < 0.50 else
             "Q3" if pos < 0.75 else "Q4")
    return label, pos


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def sample_unit(sampler_name, dim, n, seed, sobol_scramble=True):
    """Generate n samples in [0,1]^dim using the chosen sampler."""
    if sampler_name == "sobol":
        # Sobol emits a balance warning for non-power-of-2 n; suppress.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            sampler = qmc.Sobol(d=dim, seed=seed, scramble=sobol_scramble)
            unit = sampler.random(n=n)
    else:  # lhs
        sampler = qmc.LatinHypercube(d=dim, seed=seed)
        unit = sampler.random(n=n)
    return unit


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def compute_persistence(X, F, k=10):
    N = len(F)
    k_actual = min(k + 1, N)

    tree = cKDTree(X, leafsize=32)
    _, nbr_idx = tree.query(X, k=k_actual)

    order = np.argsort(F, kind="stable")

    parent = np.arange(N, dtype=np.intp)
    uf_rank = np.zeros(N, dtype=np.intp)
    birth_f = np.full(N, np.nan, dtype=np.float64)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def unite(elder, younger):
        re, ry = find(elder), find(younger)
        if re == ry:
            return re
        if uf_rank[re] < uf_rank[ry]:
            re, ry = ry, re
        parent[ry] = re
        if uf_rank[re] == uf_rank[ry]:
            uf_rank[re] += 1
        if birth_f[ry] < birth_f[re]:
            birth_f[re] = birth_f[ry]
        return re

    processed = np.zeros(N, dtype=bool)
    persistences = []

    for idx in order:
        fi = F[idx]
        nbrs = nbr_idx[idx, 1:]
        proc_roots = list({find(n) for n in nbrs if processed[n]})

        if not proc_roots:
            birth_f[idx] = fi
        else:
            eldest = min(proc_roots, key=lambda r: birth_f[r])
            for r in proc_roots:
                if r != eldest:
                    persistences.append(fi - birth_f[r])
                    eldest = unite(eldest, r)
            parent[idx] = find(eldest)

        processed[idx] = True

    n_basins = 1 + len(persistences)
    return persistences, n_basins


# ---------------------------------------------------------------------------
# Classification rules
# ---------------------------------------------------------------------------

def classify_v1(frange, mean_q):
    """Original rule: range + mean quartile."""
    if frange < 1500 or frange > 1e10:
        return "HIGH"
    if mean_q in ("Q3", "Q4"):
        return "HIGH"
    return "LOW"


def classify_v2(cls_v1, log_ratio, basin_density,
                log_ratio_thresh, basin_dens_thresh):
    """Extended rule: split HIGH into HIGH-narrow / HIGH-comp."""
    if cls_v1 == "LOW":
        return "LOW"
    is_long_tailed = log_ratio >= log_ratio_thresh
    has_many_basins = (basin_density is not None and
                       basin_density >= basin_dens_thresh)
    if is_long_tailed or has_many_basins:
        return "HIGH-comp"
    return "HIGH-narrow"


def classify_abc(frange, mean_pos):
    """A/B/C partition rule (range + mq position).

    Derived from empirical Optuna tuning study partitions:
        A: narrow flat       (range < 1500)
        B: cliff/few-basin   (range > 1e10  OR  mq >= 0.5)
        C: strict-LOW        (else)
    """
    if frange < 1500:
        return "A"
    if frange > 1e10:
        return "B"
    if mean_pos >= 0.5:
        return "B"
    return "C"


def classify_abc_v2(log_ratio, mean_pos, l_low, l_high):
    """Scale-free A/B/C partition (log_ratio + mq position).

    Replaces absolute F-unit thresholds of classify_abc (1500, 1e10) with
    dimensionless log_ratio thresholds. Invariant under f -> a*f (a > 0).
        A: narrow flat       (log_ratio < l_low,   e.g. < 0.5 decade)
        B: cliff/few-basin   (log_ratio > l_high,  e.g. > 4 decades, OR mq >= 0.5)
        C: strict-LOW        (else)
    log_ratio = +inf (fmin -> 0 with positive fmax) is treated as extreme cliff -> B.
    log_ratio = NaN (fmax <= 0) falls back to mean_pos rule only.
    """
    if np.isnan(log_ratio):
        return "B" if mean_pos >= 0.5 else "C"
    if log_ratio < l_low:
        return "A"
    if log_ratio > l_high:
        return "B"
    if mean_pos >= 0.5:
        return "B"
    return "C"


def compute_log_ratio(fmin, fmax):
    """log10(max/min) when both positive; +inf for fmin → 0 with positive fmax."""
    if fmin > 1e-30 and fmax > 0:
        return float(np.log10(fmax / fmin))
    if fmax > 0:
        return float("inf")
    return float("nan")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def classify_one_seed(suite, dim, funcs, M_factor, sampler, seed,
                      sobol_scramble, l_low, l_high):
    """Classify every function for a single seed. Returns
    {fnum: (cls_abc, cls_abc_v2, frange, mean_pos, log_ratio)}. Mirrors the
    single-seed main() path exactly (same X construction, same classify_abc
    call). Adds parallel classify_abc_v2 (scale-free) for comparison."""
    n_samples = M_factor * dim
    out = {}
    for fnum in funcs:
        lb, ub = get_bounds(suite, fnum, dim)
        unit = sample_unit(sampler, dim, n_samples, seed + fnum,
                           sobol_scramble)
        X = lb + (ub - lb) * unit
        try:
            F = get_evaluator(suite, fnum, dim)(X)
            fmin, fmax = float(np.min(F)), float(np.max(F))
            frange = fmax - fmin
            fmean = float(np.mean(F))
            _, mean_pos = quartile_label(fmean, fmin, fmax)
            log_ratio = compute_log_ratio(fmin, fmax)
            cls_abc = classify_abc(frange, mean_pos)
            cls_abc_v2 = classify_abc_v2(log_ratio, mean_pos, l_low, l_high)
            out[fnum] = (cls_abc, cls_abc_v2, frange, mean_pos, log_ratio)
        except Exception as e:
            out[fnum] = ("ERR", "ERR", float("nan"), float("nan"),
                         float("nan"))
            print(f"  seed {seed} f{fnum}: ERROR {e}")
    return out


def run_multiseed(args, funcs):
    """Multi-seed mode: sweep seeds, report per-function A/B/C frequency
    under both classify_abc (v1, hardcoded F-unit thresholds) and
    classify_abc_v2 (scale-free, log_ratio-based)."""
    n_samples = args.M_factor * args.dim
    sobol_scramble = not args.sobol_no_scramble
    seeds = list(range(args.start_seed, args.start_seed + N_SEEDS))

    print(f"Suite: {args.suite}  Dim: {args.dim}  "
          f"M_factor: {args.M_factor}  N: {n_samples}  Sampler: {args.sampler}"
          + (" (scrambled)" if args.sampler == "sobol" and sobol_scramble
             else " (unscrambled)" if args.sampler == "sobol" else ""))
    print(f"Multi-seed classification: seeds "
          f"{seeds[0]}..{seeds[-1]}  ({len(seeds)} seeds)")
    print(f"v1 thresholds: range<1500=A, range>1e10=B, mq>=0.5=B")
    print(f"v2 thresholds: log_ratio<{args.l_low}=A, "
          f"log_ratio>{args.l_high}=B, mq>=0.5=B")
    print()

    # Per function: parallel lists for v1 + v2 plus raw stats.
    labels = {f: [] for f in funcs}     # v1 (cls_abc)
    labels2 = {f: [] for f in funcs}    # v2 (cls_abc_v2)
    ranges = {f: [] for f in funcs}
    mposes = {f: [] for f in funcs}
    lrs = {f: [] for f in funcs}

    for s in seeds:
        res = classify_one_seed(args.suite, args.dim, funcs, args.M_factor,
                                args.sampler, s, sobol_scramble,
                                args.l_low, args.l_high)
        for f in funcs:
            cls, cls2, frng, mp, lr = res[f]
            labels[f].append(cls)
            labels2[f].append(cls2)
            ranges[f].append(frng)
            mposes[f].append(mp)
            lrs[f].append(lr)

    # Per-function summary: v1 and v2 side by side.
    hdr = (f"{'f':>4}  "
           f"{'v1 counts':>14}  {'v1 maj':>6}  {'v1 verdict':>11}  "
           f"{'v2 counts':>14}  {'v2 maj':>6}  {'v2 verdict':>11}  "
           f"{'range min..max':>26}  {'mean_pos min..max':>20}  "
           f"{'log_ratio min..max':>20}")
    print(hdr)
    print("-" * len(hdr))

    borderline_v1 = []
    borderline_v2 = []
    for f in funcs:
        # v1
        labs = labels[f]
        nA, nB, nC = labs.count("A"), labs.count("B"), labs.count("C")
        counts = {"A": nA, "B": nB, "C": nC}
        maj1 = max(counts, key=counts.get)
        verdict1 = "STABLE" if sum(v > 0 for v in counts.values()) == 1 \
                   else "BORDERLINE"
        if verdict1 == "BORDERLINE":
            borderline_v1.append(f)
        # v2
        labs2 = labels2[f]
        nA2, nB2, nC2 = labs2.count("A"), labs2.count("B"), labs2.count("C")
        counts2 = {"A": nA2, "B": nB2, "C": nC2}
        maj2 = max(counts2, key=counts2.get)
        verdict2 = "STABLE" if sum(v > 0 for v in counts2.values()) == 1 \
                   else "BORDERLINE"
        if verdict2 == "BORDERLINE":
            borderline_v2.append(f)
        # ranges
        rs = [r for r in ranges[f] if np.isfinite(r)]
        ms = [m for m in mposes[f] if np.isfinite(m)]
        ls = [l for l in lrs[f] if np.isfinite(l)]
        rng_str = f"{min(rs):.3e}..{max(rs):.3e}" if rs else "—"
        mp_str = f"{min(ms):.3f}..{max(ms):.3f}" if ms else "—"
        lr_str = f"{min(ls):.3f}..{max(ls):.3f}" if ls else "—"
        cnt1 = f"A:{nA} B:{nB} C:{nC}"
        cnt2 = f"A:{nA2} B:{nB2} C:{nC2}"
        print(f"f{f:<3d}  "
              f"{cnt1:>14}  {maj1:>6}  {verdict1:>11}  "
              f"{cnt2:>14}  {maj2:>6}  {verdict2:>11}  "
              f"{rng_str:>26}  {mp_str:>20}  {lr_str:>20}")

    print()
    print("=" * len(hdr))
    # Majority-vote partitions.
    for tag, lbls in (("v1", labels), ("v2", labels2)):
        for cls in ("A", "B", "C"):
            members = [f for f in funcs
                       if max({"A": lbls[f].count("A"),
                               "B": lbls[f].count("B"),
                               "C": lbls[f].count("C")}.items(),
                              key=lambda kv: kv[1])[0] == cls]
            print(f"majority-vote {tag} {cls}: {len(members)} ({members})")
        print()

    # BORDERLINE reports.
    if borderline_v1:
        print(f"BORDERLINE v1 ({len(borderline_v1)}): {borderline_v1}")
    else:
        print(f"BORDERLINE v1: none — every function is class-stable over "
              f"{len(seeds)} seeds")
    if borderline_v2:
        print(f"BORDERLINE v2 ({len(borderline_v2)}): {borderline_v2}")
    else:
        print(f"BORDERLINE v2: none — every function is class-stable over "
              f"{len(seeds)} seeds")

    # Disagreement report: which functions get different majority class.
    diffs = []
    for f in funcs:
        c1 = max({"A": labels[f].count("A"), "B": labels[f].count("B"),
                  "C": labels[f].count("C")}.items(),
                 key=lambda kv: kv[1])[0]
        c2 = max({"A": labels2[f].count("A"), "B": labels2[f].count("B"),
                  "C": labels2[f].count("C")}.items(),
                 key=lambda kv: kv[1])[0]
        if c1 != c2:
            diffs.append((f, c1, c2))
    if diffs:
        print()
        print(f"v1 -> v2 majority class shifts ({len(diffs)}):")
        for f, c1, c2 in diffs:
            print(f"  f{f}: {c1} -> {c2}")


# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    funcs = (list(map(int, args.functions.split(",")))
             if args.functions else get_suite_funcs(args.suite))

    # Multi-seed mode: separate path, leaves single-seed behaviour untouched.
    if args.start_seed is not None:
        run_multiseed(args, funcs)
        return

    n_samples = args.M_factor * args.dim
    sobol_scramble = not args.sobol_no_scramble

    print(f"Suite: {args.suite}  Dim: {args.dim}  "
          f"M_factor: {args.M_factor}  N: {n_samples}  "
          f"Seed: {args.seed}  Sampler: {args.sampler}"
          + (f" (scrambled)" if args.sampler == "sobol" and sobol_scramble else
             f" (unscrambled)" if args.sampler == "sobol" else ""))
    if args.saddle:
        print(f"Saddle analysis: ON  k_saddle: {args.k_saddle}")
        print(f"Thresholds: log_ratio>={args.log_ratio_thresh}  "
              f"basin_dens>={args.basin_dens_thresh}")
    if args.cls_abc:
        print(f"A/B/C classification: ON")
    print()

    # Header
    base_hdr = (f"{'f':>4}  {'min':>11}  {'max':>11}  {'range':>11}  "
                f"{'mean':>11}  {'mean_q':>8}  {'log_ratio':>10}  "
                f"{'cls_v1':>8}")
    abc_hdr = f"  {'cls_abc':>7}"
    saddle_hdr = (f"  {'n_bas':>5}  {'b_dens':>8}  {'max_pers':>11}  "
                  f"{'min_pers':>11}  {'cls_v2':>11}")

    full_hdr = base_hdr
    if args.cls_abc: full_hdr += abc_hdr
    if args.saddle:  full_hdr += saddle_hdr
    print(full_hdr)
    print("-" * len(full_hdr))

    rows = []  # (fnum, cls_v1, cls_v2, cls_abc)

    for fnum in funcs:
        lb, ub = get_bounds(args.suite, fnum, args.dim)
        unit = sample_unit(args.sampler, args.dim, n_samples,
                           args.seed + fnum, sobol_scramble)
        X = lb + (ub - lb) * unit

        try:
            F = get_evaluator(args.suite, fnum, args.dim)(X)
            fmin   = float(np.min(F))
            fmax   = float(np.max(F))
            frange = fmax - fmin
            fmean  = float(np.mean(F))

            mean_q, mean_pos = quartile_label(fmean, fmin, fmax)
            log_ratio = compute_log_ratio(fmin, fmax)
            cls_v1 = classify_v1(frange, mean_q)
            cls_abc = classify_abc(frange, mean_pos) if args.cls_abc else None

            base_row = (f"f{fnum:<3d}  {fmin:>11.4e}  {fmax:>11.4e}  "
                        f"{frange:>11.4e}  {fmean:>11.4e}  "
                        f"{mean_q} ({mean_pos:.2f})  "
                        f"{log_ratio:>10.3f}  {cls_v1:>8}")

            full_row = base_row
            if args.cls_abc:
                full_row += f"  {cls_abc:>7}"

            cls_v2 = None
            if args.saddle:
                # BUG FIX: was called twice (overwriting); single call now.
                pers_finite, n_bas = compute_persistence(X, F, k=args.k_saddle)
                basin_density = n_bas / n_samples
                cls_v2 = classify_v2(cls_v1, log_ratio, basin_density,
                                     args.log_ratio_thresh,
                                     args.basin_dens_thresh)

                if pers_finite:
                    arr = np.array(pers_finite, dtype=np.float64)
                    saddle_row = (f"  {n_bas:>5d}  {basin_density:>8.4f}  "
                                  f"{arr.max():>11.4e}  {arr.min():>11.4e}  "
                                  f"{cls_v2:>11}")
                else:
                    saddle_row = (f"  {n_bas:>5d}  {basin_density:>8.4f}  "
                                  f"{'—':>11}  {'—':>11}  {cls_v2:>11}")
                full_row += saddle_row

            rows.append((fnum, cls_v1, cls_v2, cls_abc))

            if args.show_diff_only and args.saddle and cls_v1 == cls_v2:
                continue

            print(full_row)

        except Exception as e:
            print(f"f{fnum:<3d}  ERROR: {e}")

    # Summary
    if rows:
        print()
        print("=" * len(full_hdr))
        v1_high = [r for r in rows if r[1] == "HIGH"]
        v1_low = [r for r in rows if r[1] == "LOW"]
        print(f"cls_v1: HIGH={len(v1_high)} ({sorted(r[0] for r in v1_high)})")
        print(f"cls_v1: LOW ={len(v1_low)} ({sorted(r[0] for r in v1_low)})")

        if args.cls_abc:
            a = [r for r in rows if r[3] == "A"]
            b = [r for r in rows if r[3] == "B"]
            c = [r for r in rows if r[3] == "C"]
            print(f"cls_abc: A={len(a)} ({sorted(r[0] for r in a)})")
            print(f"cls_abc: B={len(b)} ({sorted(r[0] for r in b)})")
            print(f"cls_abc: C={len(c)} ({sorted(r[0] for r in c)})")

        if args.saddle:
            v2_narrow = [r for r in rows if r[2] == "HIGH-narrow"]
            v2_comp = [r for r in rows if r[2] == "HIGH-comp"]
            v2_low = [r for r in rows if r[2] == "LOW"]
            print(f"cls_v2: HIGH-narrow={len(v2_narrow)} "
                  f"({sorted(r[0] for r in v2_narrow)})")
            print(f"cls_v2: HIGH-comp  ={len(v2_comp)} "
                  f"({sorted(r[0] for r in v2_comp)})")
            print(f"cls_v2: LOW        ={len(v2_low)} "
                  f"({sorted(r[0] for r in v2_low)})")

            diffs = [r for r in rows
                     if (r[1] == "HIGH" and r[2] == "HIGH-comp")]
            if diffs:
                print()
                print(f"HIGH → HIGH-comp transitions: "
                      f"{sorted(r[0] for r in diffs)}")
                print("(These functions would receive LOWrot params under v2)")


if __name__ == "__main__":
    main()
