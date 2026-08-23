#!/usr/bin/env python3

from pathlib import Path
from typing import Sequence
import run_iohanalyzer_dsc as core


# Related-work comparison:
# MSC-CMA-ES vs NEA2+ vs BIPOP-CMA-ES.
ALGORITHMS = (
    "MSC-CMA",
    "NEA2PLUS-PY",
    "BIPOP-CMA",
)

SETTINGS = (
    core.Setting("cec2017", 10,   100_000, 3),
    core.Setting("cec2020",  5,    50_000, 3),
    core.Setting("cec2020", 10, 1_000_000, 3),
    core.Setting("cec2020", 15, 3_000_000, 3),
    core.Setting("cec2022", 10,   200_000, 3),
    core.Setting("cec2022", 20, 1_000_000, 3),
)

# Reconfigure the validated generic DSC runner.
core.BASE_ALGORITHMS = ALGORITHMS
core.PAYLOAD_ALGORITHM_ALIASES["NEA2PLUS-PY"] = frozenset(
    ("NEA2PLUS-PY",)
)
core.SETTINGS = SETTINGS
core.SETTING_BY_TOKEN = {s.token: s for s in SETTINGS}

# Important: never use the placeholder/default plaintext password from
# the old runner. If DSC_PASSWORD is not set, getpass will ask interactively.
core.PLAINTEXT_DSC_PASSWORD = "<парола>"


def collect_all_orderings(output: Path):
    combined = []
    expected_algorithms = set(ALGORITHMS)

    for setting in SETTINGS:
        directory = (
            output
            / setting.suite
            / f"d{setting.dimension}"
            / f"budget_{setting.budget}"
        )

        for scope in ("all", "composition"):
            rows = core.read_csv_rows(directory / f"ordering_{scope}.csv")

            if len(rows) != 3:
                raise core.AuditError(
                    f"{setting.token}/{scope}: "
                    f"expected 3 ordering rows, got {len(rows)}"
                )

            algorithms = {row.get("algorithm", "") for row in rows}
            if algorithms != expected_algorithms:
                raise core.AuditError(
                    f"{setting.token}/{scope}: wrong algorithm set: "
                    f"{sorted(algorithms)}"
                )

            for row in rows:
                if (
                    row.get("suite") != setting.suite
                    or int(row.get("dimension", -1)) != setting.dimension
                    or int(row.get("budget", -1)) != setting.budget
                    or row.get("scope") != scope
                    or int(row.get("k", -1)) != 3
                ):
                    raise core.AuditError(
                        f"{setting.token}/{scope}: "
                        "inconsistent ordering metadata"
                    )

            combined.extend(rows)

    expected_n = len(SETTINGS) * 2 * 3
    if len(combined) != expected_n:
        raise core.AuditError(
            f"Combined grid has {len(combined)} rows, "
            f"expected {expected_n}"
        )

    return combined


core.collect_all_orderings = collect_all_orderings


def main(argv: Sequence[str] | None = None) -> int:
    return core.main(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        core.AuditError,
        OSError,
    ) as exc:
        print(f"ERROR: {exc}", file=core.sys.stderr)
        raise SystemExit(1) from exc
