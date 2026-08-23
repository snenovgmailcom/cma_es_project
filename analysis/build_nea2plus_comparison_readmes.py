#!/usr/bin/env python3
"""
Build the NEA2+ related-comparison README pages.

Inputs (already produced locally):
  experiments/.../MSC-CMA/maxevals_<B>/f*.pkl
  experiments/.../NEA2PLUS-PY/maxevals_<B>/f*.pkl
  related_comparisons/nea2plus/mwu/details.csv
  related_comparisons/nea2plus/mwu/summary.csv
  related_comparisons/nea2plus/dsc/<suite>/d<D>/budget_<B>/
      per_function_dsc_ranks.csv
      ordering_all.csv
      ordering_composition.csv

Outputs (only README files):
  related_comparisons/nea2plus/README.md
  related_comparisons/nea2plus/<suite>/d<D>/budget_<B>/README.md

The script does not alter PKL, MWU, DSC, experiment, Git, or GitHub data.
Benchmark metrics reuse analysis/summary_grid_clean.py so that flooring,
sample-std, FBTC targets, and function classes match the main benchmark pages.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

# Allow "python analysis/build_nea2plus_comparison_readmes.py" from repo root.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import summary_grid_clean as sg


REFERENCE = "MSC-CMA"
COMPETITOR = "NEA2PLUS-PY"
DSC_ALGORITHMS = ("MSC-CMA", "NEA2PLUS-PY", "BIPOP-CMA")
EXPECTED_RUNS = 51
ALPHA = 0.05

SETTINGS = (
    ("cec2017", 10,   100_000),
    ("cec2020",  5,    50_000),
    ("cec2020", 10, 1_000_000),
    ("cec2020", 15, 3_000_000),
    ("cec2022", 10,   200_000),
    ("cec2022", 20, 1_000_000),
)

FUNCTIONS = {
    "cec2017": (1, *range(3, 31)),
    "cec2020": tuple(range(1, 11)),
    "cec2022": tuple(range(1, 13)),
}

DISPLAY = {
    "MSC-CMA": "MSC-CMA-ES",
    "NEA2PLUS-PY": "NEA2+",
    "BIPOP-CMA": "BIPOP-CMA-ES",
}

CLASS_DISPLAY = {
    "basic": "unimodal and simple multimodal",
    "hybrid": "Hybrid",
    "composition": "Composition",
    "all": "ALL",
}

METRICS = ("mean", "median", "best", "worst", "std", "fbtc")
LOWER_BETTER = {"mean", "median", "best", "worst", "std"}
HIGHER_BETTER = {"fbtc"}

PREUSS_URL = (
    "https://titan.csit.rmit.edu.au/~e46507/publications/"
    "Experimental_Assessment_of_Multimodal_Optimization_Algorithms.pdf"
)


class BuildError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--experiments",
        type=Path,
        default=Path("experiments"),
        help="experiment root (default: experiments)",
    )
    p.add_argument(
        "--comparison-root",
        type=Path,
        default=Path("related_comparisons/nea2plus"),
        help="NEA2+ comparison root (default: related_comparisons/nea2plus)",
    )
    p.add_argument(
        "--check-only",
        action="store_true",
        help="validate all inputs and render in memory, but write nothing",
    )
    return p.parse_args()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise BuildError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def budget_label(b: int) -> str:
    if b % 1_000_000 == 0:
        return f"{b // 1_000_000}M"
    if b % 1_000 == 0:
        return f"{b // 1_000}K"
    return f"{b:,}"


def fmt_number(x: float, digits: int = 6) -> str:
    if not math.isfinite(x):
        return "—"
    if x == 0:
        return "0"
    ax = abs(x)
    if ax >= 1e4 or ax < 1e-4:
        return f"{x:.6e}"
    return f"{x:.{digits}g}"


def fmt_p(x: str | float | None) -> str:
    if x is None or x == "":
        return "—"
    v = float(x)
    if v < 1e-4:
        return f"{v:.6e}"
    return f"{v:.6g}"


def markdown_bold(value: str, yes: bool) -> str:
    return f"**{value}**" if yes else value


def expected_functions(suite: str) -> tuple[int, ...]:
    return FUNCTIONS[suite]


def class_functions(suite: str, cls: str) -> list[int]:
    all_funcs = set(expected_functions(suite))
    if cls == "all":
        return sorted(all_funcs)
    return sorted(all_funcs & set(sg.FUNC_CLASSES[suite][cls]))


def validate_metric_grid(
    experiments: Path, suite: str, dim: int, budget: int
) -> dict[str, dict[int, dict[str, Any]]]:
    out: dict[str, dict[int, dict[str, Any]]] = {}
    expected = set(expected_functions(suite))

    for algo in (REFERENCE, COMPETITOR):
        source = experiments / suite / f"d{dim}" / algo / f"maxevals_{budget}"
        if not source.is_dir():
            raise BuildError(f"Missing benchmark directory: {source}")

        metrics_raw = sg.load_cell_metrics(str(source))
        metrics: dict[int, dict[str, Any]] = {}
        for name, row in metrics_raw.items():
            text = str(name)
            if text.lower().startswith("f"):
                fid = int(text[1:])
            else:
                fid = int(text)
            if fid in expected:
                metrics[fid] = row

        missing = sorted(expected - set(metrics))
        if missing:
            raise BuildError(
                f"{source}: missing benchmark functions "
                + ", ".join(f"f{x}" for x in missing)
            )

        # Validate exactly 51 runs and correct budget for the used function set.
        for fid in expected:
            row = metrics[fid]
            if int(row["n_runs"]) != EXPECTED_RUNS:
                raise BuildError(
                    f"{source}/f{fid}: n_runs={row['n_runs']}, expected 51"
                )
            if int(row["maxevals"]) != budget:
                raise BuildError(
                    f"{source}/f{fid}: maxevals={row['maxevals']} != {budget}"
                )
        out[algo] = metrics

    return out


def aggregate_benchmark(
    metric_grid: dict[str, dict[int, dict[str, Any]]],
    suite: str,
) -> dict[str, dict[str, dict[str, float]]]:
    result: dict[str, dict[str, dict[str, float]]] = {}
    for cls in ("basic", "hybrid", "composition", "all"):
        fids = class_functions(suite, cls)
        result[cls] = {}
        for metric in METRICS:
            result[cls][metric] = {}
            key = "fbtc" if metric == "fbtc" else metric
            for algo in (REFERENCE, COMPETITOR):
                result[cls][metric][algo] = float(
                    sum(float(metric_grid[algo][fid][key]) for fid in fids)
                )
    return result


def render_benchmark(
    agg: dict[str, dict[str, dict[str, float]]],
    suite: str,
    dim: int,
    budget: int,
) -> str:
    lines = [
        "## Benchmark results",
        "",
        f"Fixed-budget terminal results at **B={budget:,} NFE**, using 51 runs per "
        "function for MSC-CMA-ES and NEA2+.",
        "",
        "The descriptive metrics use the same definitions as the main benchmark "
        "reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; "
        "the standard deviation is the sample standard deviation (`ddof=1`). "
        "FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform "
        "targets in `[10², 10⁻⁸]`. Class and ALL values are sums over functions.",
        "",
        "| Category | Metric | MSC-CMA-ES | NEA2+ |",
        "|:--|:--|--:|--:|",
    ]

    metric_label = {
        "mean": "mean",
        "median": "median",
        "best": "best",
        "worst": "worst",
        "std": "std",
        "fbtc": "FBTC(B)",
    }

    for cls in ("basic", "hybrid", "composition", "all"):
        fids = class_functions(suite, cls)
        first = True
        for metric in METRICS:
            a = agg[cls][metric][REFERENCE]
            b = agg[cls][metric][COMPETITOR]
            if metric in HIGHER_BETTER:
                best = max(a, b)
            else:
                best = min(a, b)
            tie = math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)
            sa = fmt_number(a, 6)
            sb = fmt_number(b, 6)
            sa = markdown_bold(sa, tie or math.isclose(a, best, rel_tol=1e-12, abs_tol=1e-15))
            sb = markdown_bold(sb, tie or math.isclose(b, best, rel_tol=1e-12, abs_tol=1e-15))
            category = (
                f"**{CLASS_DISPLAY[cls]}** (n={len(fids)})" if first else ""
            )
            lines.append(
                f"| {category} | {metric_label[metric]} | {sa} | {sb} |"
            )
            first = False

    lines += [
        "",
        "*Bold indicates the better descriptive value in that row "
        "(lower for error metrics and std; higher for FBTC(B)). "
        "These descriptive values are not significance tests.*",
        "",
    ]
    return "\n".join(lines)


def load_mwu_rows(
    comparison_root: Path,
    suite: str,
    dim: int,
    budget: int,
) -> list[dict[str, str]]:
    rows = read_csv(comparison_root / "mwu" / "details.csv")
    selected = [
        r for r in rows
        if r["suite"] == suite
        and int(r["dimension"]) == dim
        and int(r["budget"]) == budget
    ]
    expected = set(expected_functions(suite))
    found = {int(r["function"]) for r in selected}
    if found != expected or len(selected) != len(expected):
        raise BuildError(
            f"MWU {suite} D={dim} B={budget}: expected {len(expected)} rows, "
            f"got {len(selected)} with functions {sorted(found)}"
        )
    for r in selected:
        if r["competitor"] != COMPETITOR or r["reference"] != REFERENCE:
            raise BuildError(f"Unexpected MWU algorithms in row: {r}")
        if int(r["n_competitor"]) != EXPECTED_RUNS or int(r["n_reference"]) != EXPECTED_RUNS:
            raise BuildError(f"Unexpected MWU sample size in row: {r}")
        if int(r["bonferroni_family_size"]) != len(expected):
            raise BuildError(f"Unexpected MWU Bonferroni family size in row: {r}")
    return sorted(selected, key=lambda r: int(r["function"]))


def decision_symbol(decision: str) -> str:
    return {
        "NEA2+ better": "+",
        "MSC-CMA-ES better": "−",
        "not significant": "≈",
    }[decision]


def render_mwu(rows: list[dict[str, str]], suite: str) -> str:
    m = len(rows)
    counts = Counter(r["decision"] for r in rows)
    comp_rows = [r for r in rows if r["function_class"] == "composition"]
    comp_counts = Counter(r["decision"] for r in comp_rows)

    lines = [
        '<a id="mannwhitney-u"></a>',
        "",
        "## Mann–Whitney U",
        "",
        "Independent, two-sided Mann–Whitney U tests compare NEA2+ with "
        "MSC-CMA-ES on each function. Each sample contains 51 unmodified "
        "run-wise terminal errors. SciPy's asymptotic Mann–Whitney U method "
        '(`method="asymptotic"`) with continuity correction '
        '(`use_continuity=True`) is used. Bonferroni adjustment is applied '
        f"over the **{m} functions** in this setting.",
        "",
        "For minimization, `probability_nea2plus_lower` is "
        r"$P(X_{NEA2+}<X_{MSC})+\frac12P(X_{NEA2+}=X_{MSC})$.",
        "",
        f"Setting summary: NEA2+ significant on **{counts['NEA2+ better']}** "
        f"functions; MSC-CMA-ES significant on **{counts['MSC-CMA-ES better']}**; "
        f"not significant on **{counts['not significant']}**.",
        "",
        f"Composition subset: NEA2+ significant on **{comp_counts['NEA2+ better']}** "
        f"of {len(comp_rows)} functions; MSC-CMA-ES significant on "
        f"**{comp_counts['MSC-CMA-ES better']}**; not significant on "
        f"**{comp_counts['not significant']}**.",
        "",
        "`+` means NEA2+ has significantly lower terminal errors; `−` means "
        "MSC-CMA-ES has significantly lower terminal errors; `≈` means the "
        "difference is not significant at `alpha=0.05` after Bonferroni adjustment.",
        "",
        "### Mann–Whitney U statistic",
        "",
        "| Function | Class | U (NEA2+) | P(NEA2+ lower) |",
        "|:--|:--|--:|--:|",
    ]

    for r in rows:
        lines.append(
            f"| f{int(r['function'])} | {r['function_class']} | "
            f"{fmt_number(float(r['u_competitor']))} | "
            f"{fmt_number(float(r['probability_nea2plus_lower']))} |"
        )

    lines += [
        "",
        "### Raw two-sided p-value",
        "",
        "| Function | p_raw |",
        "|:--|--:|",
    ]
    for r in rows:
        lines.append(f"| f{int(r['function'])} | {fmt_p(r['p_raw'])} |")

    lines += [
        "",
        "### Bonferroni-adjusted p-value and decision",
        "",
        "| Function | p_Bonferroni | Decision |",
        "|:--|--:|:--:|",
    ]
    for r in rows:
        p = float(r["p_bonferroni"])
        symbol = decision_symbol(r["decision"])
        pv = fmt_p(p)
        if p < ALPHA:
            pv = f"**{pv}**"
        lines.append(f"| f{int(r['function'])} | {pv} | **{symbol}** |")

    lines += [
        "",
        "Full-precision MWU statistics are available in "
        "[`../../../mwu/details.csv`](../../../mwu/details.csv) "
        "relative to the NEA2+ comparison root.",
        "",
    ]
    return "\n".join(lines)


def load_dsc(
    comparison_root: Path,
    suite: str,
    dim: int,
    budget: int,
) -> tuple[list[dict[str, str]], dict[str, list[dict[str, str]]]]:
    d = comparison_root / "dsc" / suite / f"d{dim}" / f"budget_{budget}"
    ranks = read_csv(d / "per_function_dsc_ranks.csv")
    orderings = {
        "all": read_csv(d / "ordering_all.csv"),
        "composition": read_csv(d / "ordering_composition.csv"),
    }

    expected_f = set(expected_functions(suite))
    expected_a = set(DSC_ALGORITHMS)
    pairs = {(int(r["function_id"]), r["algorithm"]) for r in ranks}
    expected_pairs = {(f, a) for f in expected_f for a in expected_a}
    if pairs != expected_pairs or len(ranks) != len(expected_pairs):
        raise BuildError(
            f"DSC rank grid incomplete for {suite} D={dim} B={budget}"
        )

    for scope, rows in orderings.items():
        if len(rows) != 3 or {r["algorithm"] for r in rows} != expected_a:
            raise BuildError(
                f"DSC ordering {scope} invalid for {suite} D={dim} B={budget}"
            )
        for r in rows:
            if int(r["k"]) != 3:
                raise BuildError(f"DSC k != 3 in {suite} D={dim} B={budget}/{scope}")

    ranks.sort(
        key=lambda r: (
            int(r["function_id"]),
            DSC_ALGORITHMS.index(r["algorithm"]),
        )
    )
    return ranks, orderings


def render_dsc(
    ranks: list[dict[str, str]],
    orderings: dict[str, list[dict[str, str]]],
    suite: str,
) -> str:
    lookup = {
        (int(r["function_id"]), r["algorithm"]): float(r["dsc_rank"])
        for r in ranks
    }

    lines = [
        '<a id="deep-statistical-comparison"></a>',
        "",
        "## Deep Statistical Comparison",
        "",
        "DSC compares **MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES** using the "
        "51 unmodified terminal errors per function. Per-function rankings use "
        "Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`, "
        "`monte_carlo_iterations=0`). The rank matrices are analyzed with the "
        "Friedman omnibus test separately for all functions and for the "
        "composition-function subset. When the omnibus null hypothesis is rejected, "
        "Holm-adjusted post-hoc comparisons are performed against the algorithm "
        "with the best mean DSC rank.",
        "",
        "`★` means MSC-CMA-ES has the best mean DSC rank and Friedman rejects; "
        "`≈` means Friedman rejects but the Holm-adjusted comparison between "
        "MSC-CMA-ES and the best-ranked method is not significant; `↓` means "
        "the best-ranked method differs significantly from MSC-CMA-ES after Holm "
        "adjustment; `O` means Friedman does not reject and no post-hoc "
        "interpretation is made.",
        "",
        "### DSC ranks by function",
        "",
        "Lower DSC rank indicates better performance; tied distributions receive "
        "fractional ranks.",
        "",
        "| Function | MSC-CMA-ES | NEA2+ | BIPOP-CMA-ES |",
        "|:--|--:|--:|--:|",
    ]

    for fid in expected_functions(suite):
        vals = [
            lookup[(fid, "MSC-CMA")],
            lookup[(fid, "NEA2PLUS-PY")],
            lookup[(fid, "BIPOP-CMA")],
        ]
        lines.append(
            f"| f{fid} | {fmt_number(vals[0])} | {fmt_number(vals[1])} | "
            f"{fmt_number(vals[2])} |"
        )

    lines += [
        "",
        "### Statistical comparison",
        "",
        "| Scope | n | Best-ranked algorithm | MSC mean rank | NEA2+ mean rank | "
        "BIPOP mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | "
        "p_Holm(NEA2+) | Result |",
        "|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|",
    ]

    for scope in ("all", "composition"):
        rows = orderings[scope]
        by_alg = {r["algorithm"]: r for r in rows}
        ordered = sorted(rows, key=lambda r: float(r["position_average"]))
        best = ordered[0]["algorithm"]
        control = by_alg["MSC-CMA"]["posthoc_control"] or "—"
        p_msc = by_alg["MSC-CMA"]["posthoc_holm_p"]
        p_nea = by_alg["NEA2PLUS-PY"]["posthoc_holm_p"]
        status = by_alg["MSC-CMA"]["dsc_status"]
        n = int(by_alg["MSC-CMA"]["n_functions"])
        lines.append(
            f"| {scope} | {n} | {DISPLAY[best]} | "
            f"{fmt_number(float(by_alg['MSC-CMA']['mean_dsc_rank']))} | "
            f"{fmt_number(float(by_alg['NEA2PLUS-PY']['mean_dsc_rank']))} | "
            f"{fmt_number(float(by_alg['BIPOP-CMA']['mean_dsc_rank']))} | "
            f"{fmt_p(by_alg['MSC-CMA']['omnibus_p_value'])} | "
            f"{DISPLAY.get(control, control)} | {fmt_p(p_msc)} | "
            f"{fmt_p(p_nea)} | **{status}** |"
        )

    lines += [
        "",
        "Complete DSCTool request/response files and exact orderings are stored under "
        "`related_comparisons/nea2plus/dsc/`.",
        "",
    ]
    return "\n".join(lines)


def setting_page_path(root: Path, suite: str, dim: int, budget: int) -> Path:
    return root / suite / f"d{dim}" / f"budget_{budget}" / "README.md"


def render_setting_page(
    experiments: Path,
    comparison_root: Path,
    suite: str,
    dim: int,
    budget: int,
) -> str:
    metric_grid = validate_metric_grid(experiments, suite, dim, budget)
    agg = aggregate_benchmark(metric_grid, suite)
    mwu = load_mwu_rows(comparison_root, suite, dim, budget)
    ranks, orderings = load_dsc(comparison_root, suite, dim, budget)

    title = (
        f"# {suite.upper()}, D={dim}, B={budget_label(budget)} — "
        "MSC-CMA-ES vs NEA2+"
    )
    intro = [
        title,
        "",
        "This page combines the fixed-budget benchmark results and the two "
        "statistical analyses used for the related-method comparison with NEA2+.",
        "",
        f"- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B={budget:,} NFE.",
        "- **MWU:** NEA2+ vs MSC-CMA-ES, independent two-sided Mann–Whitney U "
        "with Bonferroni adjustment over the functions in this setting.",
        "- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and "
        "composition functions are analyzed separately.",
        "",
        "Contents: [Benchmark results](#benchmark-results) · "
        "[Mann–Whitney U](#mannwhitney-u) · "
        "[Deep Statistical Comparison](#deep-statistical-comparison)",
        "",
    ]
    return (
        "\n".join(intro)
        + render_benchmark(agg, suite, dim, budget)
        + "\n"
        + render_mwu(mwu, suite)
        + "\n"
        + render_dsc(ranks, orderings, suite)
    )


def render_index(
    comparison_root: Path,
    setting_pages: Mapping[tuple[str, int, int], str],
) -> str:
    # MWU setting summaries for compact index counts.
    mwu_summary = read_csv(comparison_root / "mwu" / "summary.csv")
    mwu_by_key = {
        (r["suite"], int(r["dimension"]), int(r["budget"])): r
        for r in mwu_summary
    }

    lines = [
        "# NEA2+ related-method comparison",
        "",
        "This supplementary comparison evaluates MSC-CMA-ES against **NEA2+** "
        "on the six suite–dimension–budget settings for which complete 51-run "
        "NEA2+ data are available.",
        "",
        f"NEA2+ reference: [Experimental Assessment of Multimodal Optimization "
        f"Algorithms]({PREUSS_URL}).",
        "",
        "Each setting page combines three views:",
        "",
        "1. **Benchmark results** — fixed-budget descriptive metrics for "
        "MSC-CMA-ES and NEA2+.",
        "2. **Mann–Whitney U** — function-wise NEA2+ vs MSC-CMA-ES tests on "
        "51 unmodified terminal errors with Bonferroni adjustment.",
        "3. **Deep Statistical Comparison** — MSC-CMA-ES, NEA2+, and "
        "BIPOP-CMA-ES, analyzed for all functions and for composition functions.",
        "",
        "CEC2020 D=20 is not included because a complete 51-run NEA2+ result "
        "set was not available.",
        "",
        "| Suite | D | Budget | Benchmark results | MWU | DSC | MWU summary "
        "(NEA2+ / MSC / NS) |",
        "|:--|--:|--:|:--|:--|:--|:--:|",
    ]

    total_functions = 0
    for suite, dim, budget in SETTINGS:
        rel = f"{suite}/d{dim}/budget_{budget}/README.md"
        m = mwu_by_key.get((suite, dim, budget))
        if m is None:
            raise BuildError(f"Missing MWU summary row for {suite} D={dim} B={budget}")
        n = int(m["n_functions"])
        total_functions += n
        counts = (
            f"{m['nea2plus_better']} / {m['msc_better']} / "
            f"{m['not_significant']}"
        )
        lines.append(
            f"| {suite.upper()} | {dim} | {budget_label(budget)} | "
            f"[Benchmark]({rel}#benchmark-results) | "
            f"[MWU]({rel}#mannwhitney-u) | "
            f"[DSC]({rel}#deep-statistical-comparison) | {counts} |"
        )

    lines += [
        "",
        f"Across the six complete settings there are **{total_functions} "
        f"functions**, i.e. **{total_functions * EXPECTED_RUNS} NEA2+ runs** "
        "and the corresponding MSC-CMA-ES runs.",
        "",
        "MWU and DSC use the stored run-wise terminal errors without clipping, "
        "rounding, sorting, or COCO-zero flooring. Descriptive benchmark metrics "
        "use the same display/aggregation convention as the main benchmark "
        "reports, including the `1e-8` zero rule.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    experiments = args.experiments.resolve()
    root = args.comparison_root.resolve()

    if not experiments.is_dir():
        raise BuildError(f"Experiment root does not exist: {experiments}")
    if not root.is_dir():
        raise BuildError(f"Comparison root does not exist: {root}")

    rendered: dict[tuple[str, int, int], str] = {}
    outputs: list[Path] = []

    for suite, dim, budget in SETTINGS:
        text = render_setting_page(experiments, root, suite, dim, budget)
        rendered[(suite, dim, budget)] = text
        outputs.append(setting_page_path(root, suite, dim, budget))

    index = render_index(root, rendered)
    outputs.append(root / "README.md")

    if args.check_only:
        print("CHECK PASSED")
        print(f"Validated {len(SETTINGS)} complete settings.")
        print(f"Would write {len(outputs)} README files:")
        for p in outputs:
            print(f"  {p}")
        return 0

    for key, text in rendered.items():
        suite, dim, budget = key
        path = setting_page_path(root, suite, dim, budget)
        atomic_write_text(path, text)

    atomic_write_text(root / "README.md", index)

    print(f"WROTE {len(outputs)} README files")
    for p in outputs:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
