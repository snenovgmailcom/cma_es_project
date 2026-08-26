#!/usr/bin/env python3
"""
Mann-Whitney U campaign for the C-ONLY positioning comparison.

Reference algorithm: MSC-CMA-Conly (the C-configuration-only schedule).
Opponents: the full benchmark portfolio (seven baselines plus the full
MSC-CMA schedule), and NEA2+ in the cells where its runs exist.

Scope: the composition class of the eight design-envelope cells.
Tests: independent two-sided Mann-Whitney U (asymptotic, continuity
corrected) on the 51 raw terminal errors per function, exactly as in
analysis/run_mwu_nea2plus.py.  Bonferroni correction is applied per
(cell, opponent) family over the composition functions of that cell;
the family size is recorded in every row.

Outputs (CSV only, nothing else is touched):
  related_comparisons/conly/mwu/details.csv
  related_comparisons/conly/mwu/summary.csv
"""

from pathlib import Path
import csv
import math
import pickle

import numpy as np
from scipy import stats


ALPHA = 0.05
RUNS = 51

REFERENCE = "MSC-CMA-Conly"

FIELD_OPPONENTS = (
    "MSC-CMA",
)

# NEA2+ runs exist only in these cells (suite, dimension, budget).
NEA2PLUS_CELLS = {
    ("cec2017", 10, 100_000),
    ("cec2020", 5, 50_000),
    ("cec2020", 10, 1_000_000),
    ("cec2020", 15, 3_000_000),
    ("cec2022", 10, 200_000),
    ("cec2022", 20, 1_000_000),
}

SETTINGS = [
    ("cec2014", 10, 100_000),
    ("cec2017", 10, 100_000),
    ("cec2020", 5, 50_000),
    ("cec2020", 10, 1_000_000),
    ("cec2020", 15, 3_000_000),
    ("cec2020", 20, 10_000_000),
    ("cec2022", 10, 200_000),
    ("cec2022", 20, 1_000_000),
]

COMPOSITION_FUNCTIONS = {
    "cec2014": tuple(range(23, 31)),
    "cec2017": tuple(range(21, 31)),
    "cec2020": tuple(range(8, 11)),
    "cec2022": tuple(range(9, 13)),
}


def load_errors(path, suite, dim, budget):
    if not path.is_file():
        raise RuntimeError(f"Missing: {path}")

    with path.open("rb") as f:
        d = pickle.load(f)

    if not isinstance(d, dict) or "errors" not in d:
        raise RuntimeError(f"{path}: missing errors")

    x = np.asarray(d["errors"])

    if x.shape != (RUNS,):
        raise RuntimeError(f"{path}: errors shape={x.shape}, expected (51,)")

    if x.dtype.kind not in "iuf":
        raise RuntimeError(f"{path}: errors are not numeric")

    x = x.astype(np.float64, copy=True)

    if not np.isfinite(x).all():
        raise RuntimeError(f"{path}: non-finite errors")

    if "maxevals" in d and int(d["maxevals"]) != budget:
        raise RuntimeError(f"{path}: maxevals={d['maxevals']} != {budget}")

    if "dim" in d and int(d["dim"]) != dim:
        raise RuntimeError(f"{path}: dim={d['dim']} != {dim}")

    if "suite" in d and str(d["suite"]).lower() != suite:
        raise RuntimeError(f"{path}: suite={d['suite']} != {suite}")

    if "seeds" in d:
        seeds = np.asarray(d["seeds"])
        if (
            seeds.shape != (RUNS,)
            or seeds.dtype.kind not in "iu"
            or not np.array_equal(
                np.sort(seeds.astype(np.int64)),
                np.arange(RUNS),
            )
        ):
            raise RuntimeError(f"{path}: seeds are not exactly 0..50")

    # Raw terminal errors, unchanged: no flooring, clipping or sorting.
    return x


def pkl_path(algo, suite, dim, budget, fid):
    return (
        Path("experiments")
        / suite
        / f"d{dim}"
        / algo
        / f"maxevals_{budget}"
        / f"f{fid}.pkl"
    )


rows = []
summary = []

for suite, dim, budget in SETTINGS:
    funcs = COMPOSITION_FUNCTIONS[suite]
    m = len(funcs)

    opponents = list(FIELD_OPPONENTS)

    print()
    print(f"=== {suite} D={dim} B={budget}  composition m={m} ===")

    ref_errors = {
        fid: load_errors(
            pkl_path(REFERENCE, suite, dim, budget, fid),
            suite, dim, budget,
        )
        for fid in funcs
    }

    for opp in opponents:
        counts = {"lower": 0, "higher": 0, "not significant": 0}

        for fid in funcs:
            x = ref_errors[fid]
            y = load_errors(
                pkl_path(opp, suite, dim, budget, fid),
                suite, dim, budget,
            )

            res = stats.mannwhitneyu(
                x,
                y,
                alternative="two-sided",
                method="asymptotic",
                use_continuity=True,
            )

            u = float(res.statistic)
            p_raw = float(res.pvalue)
            p_bonf = min(1.0, m * p_raw)

            # Probability that a random C-ONLY terminal error is lower
            # than a random opponent terminal error, ties as one half.
            p_conly_lower = 1.0 - u / (RUNS * RUNS)

            if (
                p_bonf >= ALPHA
                or math.isclose(
                    p_conly_lower, 0.5, rel_tol=0.0, abs_tol=1e-15
                )
            ):
                decision = "not significant"
            elif p_conly_lower > 0.5:
                decision = "lower"
            else:
                decision = "higher"

            counts[decision] += 1

            rows.append({
                "suite": suite,
                "dimension": dim,
                "budget": budget,
                "function": fid,
                "function_class": "composition",
                "reference": REFERENCE,
                "opponent": opp,
                "n_reference": RUNS,
                "n_opponent": RUNS,
                "u_reference": format(u, ".17g"),
                "probability_conly_lower": format(p_conly_lower, ".17g"),
                "median_conly": format(float(np.median(x)), ".17g"),
                "median_opponent": format(float(np.median(y)), ".17g"),
                "p_raw": format(p_raw, ".17g"),
                "bonferroni_family_size": m,
                "p_bonferroni": format(p_bonf, ".17g"),
                "alpha": ALPHA,
                "decision": decision,
            })

        summary.append({
            "suite": suite,
            "dimension": dim,
            "budget": budget,
            "opponent": opp,
            "n_functions": m,
            "conly_lower": counts["lower"],
            "conly_higher": counts["higher"],
            "not_significant": counts["not significant"],
        })

        print(
            f"  vs {opp:14s}  "
            f"↓={counts['lower']}  "
            f"↑={counts['higher']}  "
            f"—={counts['not significant']}"
        )


outdir = Path("related_comparisons/conly/mwu")
outdir.mkdir(parents=True, exist_ok=True)

fields = [
    "suite", "dimension", "budget", "function", "function_class",
    "reference", "opponent", "n_reference", "n_opponent",
    "u_reference", "probability_conly_lower",
    "median_conly", "median_opponent",
    "p_raw", "bonferroni_family_size", "p_bonferroni",
    "alpha", "decision",
]

with (outdir / "details.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)

fields2 = [
    "suite", "dimension", "budget", "opponent", "n_functions",
    "conly_lower", "conly_higher", "not_significant",
]

with (outdir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields2, lineterminator="\n")
    w.writeheader()
    w.writerows(summary)

print()
print("WROTE:", outdir / "details.csv")
print("WROTE:", outdir / "summary.csv")
print("TOTAL TESTS:", len(rows))
