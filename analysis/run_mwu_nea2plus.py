#!/usr/bin/env python3

from pathlib import Path
import csv
import math
import pickle

import numpy as np
from scipy import stats


ALPHA = 0.05
RUNS = 51

REFERENCE = "MSC-CMA"
COMPETITOR = "NEA2PLUS-PY"

SETTINGS = [
    ("cec2017", 10,   100_000),
    ("cec2020",  5,    50_000),
    ("cec2020", 10, 1_000_000),
    ("cec2020", 15, 3_000_000),
    ("cec2022", 10,   200_000),
    ("cec2022", 20, 1_000_000),
]

FUNCTIONS = {
    "cec2017": (1, *range(3, 31)),
    "cec2020": tuple(range(1, 11)),
    "cec2022": tuple(range(1, 13)),
}

CLASSES = {
    "cec2017": {
        "basic": {1, *range(3, 11)},
        "hybrid": set(range(11, 21)),
        "composition": set(range(21, 31)),
    },
    "cec2020": {
        "basic": set(range(1, 5)),
        "hybrid": set(range(5, 8)),
        "composition": set(range(8, 11)),
    },
    "cec2022": {
        "basic": set(range(1, 6)),
        "hybrid": set(range(6, 9)),
        "composition": set(range(9, 13)),
    },
}


def function_class(suite, fid):
    for cls, funcs in CLASSES[suite].items():
        if fid in funcs:
            return cls
    raise RuntimeError(f"Unknown class: {suite} f{fid}")


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
        raise RuntimeError(
            f"{path}: maxevals={d['maxevals']} != {budget}"
        )

    if "dim" in d and int(d["dim"]) != dim:
        raise RuntimeError(
            f"{path}: dim={d['dim']} != {dim}"
        )

    if "suite" in d and str(d["suite"]).lower() != suite:
        raise RuntimeError(
            f"{path}: suite={d['suite']} != {suite}"
        )

    if "seeds" in d:
        seeds = np.asarray(d["seeds"])
        if (
            seeds.shape != (RUNS,)
            or seeds.dtype.kind not in "iu"
            or not np.array_equal(
                np.sort(seeds.astype(np.int64)),
                np.arange(RUNS)
            )
        ):
            raise RuntimeError(f"{path}: seeds are not exactly 0..50")

    # IMPORTANT:
    # raw terminal errors are returned unchanged.
    # No flooring, clipping, rounding, sorting or improvements trace.
    return x


rows = []

for suite, dim, budget in SETTINGS:
    funcs = FUNCTIONS[suite]
    m = len(funcs)

    print()
    print(f"=== {suite} D={dim} B={budget}  m={m} ===")

    counts = {
        "NEA2+ better": 0,
        "MSC-CMA-ES better": 0,
        "not significant": 0,
    }

    for fid in funcs:
        px = (
            Path("experiments")
            / suite / f"d{dim}"
            / COMPETITOR / f"maxevals_{budget}"
            / f"f{fid}.pkl"
        )

        py = (
            Path("experiments")
            / suite / f"d{dim}"
            / REFERENCE / f"maxevals_{budget}"
            / f"f{fid}.pkl"
        )

        x = load_errors(px, suite, dim, budget)
        y = load_errors(py, suite, dim, budget)

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

        # Probability that a random NEA2+ terminal error
        # is lower than a random MSC terminal error,
        # with ties contributing one half.
        p_nea_lower = 1.0 - u / (RUNS * RUNS)

        if (
            p_bonf >= ALPHA
            or math.isclose(
                p_nea_lower, 0.5,
                rel_tol=0.0,
                abs_tol=1e-15
            )
        ):
            decision = "not significant"
        elif p_nea_lower > 0.5:
            decision = "NEA2+ better"
        else:
            decision = "MSC-CMA-ES better"

        counts[decision] += 1

        rows.append({
            "suite": suite,
            "dimension": dim,
            "budget": budget,
            "function": fid,
            "function_class": function_class(suite, fid),
            "competitor": COMPETITOR,
            "reference": REFERENCE,
            "n_competitor": RUNS,
            "n_reference": RUNS,
            "u_competitor": format(u, ".17g"),
            "probability_nea2plus_lower": format(p_nea_lower, ".17g"),
            "median_nea2plus": format(float(np.median(x)), ".17g"),
            "median_msc": format(float(np.median(y)), ".17g"),
            "p_raw": format(p_raw, ".17g"),
            "bonferroni_family_size": m,
            "p_bonferroni": format(p_bonf, ".17g"),
            "alpha": ALPHA,
            "decision": decision,
        })

    print(
        f"NEA2+ better={counts['NEA2+ better']}  "
        f"MSC-CMA-ES better={counts['MSC-CMA-ES better']}  "
        f"not significant={counts['not significant']}"
    )


outdir = Path("related_comparisons/nea2plus/mwu")
outdir.mkdir(parents=True, exist_ok=True)

fields = [
    "suite",
    "dimension",
    "budget",
    "function",
    "function_class",
    "competitor",
    "reference",
    "n_competitor",
    "n_reference",
    "u_competitor",
    "probability_nea2plus_lower",
    "median_nea2plus",
    "median_msc",
    "p_raw",
    "bonferroni_family_size",
    "p_bonferroni",
    "alpha",
    "decision",
]

with (outdir / "details.csv").open(
    "w", newline="", encoding="utf-8"
) as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)


# Compact setting summary.
summary = []

for suite, dim, budget in SETTINGS:
    rr = [
        r for r in rows
        if r["suite"] == suite
        and r["dimension"] == dim
        and r["budget"] == budget
    ]

    summary.append({
        "suite": suite,
        "dimension": dim,
        "budget": budget,
        "n_functions": len(rr),
        "nea2plus_better": sum(
            r["decision"] == "NEA2+ better" for r in rr
        ),
        "msc_better": sum(
            r["decision"] == "MSC-CMA-ES better" for r in rr
        ),
        "not_significant": sum(
            r["decision"] == "not significant" for r in rr
        ),
    })

with (outdir / "summary.csv").open(
    "w", newline="", encoding="utf-8"
) as f:
    fields2 = [
        "suite",
        "dimension",
        "budget",
        "n_functions",
        "nea2plus_better",
        "msc_better",
        "not_significant",
    ]
    w = csv.DictWriter(f, fieldnames=fields2)
    w.writeheader()
    w.writerows(summary)

print()
print("WROTE:", outdir / "details.csv")
print("WROTE:", outdir / "summary.csv")
print("TOTAL FUNCTIONS:", len(rows))
