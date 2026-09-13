#!/usr/bin/env python3
"""Generate the root and per-dimension MWU/DSC READMEs under mwu/.

The script reads ``pkl['errors']`` exactly as stored.  It does not round,
clip, floor, sort, or otherwise transform the 51 run-wise terminal errors.

For every suite--dimension--budget setting, each competitor is compared with
MSC-CMA independently on every function using a two-sided Mann--Whitney U
test. Holm--Bonferroni correction is applied across the selected function
scope separately for each (setting, competitor) family. By default both
all-function and composition-function families are reported in the same
pages. The raw tests are calculated once; each scope is adjusted separately.

Only these files are created/replaced under --output:

* <suite>/d<dimension>/details.csv
* <suite>/d<dimension>/README.md
* README.md
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

# Keep this generator standalone: only NumPy and SciPy are required.
# These presentation helpers follow analysis/report_style.py.
ARROW_HIGHER, ARROW_LOWER, ARROW_NS = "↑", "↓", "—"


def display_name(name: str) -> str:
    return {
        "MSC-CMA": "MSC-CMA-ES", "BIPOP-CMA": "BIPOP-CMA-ES",
        "LSRTDE": "L-SRTDE", "NLSHADE-RSP": "NL-SHADE-RSP",
    }.get(name, name)


def format_budget(budget: int) -> str:
    if budget <= 0:
        raise ValueError(f"Budget must be positive: {budget}")
    exponent = int(math.floor(math.log10(budget)))
    power = 10 ** exponent
    if budget % power == 0:
        coefficient = budget // power
        return f"10^{exponent}" if coefficient == 1 else f"{coefficient}×10^{exponent}"
    return f"{budget:,}"


def format_p(value: Any) -> str:
    return format(float(value), ".6g")


def holm_correction(p_values: Iterable[float]) -> list[float]:
    """Holm step-down adjustment for one complete function family."""
    values = [float(p) for p in p_values]
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in values):
        raise ValueError("Holm correction requires finite p-values in [0, 1]")
    adjusted = [0.0] * len(values)
    running_max = 0.0
    for rank, index in enumerate(sorted(range(len(values)), key=values.__getitem__)):
        running_max = max(running_max, (len(values) - rank) * values[index])
        adjusted[index] = min(1.0, running_max)
    return adjusted


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
    "scope",
    "correction",
    "competitor",
    "reference",
    "n_competitor",
    "n_reference",
    "u_competitor",
    "probability_competitor_lower",
    "median_competitor",
    "median_reference",
    "p_raw",
    "holm_family_size",
    "p_holm",
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
        default=Path("dsc"),
        help="Existing final DSCTool result root (default: dsc)",
    )
    parser.add_argument(
        "--func-class", choices=("both", "all", "basic", "hybrid", "composition"),
        default="both", help="Function families (default: both = all and composition)",
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


def selected_functions(suite: str, scope: str = "all") -> tuple[int, ...]:
    if scope == "all":
        return FUNCTIONS[suite]
    if scope not in FUNCTION_CLASSES[suite]:
        raise MwuError(f"Unknown function scope: {scope}")
    return tuple(fid for fid in FUNCTIONS[suite] if fid in FUNCTION_CLASSES[suite][scope])


def calculate_setting(
    experiments: Path, setting: Setting, scope: str = "all"
) -> list[dict[str, Any]]:
    functions = selected_functions(setting.suite, scope)
    samples: dict[str, dict[int, np.ndarray]] = {}
    for algorithm in setting.algorithms:
        budget_dir = (
            experiments / setting.suite / f"d{setting.dimension}"
            / algorithm / f"maxevals_{setting.budget}"
        )
        samples[algorithm] = {
            fid: load_errors(budget_dir / f"f{fid}.pkl", setting, fid)
            for fid in functions
        }

    reference_samples = samples[REFERENCE]
    family_size = len(functions)
    rows: list[dict[str, Any]] = []
    for competitor in sorted(set(setting.algorithms) - {REFERENCE}):
        family: list[dict[str, Any]] = []
        for fid in functions:
            x = samples[competitor][fid]
            y = reference_samples[fid]
            result = stats.mannwhitneyu(
                x, y, alternative="two-sided", method="asymptotic",
                use_continuity=True,
            )
            u = float(result.statistic)
            probability_lower = 1.0 - u / (len(x) * len(y))
            family.append({
                "suite": setting.suite,
                "dimension": setting.dimension,
                "budget": setting.budget,
                "function": fid,
                "function_class": function_class(setting.suite, fid),
                "scope": scope,
                "correction": "holm-bonferroni",
                "competitor": competitor,
                "reference": REFERENCE,
                "n_competitor": len(x),
                "n_reference": len(y),
                "u_competitor": format(u, ".17g"),
                "probability_competitor_lower": format(probability_lower, ".17g"),
                "median_competitor": format(float(np.median(np.where(np.abs(x) <= 1e-8, 0.0, x))), ".17g"),
                "median_reference": format(float(np.median(np.where(np.abs(y) <= 1e-8, 0.0, y))), ".17g"),
                "p_raw": format(float(result.pvalue), ".17g"),
                "holm_family_size": family_size,
                "alpha": ALPHA,
            })
        adjusted = holm_correction(float(row["p_raw"]) for row in family)
        for row, p_holm in zip(family, adjusted):
            probability_lower = float(row["probability_competitor_lower"])
            if p_holm > ALPHA or math.isclose(
                probability_lower, 0.5, rel_tol=0.0, abs_tol=1e-15
            ):
                decision = "not significant"
            else:
                decision = "lower" if probability_lower > 0.5 else "higher"
            row["p_holm"] = format(p_holm, ".17g")
            row["decision"] = decision
        rows.extend(family)
    return rows


def recorrect_scope(
    rows: Sequence[Mapping[str, Any]], setting: Setting, scope: str
) -> list[dict[str, Any]]:
    """Reuse raw tests and adjust a complete scope independently of all-scope p_Holm."""
    functions = selected_functions(setting.suite, scope)
    families: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for original in rows:
        if original["scope"] != "all":
            raise MwuError("Scope correction requires the all-function raw tests")
        if int(original["function"]) in functions:
            families[str(original["competitor"])].append(dict(original))
    if set(families) != set(setting.algorithms) - {REFERENCE}:
        raise MwuError(f"Incomplete competitor set for {setting} {scope}")
    result = []
    for competitor, family in sorted(families.items()):
        family.sort(key=lambda row: int(row["function"]))
        if [int(row["function"]) for row in family] != list(functions):
            raise MwuError(f"Incomplete function family: {setting} {scope} {competitor}")
        adjusted = holm_correction(float(row["p_raw"]) for row in family)
        for row, p_holm in zip(family, adjusted):
            u = float(row["u_competitor"])
            midpoint = int(row["n_competitor"]) * int(row["n_reference"]) / 2
            decision = "not significant"
            if p_holm <= ALPHA and u != midpoint:
                decision = "lower" if u < midpoint else "higher"
            row.update(scope=scope, correction="holm-bonferroni",
                       holm_family_size=len(functions),
                       p_holm=format(p_holm, ".17g"), decision=decision)
        result.extend(family)
    return result


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
        "`★` means that MSC-CMA-ES has the lowest mean DSC rank and the Friedman",
        "test rejects the null hypothesis; `≈` means that the Friedman test",
        "rejects the null hypothesis but the Holm-adjusted comparison between",
        "MSC-CMA-ES and the lowest-mean-rank method is not significant; `↓` means",
        "that the lowest-mean-rank method has a smaller mean DSC rank than",
        "MSC-CMA-ES and the Holm-adjusted comparison is significant; `O` means",
        "that the Friedman test does not reject the null hypothesis and no",
        "post-hoc interpretation is made.",
        "",
        '<a id="dsc-cell-summary"></a>',
        "",
        "### Cell summary",
        "",
        "| Budget | All functions | Composition functions |",
        "|--:|:--|:--|",
    ]
    ordered_budgets = sorted(dsc_by_budget)
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
    lines.extend([
        "",
        "<details>",
        "<summary>DSC protocol</summary>",
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
        "`p_Holm` is shown only when the lowest-mean-rank algorithm is not",
        "MSC-CMA-ES and the Friedman test rejects the null hypothesis.",
        "",
        "</details>",
        "",
    ])

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
                f'<a id="{anchor}-ranks"></a>',
                f'<a id="{anchor}-comparison"></a>',
                "",
                f"### Budget {format_budget(budget)}",
                "",
                "<details>",
                "<summary>DSC ranks by function and statistical comparison</summary>",
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
                        (format_optional_p(row["holm_p_best_vs_msc"])
                         if row["best_algorithm"] != REFERENCE
                         and float(row["friedman_p_value"]) <= ALPHA else "—"),
                        row["label"],
                    ]
                )
                + " |"
            )
        lines.extend(["", "</details>", ""])
    return lines


COMPETITOR_ORDER = (
    "BIPOP-CMA", "ARRDE", "LSRTDE", "NLSHADE-RSP", "j2020", "jSO",
)
SCOPE_LABELS = {
    "all": "All functions",
    "composition": "Composition functions",
    "basic": "Basic functions",
    "hybrid": "Hybrid functions",
}


def msc_outcome(row: Mapping[str, Any]) -> str:
    """Translate the stored competitor direction to the reference perspective."""
    labels = {"higher": "<", "lower": ">", "not significant": "="}
    try:
        return labels[str(row["decision"])]
    except KeyError as exc:
        raise MwuError(f"Unknown MWU decision: {row['decision']}") from exc


def result_counts(rows: Sequence[Mapping[str, Any]], competitor: str) -> str:
    outcomes = [msc_outcome(row) for row in rows if row["competitor"] == competitor]
    return "/".join(str(outcomes.count(label)) for label in ("<", ">", "="))


def ordered_scopes(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    present = {str(row["scope"]) for row in rows}
    if not present or not present <= set(SCOPE_LABELS):
        raise MwuError(f"Invalid or empty scope set: {present}")
    return [scope for scope in SCOPE_LABELS if scope in present]


def validate_family_rows(
    rows: Sequence[Mapping[str, Any]], suite: str, dimension: int, budget: int, scope: str
) -> None:
    functions = selected_functions(suite, scope)
    expected = {(fid, algorithm) for fid in functions for algorithm in COMPETITOR_ORDER}
    found = set()
    for row in rows:
        key = (int(row["function"]), str(row["competitor"]))
        if key in found:
            raise MwuError(f"Duplicate result: {suite} D={dimension} B={budget} {scope} {key}")
        found.add(key)
        if (row["suite"] != suite or int(row["dimension"]) != dimension
                or int(row["budget"]) != budget or row["scope"] != scope
                or row["reference"] != REFERENCE
                or row["correction"] != "holm-bonferroni"
                or int(row["holm_family_size"]) != len(functions)):
            raise MwuError(f"Wrong result metadata: {suite} D={dimension} B={budget} {scope}")
        p_holm = float(row["p_holm"])
        if not math.isfinite(p_holm) or not 0 <= p_holm <= 1:
            raise MwuError(f"Invalid p_Holm: {p_holm}")
        msc_outcome(row)
    if found != expected:
        raise MwuError(f"Incomplete result table: {suite} D={dimension} B={budget} {scope}")


def protocol_lines() -> list[str]:
    return [
        "Each competitor is compared with MSC-CMA-ES using independent, two-sided",
        "Mann–Whitney U tests on 51 stored run-wise terminal errors at the stated budget.",
        "The tests use the asymptotic method with tie and continuity corrections.",
        "No zero threshold or rounding is applied to the MWU inputs; zeros already",
        "present in the stored samples are retained.",
        "",
        "Holm–Bonferroni correction is applied separately for each competitor, suite,",
        "dimension, budget, and function scope, at `alpha=0.05`.",
        "All-function and composition-function results use independent corrections",
        "of the same raw p-values. For CEC2017 the family sizes are 29 and 10,",
        "respectively; withdrawn function f2 is excluded.",
        "",
        "**MWU symbols:**",
        "",
        "For each comparison, $\\bar R_M$ and $\\bar R_A$ are the mean ranks of",
        "the MSC-CMA-ES sample and the compared algorithm's sample in the pooled",
        "sample, using average ranks for ties. These are the observation ranks",
        "used by MWU, distinct from DSC ranks.",
        "",
        "- **`<`**: $p_{\\mathrm{Holm}}\\leq0.05$ and $\\bar R_M<\\bar R_A$.",
        "- **`>`**: $p_{\\mathrm{Holm}}\\leq0.05$ and $\\bar R_M>\\bar R_A$.",
        "- **`=`**: $p_{\\mathrm{Holm}}>0.05$; the null hypothesis is not rejected.",
        "",
        "The symbol `=` denotes non-rejection of $H_0:F_M=F_A$; it does not",
        "assert equality of the sample mean ranks.",
        "",
        "Significance uses the full-precision adjusted p-value (`p_Holm <= 0.05`).",
        "The mean-rank relation is obtained from U without rounding the input errors.",
        "Summary cells contain $n_{<}/n_{>}/n_{=}$: counts of functions in the",
        "three categories defined above.",
        "",
        "CSV values retain full numerical precision. Only descriptive medians use",
        "a separate copy with `abs(error) <= 1e-8` set to zero.",
        "",
    ]


def comparison_header(first: str = "Function") -> list[str]:
    return [
        f"| {first} | " + " | ".join(display_name(a) for a in COMPETITOR_ORDER) + " |",
        "|:--|" + "|".join("--:" for _ in COMPETITOR_ORDER) + "|",
    ]


def render_scope_table(
    suite: str, dimension: int, budget: int, scope: str,
    rows: Sequence[Mapping[str, Any]],
) -> list[str]:
    validate_family_rows(rows, suite, dimension, budget, scope)
    functions = selected_functions(suite, scope)
    lookup = {(int(row["function"]), str(row["competitor"])): row for row in rows}
    anchor = f"{budget_anchor(budget)}-{scope}"
    lines = [
        f'<a id="{anchor}"></a>', "",
        f"#### {SCOPE_LABELS[scope]}", "",
        "<details>",
        "<summary>Per-function comparisons, U statistics and raw p-values</summary>", "",
        f"Function scope: `{scope}`. Holm family size: **{len(functions)}** per competitor.",
        "Each cell reports **p_Holm · MWU symbol** (`<`, `>`, or `=`).", "",
        *comparison_header(),
    ]
    for fid in functions:
        cells = []
        for competitor in COMPETITOR_ORDER:
            row = lookup[(fid, competitor)]
            outcome = msc_outcome(row)
            cell = f"{format_p(row['p_holm'])} · `{outcome}`"
            cells.append(f"**{cell}**" if outcome != "=" else cell)
        lines.append(f"| **f{fid}** | " + " | ".join(cells) + " |")
    lines.extend([
        r"| $n_{<}/n_{>}/n_{=}$ | " + " | ".join(result_counts(rows, a) for a in COMPETITOR_ORDER) + " |",
        "", "##### U statistics and raw p-values", "",
        "U is for the compared algorithm's sample. The symbols above describe",
        "the MSC-CMA-ES sample's mean-rank relation after Holm correction.",
        "", "##### U statistic", "", *comparison_header(),
    ])
    for fid in functions:
        lines.append(f"| f{fid} | " + " | ".join(
            format_u(lookup[(fid, a)]["u_competitor"]) for a in COMPETITOR_ORDER
        ) + " |")
    lines.extend(["", "##### p_raw", "", *comparison_header()])
    for fid in functions:
        lines.append(f"| f{fid} | " + " | ".join(
            format_p(lookup[(fid, a)]["p_raw"]) for a in COMPETITOR_ORDER
        ) + " |")
    lines.extend(["", "</details>", ""])
    return lines


def render_readme(
    suite: str,
    dimension: int,
    rows: Sequence[Mapping[str, Any]],
    dsc_by_budget: Mapping[int, Mapping[str, Any]],
    scope: str = "both",
) -> str:
    scopes = ordered_scopes(rows)
    budgets = sorted({int(row["budget"]) for row in rows})
    lines = [
        f"# {suite.upper()} · D={dimension}", "",
        "[MWU overview](../../README.md) · [Full results CSV](details.csv)", "",
        "[MWU summary](#mwu-summary) · [MWU results](#mwu-results)"
        + (" · [Deep Statistical Comparison](#deep-statistical-comparison)" if dsc_by_budget else ""),
        "", "## MWU summary", "",
        "Counts are from the **MSC-CMA-ES perspective**, using 51 runs per algorithm and function. "
        "Cells report **lower / higher / not significant** pooled sample mean-rank comparisons after Holm correction:",
        "",
        "- `<`: MSC-CMA-ES has a significantly lower pooled sample mean rank.",
        "- `>`: MSC-CMA-ES has a significantly higher pooled sample mean rank.",
        "- `=`: the null hypothesis is not rejected; this does not assert equality.",
        "", *comparison_header("Budget / function scope"),
    ]
    for budget in budgets:
        for selected_scope in scopes:
            group = [r for r in rows if int(r["budget"]) == budget and r["scope"] == selected_scope]
            validate_family_rows(group, suite, dimension, budget, selected_scope)
            link = f"{format_budget(budget)} / {SCOPE_LABELS[selected_scope]}"
            lines.append(
                f"| [{link}](#{budget_anchor(budget)}-{selected_scope}) | "
                + " | ".join(result_counts(group, a) for a in COMPETITOR_ORDER) + " |"
            )
    lines.extend([
        "", r"All summary cells contain $n_{<}/n_{>}/n_{=}$ as defined above.", "",
        "<details>", "<summary>Statistical protocol and full MWU notation</summary>", "",
        *protocol_lines(), "</details>", "", "## MWU results", "",
    ])
    for budget in budgets:
        lines.extend([f'<a id="{budget_anchor(budget)}"></a>', "",
                      f"### Budget {format_budget(budget)}", ""])
        for selected_scope in scopes:
            group = [r for r in rows if int(r["budget"]) == budget and r["scope"] == selected_scope]
            lines.extend(render_scope_table(suite, dimension, budget, selected_scope, group))
    lines.extend([
        "The complete U statistics, raw and adjusted p-values, sample sizes,",
        "descriptive medians, scopes, and family sizes are in [`details.csv`](details.csv).",
        "The CSV `decision` field describes the compared algorithm's pooled mean rank",
        "conditional on rejection after Holm correction: `higher` maps to `<` for",
        "MSC-CMA-ES, `lower` to `>`, and `not significant` to `=`.", "",
    ])
    if dsc_by_budget:
        lines.extend(render_dsc_section(suite, dimension, dsc_by_budget))
    return "\n".join(lines)


def render_root_readme(rows: Sequence[Mapping[str, Any]], include_dsc: bool) -> str:
    scopes = ordered_scopes(rows)
    settings = sorted({(str(r["suite"]), int(r["dimension"]), int(r["budget"])) for r in rows})
    lines = [
        "# Mann–Whitney U comparisons with MSC-CMA-ES", "",
        "Fixed-budget comparisons with BIPOP-CMA-ES, ARRDE, L-SRTDE,",
        "NL-SHADE-RSP, j2020, and jSO.", "",
        "Contents: " + " · ".join(f"[{SCOPE_LABELS[s]}](#{s})" for s in scopes)
        + " · [Method and symbols](#method-and-symbols)", "",
        f"**{len(settings)} suite/dimension/budget settings**. "
        r"Each table cell contains $n_{<}/n_{>}/n_{=}$ for MSC-CMA-ES:",
        "counts of significantly lower or higher pooled sample mean ranks, and",
        "comparisons without a significant difference after Holm correction.", "",
        "Each setting links to the per-function p_Holm table. U and raw p-values",
        "are available in expandable sections on those pages.", "",
    ]
    for scope in scopes:
        lines.extend([
            f'<a id="{scope}"></a>', "", f"## {SCOPE_LABELS[scope]}", "",
            "| Suite | D | Budget | Functions | "
            + " | ".join(display_name(a) for a in COMPETITOR_ORDER) + " |",
            "|:--|--:|--:|--:|" + "|".join("--:" for _ in COMPETITOR_ORDER) + "|",
        ])
        for suite, dimension, budget in settings:
            group = [r for r in rows if r["suite"] == suite and int(r["dimension"]) == dimension
                     and int(r["budget"]) == budget and r["scope"] == scope]
            validate_family_rows(group, suite, dimension, budget, scope)
            link = f"{suite}/d{dimension}/README.md#{budget_anchor(budget)}-{scope}"
            lines.append(
                f"| {suite.upper()} | {dimension} | [{format_budget(budget)}]({link}) "
                f"| {len(selected_functions(suite, scope))} | "
                + " | ".join(result_counts(group, a) for a in COMPETITOR_ORDER) + " |"
            )
        lines.append("")
    lines.extend(["## Method and symbols", "", *protocol_lines()])
    if include_dsc:
        lines.extend([
            "## Deep Statistical Comparison", "",
            "Each suite/dimension page also contains the existing DSC ranks,",
            "Friedman results, and Holm-adjusted post-hoc comparisons for both scopes.",
            "They are read from the existing DSC result files; no DSC test is recomputed.",
            "", "### Symbols", "",
            "- **★** — MSC-CMA-ES has the lowest mean DSC rank and the Friedman test rejects the null hypothesis.",
            "- **≈** — the Friedman test rejects the null hypothesis, but the Holm-adjusted comparison between MSC-CMA-ES and the lowest-mean-rank algorithm is not significant.",
            "- **↓** — the lowest-mean-rank algorithm has a smaller mean DSC rank than MSC-CMA-ES and the Holm-adjusted comparison is significant.",
            "- **O** — the Friedman test does not reject the null hypothesis; no post-hoc interpretation is made.",
            "",
            "`p_Holm` is shown only when the lowest-mean-rank algorithm is not MSC-CMA-ES",
            "and the Friedman test rejects the null hypothesis.", "",
        ])
    lines.extend([
        "## Data and regeneration", "",
        "[Download all settings and scopes as CSV](mann_whitney_u_all_settings.csv).",
        "Per-dimension `details.csv` files use the same schema. The `scope` column",
        "identifies the function family used for each correction.",
        *( ["Composition functions occur once in the all-function analysis and again",
            "in the independently corrected composition analysis."]
           if scopes == ["all", "composition"] else [] ), "",
        "From the repository root:", "", "```bash",
        "python analysis/run_mwu_all_functions.py --dsc-results dsc"
        + ("" if scopes == ["all", "composition"] else f" --func-class {scopes[0]}"),
        "```", "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    experiments = args.experiments.resolve()
    output = args.output.resolve()
    if args.func_class not in {"all", "both"}:
        output = output / args.func_class
    scopes = ("all", "composition") if args.func_class == "both" else (args.func_class,)
    include_dsc = "all" in scopes
    dsc_root = args.dsc_results.resolve()
    if not experiments.is_dir():
        raise MwuError(f"Experiment directory does not exist: {experiments}")
    if include_dsc and not dsc_root.is_dir():
        raise MwuError(f"DSC result directory does not exist: {dsc_root}")
    dsc_results = load_dsc_results(dsc_root) if include_dsc else {}

    all_rows: list[dict[str, Any]] = []
    by_cell: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for setting in SETTINGS:
        print(f"[{setting.suite} D={setting.dimension} B={setting.budget}] "
              f"calculating ({', '.join(scopes)})", flush=True)
        if args.func_class == "both":
            raw_rows = calculate_setting(experiments, setting, "all")
            rows = raw_rows + recorrect_scope(raw_rows, setting, "composition")
        else:
            rows = calculate_setting(experiments, setting, args.func_class)
        expected = (len(setting.algorithms) - 1) * sum(
            len(selected_functions(setting.suite, scope)) for scope in scopes
        )
        if len(rows) != expected:
            raise MwuError(f"{setting}: calculated {len(rows)} rows, expected {expected}")
        all_rows.extend(rows)
        by_cell[(setting.suite, setting.dimension)].extend(rows)

    # Prepare and validate every page before replacing any output file.
    outputs: list[tuple[Path, str]] = []
    for (suite, dimension), rows in sorted(by_cell.items()):
        cell = output / suite / f"d{dimension}"
        dsc_by_budget = {
            setting.budget: dsc_results[(suite, dimension, setting.budget)]
            for setting in SETTINGS
            if setting.suite == suite and setting.dimension == dimension
            and (suite, dimension, setting.budget) in dsc_results
        }
        outputs.append((cell / "details.csv", csv_text(rows, FIELDS)))
        outputs.append((cell / "README.md", render_readme(suite, dimension, rows, dsc_by_budget)))
    outputs.append((output / "mann_whitney_u_all_settings.csv", csv_text(all_rows, FIELDS)))
    outputs.append((output / "README.md", render_root_readme(all_rows, include_dsc)))

    if args.dry_run:
        print(f"Dry run passed: {len(SETTINGS)} settings, {len(by_cell) + 1} READMEs, "
              f"{len(all_rows)} result rows, scopes={','.join(scopes)}")
        return 0
    for path, content in outputs:
        atomic_write_text(path, content)
    print(
        f"Wrote 1 root README, {len(by_cell)} cell READMEs, {len(by_cell)} details.csv files, "
        f"and 1 aggregate CSV ({len(all_rows)} rows; scopes={','.join(scopes)}) under {output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MwuError, OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
