#!/usr/bin/env python3
"""
DSC campaign for the C-ONLY positioning comparison.

Portfolio (k = 8): the seven benchmark baselines plus the full MSC-CMA
schedule plus MSC-CMA-Conly.  NEA2+ is intentionally excluded here: its
three-way DSC pages live in related_comparisons/nea2plus.

Scope: composition functions only.  C-ONLY runs exist only for the
composition class in most cells, so this adapter rebinds the core
runner's SUITE_FUNCTIONS to the composition sets; as a consequence the
"all" and "composition" scopes coincide and both orderings describe the
composition class.  This is documented on the generated pages.

Everything else (payload construction, DSCTool web-service calls,
auditing, CSV layout) is inherited unchanged from
analysis/run_iohanalyzer_dsc.py.  Credentials are handled exactly as in
the core runner: set DSC_PASSWORD in the environment or answer the
interactive prompt.

Suggested first invocation (single cell, then the full grid):
  python analysis/run_dsc_conly.py --setting cec2020:5:50000 \
      --experiments experiments --output related_comparisons/conly/dsc
"""

from pathlib import Path
from typing import Sequence

import run_iohanalyzer_dsc as core


ALGORITHMS = (
    "MSC-CMA",
    "MSC-CMA-Conly",
    "ARRDE",
    "BIPOP-CMA",
    "LSRTDE",
    "NLSHADE-RSP",
    "j2020",
    "jSO",
)

K = len(ALGORITHMS)

SETTINGS = (
    core.Setting("cec2014", 10, 100_000, K),
    core.Setting("cec2017", 10, 100_000, K),
    core.Setting("cec2020", 5, 50_000, K),
    core.Setting("cec2020", 10, 1_000_000, K),
    core.Setting("cec2020", 15, 3_000_000, K),
    core.Setting("cec2020", 20, 10_000_000, K),
    core.Setting("cec2022", 10, 200_000, K),
    core.Setting("cec2022", 20, 1_000_000, K),
)

# Reconfigure the validated generic DSC runner.
core.BASE_ALGORITHMS = ALGORITHMS
core.PAYLOAD_ALGORITHM_ALIASES["MSC-CMA-Conly"] = frozenset(
    ("MSC-CMA-Conly",)
)
core.SETTINGS = SETTINGS
core.SETTING_BY_TOKEN = {s.token: s for s in SETTINGS}

# Composition-only payloads: the audits and the payload builder read
# SUITE_FUNCTIONS, so rebinding it to the composition sets restricts
# the whole pipeline to the composition class.
core.SUITE_FUNCTIONS = {
    suite: tuple(funcs)
    for suite, funcs in core.COMPOSITION_FUNCTIONS.items()
}


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

            if len(rows) != K:
                raise core.AuditError(
                    f"{setting.token}/{scope}: "
                    f"expected {K} ordering rows, got {len(rows)}"
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
                    or int(row.get("k", -1)) != K
                ):
                    raise core.AuditError(
                        f"{setting.token}/{scope}: "
                        "inconsistent ordering metadata"
                    )

            combined.extend(rows)

    expected_n = len(SETTINGS) * 2 * K
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
