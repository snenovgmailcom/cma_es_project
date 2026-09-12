#!/usr/bin/env python3
"""Generate CMAES-NBC benchmark, MWU and DSC comparisons in the NEA2+ style.

Run from the project root:
    python analysis/build_cmaes_nbc_comparison_readmes.py

This single command validates all 546 input PKLs, computes MWU locally,
obtains DSC through the existing DSCTool runner, then writes 11 README files
under related_comparisons/cmaes_nbc. DSC_PASSWORD may be set in the environment;
otherwise the existing account's password is requested interactively.

--check-only validates inputs without writing files or contacting DSCTool.
--reuse-dsc recomputes MWU and rebuilds pages using validated saved DSC responses
whose requests and source hashes still match the current PKLs.

Requires the two accompanying run_*_cmaes_nbc.py scripts and the existing
summary_grid_clean.py, report_style.py and run_iohanalyzer_dsc.py modules.
Reads trusted project PKLs. Experiment data and existing report generators
are never modified. Benchmark definitions and presentation reuse the same
helpers as the current NEA2+ README generator.
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

# Allow "python analysis/build_cmaes_nbc_comparison_readmes.py" from repo root.
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
COMPETITOR = "CMAES-NBC"
DSC_ALGORITHMS = ("MSC-CMA", "CMAES-NBC", "BIPOP-CMA")
EXPECTED_RUNS = 51
ALPHA = 0.05

SETTINGS = (
    ("cec2014", 10,   100_000), ("cec2014", 30,    300_000),
    ("cec2017", 10,   100_000), ("cec2017", 30,    300_000),
    ("cec2020",  5,    50_000), ("cec2020", 10,  1_000_000),
    ("cec2020", 15, 3_000_000), ("cec2020", 20, 10_000_000),
    ("cec2022", 10,   200_000), ("cec2022", 20,  1_000_000),
)

FUNCTIONS = {
    "cec2014": tuple(range(1, 31)),
    "cec2017": (1, *range(3, 31)),
    "cec2020": tuple(range(1, 11)),
    "cec2022": tuple(range(1, 13)),
}

METRICS = ("mean", "median", "best", "worst", "std", "fbtc")
LOWER_BETTER = {"mean", "median", "best", "worst", "std"}
HIGHER_BETTER = {"fbtc"}

REFERENCE_URL = "https://doi.org/10.1016/j.asoc.2024.112361"
TERMINAL_NOTE = (
    "Here B is the configured evaluation budget. The CMAES-NBC CSV bridge "
    "stores the author's best-ever objective error at algorithm termination "
    "(`params.errors_at_exact_budget=False`). Its target coverage is computed "
    "from these stored terminal errors; exact-budget trajectories are unavailable. "
    "Thus the CMAES-NBC coverage column summarizes termination results for runs "
    "configured with B, and does not establish first-hitting-time performance."
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
        default=Path("related_comparisons/cmaes_nbc"),
        help="CMAES-NBC comparison root (default: related_comparisons/cmaes_nbc)",
    )
    p.add_argument(
        "--reuse-dsc", action="store_true",
        help="reuse saved DSC responses after verifying requests, PKL hashes and results",
    )
    p.add_argument(
        "--check-only", action="store_true",
        help="validate all PKLs (and cached DSC with --reuse-dsc), without writing or network",
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
        f"Terminal results for configured budget **B={format_budget(budget)} NFE**, using 51 runs per "
        "function for MSC-CMA-ES and CMAES-NBC.",
        "",
        TERMINAL_NOTE,
        "",
        "The descriptive metrics use the same definitions as the main benchmark "
        "reports. Errors with absolute value at most `1e-8` are treated as zero for the descriptive benchmark metrics; "
        "the standard deviation is the sample standard deviation (`ddof=1`). "
        "The FBTC(B) column uses the same 51 log-uniform "
        "targets in `[10², 10⁻⁸]`, evaluated on the stored terminal errors. "
        "Class and All values are sums over functions.",
        "",
        "| Category | Metric | MSC-CMA-ES | CMAES-NBC |",
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
            rank_a = float(r["mean_rank_competitor"])
            rank_m = float(r["mean_rank_msc"])
            probability = float(r["probability_competitor_lower"])
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
            "u_competitor", "p_raw", "probability_competitor_lower",
            "mean_rank_competitor", "mean_rank_msc", "median_competitor", "median_msc",
        ):
            if float(r[field]) != float(other[field]):
                raise BuildError(f"MWU scopes have different {field} for f{r['function']}")
    return sorted(selected, key=lambda r: (r["comparison_scope"] != "all", int(r["function"])))


def mwu_legend() -> list[str]:
    return [
        r"Let $\bar R_M$ and $\bar R_A$ denote the mean ranks of the MSC-CMA-ES "
        "and CMAES-NBC samples in their pooled sample, with ranks increasing with "
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
        "and CMAES-NBC samples on each function. Each sample contains 51 stored "
        "run-wise terminal errors, without additional rounding or zero flooring; "
        "stored zeros are retained. SciPy's asymptotic "
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
        "The `probability_competitor_lower` column is the empirical estimate of "
        r"$P(X_A<X_M)+\frac12P(X_A=X_M)$, computed as "
        r"$1-U_A/(n_A n_M)$.",
        "",
        "| Function | $U_A$ (CMAES-NBC) | $\\bar R_M$ | $\\bar R_A$ | "
        "P(CMAES-NBC lower) | $p_{\\mathrm{raw}}$ |",
        "|:--|--:|--:|--:|--:|--:|",
    ]
    for r in scoped["all"]:
        lines.append(
            f"| f{int(r['function'])} | {fmt_number(float(r['u_competitor']))} | "
            f"{fmt_number(float(r['mean_rank_msc']))} | "
            f"{fmt_number(float(r['mean_rank_competitor']))} | "
            f"{fmt_number(float(r['probability_competitor_lower']))} | "
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
        "DSC compares **MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES** using the "
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
        "| Function | MSC-CMA-ES | CMAES-NBC | BIPOP-CMA-ES |",
        "|:--|--:|--:|--:|",
    ]

    for fid in expected_functions(suite):
        vals = [
            lookup[(fid, "MSC-CMA")],
            lookup[(fid, "CMAES-NBC")],
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
        "| Scope | n | Lowest-mean-rank algorithm | MSC mean rank | CMAES-NBC mean rank | "
        "BIPOP-CMA-ES mean rank | Friedman p | Post-hoc control | p_Holm(MSC) | "
        "p_Holm(CMAES-NBC) | Result |",
        "|:--|--:|:--|--:|--:|--:|--:|:--|--:|--:|:--:|",
    ]

    for scope in ("all", "composition"):
        rows = orderings[scope]
        by_alg = {r["algorithm"]: r for r in rows}
        ordered = sorted(rows, key=lambda r: float(r["position_average"]))
        best = ordered[0]["algorithm"]
        control = by_alg["MSC-CMA"]["posthoc_control"] or "—"
        p_msc = by_alg["MSC-CMA"]["posthoc_holm_p"]
        p_competitor = by_alg["CMAES-NBC"]["posthoc_holm_p"]
        status = by_alg["MSC-CMA"]["dsc_status"]
        n = int(by_alg["MSC-CMA"]["n_functions"])
        lines.append(
            f"| {class_label(scope)} | {n} | {display_name(best)} | "
            f"{fmt_number(float(by_alg['MSC-CMA']['mean_dsc_rank']))} | "
            f"{fmt_number(float(by_alg['CMAES-NBC']['mean_dsc_rank']))} | "
            f"{fmt_number(float(by_alg['BIPOP-CMA']['mean_dsc_rank']))} | "
            f"{fmt_p(by_alg['MSC-CMA']['omnibus_p_value'])} | "
            f"{display_name(control)} | {fmt_p(p_msc)} | "
            f"{fmt_p(p_competitor)} | **{status}** |"
        )

    lines += [
        "",
        "Complete DSCTool request/response files and exact orderings are stored under "
        "`related_comparisons/cmaes_nbc/dsc/`.",
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
    mwu = load_mwu_rows(comparison_root, suite, dim, budget)
    metric_grid = validate_metric_grid(experiments, suite, dim, budget)
    agg = aggregate_benchmark(metric_grid, suite)
    ranks, orderings = load_dsc(comparison_root, suite, dim, budget)
    benchmark_text = render_benchmark(agg, suite, dim, budget) + "\n"
    dsc_text = render_dsc(ranks, orderings, suite)

    title = (
        f"# {suite.upper()}, D={dim}, B={budget_label(budget)} — "
        "MSC-CMA-ES vs CMAES-NBC"
    )
    intro = [
        title,
        "",
        "This page combines the terminal benchmark results and the two "
        "statistical analyses used for the related-method comparison with CMAES-NBC.",
        "",
        f"- **Benchmark:** MSC-CMA-ES vs CMAES-NBC, 51 runs per function with configured B={format_budget(budget)} NFE.",
        "- **MWU:** independent two-sided Mann–Whitney U tests with "
        "Holm–Bonferroni adjustment, separately for all functions and for "
        "composition functions; symbols are stated from the MSC-CMA-ES perspective.",
        "- **DSC:** MSC-CMA-ES, CMAES-NBC, and BIPOP-CMA-ES; all functions and "
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
        raise BuildError("MWU summary must have exactly the ten settings and both scopes")
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
        raise BuildError("All ten setting pages are required for the comparison index")
    mwu_by_key = validated_mwu_summary(comparison_root)
    lines = [
        "# CMAES-NBC related-method comparison",
        "",
        "This supplementary comparison evaluates MSC-CMA-ES against **CMAES-NBC** "
        "on the ten suite–dimension–budget settings for which complete 51-run "
        "CMAES-NBC data are available.",
        "",
        "CMAES-NBC reference: [Adapting the population size in CMA-ES using "
        "nearest-better clustering method for multimodal optimization]"
        f"({REFERENCE_URL}). This comparison uses the locally executed non-qN "
        "algorithm, with the author-provided corrections: restart means in "
        "[-80, 80] and a 20-iteration maximum-population window.",
        "",
        TERMINAL_NOTE,
        "",
        "Each setting page combines three views:",
        "",
        "1. **Benchmark results** — terminal descriptive metrics at each configured budget for "
        "MSC-CMA-ES and CMAES-NBC.",
        "2. **Mann–Whitney U** — independent, two-sided tests on "
        "51 stored terminal errors per sample, with Holm–Bonferroni adjustment "
        "applied separately to all functions and to composition functions "
        "within each setting.",
        "3. **Deep Statistical Comparison** — MSC-CMA-ES, CMAES-NBC, and "
        "BIPOP-CMA-ES, analyzed for all functions and for composition functions.",
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
        f"Across the ten complete settings there are **{total_functions['all']} "
        "function–setting comparisons**, including "
        f"**{total_functions['composition']} composition-function comparisons**. "
        f"They use **{total_functions['all'] * EXPECTED_RUNS} runs per algorithm**; "
        "the composition analysis reuses the corresponding samples.",
        "",
        "MWU and DSC use the stored run-wise terminal errors without additional "
        "rounding or zero flooring; stored zeros are retained. "
        "Descriptive benchmark metrics use the same display/aggregation convention "
        "as the main benchmark reports, including the `1e-8` zero rule.",
        "",
        "Full-precision results: [MWU details](mwu/details.csv) and "
        "[MWU summaries](mwu/summary.csv).",
        "",
        "## Reproduction",
        "",
        "Run from the repository root:",
        "",
        "```bash",
        "python analysis/build_cmaes_nbc_comparison_readmes.py",
        "```",
        "",
        "This computes MWU, obtains DSC through DSCTool and regenerates all pages. "
        "Use `--reuse-dsc` to regenerate locally from saved DSC responses after "
        "checking that their requests and source hashes match the current PKLs. "
        "The scripts read terminal errors and do not rerun optimization experiments.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    experiments = args.experiments.expanduser().resolve()
    root = args.comparison_root.expanduser().resolve()
    if not experiments.is_dir():
        raise BuildError(f"Experiment root does not exist: {experiments}")

    import run_mwu_cmaes_nbc as mwu
    import run_dsc_cmaes_nbc as dsc

    if tuple(mwu.SETTINGS) != SETTINGS or tuple(
        (s.suite, s.dimension, s.budget) for s in dsc.SETTINGS
    ) != SETTINGS:
        raise BuildError("MWU, DSC and README settings disagree")

    # Validate all three algorithms before creating outputs or contacting DSCTool.
    dsc.validate_inputs(experiments)
    for suite, dim, budget in SETTINGS:
        validate_metric_grid(experiments, suite, dim, budget)
    if args.reuse_dsc:
        dsc.validate_cached_outputs(experiments, root / "dsc")
    if args.check_only:
        print("CHECK PASSED: 10 settings, 182 functions, 546 PKLs, 51 runs per PKL.")
        print("No files written and no DSCTool requests sent.")
        return 0

    mwu.main(["--experiments", str(experiments), "--output-dir", str(root / "mwu")])
    if not args.reuse_dsc:
        code = dsc.main(["--experiments", str(experiments), "--output", str(root / "dsc")])
        if code:
            raise BuildError(f"DSC runner exited with status {code}")

    rendered = {
        (suite, dim, budget): render_setting_page(experiments, root, suite, dim, budget)
        for suite, dim, budget in SETTINGS
    }
    index = render_index(root, rendered)
    for (suite, dim, budget), text in rendered.items():
        atomic_write_text(setting_page_path(root, suite, dim, budget), text)
    atomic_write_text(root / "README.md", index)
    print(f"WROTE {len(rendered) + 1} README files under {root}")
    print("MWU: 238 scoped comparisons and 20 family summaries.")
    print("DSC: 546 function ranks and 60 ordering rows.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
