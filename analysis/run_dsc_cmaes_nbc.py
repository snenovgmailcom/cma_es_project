#!/usr/bin/env python3
"""DSCTool comparison of MSC-CMA-ES, CMAES-NBC and BIPOP-CMA-ES.

Reads stored terminal errors at each configured nominal budget. In particular,
CMAES-NBC errors retain their author-runner stopping and zeroing conventions;
this script does not reconstruct exact-budget errors or run trajectories.
Requires the existing analysis/run_iohanalyzer_dsc.py plus NumPy. Statistical
operations use that runner's DSCTool API. DSC_PASSWORD supplies the password;
otherwise it is requested interactively. No credentials are stored here.

Public helpers for the report builder:
  validate_inputs(experiments): audit all ten input settings, without writes.
  validate_cached_outputs(experiments, output): audit saved responses and CSVs
      against current PKLs without contacting the service or changing output.
"""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import run_iohanalyzer_dsc as core
from run_iohanalyzer_dsc import (
    ALPHA, EXPECTED_RUNS, SUITE_FUNCTIONS, AuditError,
    expected_problem_name, load_pickle, parse_function_id, scalar,
    sha256_file, validate_payload_algorithm, warn,
)

ALGORITHMS = ("MSC-CMA", "CMAES-NBC", "BIPOP-CMA")
SETTINGS = (
    core.Setting("cec2014", 10, 100_000, 3),
    core.Setting("cec2014", 30, 300_000, 3),
    core.Setting("cec2017", 10, 100_000, 3),
    core.Setting("cec2017", 30, 300_000, 3),
    core.Setting("cec2020", 5, 50_000, 3),
    core.Setting("cec2020", 10, 1_000_000, 3),
    core.Setting("cec2020", 15, 3_000_000, 3),
    core.Setting("cec2020", 20, 10_000_000, 3),
    core.Setting("cec2022", 10, 200_000, 3),
    core.Setting("cec2022", 20, 1_000_000, 3),
)
DEFAULT_OUTPUT = Path("related_comparisons/cmaes_nbc/dsc")

# The statistical engine remains unchanged; only this comparison's input grid
# and the author runner's seed identifiers differ from the standard benchmark.
core.BASE_ALGORITHMS = ALGORITHMS
core.SETTINGS = SETTINGS
core.SETTING_BY_TOKEN = {setting.token: setting for setting in SETTINGS}
core.PAYLOAD_ALGORITHM_ALIASES["CMAES-NBC"] = frozenset(("CMAES-NBC",))
core.PLAINTEXT_DSC_PASSWORD = ""

# Adapted from the validated core loader. The sole validation difference is
# accepting actual unique CMAES-NBC seed numbers, without pairing or relabeling.
def load_setting_inputs(
    experiments: Path,
    setting: core.Setting,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    expected_functions = SUITE_FUNCTIONS[setting.suite]
    algorithms = setting.algorithms
    if len(algorithms) != setting.expected_k:
        raise AuditError(f"{setting.token}: internal algorithm-count mismatch")

    request_algorithms: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []
    overrun_records: list[tuple[str, int, int, int]] = []

    for algorithm in algorithms:
        source_dir = (
            experiments
            / setting.suite
            / f"d{setting.dimension}"
            / algorithm
            / f"maxevals_{setting.budget}"
        )
        if not source_dir.is_dir():
            raise AuditError(f"Missing algorithm directory: {source_dir}")

        present: dict[int, Path] = {}
        for path in source_dir.glob("*.pkl"):
            try:
                function_id = parse_function_id(path.stem)
            except AuditError:
                continue
            if function_id in present:
                raise AuditError(f"Duplicate PKL for f{function_id} in {source_dir}")
            present[function_id] = path

        missing = sorted(set(expected_functions) - set(present))
        if missing:
            names = ", ".join(f"f{function_id}" for function_id in missing)
            raise AuditError(f"{source_dir}: missing {names}")
        extra = sorted(set(present) - set(expected_functions))
        if extra:
            warn(
                f"{source_dir}: ignoring unexpected functions "
                + ", ".join(f"f{function_id}" for function_id in extra)
            )

        problems: list[dict[str, Any]] = []
        for function_id in expected_functions:
            path = present[function_id]
            payload = load_pickle(path)
            required = {
                "suite",
                "dim",
                "func",
                "algorithm",
                "maxevals",
                "n_runs",
                "seeds",
                "errors",
            }
            missing_keys = sorted(required - set(payload))
            if missing_keys:
                raise AuditError(f"{path}: missing PKL keys: {', '.join(missing_keys)}")

            observed_suite = str(scalar(payload["suite"])).lower()
            observed_dimension = int(scalar(payload["dim"]))
            observed_function = parse_function_id(payload["func"])
            observed_algorithm = str(scalar(payload["algorithm"]))
            observed_budget = int(scalar(payload["maxevals"]))
            observed_runs = int(scalar(payload["n_runs"]))

            if observed_suite != setting.suite:
                raise AuditError(f"{path}: suite mismatch: {observed_suite!r}")
            if observed_dimension != setting.dimension:
                raise AuditError(f"{path}: dimension mismatch: {observed_dimension}")
            if observed_function != function_id:
                raise AuditError(f"{path}: function mismatch: f{observed_function}")
            if observed_budget != setting.budget:
                raise AuditError(f"{path}: budget mismatch: {observed_budget}")
            if observed_runs != EXPECTED_RUNS:
                raise AuditError(f"{path}: n_runs={observed_runs}, expected {EXPECTED_RUNS}")
            validate_payload_algorithm(path, algorithm, observed_algorithm)

            raw_errors = np.asarray(payload["errors"])
            raw_seeds = np.asarray(payload["seeds"])
            if raw_errors.shape != (EXPECTED_RUNS,):
                raise AuditError(f"{path}: errors shape is {raw_errors.shape}, expected (51,)")
            if raw_errors.dtype.kind not in "fiu" or raw_errors.dtype.kind == "b":
                raise AuditError(f"{path}: errors are not a real numeric vector")
            if raw_seeds.shape != (EXPECTED_RUNS,):
                raise AuditError(f"{path}: seeds shape is {raw_seeds.shape}, expected (51,)")
            if raw_seeds.dtype.kind not in "iu" or raw_seeds.dtype.kind == "b":
                raise AuditError(f"{path}: seeds are not an integer vector")
            errors = raw_errors.astype(np.float64, copy=False)
            seeds = raw_seeds.astype(np.int64, copy=False)
            if not np.isfinite(errors).all():
                raise AuditError(f"{path}: errors contain NaN or infinity")
            if algorithm == "CMAES-NBC":
                if len(np.unique(raw_seeds)) != EXPECTED_RUNS:
                    raise AuditError(f"{path}: CMAES-NBC seeds must be 51 unique integers")
                if "run_ids" in payload:
                    run_ids = np.asarray(payload["run_ids"])
                    if (
                        run_ids.shape != (EXPECTED_RUNS,)
                        or run_ids.dtype.kind not in "iu"
                        or not np.array_equal(np.sort(run_ids), np.arange(EXPECTED_RUNS))
                    ):
                        raise AuditError(f"{path}: run_ids must contain exactly 0:50")
            elif not np.array_equal(np.sort(seeds), np.arange(EXPECTED_RUNS)):
                raise AuditError(f"{path}: seeds must be exactly 0:50")

            nfev_total_known = "nfev_total_per_seed" in payload
            nfev_total_min: int | str = ""
            nfev_total_max: int | str = ""
            overrun_runs = 0
            max_budget_excess = 0
            if nfev_total_known:
                nfev = np.asarray(payload["nfev_total_per_seed"], dtype=np.float64)
                if nfev.shape != (EXPECTED_RUNS,):
                    raise AuditError(f"{path}: invalid nfev_total_per_seed shape")
                if not np.isfinite(nfev).all() or (nfev < 0).any():
                    raise AuditError(f"{path}: invalid nfev_total_per_seed values")
                if not np.equal(nfev, np.floor(nfev)).all():
                    raise AuditError(f"{path}: non-integer nfev_total_per_seed values")
                nfev_int = nfev.astype(np.int64)
                nfev_total_min = int(nfev_int.min())
                nfev_total_max = int(nfev_int.max())
                overrun_runs = int(np.count_nonzero(nfev_int > setting.budget))
                max_budget_excess = max(0, nfev_total_max - setting.budget)
                if overrun_runs:
                    overrun_records.append(
                        (algorithm, function_id, overrun_runs, max_budget_excess)
                    )

            transmitted = [float(value) for value in errors]
            if len(transmitted) != EXPECTED_RUNS or not all(
                math.isfinite(value) for value in transmitted
            ):
                raise AuditError(f"{path}: failed conversion to 51 finite Python floats")

            problems.append(
                {
                    "name": expected_problem_name(function_id, setting.dimension),
                    "data": transmitted,
                }
            )
            manifest.append(
                {
                    "suite": setting.suite,
                    "dimension": setting.dimension,
                    "budget": setting.budget,
                    "algorithm": algorithm,
                    "payload_algorithm": observed_algorithm,
                    "function_id": function_id,
                    "n_runs": EXPECTED_RUNS,
                    "terminal_value_source": "pkl.errors",
                    "nfev_total_known": nfev_total_known,
                    "nfev_total_min": nfev_total_min,
                    "nfev_total_max": nfev_total_max,
                    "overrun_runs": overrun_runs,
                    "max_budget_excess": max_budget_excess,
                    "source_path": str(path.resolve()),
                    "source_sha256": sha256_file(path),
                }
            )

        request_algorithms.append({"algorithm": algorithm, "problems": problems})

    expected_names = [
        expected_problem_name(function_id, setting.dimension)
        for function_id in expected_functions
    ]
    for algorithm_block in request_algorithms:
        actual_names = [problem["name"] for problem in algorithm_block["problems"]]
        if actual_names != expected_names:
            raise AuditError(
                f"{setting.token}: problem order differs for {algorithm_block['algorithm']}"
            )

    rank_request = {
        "epsilon": 0,
        "monte_carlo_iterations": 0,
        "method": {"name": "AD", "alpha": ALPHA},
        "data": request_algorithms,
    }
    if overrun_records:
        total_runs = sum(record[2] for record in overrun_records)
        maximum_excess = max(record[3] for record in overrun_records)
        warn(
            f"{setting.token}: {len(overrun_records)} PKL files contain "
            f"{total_runs} batch-end overruns; maximum B+{maximum_excess}. "
            "Stored pkl['errors'] values are preserved unchanged for historical "
            "DSC reproduction; see input_manifest.csv."
        )
    return rank_request, manifest

core.load_setting_inputs = load_setting_inputs


def validate_inputs(experiments: Path) -> None:
    """Audit every required PKL; do not write files or contact DSCTool."""
    experiments = Path(experiments).expanduser().resolve()
    if not experiments.is_dir():
        raise AuditError(f"Experiment root does not exist: {experiments}")
    for setting in SETTINGS:
        load_setting_inputs(experiments, setting)


def collect_all_orderings(output: Path) -> list[dict[str, Any]]:
    combined = []
    for setting in SETTINGS:
        directory = (
            output / setting.suite / f"d{setting.dimension}"
            / f"budget_{setting.budget}"
        )
        for scope in ("all", "composition"):
            rows = core.read_csv_rows(directory / f"ordering_{scope}.csv")
            if len(rows) != 3 or {row.get("algorithm") for row in rows} != set(ALGORITHMS):
                raise AuditError(f"{setting.token}/{scope}: wrong ordering algorithm grid")
            for row in rows:
                if (
                    row.get("suite") != setting.suite
                    or int(row.get("dimension", -1)) != setting.dimension
                    or int(row.get("budget", -1)) != setting.budget
                    or row.get("scope") != scope
                    or int(row.get("k", -1)) != 3
                ):
                    raise AuditError(f"{setting.token}/{scope}: inconsistent ordering metadata")
            # core.main compares position_min to integer 1 when selecting best rows.
            for row in rows:
                row["position_min"] = int(row["position_min"])
            combined.extend(rows)
    if len(combined) != 60:
        raise AuditError(f"Expected 60 combined DSC ordering rows, got {len(combined)}")
    return combined


core.collect_all_orderings = collect_all_orderings


def _same_file(expected: Path, cached: Path) -> None:
    if not cached.is_file():
        raise AuditError(f"Missing DSC cache file: {cached}")
    if expected.read_bytes() != cached.read_bytes():
        raise AuditError(f"Stale or inconsistent DSC cache file: {cached}")


class _ReplayClient:
    """Replay saved responses only when the newly generated request matches."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.scope_index = -1
        self.seen: set[str] = set()

    def post(self, operation: str, body: bytes) -> core.HttpJsonResponse:
        if operation == "rank":
            stem = "rank"
        elif operation == "omnibus":
            self.scope_index += 1
            if self.scope_index not in (0, 1):
                raise AuditError("Unexpected extra omnibus request during DSC replay")
            stem = f"omnibus_{('all', 'composition')[self.scope_index]}"
        elif operation == "posthoc" and self.scope_index in (0, 1):
            stem = f"posthoc_{('all', 'composition')[self.scope_index]}"
        else:
            raise AuditError(f"Unexpected DSC replay operation: {operation}")
        if stem in self.seen:
            raise AuditError(f"Duplicate DSC replay operation: {stem}")
        self.seen.add(stem)
        request = self.directory / f"{stem}_request.json"
        if not request.is_file() or request.read_bytes() != body:
            raise AuditError(f"Current inputs/request differ from DSC cache: {request}")
        digest = self.directory / f"{stem}_request.sha256"
        expected_digest = core.hashlib.sha256(body).hexdigest() + f"  {request.name}\n"
        if not digest.is_file() or digest.read_text(encoding="utf-8") != expected_digest:
            raise AuditError(f"Missing or incorrect DSC request hash: {digest}")
        response = self.directory / f"{stem}_response.json"
        if not response.is_file():
            raise AuditError(f"Missing DSC response: {response}")
        response_body = response.read_bytes()
        try:
            decoded = json.loads(response_body)
        except (ValueError, UnicodeDecodeError) as exc:
            raise AuditError(f"Invalid cached DSC JSON: {response}") from exc
        if not isinstance(decoded, dict):
            raise AuditError(f"Cached DSC response is not an object: {response}")
        return core.HttpJsonResponse(200, f"cached:{response}", response_body, decoded)


def validate_cached_outputs(experiments: Path, output: Path) -> None:
    """Refuse stale PKLs, requests, responses or derived CSVs; no network calls.

    Existing core validators reconstruct all derived files in a temporary
    directory. Exact comparison includes each input_manifest source SHA256 and
    source path, so a changed or moved PKL cannot silently reuse old results.
    """
    experiments = Path(experiments).expanduser().resolve()
    output = Path(output).expanduser().resolve()
    if not output.is_dir():
        raise AuditError(f"Missing DSC cache directory: {output}")
    with tempfile.TemporaryDirectory(prefix="cmaes-nbc-dsc-cache-") as temporary:
        replay_root = Path(temporary)
        for setting in SETTINGS:
            relative = Path(setting.suite) / f"d{setting.dimension}" / f"budget_{setting.budget}"
            cached = output / relative
            core.run_setting(setting, experiments, replay_root, _ReplayClient(cached))
            reconstructed = replay_root / relative
            for expected in reconstructed.iterdir():
                if expected.is_file():
                    _same_file(expected, cached / expected.name)
            # The core deliberately omits posthoc files after a nonsignificant
            # omnibus. Reject leftovers as stale rather than silently reusing them.
            for scope in ("all", "composition"):
                for suffix in ("request.json", "request.sha256", "response.json"):
                    name = f"posthoc_{scope}_{suffix}"
                    if (cached / name).exists() and not (reconstructed / name).exists():
                        raise AuditError(f"Stale posthoc cache file: {cached / name}")
        combined = collect_all_orderings(replay_root)
        core.atomic_csv(
            replay_root / "algorithm_orderings_all_settings.csv", combined, core.ORDERING_FIELDS
        )
        best_rows = [row for row in combined if row["position_min"] == 1]
        core.atomic_csv(replay_root / "best_algorithms.csv", best_rows, core.ORDERING_FIELDS)
        for name in ("algorithm_orderings_all_settings.csv", "best_algorithms.csv"):
            _same_file(replay_root / name, output / name)


_ORIGINAL_BUILD_PARSER = core.build_parser


def build_parser():
    parser = _ORIGINAL_BUILD_PARSER()
    parser.description = (
        "Compare MSC-CMA-ES, CMAES-NBC and BIPOP-CMA-ES in ten settings "
        "using stored terminal errors and the DSCTool service."
    )
    parser.set_defaults(output=DEFAULT_OUTPUT)
    for action in parser._actions:
        if action.dest == "output":
            action.help = f"output root (default: {DEFAULT_OUTPUT})"
        elif action.dest == "setting":
            action.help = "run one of the configured 10 settings; repeatable"
    return parser


core.build_parser = build_parser


def main(argv: Sequence[str] | None = None) -> int:
    return core.main(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, core.pickle.UnpicklingError, ValueError) as exc:
        print(f"ERROR: {exc}", file=core.sys.stderr)
        raise SystemExit(1) from exc
