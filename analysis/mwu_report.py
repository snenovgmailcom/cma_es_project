#!/usr/bin/env python3
"""Generate compact MWU/Holm reports from run-wise terminal errors.

For each suite/dimension/budget and each competitor versus the reference:

* load one terminal error per independent run from every ``f*.pkl`` file;
* run an independent, two-sided Mann--Whitney U test per function;
* apply Holm--Bonferroni across all functions in that cell, separately for
  every (budget, competitor) family;
* write one detailed CSV and one compact README per suite/dimension cell.

The four README tables (all/basic/hybrid/composition) contain counts in the
order ``competitor better / reference better / not significant``.  The three
class tables are filtered views of the all-functions analysis; Holm is not
recomputed within a class.
"""

from __future__ import annotations

import argparse
import csv
import pickle
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import stats


DEFAULT_ALGORITHMS = [
    "ARRDE",
    "BIPOP-CMA",
    "LSRTDE",
    "MSC-CMA",
    "NLSHADE-RSP",
    "j2020",
    "jSO",
]

DEFAULT_CELLS = [
    "cec2014/d10",
    "cec2014/d30",
    "cec2017/d10",
    "cec2017/d30",
    "cec2020/d5",
    "cec2020/d10",
    "cec2020/d15",
    "cec2020/d20",
    "cec2022/d10",
    "cec2022/d20",
]

FUNCTIONS = {
    "cec2014": list(range(1, 31)),
    "cec2017": [1] + list(range(3, 31)),  # f2 was withdrawn
    "cec2020": list(range(1, 11)),
    "cec2022": list(range(1, 13)),
}

CLASSES = {
    "cec2014": {
        "basic": set(range(1, 17)),
        "hybrid": set(range(17, 23)),
        "composition": set(range(23, 31)),
    },
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

CLASS_LABELS = {
    "all": "All functions",
    "basic": "Unimodal and simple multimodal functions",
    "hybrid": "Hybrid functions",
    "composition": "Composition functions",
}


@dataclass(frozen=True)
class Result:
    suite: str
    dimension: int
    budget: int
    function: int
    function_class: str
    algorithm: str
    reference: str
    n_algorithm: int
    n_reference: int
    u: float
    theta: float
    p_raw: float
    p_holm: float
    decision: str


def parse_cell(text: str) -> tuple[str, int]:
    match = re.fullmatch(r"(cec\d+)/d(\d+)", text.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError(
            f"invalid cell '{text}'; expected e.g. cec2017/d10"
        )
    suite, dimension = match.groups()
    if suite not in FUNCTIONS:
        raise argparse.ArgumentTypeError(f"unsupported suite '{suite}'")
    return suite, int(dimension)


def function_class(suite: str, function: int) -> str:
    for name in ("basic", "hybrid", "composition"):
        if function in CLASSES[suite][name]:
            return name
    raise ValueError(f"f{function} has no class mapping for {suite}")


def floor_errors(values, zero_tol: float) -> np.ndarray:
    errors = np.asarray(values, dtype=np.float64).copy()
    if errors.ndim != 1:
        raise ValueError(f"expected a one-dimensional errors vector, got {errors.shape}")
    if not np.all(np.isfinite(errors)):
        raise ValueError("terminal errors contain NaN or infinity")
    errors[np.abs(errors) <= zero_tol] = 0.0
    return errors


def load_errors(path: Path, expected_runs: int, zero_tol: float) -> np.ndarray:
    with path.open("rb") as stream:
        payload = pickle.load(stream)
    if not isinstance(payload, dict) or "errors" not in payload:
        raise ValueError(f"{path}: pickle has no 'errors' field")
    errors = floor_errors(payload["errors"], zero_tol)
    if expected_runs > 0 and len(errors) != expected_runs:
        raise ValueError(
            f"{path}: expected {expected_runs} terminal errors, found {len(errors)}"
        )
    return errors


def available_budgets(cell_dir: Path, algorithm: str) -> set[int]:
    alg_dir = cell_dir / algorithm
    if not alg_dir.is_dir():
        raise FileNotFoundError(f"missing algorithm directory: {alg_dir}")
    budgets = set()
    for path in alg_dir.glob("maxevals_*"):
        if path.is_dir() and all((path / f"f{function}.pkl").is_file() for function in FUNCTIONS[cell_dir.parent.name]):
            try:
                budgets.add(int(path.name.removeprefix("maxevals_")))
            except ValueError:
                pass
    if not budgets:
        raise FileNotFoundError(f"no maxevals_* directories under {alg_dir}")
    return budgets


def common_budgets(cell_dir: Path, algorithms: list[str]) -> list[int]:
    sets = [available_budgets(cell_dir, algorithm) for algorithm in algorithms]
    return sorted(set.intersection(*sets))


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm-adjusted p-values, returned in the original order."""
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda index: p_values[index])
    adjusted = [1.0] * m
    running_max = 0.0
    for position, index in enumerate(order):
        candidate = min(1.0, (m - position) * p_values[index])
        running_max = max(running_max, candidate)
        adjusted[index] = running_max
    return adjusted


def calculate_cell(
    experiments_dir: Path,
    suite: str,
    dimension: int,
    algorithms: list[str],
    reference: str,
    alpha: float,
    expected_runs: int,
    zero_tol: float,
) -> tuple[list[int], list[Result]]:
    cell_dir = experiments_dir / suite / f"d{dimension}"
    if not cell_dir.is_dir():
        raise FileNotFoundError(f"missing cell directory: {cell_dir}")

    budgets = common_budgets(cell_dir, algorithms)
    if not budgets:
        raise ValueError(f"no budget common to all algorithms in {cell_dir}")

    functions = FUNCTIONS[suite]
    competitors = [algorithm for algorithm in algorithms if algorithm != reference]
    output: list[Result] = []

    for budget in budgets:
        errors: dict[str, dict[int, np.ndarray]] = {}
        for algorithm in algorithms:
            budget_dir = cell_dir / algorithm / f"maxevals_{budget}"
            errors[algorithm] = {}
            for function in functions:
                path = budget_dir / f"f{function}.pkl"
                if not path.is_file():
                    raise FileNotFoundError(f"missing run data: {path}")
                errors[algorithm][function] = load_errors(
                    path, expected_runs, zero_tol
                )

        for algorithm in competitors:
            raw: list[tuple[int, float, float, float, int, int]] = []
            for function in functions:
                sample = errors[algorithm][function]
                control = errors[reference][function]
                test = stats.mannwhitneyu(
                    sample,
                    control,
                    alternative="two-sided",
                    method="asymptotic",
                    use_continuity=True,
                )
                u = float(test.statistic)
                p_raw = float(test.pvalue)
                n_algorithm = len(sample)
                n_reference = len(control)
                # SciPy's U for the first sample counts sample > control,
                # with ties contributing one half.  Errors are minimized, so
                # the probability that the competitor is better is 1-U/(nA*nR).
                theta = 1.0 - u / (n_algorithm * n_reference)
                raw.append(
                    (function, u, theta, p_raw, n_algorithm, n_reference)
                )

            adjusted = holm_adjust([row[3] for row in raw])
            for row, p_holm in zip(raw, adjusted):
                function, u, theta, p_raw, n_algorithm, n_reference = row
                if p_holm > alpha:
                    decision = "n.s."
                elif theta > 0.5:
                    decision = "competitor better"
                elif theta < 0.5:
                    decision = "reference better"
                else:
                    decision = "n.s."
                output.append(
                    Result(
                        suite=suite,
                        dimension=dimension,
                        budget=budget,
                        function=function,
                        function_class=function_class(suite, function),
                        algorithm=algorithm,
                        reference=reference,
                        n_algorithm=n_algorithm,
                        n_reference=n_reference,
                        u=u,
                        theta=theta,
                        p_raw=p_raw,
                        p_holm=p_holm,
                        decision=decision,
                    )
                )

    return budgets, output


def format_budget(value: int) -> str:
    if value >= 1_000_000 and value % 1_000_000 == 0:
        return f"{value // 1_000_000}M"
    if value >= 1_000 and value % 1_000 == 0:
        return f"{value // 1_000}K"
    return str(value)


def count_cell(rows: list[Result]) -> str:
    competitor = sum(row.decision == "competitor better" for row in rows)
    reference = sum(row.decision == "reference better" for row in rows)
    not_significant = sum(row.decision == "n.s." for row in rows)
    return f"{competitor} / {reference} / {not_significant}"


def render_summary_table(
    results: list[Result],
    budgets: list[int],
    competitors: list[str],
    scope: str,
) -> list[str]:
    scoped = results if scope == "all" else [
        row for row in results if row.function_class == scope
    ]
    n_functions = len({row.function for row in scoped})
    lines = [f"## {CLASS_LABELS[scope]} (n={n_functions})", ""]
    header = "| Algorithm | " + " | ".join(map(format_budget, budgets)) + " |"
    align = "|:--|" + "|".join("--:" for _ in budgets) + "|"
    lines.extend([header, align])
    for algorithm in competitors:
        cells = []
        for budget in budgets:
            selected = [
                row for row in scoped
                if row.algorithm == algorithm and row.budget == budget
            ]
            cells.append(count_cell(selected))
        lines.append(f"| {algorithm} | " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def write_details(path: Path, results: list[Result]) -> None:
    fields = [
        "suite",
        "dimension",
        "budget",
        "class",
        "function",
        "algorithm",
        "reference",
        "n_algorithm",
        "n_reference",
        "U",
        "theta_competitor_better",
        "p_raw",
        "p_holm",
        "decision",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in sorted(
            results,
            key=lambda item: (item.budget, item.algorithm, item.function),
        ):
            writer.writerow(
                {
                    "suite": row.suite,
                    "dimension": row.dimension,
                    "budget": row.budget,
                    "class": row.function_class,
                    "function": f"f{row.function}",
                    "algorithm": row.algorithm,
                    "reference": row.reference,
                    "n_algorithm": row.n_algorithm,
                    "n_reference": row.n_reference,
                    "U": f"{row.u:.1f}",
                    "theta_competitor_better": f"{row.theta:.12g}",
                    "p_raw": f"{row.p_raw:.12g}",
                    "p_holm": f"{row.p_holm:.12g}",
                    "decision": row.decision,
                }
            )


def write_readme(
    path: Path,
    suite: str,
    dimension: int,
    budgets: list[int],
    results: list[Result],
    competitors: list[str],
    reference: str,
    alpha: float,
    zero_tol: float,
) -> None:
    title_suite = suite.upper()
    lines = [
        f"# {title_suite} / D={dimension} — Mann–Whitney U tests on terminal errors",
        "",
        f"Reference algorithm: **{reference}**. Each comparison uses independent, "
        "two-sided Mann–Whitney U tests on the run-wise terminal errors. For each "
        "fixed budget and competitor, Holm–Bonferroni correction is applied across "
        f"all functions at family-wise level `{alpha:g}`. Values with absolute error "
        f"at most `{zero_tol:g}` are treated as zero.",
        "",
        "Every table entry is `competitor better / reference better / n.s.`. "
        "The class tables are filtered summaries of the all-functions analysis; "
        "the Holm correction is not recomputed within a class.",
        "",
        "Complete per-function statistics (`U`, effect size, raw p-value, "
        "Holm-adjusted p-value, and decision) are in [details.csv](details.csv).",
        "",
    ]
    for scope in ("all", "basic", "hybrid", "composition"):
        lines.extend(
            render_summary_table(results, budgets, competitors, scope)
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate compact MWU/Holm reports from terminal-error pickles."
    )
    parser.add_argument("--experiments-dir", type=Path, default=Path("experiments"))
    parser.add_argument("--output-dir", type=Path, default=Path("mwu"))
    parser.add_argument("--ref", default="MSC-CMA")
    parser.add_argument(
        "--algorithms",
        default=",".join(DEFAULT_ALGORITHMS),
        help="Comma-separated fixed algorithm set used to find common budgets.",
    )
    parser.add_argument(
        "--cells",
        default=",".join(DEFAULT_CELLS),
        help="Comma-separated suite/dimension cells, e.g. cec2017/d10.",
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--expected-runs", type=int, default=51)
    parser.add_argument("--zero-tol", type=float, default=1e-8)
    args = parser.parse_args()

    algorithms = [item.strip() for item in args.algorithms.split(",") if item.strip()]
    if args.ref not in algorithms:
        parser.error(f"reference '{args.ref}' is absent from --algorithms")
    if len(set(algorithms)) != len(algorithms):
        parser.error("--algorithms contains duplicates")
    cells = [parse_cell(item) for item in args.cells.split(",") if item.strip()]
    if not 0.0 < args.alpha < 1.0:
        parser.error("--alpha must be between 0 and 1")
    if args.expected_runs < 0:
        parser.error("--expected-runs must be non-negative")
    if args.zero_tol < 0.0:
        parser.error("--zero-tol must be non-negative")

    competitors = [algorithm for algorithm in algorithms if algorithm != args.ref]
    for suite, dimension in cells:
        budgets, results = calculate_cell(
            experiments_dir=args.experiments_dir,
            suite=suite,
            dimension=dimension,
            algorithms=algorithms,
            reference=args.ref,
            alpha=args.alpha,
            expected_runs=args.expected_runs,
            zero_tol=args.zero_tol,
        )
        destination = args.output_dir / suite / f"d{dimension}"
        destination.mkdir(parents=True, exist_ok=True)
        write_details(destination / "details.csv", results)
        write_readme(
            destination / "README.md",
            suite,
            dimension,
            budgets,
            results,
            competitors,
            args.ref,
            args.alpha,
            args.zero_tol,
        )
        print(
            f"{suite}/d{dimension}: {len(budgets)} budgets "
            f"({', '.join(map(format_budget, budgets))}) -> {destination}"
        )


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
