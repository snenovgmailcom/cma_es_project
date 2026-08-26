#!/usr/bin/env python3
"""Generate per-cell MWU and DSC supplementary-material READMEs.

The script reads ``pkl['errors']`` exactly as stored.  It does not round,
clip, floor, sort, or otherwise transform the 51 run-wise terminal errors.

For every suite--dimension--budget setting, each competitor is compared with
MSC-CMA independently on every function using a two-sided Mann--Whitney U
test.  Bonferroni correction is applied across all functions separately for
each (setting, competitor) family.

Only these files are created/replaced under --output:

* <suite>/d<dimension>/details.csv
* <suite>/d<dimension>/README.md
* mann_whitney_u_all_settings.csv

No existing directory is deleted and no unrelated file is modified.

The Deep Statistical Comparison section is rendered from an existing,
already-computed DSCTool result tree supplied through ``--dsc-results``.
This script does not recompute or alter any DSC statistic.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import pickle
import re
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import stats

from report_style import (
    ARROW_HIGHER,
    ARROW_LOWER,
    ARROW_NS,
    display_name,
    format_budget,
    format_p,
)


REFERENCE = "MSC-CMA"
EXPECTED_RUNS = 51
ALPHA = 0.05

BASE_ALGORITHMS = (
    "ARRDE",
    "BIPOP-CMA",
    "LSRTDE",
    "MSC-CMA",
    "NLSHADE-RSP",
    "j2020",
    "jSO",
)

DSC_TABLE_ORDER = (
    "MSC-CMA",
    "BIPOP-CMA",
    "ARRDE",
    "LSRTDE",
    "NLSHADE-RSP",
    "j2020",
    "jSO",
)


@dataclass(frozen=True)
class Setting:
    suite: str
    dimension: int
    budget: int

    @property
    def algorithms(self) -> tuple[str, ...]:
        return BASE_ALGORITHMS


SETTINGS = (
    Setting("cec2014", 10, 100_000),
    Setting("cec2014", 10, 1_000_000),
    Setting("cec2014", 30, 300_000),
    Setting("cec2014", 30, 1_000_000),
    Setting("cec2017", 10, 100_000),
    Setting("cec2017", 10, 1_000_000),
    Setting("cec2017", 30, 300_000),
    Setting("cec2017", 30, 1_000_000),
    Setting("cec2020", 5, 50_000),
    Setting("cec2020", 5, 1_000_000),
    Setting("cec2020", 10, 1_000_000),
    Setting("cec2020", 10, 20_000_000),
    Setting("cec2020", 15, 3_000_000),
    Setting("cec2020", 20, 10_000_000),
    Setting("cec2022", 10, 200_000),
    Setting("cec2022", 10, 1_000_000),
    Setting("cec2022", 20, 1_000_000),
)

FUNCTIONS = {
    "cec2014": tuple(range(1, 31)),
    "cec2017": (1, *range(3, 31)),  # CEC2017 f2 is excluded.
    "cec2020": tuple(range(1, 11)),
    "cec2022": tuple(range(1, 13)),
}

FUNCTION_CLASSES = {
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

FIELDS = (
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
    "probability_competitor_lower",
    "median_competitor",
    "median_reference",
    "p_raw",
    "bonferroni_family_size",
    "p_bonferroni",
    "alpha",
    "decision",
)

class MwuError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiments",
        type=Path,
        default=Path("experiments"),
        help="Experiment root (default: experiments)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("mwu"),
        help="Output root (default: mwu)",
    )
    parser.add_argument(
        "--dsc-results",
        type=Path,
        default=Path("dsc_python_results_final"),
        help="Existing final DSCTool result root (default: dsc_python_results_final)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and calculate everything without writing files",
    )
    return parser.parse_args()


def function_class(suite: str, fid: int) -> str:
    for name in ("basic", "hybrid", "composition"):
        if fid in FUNCTION_CLASSES[suite][name]:
            return name
    raise MwuError(f"No class mapping for {suite} f{fid}")


def load_errors(path: Path, setting: Setting, fid: int) -> np.ndarray:
    if not path.is_file():
        raise MwuError(f"Missing input file: {path}")
    try:
        with path.open("rb") as stream:
            payload = pickle.load(stream)
    except Exception as exc:
        raise MwuError(f"Cannot read {path}: {exc}") from exc

    if not isinstance(payload, dict) or "errors" not in payload:
        raise MwuError(f"{path}: expected a dict containing 'errors'")
    raw = np.asarray(payload["errors"])
    if raw.shape != (EXPECTED_RUNS,):
        raise MwuError(
            f"{path}: expected {EXPECTED_RUNS} terminal errors, got {raw.shape}"
        )
    if raw.dtype.kind not in "iuf":
        raise MwuError(f"{path}: errors must be real numeric values")
    values = raw.astype(np.float64, copy=True)
    if not np.isfinite(values).all():
        raise MwuError(f"{path}: errors contain NaN or infinity")

    if "maxevals" in payload and int(payload["maxevals"]) != setting.budget:
        raise MwuError(
            f"{path}: maxevals={payload['maxevals']} != {setting.budget}"
        )
    if "dim" in payload and int(payload["dim"]) != setting.dimension:
        raise MwuError(f"{path}: dim={payload['dim']} != {setting.dimension}")
    if "suite" in payload and str(payload["suite"]).lower() != setting.suite:
        raise MwuError(f"{path}: suite={payload['suite']!r} != {setting.suite!r}")
    if "n_runs" in payload and int(payload["n_runs"]) != EXPECTED_RUNS:
        raise MwuError(f"{path}: n_runs={payload['n_runs']} != {EXPECTED_RUNS}")
    if "seeds" in payload:
        seeds_raw = np.asarray(payload["seeds"])
        if seeds_raw.shape != (EXPECTED_RUNS,) or seeds_raw.dtype.kind not in "iu":
            raise MwuError(f"{path}: expected 51 integer seeds")
        seeds = seeds_raw.astype(np.int64, copy=False)
        if not np.array_equal(np.sort(seeds), np.arange(EXPECTED_RUNS)):
            raise MwuError(f"{path}: seeds are not exactly 0..50")

    # Deliberately return the stored errors unchanged.  In particular, there
    # is no COCO-zero flooring and no use of the optional improvements trace.
    return values


def calculate_setting(experiments: Path, setting: Setting) -> list[dict[str, Any]]:
    functions = FUNCTIONS[setting.suite]
    samples: dict[str, dict[int, np.ndarray]] = {}
    for algorithm in setting.algorithms:
        budget_dir = (
            experiments
            / setting.suite
            / f"d{setting.dimension}"
            / algorithm
            / f"maxevals_{setting.budget}"
        )
        samples[algorithm] = {
            fid: load_errors(budget_dir / f"f{fid}.pkl", setting, fid)
            for fid in functions
        }

    reference_samples = samples[REFERENCE]
    family_size = len(functions)
    rows: list[dict[str, Any]] = []
    for competitor in sorted(set(setting.algorithms) - {REFERENCE}):
        for fid in functions:
            x = samples[competitor][fid]
            y = reference_samples[fid]
            result = stats.mannwhitneyu(
                x,
                y,
                alternative="two-sided",
                method="asymptotic",
                use_continuity=True,
            )
            u = float(result.statistic)
            p_raw = float(result.pvalue)
            p_bonferroni = min(1.0, family_size * p_raw)
            probability_lower = 1.0 - u / (len(x) * len(y))

            if p_bonferroni >= ALPHA or math.isclose(
                probability_lower, 0.5, rel_tol=0.0, abs_tol=1e-15
            ):
                decision = "not significant"
            elif probability_lower > 0.5:
                decision = "lower"
            else:
                decision = "higher"

            rows.append(
                {
                    "suite": setting.suite,
                    "dimension": setting.dimension,
                    "budget": setting.budget,
                    "function": fid,
                    "function_class": function_class(setting.suite, fid),
                    "competitor": competitor,
                    "reference": REFERENCE,
                    "n_competitor": len(x),
                    "n_reference": len(y),
                    "u_competitor": format(u, ".17g"),
                    "probability_competitor_lower": format(
                        probability_lower, ".17g"
                    ),
                    "median_competitor": format(float(np.median(x)), ".17g"),
                    "median_reference": format(float(np.median(y)), ".17g"),
                    "p_raw": format(p_raw, ".17g"),
                    "bonferroni_family_size": family_size,
                    "p_bonferroni": format(p_bonferroni, ".17g"),
                    "alpha": ALPHA,
                    "decision": decision,
                }
            )
    return rows


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def csv_text(rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> str:
    import io

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=list(fields),
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise MwuError(f"Missing DSC result file: {path}")
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def expected_dsc_algorithms(setting: Setting) -> set[str]:
    return set(BASE_ALGORITHMS)


def load_dsc_results(dsc_root: Path) -> dict[tuple[str, int, int], dict[str, Any]]:
    long_rows = read_csv_rows(dsc_root / "dsc_results_final_long.csv")
    summaries: dict[tuple[str, int, int], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in long_rows:
        key = (row["suite"], int(row["dimension"]), int(row["budget"]))
        scope = row["scope"]
        if scope not in {"all", "composition"} or scope in summaries[key]:
            raise MwuError(f"Invalid or duplicate DSC summary row: {key} {scope}")
        summaries[key][scope] = row

    loaded: dict[tuple[str, int, int], dict[str, Any]] = {}
    for setting in SETTINGS:
        key = (setting.suite, setting.dimension, setting.budget)
        if set(summaries.get(key, {})) != {"all", "composition"}:
            raise MwuError(f"Missing all/composition DSC summaries for {key}")
        setting_dir = (
            dsc_root
            / setting.suite
            / f"d{setting.dimension}"
            / f"budget_{setting.budget}"
        )
        rank_rows = read_csv_rows(setting_dir / "per_function_dsc_ranks.csv")
        expected_functions = set(FUNCTIONS[setting.suite])
        expected_algorithms = expected_dsc_algorithms(setting)
        rank_lookup: dict[tuple[int, str], float] = {}
        for row in rank_rows:
            if (
                row["suite"] != setting.suite
                or int(row["dimension"]) != setting.dimension
                or int(row["budget"]) != setting.budget
            ):
                raise MwuError(f"Wrong DSC rank metadata in {setting_dir}")
            fid = int(row["function_id"])
            algorithm = row["algorithm"]
            rank = float(row["dsc_rank"])
            if fid not in expected_functions or algorithm not in expected_algorithms:
                raise MwuError(
                    f"Unexpected DSC rank key in {setting_dir}: f{fid} {algorithm}"
                )
            pair = (fid, algorithm)
            if (
                pair in rank_lookup
                or not math.isfinite(rank)
                or rank < 1
                or rank > len(expected_algorithms)
                or not math.isclose(2 * rank, round(2 * rank), rel_tol=0.0, abs_tol=1e-12)
            ):
                raise MwuError(f"Duplicate/nonfinite DSC rank in {setting_dir}: {pair}")
            rank_lookup[pair] = rank
        expected_pairs = {
            (fid, algorithm)
            for fid in expected_functions
            for algorithm in expected_algorithms
        }
        if set(rank_lookup) != expected_pairs:
            raise MwuError(f"Incomplete DSC rank matrix in {setting_dir}")
        expected_rank_sum = len(expected_algorithms) * (len(expected_algorithms) + 1) / 2
        for fid in expected_functions:
            rank_sum = sum(rank_lookup[(fid, algorithm)] for algorithm in expected_algorithms)
            if not math.isclose(rank_sum, expected_rank_sum, rel_tol=0.0, abs_tol=1e-12):
                raise MwuError(f"Invalid DSC rank sum for {setting_dir}/f{fid}")

        for scope, summary in summaries[key].items():
            if int(summary["k"]) != len(expected_algorithms):
                raise MwuError(f"Wrong DSC k for {key} {scope}")
            expected_n = (
                len(expected_functions)
                if scope == "all"
                else len(FUNCTION_CLASSES[setting.suite]["composition"])
            )
            if int(summary["n_functions"]) != expected_n:
                raise MwuError(f"Wrong DSC function count for {key} {scope}")
            if summary["best_algorithm"] not in expected_algorithms:
                raise MwuError(f"Wrong DSC best algorithm for {key} {scope}")
            if not re.fullmatch(r"(?:\d+(?:\.5)?)/7", summary["msc_position"]):
                raise MwuError(f"Wrong DSC MSC position for {key} {scope}")
            if summary["label"] not in {"★", "≈", "↓", "O"}:
                raise MwuError(f"Unknown DSC label for {key} {scope}")

        loaded[key] = {
            "rank_lookup": rank_lookup,
            "algorithms": expected_algorithms,
            "summaries": summaries[key],
        }

    if set(loaded) != {
        (setting.suite, setting.dimension, setting.budget) for setting in SETTINGS
    }:
        raise MwuError("DSC setting set is incomplete")
    return loaded


def budget_slug(budget: int) -> str:
    """Stable URL-anchor slug; not a reader-facing budget label."""
    if budget >= 1_000_000 and budget % 1_000_000 == 0:
        return f"{budget // 1_000_000}m"
    if budget >= 1_000 and budget % 1_000 == 0:
        return f"{budget // 1_000}k"
    return str(budget)


def format_u(value: Any) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return format(number, ".6g")


def decision_symbol(decision: str) -> str:
    if decision == "lower":
        return ARROW_LOWER
    if decision == "higher":
        return ARROW_HIGHER
    if decision == "not significant":
        return ARROW_NS
    raise MwuError(f"Unknown decision: {decision}")


def budget_anchor(budget: int) -> str:
    return f"budget-{budget_slug(budget)}"


def dsc_budget_anchor(budget: int) -> str:
    return f"dsc-budget-{budget_slug(budget)}"


def format_optional_p(value: str) -> str:
    return "—" if value == "" else format_p(value)


def render_dsc_section(
    suite: str,
    dimension: int,
    dsc_by_budget: Mapping[int, Mapping[str, Any]],
) -> list[str]:
    lines = [
        "## Deep Statistical Comparison",
        "",
        "Following the fixed-budget analysis workflow described by",
        "[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied",
        "[Deep Statistical Comparison (Eftimov et al., 2017)](https://doi.org/10.1016/j.ins.2017.07.015)",
        "through [DSCTool (Eftimov et al., 2020)](https://doi.org/10.1016/j.asoc.2019.105977)",
        "to the 51 run-wise terminal errors for each function.",
        "",
        "IOHanalyzer: <https://iohanalyzer.liacs.nl/>; DSCTool service used for",
        "the analysis: <https://ws.ijs.si/dsc/>.",
        "",
        "Settings: Anderson–Darling comparisons at `alpha=0.05`, `epsilon=0`,",
        "and `monte_carlo_iterations=0`; Friedman omnibus tests over functions;",
        "and, after rejection of the omnibus null hypothesis, Holm-adjusted",
        "post-hoc comparisons against the method with the lowest mean DSC rank.",
        "",
        "`★` means that MSC-CMA-ES has the lowest mean DSC rank and the Friedman",
        "test rejects the null hypothesis; `≈` means that the Friedman test",
        "rejects the null hypothesis but the Holm-adjusted comparison between",
        "MSC-CMA-ES and the lowest-mean-rank method is not significant; `↓` means",
        "that the lowest-mean-rank method has a smaller mean DSC rank than",
        "MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means",
        "that the Friedman test does not reject the null hypothesis and no",
        "post-hoc interpretation is made.",
        "",
    ]

    ordered_budgets = sorted(dsc_by_budget)
    for budget in ordered_budgets:
        data = dsc_by_budget[budget]
        rank_lookup = data["rank_lookup"]
        algorithms = [
            algorithm
            for algorithm in DSC_TABLE_ORDER
            if algorithm in data["algorithms"]
        ]
        functions = list(FUNCTIONS[suite])
        anchor = dsc_budget_anchor(budget)
        lines.extend(
            [
                f'<a id="{anchor}"></a>',
                "",
                f"### Budget {format_budget(budget)}",
                "",
                f'<a id="{anchor}-ranks"></a>',
                "",
                "#### DSC ranks by function",
                "",
                "DSC ranks are ordered from 1 upward; tied distributions receive",
                "fractional ranks. Smaller numerical ranks are lower in this ordering.",
                "",
                "| Function | "
                + " | ".join(display_name(algorithm) for algorithm in algorithms)
                + " |",
                "|:--|" + "|".join("--:" for _ in algorithms) + "|",
            ]
        )
        for fid in functions:
            cells = [format_u(rank_lookup[(fid, algorithm)]) for algorithm in algorithms]
            lines.append(f"| **f{fid}** | " + " | ".join(cells) + " |")

        composition_ids = sorted(FUNCTION_CLASSES[suite]["composition"])
        composition_label = (
            f"f{composition_ids[0]}–f{composition_ids[-1]}"
            if composition_ids == list(range(composition_ids[0], composition_ids[-1] + 1))
            else ", ".join(f"f{fid}" for fid in composition_ids)
        )
        lines.extend(
            [
                "",
                f"Composition-function set: `{composition_label}`.",
                "",
                f'<a id="{anchor}-comparison"></a>',
                "",
                "#### Statistical comparison",
                "",
                "| Function set | n | Lowest-mean-rank method | Lowest mean rank | MSC-CMA-ES mean rank | MSC position | Friedman Q | Friedman p | p_Holm | Result |",
                "|:--|--:|:--|--:|--:|:--:|--:|--:|--:|:--:|",
            ]
        )
        for scope, scope_label in (("all", "All functions"), ("composition", "Composition functions")):
            row = data["summaries"][scope]
            lines.append(
                "| "
                + " | ".join(
                    [
                        scope_label,
                        row["n_functions"],
                        display_name(row["best_algorithm"]),
                        format_u(row["best_mean_dsc_rank"]),
                        format_u(row["msc_mean_dsc_rank"]),
                        row["msc_position"],
                        format_p(row["friedman_statistic"]),
                        format_p(row["friedman_p_value"]),
                        format_optional_p(row["holm_p_best_vs_msc"]),
                        row["label"],
                    ]
                )
                + " |"
            )
        lines.append("")

    lines.extend(
        [
            '<a id="dsc-cell-summary"></a>',
            "",
            "### Cell summary",
            "",
            "| Budget | All functions | Composition functions |",
            "|--:|:--|:--|",
        ]
    )
    for budget in ordered_budgets:
        summaries = dsc_by_budget[budget]["summaries"]
        cells = []
        for scope in ("all", "composition"):
            row = summaries[scope]
            cells.append(
                f"{display_name(row['best_algorithm'])} · "
                f"{row['msc_position']} · {row['label']}"
            )
        lines.append(
            f"| {format_budget(budget)} | {cells[0]} | {cells[1]} |"
        )
    lines.append("")
    return lines


def render_readme(
    suite: str,
    dimension: int,
    rows: Sequence[Mapping[str, Any]],
    dsc_by_budget: Mapping[int, Mapping[str, Any]],
) -> str:
    by_budget: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_budget[int(row["budget"])].append(row)

    lines = [
        f"# {suite.upper()}, D={dimension}",
        "",
        "Contents: [Mann–Whitney U tests on terminal errors]"
        "(#mannwhitney-u-tests-on-terminal-errors) · "
        "[Deep Statistical Comparison](#deep-statistical-comparison)",
        "",
        "## Mann–Whitney U tests on terminal errors",
        "",
    ]

    lines.extend(
        [
            "Independent, two-sided Mann–Whitney U tests compare each competitor",
            "with MSC-CMA-ES on every function. Each sample contains 51 unmodified",
            "run-wise terminal errors. Bonferroni adjustment is applied over all",
            "functions separately for each budget and competitor.",
            "The test is evaluated with SciPy's asymptotic Mann–Whitney U method",
            "(`method=\"asymptotic\"`) with continuity correction (`use_continuity=True`).",
            "",
            "The U statistic in [`details.csv`](details.csv) is for the competitor",
            "sample. For minimization, `probability_competitor_lower` is",
            r"$P(X_{competitor}<X_{MSC})+\frac12P(X_{competitor}=X_{MSC})$.",
            "",
            "Each function is reported with the U statistic, p_raw, and",
            "p_Bonferroni. Direction is stated from the competitor perspective:",
            "`↓` denotes a statistically significant shift toward lower terminal",
            "errors, `↑` a statistically significant shift toward higher terminal",
            "errors, and `—` no statistically significant difference after",
            "Bonferroni correction. Significant adjusted p-values are shown in bold.",
            "",
        ]
    )

    for budget, budget_rows in sorted(by_budget.items()):
        competitors = sorted({str(row["competitor"]) for row in budget_rows})
        functions = sorted({int(row["function"]) for row in budget_rows})
        lookup = {
            (int(row["function"]), str(row["competitor"])): row
            for row in budget_rows
        }
        if len(lookup) != len(budget_rows):
            raise MwuError(
                f"Duplicate function/competitor result in {suite} D={dimension} "
                f"B={budget}"
            )

        ordered = ["BIPOP-CMA"]
        ordered.extend(
            algorithm
            for algorithm in ("ARRDE", "LSRTDE", "NLSHADE-RSP", "j2020", "jSO")
            if algorithm in competitors
        )
        if set(ordered) != set(competitors):
            raise MwuError(
                f"Unexpected competitor set in {suite} D={dimension} B={budget}: "
                f"{competitors}"
            )

        family_size = len(functions)
        anchor = budget_anchor(budget)
        lines.extend(
            [
                f'<a id="{anchor}"></a>',
                "",
                f"### Budget {format_budget(budget)}",
                "",
                f"Bonferroni family size: `{family_size}` functions.",
                "",
            ]
        )

        header = (
            "| Function | "
            + " | ".join(display_name(algorithm) for algorithm in ordered)
            + " |"
        )
        alignment = "|:--|" + "|".join("--:" for _ in ordered) + "|"

        lines.extend(
            [
                f'<a id="{anchor}-u"></a>',
                "",
                "#### Mann–Whitney U statistic",
                "",
                header,
                alignment,
            ]
        )
        for fid in functions:
            function_rows = [lookup[(fid, algorithm)] for algorithm in ordered]
            u_cells = [format_u(row["u_competitor"]) for row in function_rows]
            lines.append(
                f"| **f{fid}** | "
                + " | ".join(u_cells)
                + " |"
            )

        lines.extend(
            [
                "",
                f'<a id="{anchor}-raw-p"></a>',
                "",
                "#### p_raw",
                "",
                header,
                alignment,
            ]
        )
        for fid in functions:
            function_rows = [lookup[(fid, algorithm)] for algorithm in ordered]
            raw_cells = [format_p(row["p_raw"]) for row in function_rows]
            lines.append(
                f"| **f{fid}** | "
                + " | ".join(raw_cells)
                + " |"
            )

        lines.extend(
            [
                "",
                f'<a id="{anchor}-bonferroni"></a>',
                "",
                "#### p_Bonferroni and Direction",
                "",
                header,
                alignment,
            ]
        )
        for fid in functions:
            function_rows = [lookup[(fid, algorithm)] for algorithm in ordered]
            adjusted_cells = []
            for row in function_rows:
                p_adjusted = format_p(row["p_bonferroni"])
                symbol = decision_symbol(str(row["decision"]))
                cell = f"{p_adjusted} ({symbol})"
                if symbol != ARROW_NS:
                    cell = f"**{cell}**"
                adjusted_cells.append(cell)
            lines.append(
                f"| **f{fid}** | "
                + " | ".join(adjusted_cells)
                + " |"
            )
        lines.append("")

    lines.extend(
        [
            "Full-precision U statistics, raw and Bonferroni-adjusted p-values,",
            "effect directions, sample medians, and family sizes are available in",
            "[`details.csv`](details.csv).",
            "",
        ]
    )
    lines.extend(render_dsc_section(suite, dimension, dsc_by_budget))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    experiments = args.experiments.resolve()
    output = args.output.resolve()
    dsc_root = args.dsc_results.resolve()
    if not experiments.is_dir():
        raise MwuError(f"Experiment directory does not exist: {experiments}")
    if not dsc_root.is_dir():
        raise MwuError(f"DSC result directory does not exist: {dsc_root}")

    dsc_results = load_dsc_results(dsc_root)

    all_rows: list[dict[str, Any]] = []
    by_cell: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for setting in SETTINGS:
        print(
            f"[{setting.suite} D={setting.dimension} B={setting.budget}] calculating",
            flush=True,
        )
        rows = calculate_setting(experiments, setting)
        expected = (len(setting.algorithms) - 1) * len(FUNCTIONS[setting.suite])
        if len(rows) != expected:
            raise MwuError(
                f"{setting}: calculated {len(rows)} rows, expected {expected}"
            )
        all_rows.extend(rows)
        by_cell[(setting.suite, setting.dimension)].extend(rows)

    if len(all_rows) != 1992:
        raise MwuError(f"Calculated {len(all_rows)} total rows, expected 1992")

    if args.dry_run:
        print(f"Dry run passed: {len(SETTINGS)} settings, {len(by_cell)} cells, 1992 tests")
        return 0

    for (suite, dimension), rows in sorted(by_cell.items()):
        cell = output / suite / f"d{dimension}"
        dsc_by_budget = {
            setting.budget: dsc_results[(suite, dimension, setting.budget)]
            for setting in SETTINGS
            if setting.suite == suite and setting.dimension == dimension
        }
        atomic_write_text(cell / "details.csv", csv_text(rows, FIELDS))
        atomic_write_text(
            cell / "README.md",
            render_readme(suite, dimension, rows, dsc_by_budget),
        )
    atomic_write_text(
        output / "mann_whitney_u_all_settings.csv",
        csv_text(all_rows, FIELDS),
    )

    print(
        f"Wrote 10 MWU+DSC cell READMEs, 10 details.csv files, and 1 aggregate CSV under {output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MwuError, OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
