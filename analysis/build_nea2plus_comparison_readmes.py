#!/usr/bin/env python3
"""
Build the NEA2+ related-comparison README pages.

Inputs (already produced locally):
  experiments/.../MSC-CMA/maxevals_<B>/f*.pkl
  experiments/.../NEA2PLUS-PY/maxevals_<B>/f*.pkl
  related_comparisons/nea2plus/mwu/details.csv
  related_comparisons/nea2plus/mwu/summary.csv (all/composition scope rows)
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
With --reuse-benchmark-and-dsc, existing benchmark and DSC sections are
preserved exactly; only the MWU text, introduction, and root index are rebuilt.
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

from report_style import (
    DESCRIPTIVE_BOLD_NOTE,
    class_label,
    display_name,
    format_budget,
    format_p as style_format_p,
    format_value,
    metric_label,
)


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
        "--reuse-benchmark-and-dsc",
        action="store_true",
        help="preserve existing benchmark and DSC README sections; rebuild only MWU and navigation",
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
    return format_budget(b)


def fmt_number(x: float, digits: int = 6) -> str:
    if not math.isfinite(x):
        return "—"
    return format_value(float(x), sig=digits)


def fmt_p(x: str | float | None) -> str:
    if x is None or x == "":
        return "—"
    return style_format_p(float(x))


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
        f"Fixed-budget terminal results at **B={format_budget(budget)} NFE**, using 51 runs per "
        "function for MSC-CMA-ES and NEA2+.",
        "",
        "The descriptive metrics use the same definitions as the main benchmark "
        "reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; "
        "the standard deviation is the sample standard deviation (`ddof=1`). "
        "FBTC(B) is the Fixed-Budget Target Coverage over the same 51 log-uniform "
        "targets in `[10², 10⁻⁸]`. Class and All values are sums over functions.",
        "",
        "| Category | Metric | MSC-CMA-ES | NEA2+ |",
        "|:--|:--|--:|--:|",
    ]

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
                f"**{class_label(cls)}** (n={len(fids)})" if first else ""
            )
            lines.append(
                f"| {category} | {metric_label(metric)} | {sa} | {sb} |"
            )
            first = False

    lines += [
        "",
        f"*{DESCRIPTIVE_BOLD_NOTE}*",
        "",
    ]
    return "\n".join(lines)


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    """Step-down adjusted p-values, in the original function order."""
    order = sorted(range(len(p_values)), key=p_values.__getitem__)
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for index, position in enumerate(order):
        running = max(running, (len(p_values) - index) * p_values[position])
        adjusted[position] = min(1.0, running)
    return adjusted


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)


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
    if {r["comparison_scope"] for r in selected} != {"all", "composition"}:
        raise BuildError(f"MWU {suite} D={dim} B={budget}: both scopes are required")

    for scope in ("all", "composition"):
        scoped = [r for r in selected if r["comparison_scope"] == scope]
        expected = set(class_functions(suite, scope))
        found = {int(r["function"]) for r in scoped}
        if found != expected or len(scoped) != len(expected):
            raise BuildError(
                f"MWU {suite} D={dim} B={budget}/{scope}: "
                f"expected {len(expected)} rows, got {len(scoped)} "
                f"with functions {sorted(found)}"
            )
        adjusted = holm_adjust([float(r["p_raw"]) for r in scoped])
        for r, expected_p in zip(scoped, adjusted):
            if r["competitor"] != COMPETITOR or r["reference"] != REFERENCE:
                raise BuildError(f"Unexpected MWU algorithms in row: {r}")
            if int(r["n_competitor"]) != EXPECTED_RUNS or int(r["n_reference"]) != EXPECTED_RUNS:
                raise BuildError(f"Unexpected MWU sample size in row: {r}")
            if int(r["test_family_size"]) != len(expected):
                raise BuildError(f"Unexpected MWU family size in row: {r}")
            if r["correction"] != "holm-bonferroni" or float(r["alpha"]) != ALPHA:
                raise BuildError(f"Unexpected MWU correction or alpha in row: {r}")
            fid = int(r["function"])
            expected_class = next(
                cls for cls in ("basic", "hybrid", "composition")
                if fid in class_functions(suite, cls)
            )
            if r["function_class"] != expected_class:
                raise BuildError(f"Unexpected MWU function class in row: {r}")
            raw_p, p_holm = float(r["p_raw"]), float(r["p_holm"])
            if not (0 <= raw_p <= 1 and 0 <= p_holm <= 1 and close(p_holm, expected_p)):
                raise BuildError(f"Invalid Holm-adjusted p-value in row: {r}")
            u_a = float(r["u_competitor"])
            n_a, n_m = int(r["n_competitor"]), int(r["n_reference"])
            rank_a = float(r["mean_rank_nea2plus"])
            rank_m = float(r["mean_rank_msc"])
            probability = float(r["probability_nea2plus_lower"])
            if not (
                0 <= u_a <= n_a * n_m
                and close(rank_a, u_a / n_a + (n_a + 1) / 2)
                and close(rank_m, (n_a * n_m - u_a) / n_m + (n_m + 1) / 2)
                and close(probability, 1 - u_a / (n_a * n_m))
            ):
                raise BuildError(f"Inconsistent U, pooled mean ranks, or probability in row: {r}")
            if p_holm > ALPHA:
                expected_symbol = "="
            elif rank_m < rank_a:
                expected_symbol = "<"
            elif rank_m > rank_a:
                expected_symbol = ">"
            else:
                raise BuildError(f"Rejected MWU null with equal pooled mean ranks in row: {r}")
            if r["mwu_symbol"] != expected_symbol:
                raise BuildError(f"Inconsistent MSC-oriented MWU symbol in row: {r}")

    # The same function samples have identical unadjusted statistics in both scopes.
    all_rows = {r["function"]: r for r in selected if r["comparison_scope"] == "all"}
    for r in selected:
        if r["comparison_scope"] != "composition":
            continue
        other = all_rows[r["function"]]
        for field in (
            "u_competitor", "p_raw", "probability_nea2plus_lower",
            "mean_rank_nea2plus", "mean_rank_msc", "median_nea2plus", "median_msc",
        ):
            if float(r[field]) != float(other[field]):
                raise BuildError(f"MWU scopes have different {field} for f{r['function']}")
    return sorted(selected, key=lambda r: (r["comparison_scope"] != "all", int(r["function"])))


def mwu_legend() -> list[str]:
    return [
        r"Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES "
        "and NEA2+ samples in their pooled sample, with ranks increasing with "
        "terminal error and average ranks assigned to ties.",
        "",
        r"- `<`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M<\bar R_A$.",
        r"- `>`: $p_{\mathrm{Holm}}\leq0.05$ and $\bar R_M>\bar R_A$.",
        r"- `=`: $p_{\mathrm{Holm}}>0.05$; the null hypothesis "
        r"$H_0:F_M=F_A$ is not rejected.",
        "",
        "The `=` symbol denotes non-rejection; it does not assert equality of "
        "the sample mean ranks or distributions. "
        r"Counts are reported as $n_{<}/n_{>}/n_{=}$ from the MSC-CMA-ES perspective.",
        "",
    ]


def render_mwu(rows: list[dict[str, str]], suite: str) -> str:
    scoped = {
        scope: [r for r in rows if r["comparison_scope"] == scope]
        for scope in ("all", "composition")
    }
    lines = [
        '<a id="mannwhitney-u"></a>',
        "",
        "## Mann–Whitney U",
        "",
        "Independent, two-sided Mann–Whitney U tests compare the MSC-CMA-ES "
        "and NEA2+ samples on each function. Each sample contains 51 stored "
        "run-wise terminal errors, without additional rounding or zero flooring; "
        "zeros returned by the algorithms are retained. SciPy's asymptotic "
        'method (`method="asymptotic"`) with continuity correction '
        "(`use_continuity=True`) is used.",
        "",
        "Holm–Bonferroni adjustment is applied separately within this setting "
        f"to **all {len(scoped['all'])} functions** and to the "
        f"**{len(scoped['composition'])} composition functions**. "
        "These are two independently adjusted families of hypotheses.",
        "",
        *mwu_legend(),
        "| Scope | Family size | $n_{<}$ | $n_{>}$ | $n_{=}$ |",
        "|:--|--:|--:|--:|--:|",
    ]
    for scope, scope_rows in scoped.items():
        counts = Counter(r["mwu_symbol"] for r in scope_rows)
        lines.append(
            f"| {class_label(scope)} | {len(scope_rows)} | "
            f"{counts['<']} | {counts['>']} | {counts['=']} |"
        )

    for scope, scope_rows in scoped.items():
        lines += [
            "",
            f"### {class_label(scope)} functions: Holm-adjusted comparisons",
            "",
            "| Function | Class | $p_{\\mathrm{Holm}}$ | Symbol |",
            "|:--|:--|--:|:--:|",
        ]
        for r in scope_rows:
            rejected = float(r["p_holm"]) <= ALPHA
            p_text = markdown_bold(fmt_p(r["p_holm"]), rejected)
            symbol = markdown_bold(f"`{r['mwu_symbol']}`", rejected)
            lines.append(
                f"| f{int(r['function'])} | {class_label(r['function_class'])} | "
                f"{p_text} | {symbol} |"
            )

    lines += [
        "",
        "Bold entries indicate rejection of the null hypothesis at the "
        "specified Holm-adjusted threshold.",
        "",
        "<details>",
        "<summary>Unadjusted statistics and pooled-sample mean ranks</summary>",
        "",
        "These statistics are shared by both scopes for a given function. "
        "The `probability_nea2plus_lower` column is the empirical estimate of "
        r"$P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as "
        r"$1-U_A/(n_A n_M)$.",
        "",
        "| Function | $U_A$ (NEA2+) | $\\bar R_M$ | $\\bar R_A$ | "
        "P(NEA2+ lower) | $p_{\\mathrm{raw}}$ |",
        "|:--|--:|--:|--:|--:|--:|",
    ]
    for r in scoped["all"]:
        lines.append(
            f"| f{int(r['function'])} | {fmt_number(float(r['u_competitor']))} | "
            f"{fmt_number(float(r['mean_rank_msc']))} | "
            f"{fmt_number(float(r['mean_rank_nea2plus']))} | "
            f"{fmt_number(float(r['probability_nea2plus_lower']))} | "
            f"{fmt_p(r['p_raw'])} |"
        )
    lines += [
        "",
        "</details>",
        "",
        "Full-precision MWU statistics for both scopes are available in "
        "[`mwu/details.csv`](../../../mwu/details.csv).",
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
        "with the lowest mean DSC rank.",
        "",
        "`★` means MSC-CMA-ES has the lowest mean DSC rank and the Friedman "
        "test rejects the null hypothesis; `≈` means the Friedman test rejects "
        "the null hypothesis but the Holm-adjusted comparison between MSC-CMA-ES "
        "and the lowest-mean-rank algorithm is not significant; `↓` means the "
        "lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES "
        "and the Holm-adjusted comparison is significant; `O` means the Friedman "
        "test does not reject the null hypothesis and no post-hoc interpretation "
        "is made.",
        "",
        "### DSC ranks by function",
        "",
        "DSC ranks are ordered from 1 upward; tied distributions receive "
        "fractional ranks. Smaller numerical ranks are lower in this ordering.",
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
        "| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | NEA2+ mean rank | "
        "BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | "
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
            f"| {class_label(scope)} | {n} | {display_name(best)} | "
            f"{fmt_number(float(by_alg['MSC-CMA']['mean_dsc_rank']))} | "
            f"{fmt_number(float(by_alg['NEA2PLUS-PY']['mean_dsc_rank']))} | "
            f"{fmt_number(float(by_alg['BIPOP-CMA']['mean_dsc_rank']))} | "
            f"{fmt_p(by_alg['MSC-CMA']['omnibus_p_value'])} | "
            f"{display_name(control)} | {fmt_p(p_msc)} | "
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


def existing_benchmark_and_dsc(path: Path) -> tuple[str, str]:
    """Return exact existing sections; do not infer missing experimental data."""
    if not path.is_file():
        raise BuildError(f"Missing existing setting README for reuse: {path}")
    text = path.read_bytes().decode("utf-8")
    markers = (
        "## Benchmark results",
        '<a id="mannwhitney-u"></a>',
        '<a id="deep-statistical-comparison"></a>',
    )
    if any(text.count(marker) != 1 for marker in markers):
        raise BuildError(f"Missing or repeated benchmark/MWU/DSC section marker: {path}")
    benchmark_start, mwu_start, dsc_start = (text.index(marker) for marker in markers)
    if not benchmark_start < mwu_start < dsc_start:
        raise BuildError(f"Unexpected benchmark/MWU/DSC section order: {path}")
    return text[benchmark_start:mwu_start], text[dsc_start:]


def render_setting_page(
    experiments: Path,
    comparison_root: Path,
    suite: str,
    dim: int,
    budget: int,
    reuse_benchmark_and_dsc: bool = False,
) -> str:
    mwu = load_mwu_rows(comparison_root, suite, dim, budget)
    if reuse_benchmark_and_dsc:
        benchmark_text, dsc_text = existing_benchmark_and_dsc(
            setting_page_path(comparison_root, suite, dim, budget)
        )
    else:
        metric_grid = validate_metric_grid(experiments, suite, dim, budget)
        agg = aggregate_benchmark(metric_grid, suite)
        ranks, orderings = load_dsc(comparison_root, suite, dim, budget)
        benchmark_text = render_benchmark(agg, suite, dim, budget) + "\n"
        dsc_text = render_dsc(ranks, orderings, suite)

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
        f"- **Benchmark:** MSC-CMA-ES vs NEA2+, 51 runs per function at B={format_budget(budget)} NFE.",
        "- **MWU:** independent two-sided Mann–Whitney U tests with "
        "Holm–Bonferroni adjustment, separately for all functions and for "
        "composition functions; symbols are stated from the MSC-CMA-ES perspective.",
        "- **DSC:** MSC-CMA-ES, NEA2+, and BIPOP-CMA-ES; all functions and "
        "composition functions are analyzed separately.",
        "",
        "Contents: [Benchmark results](#benchmark-results) · "
        "[Mann–Whitney U](#mannwhitney-u) · "
        "[Deep Statistical Comparison](#deep-statistical-comparison)",
        "",
    ]
    return "\n".join(intro) + benchmark_text + render_mwu(mwu, suite) + "\n" + dsc_text


def validated_mwu_summary(comparison_root: Path) -> dict[tuple[str, int, int, str], dict[str, str]]:
    rows = read_csv(comparison_root / "mwu" / "summary.csv")
    expected = {(*setting, scope) for setting in SETTINGS for scope in ("all", "composition")}
    by_key = {
        (r["suite"], int(r["dimension"]), int(r["budget"]), r["comparison_scope"]): r
        for r in rows
    }
    if len(rows) != len(expected) or set(by_key) != expected:
        raise BuildError("MWU summary must have exactly the six settings and both scopes")
    for suite, dim, budget in SETTINGS:
        details = load_mwu_rows(comparison_root, suite, dim, budget)
        for scope in ("all", "composition"):
            detail_rows = [r for r in details if r["comparison_scope"] == scope]
            counts = Counter(r["mwu_symbol"] for r in detail_rows)
            row = by_key[(suite, dim, budget, scope)]
            if (
                int(row["n_functions"]) != len(detail_rows)
                or int(row["n_lt"]) != counts["<"]
                or int(row["n_gt"]) != counts[">"]
                or int(row["n_eq"]) != counts["="]
            ):
                raise BuildError(f"MWU summary disagrees with details: {suite} D={dim} B={budget}/{scope}")
    return by_key


def render_index(
    comparison_root: Path,
    setting_pages: Mapping[tuple[str, int, int], str],
) -> str:
    if set(setting_pages) != set(SETTINGS):
        raise BuildError("All six setting pages are required for the comparison index")
    mwu_by_key = validated_mwu_summary(comparison_root)
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
        "2. **Mann–Whitney U** — independent, two-sided tests on "
        "51 stored terminal errors per sample, with Holm–Bonferroni adjustment "
        "applied separately to all functions and to composition functions "
        "within each setting.",
        "3. **Deep Statistical Comparison** — MSC-CMA-ES, NEA2+, and "
        "BIPOP-CMA-ES, analyzed for all functions and for composition functions.",
        "",
        "CEC2020 D=20 is not included because a complete 51-run NEA2+ result "
        "set was not available.",
        "",
        "## MWU symbols",
        "",
        *mwu_legend(),
        "## Settings",
        "",
        "The two MWU count columns use independently adjusted families. "
        "The composition column is not a subset of decisions adjusted over all functions.",
        "",
        "| Suite | D | Budget | Benchmark results | MWU | DSC | "
        "All: $n_{<}/n_{>}/n_{=}$ | Composition: $n_{<}/n_{>}/n_{=}$ |",
        "|:--|--:|--:|:--|:--|:--|:--:|:--:|",
    ]
    totals = {scope: Counter() for scope in ("all", "composition")}
    total_functions = {scope: 0 for scope in totals}
    for suite, dim, budget in SETTINGS:
        rel = f"{suite}/d{dim}/budget_{budget}/README.md"
        cells = []
        for scope in ("all", "composition"):
            row = mwu_by_key[(suite, dim, budget, scope)]
            total_functions[scope] += int(row["n_functions"])
            totals[scope].update({field: int(row[field]) for field in ("n_lt", "n_gt", "n_eq")})
            cells.append(f"{row['n_lt']} / {row['n_gt']} / {row['n_eq']}")
        lines.append(
            f"| {suite.upper()} | {dim} | {budget_label(budget)} | "
            f"[Benchmark]({rel}#benchmark-results) | "
            f"[MWU]({rel}#mannwhitney-u) | "
            f"[DSC]({rel}#deep-statistical-comparison) | {cells[0]} | {cells[1]} |"
        )
    count_totals = [
        " / ".join(str(totals[scope][field]) for field in ("n_lt", "n_gt", "n_eq"))
        for scope in ("all", "composition")
    ]
    lines += [
        f"| **Total** | | | | | | **{count_totals[0]}** | **{count_totals[1]}** |",
        "",
        f"Across the six complete settings there are **{total_functions['all']} "
        "function–setting comparisons**, including "
        f"**{total_functions['composition']} composition-function comparisons**. "
        f"They use **{total_functions['all'] * EXPECTED_RUNS} runs per algorithm**; "
        "the composition analysis reuses the corresponding samples.",
        "",
        "MWU and DSC use the stored run-wise terminal errors without additional "
        "rounding or zero flooring; zeros returned by the algorithms are retained. "
        "Descriptive benchmark metrics use the same display/aggregation convention "
        "as the main benchmark reports, including the `1e-8` zero rule.",
        "",
        "Full-precision results: [MWU details](mwu/details.csv) and "
        "[MWU summaries](mwu/summary.csv).",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    experiments = args.experiments.resolve()
    root = args.comparison_root.resolve()

    if not args.reuse_benchmark_and_dsc and not experiments.is_dir():
        raise BuildError(f"Experiment root does not exist: {experiments}")
    if not root.is_dir():
        raise BuildError(f"Comparison root does not exist: {root}")

    rendered: dict[tuple[str, int, int], str] = {}
    outputs: list[Path] = []

    for suite, dim, budget in SETTINGS:
        text = render_setting_page(
            experiments, root, suite, dim, budget,
            reuse_benchmark_and_dsc=args.reuse_benchmark_and_dsc,
        )
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
