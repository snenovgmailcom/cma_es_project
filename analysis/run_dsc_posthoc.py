#!/usr/bin/env python3
"""Complete missing DSCTool post-hoc calls from existing DSC results (fixed build 20260817).

This script does not read PKL files and does not repeat /rank or /omnibus.
It reads dsc_python_results, sends /posthoc only where Friedman rejected H0
then writes the final labels. No rank or omnibus call is repeated.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from run_iohanalyzer_dsc import (
    ALPHA,
    DEFAULT_BASE_URL,
    DscClient,
    AuditError,
    SETTINGS,
    atomic_bytes,
    atomic_csv,
    atomic_text,
    get_credentials,
    json_request_bytes,
    unwrap_response,
)


LONG_FIELDS = (
    "suite",
    "dimension",
    "budget",
    "scope",
    "best_algorithm",
    "best_mean_dsc_rank",
    "msc_position",
    "msc_position_interval",
    "msc_mean_dsc_rank",
    "k",
    "n_functions",
    "friedman_statistic",
    "friedman_p_value",
    "holm_p_best_vs_msc",
    "label",
)

TABLE_FIELDS = (
    "suite",
    "dimension",
    "budget",
    "all_best_algorithm",
    "all_msc_position",
    "all_friedman_p_value",
    "all_holm_p_best_vs_msc",
    "all_label",
    "composition_best_algorithm",
    "composition_msc_position",
    "composition_friedman_p_value",
    "composition_holm_p_best_vs_msc",
    "composition_label",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Cannot read valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"JSON root is not an object: {path}")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))
    except OSError as exc:
        raise AuditError(f"Cannot read CSV: {path}") from exc


def finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise AuditError(f"{label} is boolean")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f"{label} is not numeric") from exc
    if not math.isfinite(number):
        raise AuditError(f"{label} is not finite")
    return number


def unwrap_posthoc_response(response: Mapping[str, Any], operation: str) -> list[Any]:
    if response.get("success") is not True:
        message = response.get("message") or response.get("error") or "unknown service error"
        raise AuditError(f"DSCTool {operation} reported failure: {message}")
    result = response.get("result")
    if not isinstance(result, list):
        raise AuditError(f"DSCTool {operation} response has no result list")
    return result


def validate_posthoc(
    result: Any,
    setting: Any,
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
        values = block.get("algorithms")
        if name in tables or not isinstance(values, list):
            raise AuditError(f"Malformed or duplicate posthoc block {name}/{scope}")
        table: dict[str, float] = {}
        for row in values:
            if not isinstance(row, dict):
                raise AuditError(f"Malformed posthoc row for {name}/{scope}")
            algorithm = str(row.get("algorithm"))
            if algorithm in table:
                raise AuditError(f"Duplicate {algorithm} in {name}/{scope}")
            value = finite(row.get("value"), f"{name}/{algorithm}/{scope}")
            if name != "ZValue" and not 0.0 <= value <= 1.0:
                raise AuditError(f"Invalid probability in {name}/{algorithm}/{scope}")
            table[algorithm] = value
        if set(table) != expected:
            raise AuditError(f"Posthoc {name}/{scope} algorithm set is incorrect")
        tables[name] = table
    if set(tables) != required:
        raise AuditError(f"Posthoc {scope} blocks differ from {sorted(required)}")
    return tables


def analyze_scope(
    directory: Path,
    scope: str,
    setting: Any,
    client: DscClient | None,
    force: bool,
) -> dict[str, Any]:
    ordering = read_csv(directory / f"ordering_{scope}.csv")
    if not ordering:
        raise AuditError(f"Empty ordering for {directory}/{scope}")

    best_rows = [row for row in ordering if int(row["position_min"]) == 1]
    if len(best_rows) != 1:
        raise AuditError(f"No unique best algorithm for {directory}/{scope}")
    best = best_rows[0]
    msc_rows = [row for row in ordering if row["algorithm"] == "MSC-CMA"]
    if len(msc_rows) != 1:
        raise AuditError(f"No unique MSC-CMA row for {directory}/{scope}")
    msc = msc_rows[0]

    p_value = finite(msc["omnibus_p_value"], "Friedman p-value")
    statistic = finite(msc["omnibus_statistic"], "Friedman statistic")
    k = int(msc["k"])
    n_functions = int(msc["n_functions"])
    label: str
    holm_p: float | str = ""

    if p_value >= ALPHA:
        label = "O"
    else:
        omnibus_envelope = read_json(directory / f"omnibus_{scope}_response.json")
        omnibus_result = unwrap_response(omnibus_envelope, f"omnibus/{scope}")
        algorithm_means = omnibus_result.get("algorithm_means")
        method = omnibus_result.get("method")
        if not isinstance(algorithm_means, list) or not isinstance(method, dict):
            raise AuditError(f"Invalid omnibus result for {directory}/{scope}")
        request_value = {
            "algorithm_means": algorithm_means,
            "k": k,
            "n": n_functions,
            "base_algorithm": best["algorithm"],
            "method": method,
        }
        request_body = json_request_bytes(request_value)
        request_path = directory / f"posthoc_{scope}_request.json"
        response_path = directory / f"posthoc_{scope}_response.json"
        atomic_bytes(request_path, request_body)
        atomic_text(
            directory / f"posthoc_{scope}_request.sha256",
            hashlib.sha256(request_body).hexdigest()
            + f"  posthoc_{scope}_request.json\n",
        )

        if client is None:
            label = "PENDING"
        else:
            if force or not response_path.is_file():
                response = client.post("posthoc", request_body)
                atomic_bytes(response_path, response.body)
                envelope = response.decoded
            else:
                envelope = read_json(response_path)
            result = unwrap_posthoc_response(envelope, f"posthoc/{scope}")
            tables = validate_posthoc(
                result, setting, scope, str(best["algorithm"])
            )
            if best["algorithm"] == "MSC-CMA":
                label = "★"
            else:
                holm_p = tables["Holm"]["MSC-CMA"]
                label = "↓" if holm_p < ALPHA else "≈"

    return {
        "suite": msc["suite"],
        "dimension": int(msc["dimension"]),
        "budget": int(msc["budget"]),
        "scope": scope,
        "best_algorithm": best["algorithm"],
        "best_mean_dsc_rank": finite(best["mean_dsc_rank"], "best mean rank"),
        "msc_position": msc["position_label"],
        "msc_position_interval": msc["position_interval"],
        "msc_mean_dsc_rank": finite(msc["mean_dsc_rank"], "MSC mean rank"),
        "k": k,
        "n_functions": n_functions,
        "friedman_statistic": statistic,
        "friedman_p_value": p_value,
        "holm_p_best_vs_msc": holm_p,
        "label": label,
    }


def make_wide(long_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_setting: dict[tuple[str, int, int], dict[str, Mapping[str, Any]]] = {}
    for row in long_rows:
        key = (str(row["suite"]), int(row["dimension"]), int(row["budget"]))
        by_setting.setdefault(key, {})[str(row["scope"])] = row
    output: list[dict[str, Any]] = []
    for setting in SETTINGS:
        key = (setting.suite, setting.dimension, setting.budget)
        scopes = by_setting.get(key, {})
        if set(scopes) != {"all", "composition"}:
            raise AuditError(f"Incomplete final table for {setting.token}")
        all_row = scopes["all"]
        comp_row = scopes["composition"]
        output.append(
            {
                "suite": setting.suite,
                "dimension": setting.dimension,
                "budget": setting.budget,
                "all_best_algorithm": all_row["best_algorithm"],
                "all_msc_position": all_row["msc_position"],
                "all_friedman_p_value": all_row["friedman_p_value"],
                "all_holm_p_best_vs_msc": all_row["holm_p_best_vs_msc"],
                "all_label": all_row["label"],
                "composition_best_algorithm": comp_row["best_algorithm"],
                "composition_msc_position": comp_row["msc_position"],
                "composition_friedman_p_value": comp_row["friedman_p_value"],
                "composition_holm_p_best_vs_msc": comp_row[
                    "holm_p_best_vs_msc"
                ],
                "composition_label": comp_row["label"],
            }
        )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run only the missing DSCTool post-hoc calls from existing results."
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("dsc_python_results"),
        help="existing DSC result root (default: dsc_python_results)",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--ca-bundle", type=Path, default=None)
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="disable TLS certificate verification (equivalent to curl -k)",
    )
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument(
        "--force",
        action="store_true",
        help="repeat post-hoc calls even when response files already exist",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="write post-hoc requests without contacting DSCTool",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.results.expanduser().resolve()
    if not root.is_dir():
        raise AuditError(f"Result root does not exist: {root}")

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

    long_rows: list[dict[str, Any]] = []
    for setting in SETTINGS:
        directory = (
            root
            / setting.suite
            / f"d{setting.dimension}"
            / f"budget_{setting.budget}"
        )
        for scope in ("all", "composition"):
            row = analyze_scope(directory, scope, setting, client, args.force)
            long_rows.append(row)
            print(
                f"{setting.suite} D={setting.dimension} B={setting.budget} "
                f"{scope}: {row['best_algorithm']} · {row['msc_position']} · "
                f"{row['label']}",
                flush=True,
            )

    wide_rows = make_wide(long_rows)
    atomic_csv(root / "dsc_results_final_long.csv", long_rows, LONG_FIELDS)
    atomic_csv(root / "dsc_results_final_table.csv", wide_rows, TABLE_FIELDS)
    if args.dry_run:
        pending = sum(row["label"] == "PENDING" for row in long_rows)
        print(f"Dry run complete: {pending} post-hoc requests written.")
    else:
        print(f"Final table: {root / 'dsc_results_final_table.csv'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        raise SystemExit(1) from exc
