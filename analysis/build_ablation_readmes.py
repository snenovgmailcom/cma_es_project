#!/usr/bin/env python3

from pathlib import Path
import argparse
import csv
import math
import pickle

import numpy as np
from scipy import stats

import summary_grid_clean as sg


SUITE = "cec2017"
DIM = 10
BUDGET = 100_000
N_RUNS = 51
ALPHA = 0.05

FUNCS = (1, *range(3, 31))  # CEC2017 f2 excluded

CLASSES = {
    "basic": {1, *range(3, 11)},
    "hybrid": set(range(11, 21)),
    "composition": set(range(21, 31)),
}

CLASS_DISPLAY = {
    "basic": "unimodal and simple multimodal",
    "hybrid": "Hybrid",
    "composition": "Composition",
}

FULL_DIR = Path(
    "experiments/cec2017/d10/MSC-CMA/maxevals_100000"
)

VARIANTS = {
    "NO-NBC": {
        "data": Path(
            "ablations/experiments/cec2017/d10/NO-NBC/maxevals_100000"
        ),
        "description": (
            "This control removes nearest-better clustering and the "
            "basin-based restart structure. The Phase-0 Sobol points are "
            "ranked by objective value and CMA-ES restarts are launched "
            "sequentially from the ranked points until the budget is exhausted."
        ),
        "component": (
            "Removal of nearest-better clustering and the basin-based "
            "structure layer"
        ),
    },

    "FIXED-PHI": {
        "data": Path(
            "ablations/experiments/cec2017/d10/FIXED-PHI/maxevals_100000"
        ),
        "description": (
            "The automatic staircase selection of the NBC cutting threshold "
            "is disabled and a fixed `phi = 2` is used. The remaining "
            "MSC-CMA-ES structure is retained."
        ),
        "component": (
            "Fixed NBC threshold `phi = 2` instead of automatic staircase "
            "selection"
        ),
    },

    "NO-EXCLUSION": {
        "data": Path(
            "ablations/experiments/cec2017/d10/NO-EXCLUSION/maxevals_100000"
        ),
        "description": (
            "The k-NN convergence-tracking mechanism is retained for basin "
            "identification, but repeatedly resolved basins are not excluded "
            "from subsequent restarts."
        ),
        "component": (
            "Removal of suppression of repeatedly resolved basins"
        ),
    },

    "C-ONLY": {
        "data": Path(
            "experiments/cec2017/d10/MSC-CMA-Conly/maxevals_100000"
        ),
        "description": (
            "Only the C configuration is used. C/B alternation is disabled "
            "and therefore the cross-cycle Phase-0 reuse associated with the "
            "alternating schedule is also absent. NBC, staircase threshold "
            "selection, basin-dependent restart parameterization, exclusion, "
            "and final refinement are retained."
        ),
        "component": (
            "C configuration only, without C/B alternation and cross-cycle "
            "Phase-0 reuse"
        ),
    },
}

OUT_ROOT = Path("ablations/cec2017/d10/budget_100000")


def func_class(fid):
    for name, fs in CLASSES.items():
        if fid in fs:
            return name
    raise ValueError(f"no class for f{fid}")


def fmt(x):
    x = float(x)
    if not np.isfinite(x):
        return "—"
    if x == 0:
        return "0"
    if abs(x) >= 1e4 or abs(x) < 1e-3:
        return f"{x:.6e}"
    return f"{x:.6g}"


def load_payload(path):
    if not path.is_file():
        raise RuntimeError(f"Missing file: {path}")

    with path.open("rb") as f:
        d = pickle.load(f)

    e = np.asarray(d.get("errors", []), dtype=np.float64)

    if e.shape != (N_RUNS,):
        raise RuntimeError(
            f"{path}: expected 51 errors, got {e.shape}"
        )

    if not np.isfinite(e).all():
        raise RuntimeError(f"{path}: non-finite errors")

    if int(d.get("maxevals", BUDGET)) != BUDGET:
        raise RuntimeError(f"{path}: wrong maxevals")

    if int(d.get("dim", DIM)) != DIM:
        raise RuntimeError(f"{path}: wrong dimension")

    if "seeds" in d:
        seeds = np.asarray(d["seeds"])
        if not np.array_equal(np.sort(seeds), np.arange(51)):
            raise RuntimeError(f"{path}: seeds are not exactly 0..50")

    return d


def load_dir(directory):
    result = {}
    for fid in FUNCS:
        p = directory / f"f{fid}.pkl"
        result[fid] = load_payload(p)
    return result


def descriptive(errors):
    raw = np.asarray(errors, dtype=np.float64)
    e = sg._floor(raw)

    return {
        "mean": float(e.mean()),
        "median": float(np.median(e)),
        "best": float(e.min()),
        "worst": float(e.max()),
        "std": float(e.std(ddof=1)),
        "fbtc": float(sg._fbtc_from_final_errs(raw)),
    }


def aggregated_descriptive(payloads, ids):
    sums = {
        "mean": 0.0,
        "median": 0.0,
        "best": 0.0,
        "worst": 0.0,
        "std": 0.0,
        "fbtc": 0.0,
    }

    for fid in ids:
        m = descriptive(payloads[fid]["errors"])
        for key in sums:
            sums[key] += m[key]

    return sums


def bold_pair(a, b, higher=False):
    if math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15):
        return f"**{fmt(a)}**", f"**{fmt(b)}**"

    a_better = a > b if higher else a < b

    if a_better:
        return f"**{fmt(a)}**", fmt(b)

    return fmt(a), f"**{fmt(b)}**"


def calculate_mwu(full, variant):
    rows = []

    for fid in FUNCS:
        x = np.asarray(variant[fid]["errors"], dtype=np.float64)
        y = np.asarray(full[fid]["errors"], dtype=np.float64)

        r = stats.mannwhitneyu(
            x,
            y,
            alternative="two-sided",
            method="asymptotic",
            use_continuity=True,
        )

        u = float(r.statistic)
        p_raw = float(r.pvalue)
        p_bonf = min(1.0, len(FUNCS) * p_raw)

        # For minimization:
        # P(X_variant < X_full) + 1/2 P(equal)
        probability_lower = 1.0 - u / (len(x) * len(y))

        if p_bonf >= ALPHA or math.isclose(
            probability_lower, 0.5, abs_tol=1e-15
        ):
            decision = "not significant"
            symbol = "≈"
        elif probability_lower > 0.5:
            decision = "variant better"
            symbol = "+"
        else:
            decision = "MSC-CMA-ES better"
            symbol = "−"

        rows.append({
            "function": fid,
            "class": func_class(fid),
            "u_variant": u,
            "probability_variant_lower": probability_lower,
            "p_raw": p_raw,
            "p_bonferroni": p_bonf,
            "decision": decision,
            "symbol": symbol,
        })

    return rows


def count_decisions(rows, ids=None):
    if ids is not None:
        ids = set(ids)
        rows = [r for r in rows if r["function"] in ids]

    vb = sum(r["decision"] == "variant better" for r in rows)
    fb = sum(r["decision"] == "MSC-CMA-ES better" for r in rows)
    ns = sum(r["decision"] == "not significant" for r in rows)

    return vb, fb, ns


def write_mwu_csv(path, rows):
    fields = [
        "function",
        "class",
        "u_variant",
        "probability_variant_lower",
        "p_raw",
        "p_bonferroni",
        "decision",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for r in rows:
            w.writerow({
                k: (
                    format(r[k], ".17g")
                    if isinstance(r[k], float)
                    else r[k]
                )
                for k in fields
            })


def render_variant(name, info, full, variant, rows):
    categories = [
        ("basic", sorted(CLASSES["basic"])),
        ("hybrid", sorted(CLASSES["hybrid"])),
        ("composition", sorted(CLASSES["composition"])),
        ("all", list(FUNCS)),
    ]

    text = [
        f"# {name} — CEC2017, D=10, B=100K",
        "",
        "## Ablation",
        "",
        info["description"],
        "",
        "Reference: full MSC-CMA-ES at the same suite, dimension, budget, "
        "and 51-run protocol.",
        "",
        f"Raw ablation data: `{info['data']}/`",
        "",
        "Contents: [Benchmark results](#benchmark-results) · "
        "[Mann–Whitney U](#mannwhitney-u)",
        "",
        "## Benchmark results",
        "",
        "Fixed-budget terminal results at **B=100,000 NFE**, using 51 runs "
        "per function.",
        "",
        "The descriptive metrics use the same definitions as the main "
        "benchmark reports. Errors with absolute value at most `1e-8` are "
        "treated as zero for descriptive metrics; standard deviation is the "
        "sample standard deviation (`ddof=1`). FBTC(B) uses the same 51 "
        "log-uniform targets in `[10², 10⁻⁸]`. Class and ALL values are sums "
        "over functions.",
        "",
        "| Category | Metric | MSC-CMA-ES | " + name + " |",
        "|:--|:--|--:|--:|",
    ]

    metrics = [
        ("mean", False, "mean"),
        ("median", False, "median"),
        ("best", False, "best"),
        ("worst", False, "worst"),
        ("std", False, "std"),
        ("fbtc", True, "FBTC(B)"),
    ]

    for cname, ids in categories:
        fm = aggregated_descriptive(full, ids)
        vm = aggregated_descriptive(variant, ids)

        label = (
            "**ALL**"
            if cname == "all"
            else f"**{CLASS_DISPLAY[cname]}**"
        )

        label += f" (n={len(ids)})"

        first = True
        for key, higher, display in metrics:
            a, b = bold_pair(fm[key], vm[key], higher=higher)

            if first:
                text.append(
                    f"| {label} | {display} | {a} | {b} |"
                )
                first = False
            else:
                text.append(
                    f"|  | {display} | {a} | {b} |"
                )

    text += [
        "",
        "*Bold indicates the better descriptive value in that row "
        "(lower for error metrics and std; higher for FBTC(B)). "
        "These values are not significance tests.*",
        "",
        '<a id="mannwhitney-u"></a>',
        "",
        "## Mann–Whitney U",
        "",
        "Independent, two-sided Mann–Whitney U tests compare "
        f"**{name}** with **MSC-CMA-ES** on each function. Each sample "
        "contains 51 unmodified run-wise terminal errors. SciPy's "
        "asymptotic method (`method=\"asymptotic\"`) with continuity "
        "correction (`use_continuity=True`) is used. Bonferroni adjustment "
        "is applied over the **29 CEC2017 functions**.",
        "",
    ]

    vb, fb, ns = count_decisions(rows)
    cvb, cfb, cns = count_decisions(
        rows, CLASSES["composition"]
    )

    text += [
        f"Setting summary: {name} significant on **{vb}** functions; "
        f"MSC-CMA-ES significant on **{fb}**; not significant on **{ns}**.",
        "",
        f"Composition subset: {name} significant on **{cvb}** of 10 "
        f"functions; MSC-CMA-ES significant on **{cfb}**; "
        f"not significant on **{cns}**.",
        "",
        f"`+` means {name} has significantly lower terminal errors; "
        "`−` means MSC-CMA-ES has significantly lower terminal errors; "
        "`≈` means the difference is not significant after Bonferroni "
        "adjustment.",
        "",
        "| Function | Class | U (" + name + ") | "
        "P(" + name + " lower) | p_raw | p_Bonferroni | Result |",
        "|:--|:--|--:|--:|--:|--:|:--:|",
    ]

    for r in rows:
        text.append(
            f"| f{r['function']} | {r['class']} | "
            f"{fmt(r['u_variant'])} | "
            f"{fmt(r['probability_variant_lower'])} | "
            f"{fmt(r['p_raw'])} | "
            f"{fmt(r['p_bonferroni'])} | "
            f"**{r['symbol']}** |"
        )

    text += [
        "",
        "Full-precision statistics: [`mwu_details.csv`](mwu_details.csv).",
        "",
    ]

    return "\n".join(text)


def render_refinement(full):
    rows = []

    for fid in FUNCS:
        d = full[fid]

        if "pre_refine_errors_per_seed" not in d:
            raise RuntimeError(
                f"f{fid}.pkl has no pre_refine_errors_per_seed"
            )

        pre = np.asarray(
            d["pre_refine_errors_per_seed"], dtype=np.float64
        )
        final = np.asarray(d["errors"], dtype=np.float64)

        if pre.shape != (51,):
            raise RuntimeError(
                f"f{fid}: bad pre-refinement shape {pre.shape}"
            )

        if not np.isfinite(pre).all():
            raise RuntimeError(
                f"f{fid}: non-finite pre-refinement errors"
            )

        pre_d = sg._floor(pre)
        final_d = sg._floor(final)

        improved = int(np.sum(final < pre))

        rows.append({
            "fid": fid,
            "class": func_class(fid),
            "median_pre": float(np.median(pre_d)),
            "median_final": float(np.median(final_d)),
            "improved": improved,
        })

    text = [
        "# Final-refinement contribution — CEC2017, D=10, B=100K",
        "",
        "## Analysis",
        "",
        "This analysis uses the full MSC-CMA-ES runs and compares the "
        "incumbent recorded immediately before the final refinement stage "
        "with the terminal incumbent after refinement.",
        "",
        "This is **not** treated as a separate fixed-budget algorithmic "
        "ablation. The two values come from the same run and correspond to "
        "different evaluation counts: the pre-refinement incumbent is "
        "recorded before the reserved refinement budget is spent, while the "
        "final incumbent is recorded at the end of the run.",
        "",
        "Raw data: "
        "`experiments/cec2017/d10/MSC-CMA/maxevals_100000/`",
        "",
        "For descriptive display, errors with absolute value at most `1e-8` "
        "are treated as zero, consistently with the main benchmark tables.",
        "",
        "## Class summary",
        "",
        "| Category | SUM(median before) | SUM(median after) | "
        "Improved run-function pairs |",
        "|:--|--:|--:|--:|",
    ]

    for cname in ("basic", "hybrid", "composition"):
        rr = [r for r in rows if r["class"] == cname]
        sp = sum(r["median_pre"] for r in rr)
        sf = sum(r["median_final"] for r in rr)
        imp = sum(r["improved"] for r in rr)
        total = len(rr) * 51

        text.append(
            f"| **{CLASS_DISPLAY[cname]}** (n={len(rr)}) | "
            f"{fmt(sp)} | {fmt(sf)} | {imp}/{total} |"
        )

    sp = sum(r["median_pre"] for r in rows)
    sf = sum(r["median_final"] for r in rows)
    imp = sum(r["improved"] for r in rows)

    text.append(
        f"| **ALL** (n=29) | {fmt(sp)} | {fmt(sf)} | "
        f"{imp}/{29 * 51} |"
    )

    text += [
        "",
        "## Per-function refinement contribution",
        "",
        "| Function | Class | Median before | Median after | "
        "Runs improved |",
        "|:--|:--|--:|--:|--:|",
    ]

    for r in rows:
        text.append(
            f"| f{r['fid']} | {r['class']} | "
            f"{fmt(r['median_pre'])} | "
            f"{fmt(r['median_final'])} | "
            f"{r['improved']}/51 |"
        )

    text += [
        "",
        "No independent-sample MWU test is attached to this table because "
        "pre- and post-refinement values are stages of the same optimization "
        "run rather than results from two independently executed algorithms.",
        "",
    ]

    return "\n".join(text)


def render_overview(summaries):
    lines = [
        "# MSC-CMA-ES ablation studies",
        "",
        "The ablation study is performed on **CEC2017, D=10, "
        "B=100,000 NFE**, using 51 runs per function and excluding the "
        "deprecated CEC2017 `f2`.",
        "",
        "The two MSC-CMA-ES configurations were tuned with Optuna only once, "
        "on CEC2017 at D=10 under the official 100K evaluation budget. "
        "The resulting parameterization is reused across suites, dimensions, "
        "and budgets; only the predefined dimension scaling of the CMA "
        "initial step-size parameter is applied. For this reason, the "
        "ablation study is performed on the same CEC2017 D=10 tuning cell.",
        "",
        "The following ablations are considered:",
        "",
        "| Ablation | Component tested | Results | MWU summary "
        "(variant / MSC / NS) |",
        "|:--|:--|:--|--:|",
    ]

    for name, info in VARIANTS.items():
        vb, fb, ns = summaries[name]
        link = f"cec2017/d10/budget_100000/{name}/README.md"

        lines.append(
            f"| {name} | {info['component']} | "
            f"[Data + MWU]({link}) | {vb} / {fb} / {ns} |"
        )

    lines += [
        "| Final refinement | Incumbent immediately before vs after the "
        "final refinement stage | "
        "[Contribution analysis]"
        "(cec2017/d10/budget_100000/REFINEMENT/README.md) | — |",
        "",
        "For the four algorithmic ablations, statistical comparisons against "
        "full MSC-CMA-ES use independent two-sided Mann–Whitney U tests on "
        "the 51 raw terminal errors per function, with Bonferroni correction "
        "across the 29 CEC2017 functions.",
        "",
        "Deep Statistical Comparison is not used for the ablation study: "
        "each ablation addresses a direct component-wise comparison against "
        "the full algorithm rather than a multi-algorithm ranking question.",
        "",
    ]

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    full = load_dir(FULL_DIR)

    variant_payloads = {}
    variant_mwu = {}
    summaries = {}

    for name, info in VARIANTS.items():
        data = load_dir(info["data"])
        rows = calculate_mwu(full, data)

        variant_payloads[name] = data
        variant_mwu[name] = rows
        summaries[name] = count_decisions(rows)

    # Validate refinement data too.
    refinement_text = render_refinement(full)

    if args.check_only:
        print("CHECK PASSED")
        print("FULL: 29 functions x 51 runs")
        for name in VARIANTS:
            vb, fb, ns = summaries[name]
            print(
                f"{name}: 29 functions x 51 runs; "
                f"MWU variant/MSC/NS = {vb}/{fb}/{ns}"
            )
        print("REFINEMENT: pre-refinement data available for all 29 functions")
        print("Would write 6 README files + 4 mwu_details.csv files")
        return

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    for name, info in VARIANTS.items():
        out = OUT_ROOT / name
        out.mkdir(parents=True, exist_ok=True)

        readme = render_variant(
            name,
            info,
            full,
            variant_payloads[name],
            variant_mwu[name],
        )

        (out / "README.md").write_text(
            readme + "\n", encoding="utf-8"
        )

        write_mwu_csv(
            out / "mwu_details.csv",
            variant_mwu[name],
        )

        print("WROTE", out / "README.md")
        print("WROTE", out / "mwu_details.csv")

    refdir = OUT_ROOT / "REFINEMENT"
    refdir.mkdir(parents=True, exist_ok=True)
    (refdir / "README.md").write_text(
        refinement_text + "\n", encoding="utf-8"
    )
    print("WROTE", refdir / "README.md")

    Path("ablations/README.md").write_text(
        render_overview(summaries) + "\n",
        encoding="utf-8",
    )
    print("WROTE ablations/README.md")


if __name__ == "__main__":
    main()
