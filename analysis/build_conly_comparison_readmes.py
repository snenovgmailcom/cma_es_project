#!/usr/bin/env python3
"""
Build the C-ONLY positioning README pages.

Inputs (already produced locally):
  experiments/<suite>/d<D>/<ALGO>/maxevals_<B>/f*.pkl
  related_comparisons/conly/mwu/details.csv      (run_mwu_conly.py)
  related_comparisons/conly/mwu/summary.csv      (run_mwu_conly.py)
  related_comparisons/conly/dsc/<suite>/d<D>/budget_<B>/
      ordering_composition.csv                   (run_dsc_conly.py, optional)

Outputs (README files only):
  related_comparisons/conly/README.md
  related_comparisons/conly/<suite>/d<D>/budget_<B>/README.md

The script does not alter PKL, MWU, DSC, experiment, Git, or GitHub
data.  FBTC(B) uses the target grid of analysis/summary_grid_clean.py
so that coverage numbers match the main benchmark pages.

Style: this generator emits the canonical repository style (official
algorithm names, p_raw / p_Bonferroni labels, %.4g statistics, powers
of ten for budgets, capitalised class labels, FBTC(B)).
"""

from __future__ import annotations

import csv
import pickle
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import summary_grid_clean as sg


RUNS = 51
REFERENCE = "MSC-CMA-Conly"

PORTFOLIO = (
    "MSC-CMA-Conly",
    "MSC-CMA",
)

NEA2PLUS_CELLS = set()

SETTINGS = (
    ("cec2014", 10, 100_000),
    ("cec2017", 10, 100_000),
    ("cec2020", 5, 50_000),
    ("cec2020", 10, 1_000_000),
    ("cec2020", 15, 3_000_000),
    ("cec2020", 20, 10_000_000),
    ("cec2022", 10, 200_000),
    ("cec2022", 20, 1_000_000),
)

COMPOSITION_FUNCTIONS = {
    "cec2014": tuple(range(23, 31)),
    "cec2017": tuple(range(21, 31)),
    "cec2020": tuple(range(8, 11)),
    "cec2022": tuple(range(9, 13)),
}

DISPLAY = {
    "MSC-CMA-Conly": "MSC-CMA-ES (C-only)",
    "MSC-CMA": "MSC-CMA-ES",
    "ARRDE": "ARRDE",
    "BIPOP-CMA": "BIPOP-CMA-ES",
    "LSRTDE": "L-SRTDE",
    "NLSHADE-RSP": "NL-SHADE-RSP",
    "j2020": "j2020",
    "jSO": "jSO",
    "NEA2PLUS-PY": "NEA2+",
}


def fmt_budget(n: int) -> str:
    e = 0
    while n % 10 == 0:
        n //= 10
        e += 1
    if n == 1:
        return f"10^{e}"
    return f"{n}x10^{e}"


def fmt(v: float) -> str:
    return format(float(v), ".4g")


def load_errors(path: Path, suite: str, dim: int, budget: int) -> np.ndarray:
    if not path.is_file():
        raise RuntimeError(f"Missing: {path}")
    with path.open("rb") as f:
        d = pickle.load(f)
    x = np.asarray(d["errors"], dtype=np.float64)
    if x.shape != (RUNS,) or not np.isfinite(x).all():
        raise RuntimeError(f"{path}: bad errors array")
    if "maxevals" in d and int(d["maxevals"]) != budget:
        raise RuntimeError(f"{path}: wrong maxevals")
    if "dim" in d and int(d["dim"]) != dim:
        raise RuntimeError(f"{path}: wrong dim")
    return x


def cell_algorithms(suite: str, dim: int, budget: int) -> list[str]:
    algos = list(PORTFOLIO)
    if (suite, dim, budget) in NEA2PLUS_CELLS:
        algos.append("NEA2PLUS-PY")
    return algos


def load_cell(suite: str, dim: int, budget: int):
    funcs = COMPOSITION_FUNCTIONS[suite]
    data = {}
    for algo in cell_algorithms(suite, dim, budget):
        per_func = {}
        for fid in funcs:
            p = (
                Path("experiments") / suite / f"d{dim}" / algo
                / f"maxevals_{budget}" / f"f{fid}.pkl"
            )
            per_func[fid] = load_errors(p, suite, dim, budget)
        data[algo] = per_func
    return funcs, data


def fbtc(errors: np.ndarray) -> float:
    return float(sg._fbtc_from_final_errs(errors))


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mwu_for_cell(details, suite, dim, budget):
    return [
        r for r in details
        if r["suite"] == suite
        and int(r["dimension"]) == dim
        and int(r["budget"]) == budget
    ]


def dsc_ordering(suite, dim, budget):
    p = (
        Path("related_comparisons/conly/dsc") / suite / f"d{dim}"
        / f"budget_{budget}" / "ordering_composition.csv"
    )
    if not p.is_file():
        return None
    rows = read_rows(p)
    key = None
    for cand in ("mean_rank", "mean", "dsc_mean_rank"):
        if rows and cand in rows[0]:
            key = cand
            break
    if key is None:
        return None
    rows.sort(key=lambda r: float(r[key]))
    return [(r["algorithm"], float(r[key])) for r in rows], p


def cell_page(suite, dim, budget, details) -> str:
    funcs, data = load_cell(suite, dim, budget)
    m = len(funcs)
    b = fmt_budget(budget)

    agg = {}
    for algo, per_func in data.items():
        errs = [per_func[f] for f in funcs]
        agg[algo] = {
            "mean": sum(float(np.mean(e)) for e in errs),
            "median": sum(float(np.median(e)) for e in errs),
            "best": sum(float(np.min(e)) for e in errs),
            "worst": sum(float(np.max(e)) for e in errs),
            "fbtc": sum(fbtc(e) for e in errs),
        }

    lines = []
    a = lines.append
    a(f"# C-only positioning - {suite.upper()}, D = {dim}, budget {b}")
    a("")
    a(
        f"Composition class ({m} functions: "
        f"f{funcs[0]}-f{funcs[-1]}), {RUNS} runs per function, "
        f"seeds 0-50, raw terminal errors."
    )
    a("")
    a("## Benchmark summary (sums over the composition functions)")
    a("")
    a("| Algorithm | SUM(mean) | SUM(median) | SUM(best) | SUM(worst) | SUM(FBTC(B)) |")
    a("|:--|--:|--:|--:|--:|--:|")
    for algo in sorted(agg, key=lambda x: agg[x]["mean"]):
        v = agg[algo]
        a(
            f"| {DISPLAY[algo]} | {fmt(v['mean'])} | {fmt(v['median'])} "
            f"| {fmt(v['best'])} | {fmt(v['worst'])} | {fmt(v['fbtc'])} |"
        )
    a("")

    a("## FBTC(B) per function")
    a("")
    order = [x for x in cell_algorithms(suite, dim, budget)]
    a("| Function | " + " | ".join(DISPLAY[x] for x in order) + " |")
    a("|:--|" + "--:|" * len(order))
    for fid in funcs:
        vals = [fmt(fbtc(data[x][fid])) for x in order]
        a(f"| f{fid} | " + " | ".join(vals) + " |")
    a("")

    a("## Mann-Whitney U: C-only vs full MSC-CMA-ES")
    a("")
    a(
        "Two-sided Mann-Whitney U on the 51 raw terminal errors per "
        "function; p_Bonferroni corrects within this cell over the "
        f"{m} composition functions per opponent. Arrows mark "
        "significant results at alpha = 0.05 from the C-only "
        "perspective: up = C-only better, down = opponent better."
    )
    a("")
    rows = mwu_for_cell(details, suite, dim, budget)
    opponents = sorted(
        {r["opponent"] for r in rows},
        key=lambda o: order.index(o) if o in order else 99,
    )
    a("| Function | " + " | ".join(DISPLAY[o] for o in opponents) + " |")
    a("|:--|" + "--:|" * len(opponents))
    for fid in funcs:
        cells = []
        for o in opponents:
            rr = [
                r for r in rows
                if int(r["function"]) == fid and r["opponent"] == o
            ]
            if not rr:
                cells.append("-")
                continue
            r = rr[0]
            p = fmt(float(r["p_bonferroni"]))
            mark = ""
            if r["decision"] == "conly better":
                mark = " &#8593;"
            elif r["decision"] == "opponent better":
                mark = " &#8595;"
            cells.append(p + mark)
        a(f"| f{fid} | " + " | ".join(cells) + " |")
    a("")
    a("| Opponent | C-only better | Opponent better | Not significant |")
    a("|:--|--:|--:|--:|")
    for o in opponents:
        rr = [r for r in rows if r["opponent"] == o]
        cb = sum(r["decision"] == "conly better" for r in rr)
        ob = sum(r["decision"] == "opponent better" for r in rr)
        ns = sum(r["decision"] == "not significant" for r in rr)
        a(f"| {DISPLAY[o]} | {cb} | {ob} | {ns} |")
    a("")

    dsc = None
    if dsc is not None:
        ordering, path = dsc
        a("## Deep Statistical Comparison (composition scope, k = 8)")
        a("")
        a("| Algorithm | Mean DSC rank |")
        a("|:--|--:|")
        for algo, mr in ordering:
            a(f"| {DISPLAY.get(algo, algo)} | {fmt(mr)} |")
        a("")
        a(
            f"Full DSC artefacts (per-function ranks, omnibus, "
            f"Holm post-hoc): `{path.parent.as_posix()}/`."
        )
        a("")

    a("## Protocol notes")
    a("")
    a(
        "- The C-only variant runs `benchmark/msc.py --conly`: the C "
        "configuration alone, without C/B alternation and without "
        "cross-cycle Phase-0 reuse; clustering, staircase, adaptive "
        "basin parameters, exclusion and refinement are unchanged."
    )
    a(
        "- FBTC(B) is the raw fixed-budget target coverage at this "
        "cell's budget, on the target grid of the main benchmark pages."
    )
    a(
        "- This page is a positioning comparison of the C-only "
        "schedule directly against the full MSC-CMA-ES method; the component ablations "
        "of MSC-CMA-ES are documented in `ablations/`."
    )
    a("")
    return "\n".join(lines)


def top_page(details, summary) -> str:
    lines = []
    a = lines.append

    a("# C-only cross-suite comparison")
    a("")
    a(
        "Direct comparison of MSC-CMA-ES (C-only) with the full "
        "MSC-CMA-ES method on the composition-function subsets of eight "
        "suite-dimension-budget cells."
    )
    a("")
    a(
        "Statistics: independent two-sided Mann-Whitney U tests on 51 "
        "raw terminal errors per function, with Bonferroni correction "
        "within each cell over its composition functions."
    )
    a("")
    a("| Cell | Budget | Composition functions | C-only / FULL / n.s. | Page |")
    a("|:--|:--|:--|:--|:--|")

    for suite, dim, budget in SETTINGS:
        m = len(COMPOSITION_FUNCTIONS[suite])

        rr = [
            r for r in summary
            if r["suite"] == suite
            and int(r["dimension"]) == dim
            and int(r["budget"]) == budget
            and r["opponent"] == "MSC-CMA"
        ]

        if rr:
            r = rr[0]
            triple = (
                f"{r['conly_better']} / {r['opponent_better']} / "
                f"{r['not_significant']}"
            )
        else:
            triple = "-"

        link = f"{suite}/d{dim}/budget_{budget}/README.md"

        a(
            f"| {suite.upper()} D={dim} | {fmt_budget(budget)} | {m} | "
            f"{triple} | [results]({link}) |"
        )

    a("")
    a(
        "Triples are: C-only significantly better / full MSC-CMA-ES "
        "significantly better / not significant, counted over the "
        "composition functions of the cell."
    )
    a("")

    return "\n".join(lines)


def main() -> int:
    root = Path("related_comparisons/conly")
    details = read_rows(root / "mwu" / "details.csv")
    summary = read_rows(root / "mwu" / "summary.csv")

    for suite, dim, budget in SETTINGS:
        page = cell_page(suite, dim, budget, details)
        out = root / suite / f"d{dim}" / f"budget_{budget}" / "README.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print("WROTE:", out)

    top = top_page(details, summary)
    (root / "README.md").write_text(top, encoding="utf-8")
    print("WROTE:", root / "README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
