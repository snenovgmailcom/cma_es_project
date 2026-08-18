#!/usr/bin/env python3
"""Generate per-cell Mann--Whitney U results from terminal-error PKL files.

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
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import pickle
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import stats


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


@dataclass(frozen=True)
class Setting:
    suite: str
    dimension: int
    budget: int
    include_nea2plus: bool = False

    @property
    def algorithms(self) -> tuple[str, ...]:
        if self.include_nea2plus:
            return (*BASE_ALGORITHMS, "NEA2PLUS-PY")
        return BASE_ALGORITHMS


SETTINGS = (
    Setting("cec2014", 10, 100_000),
    Setting("cec2014", 10, 1_000_000),
    Setting("cec2014", 30, 300_000),
    Setting("cec2014", 30, 1_000_000),
    Setting("cec2017", 10, 100_000, True),
    Setting("cec2017", 10, 1_000_000),
    Setting("cec2017", 30, 300_000),
    Setting("cec2017", 30, 1_000_000),
    Setting("cec2020", 5, 50_000, True),
    Setting("cec2020", 5, 1_000_000),
    Setting("cec2020", 10, 1_000_000, True),
    Setting("cec2020", 10, 20_000_000),
    Setting("cec2020", 15, 3_000_000, True),
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

DISPLAY_NAMES = {
    "MSC-CMA": "MSC-CMA-ES",
    "BIPOP-CMA": "BIPOP-CMA-ES",
    "LSRTDE": "L-SRTDE",
    "NLSHADE-RSP": "NL-SHADE-RSP",
    "NEA2PLUS-PY": "NEA2+",
}


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
                decision = "competitor better"
            else:
                decision = "MSC-CMA-ES better"

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


def display_name(algorithm: str) -> str:
    return DISPLAY_NAMES.get(algorithm, algorithm)


def format_budget(budget: int) -> str:
    if budget >= 1_000_000 and budget % 1_000_000 == 0:
        return f"{budget // 1_000_000}M"
    if budget >= 1_000 and budget % 1_000 == 0:
        return f"{budget // 1_000}K"
    return str(budget)


def format_u(value: Any) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return format(number, ".6g")


def format_p(value: Any) -> str:
    return format(float(value), ".6g")


def decision_symbol(decision: str) -> str:
    if decision == "competitor better":
        return "+"
    if decision == "MSC-CMA-ES better":
        return "−"
    if decision == "not significant":
        return "≈"
    raise MwuError(f"Unknown decision: {decision}")


def render_readme(suite: str, dimension: int, rows: Sequence[Mapping[str, Any]]) -> str:
    by_budget: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_budget[int(row["budget"])].append(row)

    lines = [
        f"# {suite.upper()}, D={dimension}",
        "",
        "## Mann–Whitney U tests on terminal errors",
        "",
        "Independent, two-sided Mann–Whitney U tests compare each competitor",
        "with MSC-CMA-ES on every function. Each sample contains 51 unmodified",
        "run-wise terminal errors. Bonferroni adjustment is applied over all",
        "functions separately for each budget and competitor.",
        "",
        "The U statistic in [`details.csv`](details.csv) is for the competitor",
        "sample. For minimization, `probability_competitor_lower` is",
        r"$P(X_{competitor}<X_{MSC})+\frac12P(X_{competitor}=X_{MSC})$.",
        "",
        "Each function is reported with the U statistic, the raw two-sided",
        "p-value, and the Bonferroni-adjusted p-value. In the adjusted-p rows,",
        "`+` means that the competitor has significantly lower terminal errors,",
        "`−` means that MSC-CMA-ES has significantly lower terminal errors, and",
        "`≈` means that the difference is not significant at alpha=0.05.",
        "Significant adjusted p-values are shown in bold.",
        "",
    ]

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
        if "NEA2PLUS-PY" in competitors:
            ordered.append("NEA2PLUS-PY")
        if set(ordered) != set(competitors):
            raise MwuError(
                f"Unexpected competitor set in {suite} D={dimension} B={budget}: "
                f"{competitors}"
            )

        family_size = len(functions)
        lines.extend(
            [
                f"### Budget {format_budget(budget)}",
                "",
                f"Bonferroni family size: `{family_size}` functions.",
                "",
                "| Function | Statistic | MSC-CMA-ES | BIPOP-CMA-ES |  | "
                + " | ".join(
                    display_name(algorithm) for algorithm in ordered[1:]
                )
                + " |",
                "|:--|:--|--:|--:|:-:|"
                + "|".join("--:" for _ in ordered[1:])
                + "|",
            ]
        )

        for fid in functions:
            function_rows = [lookup[(fid, algorithm)] for algorithm in ordered]
            u_cells = [format_u(row["u_competitor"]) for row in function_rows]
            raw_cells = [format_p(row["p_raw"]) for row in function_rows]
            adjusted_cells = []
            for row in function_rows:
                p_adjusted = format_p(row["p_bonferroni"])
                symbol = decision_symbol(str(row["decision"]))
                cell = f"{p_adjusted} ({symbol})"
                if symbol != "≈":
                    cell = f"**{cell}**"
                adjusted_cells.append(cell)

            # The blank column reproduces the visual separation used by the
            # existing result matrices between CMA-ES and the other baselines.
            lines.append(
                f"| **f{fid}** | U | reference | {u_cells[0]} |  | "
                + " | ".join(u_cells[1:])
                + " |"
            )
            lines.append(
                f"|  | p | — | {raw_cells[0]} |  | "
                + " | ".join(raw_cells[1:])
                + " |"
            )
            lines.append(
                f"|  | p_Bonf | — | {adjusted_cells[0]} |  | "
                + " | ".join(adjusted_cells[1:])
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
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    experiments = args.experiments.resolve()
    output = args.output.resolve()
    if not experiments.is_dir():
        raise MwuError(f"Experiment directory does not exist: {experiments}")

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

    if len(all_rows) != 2051:
        raise MwuError(f"Calculated {len(all_rows)} total rows, expected 2051")

    if args.dry_run:
        print(f"Dry run passed: {len(SETTINGS)} settings, {len(by_cell)} cells, 2051 tests")
        return 0

    for (suite, dimension), rows in sorted(by_cell.items()):
        cell = output / suite / f"d{dimension}"
        atomic_write_text(cell / "details.csv", csv_text(rows, FIELDS))
        atomic_write_text(cell / "README.md", render_readme(suite, dimension, rows))
    atomic_write_text(
        output / "mann_whitney_u_all_settings.csv",
        csv_text(all_rows, FIELDS),
    )

    print(
        f"Wrote 10 cell READMEs, 10 details.csv files, and 1 aggregate CSV under {output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MwuError, OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
