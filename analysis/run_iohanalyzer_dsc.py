#!/usr/bin/env python3
"""Obtain fixed-budget DSC algorithm orderings through the DSCTool REST API.

IOHanalyzer's DSC interface is a client for the same REST operations used here:
rank -> omnibus -> posthoc.  This script reads the project's trusted PKL files, sends the
51 terminal errors without clipping, rounding, sorting, or aggregation, and
exports the resulting per-function ranks and all/composition orderings.

The script does not implement Anderson-Darling, DSC, Friedman, or Holm locally.
"""

from __future__ import annotations

import argparse
import base64
import csv
import getpass
import hashlib
import json
import math
import os
import pickle
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    import numpy as np
except ImportError as exc:  # NumPy is also required to unpickle the experiment files.
    raise SystemExit("NumPy is required. Activate the project's Python environment.") from exc


ALPHA = 0.05
EXPECTED_RUNS = 51
DEFAULT_BASE_URL = "https://ws.ijs.si/dsc/service"
DEFAULT_DSC_USERNAME = "snenov"

# Plaintext credential explicitly requested for this script.
# DSC_PASSWORD from the environment can still override it.
PLAINTEXT_DSC_PASSWORD = "<парола>"

BASE_ALGORITHMS = (
    "ARRDE",
    "BIPOP-CMA",
    "LSRTDE",
    "MSC-CMA",
    "NLSHADE-RSP",
    "j2020",
    "jSO",
)

PAYLOAD_ALGORITHM_ALIASES: dict[str, frozenset[str]] = {
    "ARRDE": frozenset(("ARRDE", "ARRDE-minionpy")),
    "BIPOP-CMA": frozenset(("BIPOP-CMA", "BIPOP-CMA-pycma")),
    "LSRTDE": frozenset(("LSRTDE", "LSRTDE-minionpy")),
    "MSC-CMA": frozenset(("MSC-CMA",)),
    "NLSHADE-RSP": frozenset(("NLSHADE-RSP", "NLSHADE-RSP-minionpy")),
    "j2020": frozenset(("j2020", "j2020-minionpy")),
    "jSO": frozenset(("jSO", "jSO-minionpy")),
}

SUITE_FUNCTIONS: dict[str, tuple[int, ...]] = {
    "cec2014": tuple(range(1, 31)),
    "cec2017": (1, *range(3, 31)),
    "cec2020": tuple(range(1, 11)),
    "cec2022": tuple(range(1, 13)),
}

COMPOSITION_FUNCTIONS: dict[str, tuple[int, ...]] = {
    "cec2014": tuple(range(23, 31)),
    "cec2017": tuple(range(21, 31)),
    "cec2020": tuple(range(8, 11)),
    "cec2022": tuple(range(9, 13)),
}


@dataclass(frozen=True)
class Setting:
    suite: str
    dimension: int
    budget: int
    expected_k: int

    @property
    def token(self) -> str:
        return f"{self.suite}:{self.dimension}:{self.budget}"

    @property
    def algorithms(self) -> tuple[str, ...]:
        return BASE_ALGORITHMS


SETTINGS = (
    Setting("cec2014", 10, 100_000, 7),
    Setting("cec2014", 10, 1_000_000, 7),
    Setting("cec2014", 30, 300_000, 7),
    Setting("cec2014", 30, 1_000_000, 7),
    Setting("cec2017", 10, 100_000, 7),
    Setting("cec2017", 10, 1_000_000, 7),
    Setting("cec2017", 30, 300_000, 7),
    Setting("cec2017", 30, 1_000_000, 7),
    Setting("cec2020", 5, 50_000, 7),
    Setting("cec2020", 5, 1_000_000, 7),
    Setting("cec2020", 10, 1_000_000, 7),
    Setting("cec2020", 10, 20_000_000, 7),
    Setting("cec2020", 15, 3_000_000, 7),
    Setting("cec2020", 20, 10_000_000, 7),
    Setting("cec2022", 10, 200_000, 7),
    Setting("cec2022", 10, 1_000_000, 7),
    Setting("cec2022", 20, 1_000_000, 7),
)

SETTING_BY_TOKEN = {setting.token: setting for setting in SETTINGS}


class AuditError(RuntimeError):
    """Raised when input or service output does not match the expected grid."""


@dataclass(frozen=True)
class HttpJsonResponse:
    status: int
    url: str
    body: bytes
    decoded: dict[str, Any]


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr, flush=True)


def parse_function_id(value: Any) -> int:
    text = str(scalar(value))
    match = re.fullmatch(r"[fF]?(\d+)", text)
    if match is None:
        raise AuditError(f"Invalid function id: {text!r}")
    return int(match.group(1))


def scalar(value: Any) -> Any:
    array = np.asarray(value)
    if array.size != 1:
        raise AuditError(f"Expected a scalar, got shape {array.shape}")
    return array.reshape(-1)[0].item()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_request_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def atomic_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("wb") as stream:
        stream.write(value)
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    atomic_bytes(path, value.encode("utf-8"))


def atomic_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(fields), extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise AuditError(f"Missing result file: {path}")
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def expected_problem_name(function_id: int, dimension: int) -> str:
    return f"F{function_id}_{dimension}D"


def parse_problem_name(name: Any, dimension: int) -> int:
    text = str(name)
    match = re.fullmatch(rf"F(\d+)_{dimension}D", text)
    if match is None:
        raise AuditError(f"Unexpected problem name: {text!r}")
    return int(match.group(1))


def load_pickle(path: Path) -> dict[str, Any]:
    # Python pickle may execute code. Only project-generated, trusted files are valid input.
    with path.open("rb") as stream:
        payload = pickle.load(stream)
    if not isinstance(payload, dict):
        raise AuditError(f"{path}: PKL root is not a dict")
    return payload


def validate_payload_algorithm(path: Path, canonical: str, observed: str) -> None:
    if observed not in PAYLOAD_ALGORITHM_ALIASES[canonical]:
        raise AuditError(
            f"{path}: PKL algorithm {observed!r} does not match canonical {canonical!r}"
        )


def load_setting_inputs(
    experiments: Path,
    setting: Setting,
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
            if not np.array_equal(np.sort(seeds), np.arange(EXPECTED_RUNS)):
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


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects so Basic credentials are never forwarded elsewhere."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


class DscClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: float,
        retries: int,
        ca_bundle: Path | None,
        insecure: bool,
    ) -> None:
        base_url = base_url.rstrip("/")
        parsed = urllib.parse.urlparse(base_url)
        if parsed.scheme.lower() != "https" or not parsed.netloc:
            raise AuditError("--base-url must be a valid HTTPS URL")
        if parsed.query or parsed.fragment:
            raise AuditError("--base-url must not contain a query or fragment")
        if not username or not password:
            raise AuditError("Empty DSC username or password")
        if timeout <= 0:
            raise AuditError("--timeout must be positive")
        if retries < 0:
            raise AuditError("--retries cannot be negative")
        if ca_bundle is not None and not ca_bundle.is_file():
            raise AuditError(f"CA bundle does not exist: {ca_bundle}")

        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
        if insecure:
            if ca_bundle is not None:
                raise AuditError("--ca-bundle and --insecure cannot be used together")
            warn("TLS certificate verification is DISABLED (--insecure).")
            self.ssl_context = ssl._create_unverified_context()
        else:
            self.ssl_context = ssl.create_default_context(
                cafile=str(ca_bundle) if ca_bundle is not None else None
            )
        self.opener = urllib.request.build_opener(
            NoRedirectHandler(),
            urllib.request.HTTPSHandler(context=self.ssl_context),
        )
        credentials = f"{username}:{password}".encode("utf-8")
        self.authorization = "Basic " + base64.b64encode(credentials).decode("ascii")

    def post(self, operation: str, body: bytes) -> HttpJsonResponse:
        if not re.fullmatch(r"[a-z]+", operation):
            raise AuditError(f"Invalid operation: {operation!r}")
        url = f"{self.base_url}/{operation}"

        for attempt in range(self.retries + 1):
            request = urllib.request.Request(
                url,
                data=body,
                method="POST",
                headers={
                    "Authorization": self.authorization,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "cma-es-project-dsc-client/1.0",
                },
            )
            try:
                with self.opener.open(
                    request,
                    timeout=self.timeout,
                ) as response:
                    status = response.status
                    response_body = response.read()
                if status < 200 or status >= 300:
                    raise AuditError(f"POST {url} returned HTTP {status}")
                try:
                    decoded = json.loads(response_body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise AuditError(f"POST {url} returned invalid JSON") from exc
                if not isinstance(decoded, dict):
                    raise AuditError(f"POST {url} returned a non-object JSON response")
                return HttpJsonResponse(
                    status=status,
                    url=url,
                    body=response_body,
                    decoded=decoded,
                )
            except urllib.error.HTTPError as exc:
                error_body = exc.read().decode("utf-8", errors="replace")[:2000]
                retryable = exc.code in (429, 500, 502, 503, 504)
                if retryable and attempt < self.retries:
                    time.sleep(2**attempt)
                    continue
                raise AuditError(
                    f"POST {url} failed with HTTP {exc.code}: {error_body}"
                ) from exc
            except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
                if attempt < self.retries:
                    time.sleep(2**attempt)
                    continue
                raise AuditError(f"POST {url} failed: {exc}") from exc

        raise AssertionError("unreachable")


def unwrap_response(response: Mapping[str, Any], operation: str) -> dict[str, Any]:
    if response.get("success") is not True:
        message = response.get("message") or response.get("error") or "unknown service error"
        raise AuditError(f"DSCTool {operation} reported failure: {message}")
    result = response.get("result")
    if not isinstance(result, dict):
        raise AuditError(f"DSCTool {operation} response has no result object")
    return result


def unwrap_posthoc_response(response: Mapping[str, Any], operation: str) -> list[Any]:
    if response.get("success") is not True:
        message = response.get("message") or response.get("error") or "unknown service error"
        raise AuditError(f"DSCTool {operation} reported failure: {message}")
    result = response.get("result")
    if not isinstance(result, list):
        raise AuditError(f"DSCTool {operation} response has no result list")
    return result


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise AuditError(f"{label} is boolean, not numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f"{label} is not numeric: {value!r}") from exc
    if not math.isfinite(number):
        raise AuditError(f"{label} is not finite")
    return number


def validate_rank_result(
    result: Mapping[str, Any],
    setting: Setting,
) -> list[dict[str, Any]]:
    try:
        number_algorithms = int(result["number_algorithms"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AuditError("Rank response has invalid number_algorithms") from exc
    if number_algorithms != setting.expected_k:
        raise AuditError(
            f"Rank response number_algorithms={number_algorithms}, expected {setting.expected_k}"
        )

    valid_methods = result.get("valid_methods")
    if not isinstance(valid_methods, list) or "friedman" not in valid_methods:
        raise AuditError(f"Rank response does not allow Friedman: {valid_methods!r}")
    if not isinstance(result.get("parametric_tests"), bool):
        raise AuditError("Rank response parametric_tests is not boolean")

    ranked_matrix = result.get("ranked_matrix")
    if not isinstance(ranked_matrix, list):
        raise AuditError("Rank response ranked_matrix is not a list")

    expected_functions = set(SUITE_FUNCTIONS[setting.suite])
    expected_algorithms = set(setting.algorithms)
    seen_functions: set[int] = set()
    rows: list[dict[str, Any]] = []

    for block in ranked_matrix:
        if not isinstance(block, dict):
            raise AuditError("Rank response contains a non-object problem block")
        function_id = parse_problem_name(block.get("problem"), setting.dimension)
        if function_id in seen_functions:
            raise AuditError(f"Duplicate rank block for f{function_id}")
        seen_functions.add(function_id)
        algorithm_results = block.get("result")
        if not isinstance(algorithm_results, list):
            raise AuditError(f"Rank block f{function_id} has no result list")
        seen_algorithms: set[str] = set()
        rank2_sum = 0
        for algorithm_result in algorithm_results:
            if not isinstance(algorithm_result, dict):
                raise AuditError(f"Rank block f{function_id} contains a malformed row")
            algorithm = str(algorithm_result.get("algorithm"))
            if algorithm in seen_algorithms:
                raise AuditError(f"Duplicate rank for {algorithm}/f{function_id}")
            seen_algorithms.add(algorithm)
            rank = finite_number(
                algorithm_result.get("rank"), f"rank for {algorithm}/f{function_id}"
            )
            if rank < 1 or rank > setting.expected_k:
                raise AuditError(f"Rank outside [1,{setting.expected_k}] for {algorithm}/f{function_id}")
            rank2 = int(round(2 * rank))
            if not math.isclose(2 * rank, rank2, rel_tol=0.0, abs_tol=1e-12):
                raise AuditError(
                    f"Rank is not an integer/half-integer for {algorithm}/f{function_id}"
                )
            rank2_sum += rank2
            rows.append(
                {
                    "suite": setting.suite,
                    "dimension": setting.dimension,
                    "budget": setting.budget,
                    "function_id": function_id,
                    "problem": block["problem"],
                    "algorithm": algorithm,
                    "dsc_rank": rank,
                    "dsc_rank2": rank2,
                }
            )
        if seen_algorithms != expected_algorithms:
            raise AuditError(
                f"Rank block f{function_id} algorithm set differs from the requested set"
            )
        if rank2_sum != setting.expected_k * (setting.expected_k + 1):
            raise AuditError(
                f"Ranks for f{function_id} do not sum to k(k+1)/2"
            )

    if seen_functions != expected_functions:
        raise AuditError("Rank response function set differs from the requested set")
    if len(rows) != setting.expected_k * len(expected_functions):
        raise AuditError("Rank response grid has an unexpected size")

    algorithm_order = {algorithm: index for index, algorithm in enumerate(setting.algorithms)}
    rows.sort(key=lambda row: (row["function_id"], algorithm_order[row["algorithm"]]))
    return rows


def rank_blocks_for_functions(
    rank_result: Mapping[str, Any],
    function_ids: Iterable[int],
    dimension: int,
) -> list[dict[str, Any]]:
    wanted = set(function_ids)
    selected: list[dict[str, Any]] = []
    seen: set[int] = set()
    for block in rank_result["ranked_matrix"]:
        function_id = parse_problem_name(block["problem"], dimension)
        if function_id in wanted:
            selected.append(block)
            seen.add(function_id)
    if seen != wanted or len(selected) != len(wanted):
        raise AuditError("Could not select the exact requested rank subset")
    return selected


def validate_omnibus_and_make_ordering(
    result: Mapping[str, Any],
    rank_rows: Sequence[Mapping[str, Any]],
    setting: Setting,
    scope: str,
    function_ids: Sequence[int],
) -> list[dict[str, Any]]:
    algorithm_means = result.get("algorithm_means")
    if not isinstance(algorithm_means, list):
        raise AuditError(f"Omnibus {scope} response has no algorithm_means list")

    expected_algorithms = set(setting.algorithms)
    means: dict[str, float] = {}
    for row in algorithm_means:
        if not isinstance(row, dict):
            raise AuditError(f"Omnibus {scope} contains a malformed algorithm mean")
        algorithm = str(row.get("algorithm"))
        if algorithm in means:
            raise AuditError(f"Omnibus {scope} duplicates algorithm {algorithm}")
        mean_rank = finite_number(
            row.get("mean"), f"omnibus mean for {algorithm}/{scope}"
        )
        if mean_rank < 1 or mean_rank > setting.expected_k:
            raise AuditError(f"Omnibus mean outside [1,{setting.expected_k}] for {algorithm}/{scope}")
        means[algorithm] = mean_rank
    if set(means) != expected_algorithms:
        raise AuditError(f"Omnibus {scope} algorithm set differs from the requested set")

    wanted_functions = set(function_ids)
    rank_sum2 = {algorithm: 0 for algorithm in setting.algorithms}
    local_counts = {algorithm: 0 for algorithm in setting.algorithms}
    for row in rank_rows:
        if int(row["function_id"]) not in wanted_functions:
            continue
        algorithm = str(row["algorithm"])
        rank_sum2[algorithm] += int(row["dsc_rank2"])
        local_counts[algorithm] += 1
    for algorithm in setting.algorithms:
        if local_counts[algorithm] != len(function_ids):
            raise AuditError(f"Incomplete returned ranks for {algorithm}/{scope}")
        local_mean = rank_sum2[algorithm] / (2 * local_counts[algorithm])
        if not math.isclose(local_mean, means[algorithm], rel_tol=0.0, abs_tol=1e-12):
            raise AuditError(
                f"Omnibus mean for {algorithm}/{scope} does not match returned ranks"
            )

    p_value = finite_number(result.get("p_value"), f"omnibus p-value/{scope}")
    if p_value < 0 or p_value > 1:
        raise AuditError(f"Omnibus p-value outside [0,1] for {scope}")
    statistic = finite_number(result.get("t"), f"omnibus statistic/{scope}")
    if statistic < 0:
        raise AuditError(f"Negative omnibus statistic for {scope}")
    method = result.get("method")
    if not isinstance(method, dict) or str(method.get("name")) != "friedman":
        raise AuditError(f"Unexpected omnibus method for {scope}: {method!r}")
    message = str(result.get("message", ""))

    ordered = sorted(setting.algorithms, key=lambda algorithm: (rank_sum2[algorithm], algorithm))
    all_scores = list(rank_sum2.values())
    dense_group_by_score = {
        score: index + 1 for index, score in enumerate(sorted(set(all_scores)))
    }
    rows: list[dict[str, Any]] = []
    for algorithm in ordered:
        score = rank_sum2[algorithm]
        mean_rank = score / (2 * len(function_ids))
        position_min = 1 + sum(value < score for value in all_scores)
        position_max = sum(value <= score for value in all_scores)
        position_average = (position_min + position_max) / 2
        position_text = f"{position_average:g}"
        if position_min == position_max:
            position_interval = f"{position_min}/{setting.expected_k}"
        else:
            position_interval = (
                f"{position_min}-{position_max}/{setting.expected_k} (tie)"
            )
        rows.append(
            {
                "suite": setting.suite,
                "dimension": setting.dimension,
                "budget": setting.budget,
                "scope": scope,
                "position_average": position_average,
                "position_min": position_min,
                "position_max": position_max,
                "position_label": f"{position_text}/{setting.expected_k}",
                "position_interval": position_interval,
                "tie_size": position_max - position_min + 1,
                "dense_group": dense_group_by_score[score],
                "algorithm": algorithm,
                "rank_sum2": score,
                "mean_dsc_rank": mean_rank,
                "k": setting.expected_k,
                "n_functions": len(function_ids),
                "omnibus_method": "friedman",
                "omnibus_statistic": statistic,
                "omnibus_p_value": p_value,
                "omnibus_message": message,
            }
        )
    return rows


def validate_posthoc(
    result: Any,
    setting: Setting,
    scope: str,
    control: str,
) -> dict[str, dict[str, float]]:
    if not isinstance(result, list):
        raise AuditError(f"Posthoc {scope} result is not a list")
    expected = set(setting.algorithms) - {control}
    required = {"ZValue", "UnadjustedPValue", "Holm", "Hochberg"}
    tables: dict[str, dict[str, float]] = {}
    for block in result:
        if not isinstance(block, dict):
            raise AuditError(f"Malformed posthoc block for {scope}")
        name = str(block.get("name"))
        if name in tables:
            raise AuditError(f"Duplicate posthoc block {name}/{scope}")
        values = block.get("algorithms")
        if not isinstance(values, list):
            raise AuditError(f"Malformed posthoc values for {name}/{scope}")
        table: dict[str, float] = {}
        for row in values:
            if not isinstance(row, dict):
                raise AuditError(f"Malformed posthoc row for {name}/{scope}")
            algorithm = str(row.get("algorithm"))
            if algorithm in table:
                raise AuditError(f"Duplicate {algorithm} in {name}/{scope}")
            value = finite_number(row.get("value"), f"{name}/{algorithm}/{scope}")
            if name != "ZValue" and not 0.0 <= value <= 1.0:
                raise AuditError(f"Invalid probability in {name}/{algorithm}/{scope}")
            table[algorithm] = value
        if set(table) != expected:
            raise AuditError(f"Posthoc {name}/{scope} algorithm set is incorrect")
        tables[name] = table
    if set(tables) != required:
        raise AuditError(f"Posthoc {scope} blocks differ from {sorted(required)}")
    return tables


MANIFEST_FIELDS = (
    "suite",
    "dimension",
    "budget",
    "algorithm",
    "payload_algorithm",
    "function_id",
    "n_runs",
    "terminal_value_source",
    "nfev_total_known",
    "nfev_total_min",
    "nfev_total_max",
    "overrun_runs",
    "max_budget_excess",
    "source_path",
    "source_sha256",
)

RANK_FIELDS = (
    "suite",
    "dimension",
    "budget",
    "function_id",
    "problem",
    "algorithm",
    "dsc_rank",
    "dsc_rank2",
)

ORDERING_FIELDS = (
    "suite",
    "dimension",
    "budget",
    "scope",
    "position_average",
    "position_min",
    "position_max",
    "position_label",
    "position_interval",
    "tie_size",
    "dense_group",
    "algorithm",
    "rank_sum2",
    "mean_dsc_rank",
    "k",
    "n_functions",
    "omnibus_method",
    "omnibus_statistic",
    "omnibus_p_value",
    "omnibus_message",
    "dsc_status",
    "posthoc_control",
    "posthoc_holm_p",
)


def run_setting(
    setting: Setting,
    experiments: Path,
    output: Path,
    client: DscClient | None,
) -> list[dict[str, Any]]:
    directory = (
        output
        / setting.suite
        / f"d{setting.dimension}"
        / f"budget_{setting.budget}"
    )
    directory.mkdir(parents=True, exist_ok=True)
    print(
        f"[{setting.suite} D={setting.dimension} B={setting.budget} "
        f"k={setting.expected_k}] loading PKL files",
        flush=True,
    )

    rank_request, manifest = load_setting_inputs(experiments, setting)
    rank_request_body = json_request_bytes(rank_request)
    atomic_bytes(directory / "rank_request.json", rank_request_body)
    atomic_text(
        directory / "rank_request.sha256",
        hashlib.sha256(rank_request_body).hexdigest() + "  rank_request.json\n",
    )
    atomic_csv(directory / "input_manifest.csv", manifest, MANIFEST_FIELDS)
    print("  input audit passed; rank request written", flush=True)

    if client is None:
        return []

    rank_http = client.post("rank", rank_request_body)
    atomic_bytes(directory / "rank_response.json", rank_http.body)
    rank_result = unwrap_response(rank_http.decoded, "rank")
    rank_rows = validate_rank_result(rank_result, setting)
    atomic_csv(directory / "per_function_dsc_ranks.csv", rank_rows, RANK_FIELDS)

    scopes = {
        "all": SUITE_FUNCTIONS[setting.suite],
        "composition": COMPOSITION_FUNCTIONS[setting.suite],
    }
    all_orderings: list[dict[str, Any]] = []
    for scope, function_ids in scopes.items():
        ranked_matrix = rank_blocks_for_functions(
            rank_result, function_ids, setting.dimension
        )
        omnibus_request = {
            "method": {"name": "friedman", "alpha": ALPHA},
            "ranked_matrix": ranked_matrix,
            "number_algorithms": int(rank_result["number_algorithms"]),
            "parametric_tests": rank_result["parametric_tests"],
        }
        omnibus_request_body = json_request_bytes(omnibus_request)
        atomic_bytes(
            directory / f"omnibus_{scope}_request.json", omnibus_request_body
        )
        atomic_text(
            directory / f"omnibus_{scope}_request.sha256",
            hashlib.sha256(omnibus_request_body).hexdigest()
            + f"  omnibus_{scope}_request.json\n",
        )
        omnibus_http = client.post("omnibus", omnibus_request_body)
        atomic_bytes(
            directory / f"omnibus_{scope}_response.json", omnibus_http.body
        )
        omnibus_result = unwrap_response(
            omnibus_http.decoded, f"omnibus/{scope}"
        )
        ordering = validate_omnibus_and_make_ordering(
            omnibus_result,
            rank_rows,
            setting,
            scope,
            function_ids,
        )
        omnibus_p = float(ordering[0]["omnibus_p_value"])
        if omnibus_p < ALPHA:
            best = [row["algorithm"] for row in ordering if row["position_min"] == 1]
            if len(best) != 1:
                raise AuditError(
                    f"Significant omnibus {scope} has tied best controls: {best}"
                )
            control = str(best[0])
            posthoc_request = {
                "algorithm_means": omnibus_result["algorithm_means"],
                "k": setting.expected_k,
                "n": len(function_ids),
                "base_algorithm": control,
                "method": {"name": "friedman", "alpha": ALPHA},
            }
            posthoc_body = json_request_bytes(posthoc_request)
            atomic_bytes(directory / f"posthoc_{scope}_request.json", posthoc_body)
            atomic_text(
                directory / f"posthoc_{scope}_request.sha256",
                hashlib.sha256(posthoc_body).hexdigest()
                + f"  posthoc_{scope}_request.json\n",
            )
            posthoc_http = client.post("posthoc", posthoc_body)
            atomic_bytes(directory / f"posthoc_{scope}_response.json", posthoc_http.body)
            posthoc_result = unwrap_posthoc_response(
                posthoc_http.decoded, f"posthoc/{scope}"
            )
            posthoc = validate_posthoc(posthoc_result, setting, scope, control)
            for row in ordering:
                algorithm = str(row["algorithm"])
                row["posthoc_control"] = control
                row["posthoc_holm_p"] = "" if algorithm == control else posthoc["Holm"][algorithm]
            msc_holm = None if control == "MSC-CMA" else posthoc["Holm"]["MSC-CMA"]
            status = "★" if control == "MSC-CMA" else ("↓" if msc_holm < ALPHA else "≈")
        else:
            status = "O"
            for stale in (
                directory / f"posthoc_{scope}_request.json",
                directory / f"posthoc_{scope}_request.sha256",
                directory / f"posthoc_{scope}_response.json",
            ):
                stale.unlink(missing_ok=True)
            for row in ordering:
                row["posthoc_control"] = ""
                row["posthoc_holm_p"] = ""
        for row in ordering:
            row["dsc_status"] = status
        atomic_csv(
            directory / f"ordering_{scope}.csv", ordering, ORDERING_FIELDS
        )
        all_orderings.extend(ordering)
        print(
            f"  {scope}: "
            + ", ".join(
                f"{row['algorithm']}={row['mean_dsc_rank']:g}" for row in ordering
            ),
            flush=True,
        )
    return all_orderings


def parse_settings(tokens: Sequence[str]) -> tuple[Setting, ...]:
    if not tokens:
        return SETTINGS
    selected: list[Setting] = []
    seen: set[str] = set()
    for token in tokens:
        normalized = token.lower()
        setting = SETTING_BY_TOKEN.get(normalized)
        if setting is None:
            choices = ", ".join(SETTING_BY_TOKEN)
            raise AuditError(
                f"Unknown --setting {token!r}. Expected one of: {choices}"
            )
        if normalized not in seen:
            selected.append(setting)
            seen.add(normalized)
    return tuple(selected)


def collect_all_orderings(output: Path) -> list[dict[str, str]]:
    """Rebuild aggregate CSVs from all 17 validated per-setting outputs."""
    combined: list[dict[str, str]] = []
    expected_algorithms = set(BASE_ALGORITHMS)
    for setting in SETTINGS:
        directory = (
            output
            / setting.suite
            / f"d{setting.dimension}"
            / f"budget_{setting.budget}"
        )
        for scope in ("all", "composition"):
            rows = read_csv_rows(directory / f"ordering_{scope}.csv")
            if len(rows) != len(BASE_ALGORITHMS):
                raise AuditError(
                    f"{setting.token}/{scope}: expected 7 ordering rows, got {len(rows)}"
                )
            algorithms = {row.get("algorithm", "") for row in rows}
            if algorithms != expected_algorithms:
                raise AuditError(
                    f"{setting.token}/{scope}: ordering is not the common 7-algorithm set"
                )
            for row in rows:
                if (
                    row.get("suite") != setting.suite
                    or int(row.get("dimension", -1)) != setting.dimension
                    or int(row.get("budget", -1)) != setting.budget
                    or row.get("scope") != scope
                    or int(row.get("k", -1)) != 7
                ):
                    raise AuditError(
                        f"{setting.token}/{scope}: inconsistent ordering metadata"
                    )
            combined.extend(rows)
    if len(combined) != len(SETTINGS) * 2 * len(BASE_ALGORITHMS):
        raise AuditError("Combined ordering grid is incomplete")
    return combined


def get_credentials() -> tuple[str, str]:
    username = os.environ.get("DSC_USERNAME", DEFAULT_DSC_USERNAME).strip()
    password = os.environ.get("DSC_PASSWORD", PLAINTEXT_DSC_PASSWORD)
    if not password:
        password = getpass.getpass("DSC password: ")
    if not username or not password:
        raise AuditError("DSC username and password are required")
    return username, password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read trusted experiment PKLs, call DSCTool rank/omnibus/posthoc, and "
            "export all/composition DSC algorithm orderings."
        )
    )
    parser.add_argument(
        "--experiments",
        type=Path,
        default=Path("experiments"),
        help="experiment root (default: experiments)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dsc_python_results"),
        help="output root (default: dsc_python_results)",
    )
    parser.add_argument(
        "--setting",
        action="append",
        default=[],
        metavar="SUITE:D:B",
        help="run one of the configured 17 settings; repeatable",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"DSCTool service base (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--ca-bundle",
        type=Path,
        default=None,
        help="optional PEM CA bundle",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="disable TLS certificate verification (equivalent to curl -k)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=600.0,
        help="HTTP timeout in seconds (default: 600)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="retries for network/HTTP 5xx failures (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate PKLs and write rank requests without contacting DSCTool",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = parse_settings(args.setting)
    experiments = args.experiments.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not experiments.is_dir():
        raise AuditError(f"Experiment root does not exist: {experiments}")
    output.mkdir(parents=True, exist_ok=True)

    client: DscClient | None
    if args.dry_run:
        client = None
    else:
        username, password = get_credentials()
        client = DscClient(
            base_url=args.base_url,
            username=username,
            password=password,
            timeout=args.timeout,
            retries=args.retries,
            ca_bundle=args.ca_bundle,
            insecure=args.insecure,
        )
        del password

    for setting in settings:
        run_setting(setting, experiments, output, client)

    if args.dry_run:
        print("Dry run complete: available inputs passed and requests were written.")
        return 0

    all_orderings = collect_all_orderings(output)
    atomic_csv(
        output / "algorithm_orderings_all_settings.csv",
        all_orderings,
        ORDERING_FIELDS,
    )
    best_rows = [row for row in all_orderings if row["position_min"] == 1]
    atomic_csv(output / "best_algorithms.csv", best_rows, ORDERING_FIELDS)
    print(f"Combined ordering: {output / 'algorithm_orderings_all_settings.csv'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, pickle.UnpicklingError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
