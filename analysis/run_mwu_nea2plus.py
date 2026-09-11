#!/usr/bin/env python3
"""Generate NEA2+--MSC-CMA-ES MWU tables with separate Holm families.

From the stored run-wise terminal errors (51 runs per sample)::

    python analysis/run_mwu_nea2plus.py

Recalculate Holm adjustment and presentation from published raw U/p values::

    python analysis/run_mwu_nea2plus.py --from-details old/details.csv

Both commands write all-function and composition-only scopes to
related_comparisons/nea2plus/mwu. Use --experiments and --output-dir to
select different input and output directories. CSV regeneration does not
rerun MWU and preserves the original U, raw p, and probability strings.
"""

import argparse
import csv
import math
import pickle
from pathlib import Path

import numpy as np
from scipy import stats


ALPHA = 0.05
RUNS = 51

REFERENCE = "MSC-CMA"
COMPETITOR = "NEA2PLUS-PY"

SETTINGS = [
    ("cec2017", 10,   100_000),
    ("cec2020",  5,    50_000),
    ("cec2020", 10, 1_000_000),
    ("cec2020", 15, 3_000_000),
    ("cec2022", 10,   200_000),
    ("cec2022", 20, 1_000_000),
]

FUNCTIONS = {
    "cec2017": (1, *range(3, 31)),
    "cec2020": tuple(range(1, 11)),
    "cec2022": tuple(range(1, 13)),
}

CLASSES = {
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


def function_class(suite, fid):
    for cls, funcs in CLASSES[suite].items():
        if fid in funcs:
            return cls
    raise RuntimeError(f"Unknown class: {suite} f{fid}")


def load_errors(path, suite, dim, budget):
    if not path.is_file():
        raise RuntimeError(f"Missing: {path}")

    with path.open("rb") as f:
        d = pickle.load(f)

    if not isinstance(d, dict) or "errors" not in d:
        raise RuntimeError(f"{path}: missing errors")

    x = np.asarray(d["errors"])

    if x.shape != (RUNS,):
        raise RuntimeError(f"{path}: errors shape={x.shape}, expected (51,)")

    if x.dtype.kind not in "iuf":
        raise RuntimeError(f"{path}: errors are not numeric")

    x = x.astype(np.float64, copy=True)

    if not np.isfinite(x).all():
        raise RuntimeError(f"{path}: non-finite errors")

    if "maxevals" in d and int(d["maxevals"]) != budget:
        raise RuntimeError(
            f"{path}: maxevals={d['maxevals']} != {budget}"
        )

    if "dim" in d and int(d["dim"]) != dim:
        raise RuntimeError(
            f"{path}: dim={d['dim']} != {dim}"
        )

    if "suite" in d and str(d["suite"]).lower() != suite:
        raise RuntimeError(
            f"{path}: suite={d['suite']} != {suite}"
        )

    if "seeds" in d:
        seeds = np.asarray(d["seeds"])
        if (
            seeds.shape != (RUNS,)
            or seeds.dtype.kind not in "iu"
            or not np.array_equal(
                np.sort(seeds.astype(np.int64)),
                np.arange(RUNS)
            )
        ):
            raise RuntimeError(f"{path}: seeds are not exactly 0..50")

    # IMPORTANT:
    # raw terminal errors are returned unchanged.
    # No flooring, clipping, rounding, sorting or improvements trace.
    return x


SCOPES = ("all", "composition")
REPORT_ZERO = 1e-8
DETAIL_FIELDS = [
    "suite", "dimension", "budget", "comparison_scope", "function",
    "function_class", "competitor", "reference", "n_competitor",
    "n_reference", "u_competitor", "probability_nea2plus_lower",
    "mean_rank_nea2plus", "mean_rank_msc", "median_nea2plus", "median_msc",
    "p_raw", "test_family_size", "correction", "p_holm", "alpha", "mwu_symbol",
]
SUMMARY_FIELDS = [
    "suite", "dimension", "budget", "comparison_scope", "n_functions",
    "n_lt", "n_gt", "n_eq",
]
RAW_FIELDS = [
    "u_competitor", "probability_nea2plus_lower", "median_nea2plus",
    "median_msc", "p_raw",
]


def holm_adjust(p_values):
    """Return Holm step-down adjusted p-values in the input order."""
    values = np.asarray(p_values, dtype=float)
    if values.ndim != 1 or not len(values):
        raise ValueError("Holm adjustment requires a nonempty 1-D family")
    if not np.isfinite(values).all() or np.any((values < 0) | (values > 1)):
        raise ValueError("Raw p-values must be finite and in [0, 1]")
    order = np.argsort(values, kind="stable")
    adjusted = np.empty(len(values), dtype=float)
    running = 0.0
    for index, original_index in enumerate(order):
        running = max(running, (len(values) - index) * values[original_index])
        adjusted[original_index] = min(1.0, running)
    return adjusted


def pooled_mean_ranks(u_competitor, n_competitor=RUNS, n_reference=RUNS):
    """Mean ranks in the pooled sample; U includes half contributions for ties."""
    rank_nea = u_competitor / n_competitor + (n_competitor + 1) / 2
    u_reference = n_competitor * n_reference - u_competitor
    rank_msc = u_reference / n_reference + (n_reference + 1) / 2
    return rank_nea, rank_msc


def mwu_symbol(p_holm, rank_nea, rank_msc):
    """MSC-oriented symbols, conditional on the two-sided Holm decision."""
    if p_holm > ALPHA:
        return "="
    if rank_msc < rank_nea:
        return "<"
    if rank_msc > rank_nea:
        return ">"
    raise ValueError("Significant MWU result with equal pooled-sample mean ranks")


def reporting_median(value):
    """Apply the reporting convention only; never modify the MWU inputs."""
    value = float(value)
    return format(0.0 if abs(value) <= REPORT_ZERO else value, ".17g")


def scope_functions(suite, scope):
    return tuple(
        fid for fid in FUNCTIONS[suite]
        if scope == "all" or function_class(suite, fid) == "composition"
    )


def base_row(suite, dim, budget, fid):
    return {
        "suite": suite, "dimension": dim, "budget": budget, "function": fid,
        "function_class": function_class(suite, fid), "competitor": COMPETITOR,
        "reference": REFERENCE, "n_competitor": RUNS, "n_reference": RUNS,
    }


def calculate_raw_rows(experiments):
    """Compute each raw MWU comparison once, using unmodified terminal errors."""
    rows = []
    for suite, dim, budget in SETTINGS:
        print(f"[{suite} D={dim} B={budget}] calculating raw MWU")
        for fid in FUNCTIONS[suite]:
            folder = Path(experiments) / suite / f"d{dim}"
            x = load_errors(
                folder / COMPETITOR / f"maxevals_{budget}" / f"f{fid}.pkl",
                suite, dim, budget,
            )
            y = load_errors(
                folder / REFERENCE / f"maxevals_{budget}" / f"f{fid}.pkl",
                suite, dim, budget,
            )
            result = stats.mannwhitneyu(
                x, y, alternative="two-sided", method="asymptotic",
                use_continuity=True,
            )
            u = float(result.statistic)
            row = base_row(suite, dim, budget, fid)
            row.update({
                "u_competitor": format(u, ".17g"),
                "probability_nea2plus_lower": format(1.0 - u / (RUNS * RUNS), ".17g"),
                # With 51 observations the median is the middle order statistic.
                # Flooring this value equals taking the median of a reporting copy.
                "median_nea2plus": reporting_median(np.median(x)),
                "median_msc": reporting_median(np.median(y)),
                "p_raw": format(float(result.pvalue), ".17g"),
            })
            rows.append(row)
    return rows


def finite_float(row, field, context):
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{context}: invalid {field}") from exc
    if not math.isfinite(value):
        raise ValueError(f"{context}: non-finite {field}")
    return value


def integer_field(row, field, context):
    try:
        return int(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{context}: invalid integer {field}") from exc


def read_raw_details(path):
    """Read legacy 83-row or scoped 110-row CSV, validating its raw statistics.

    A scoped input must contain both complete scopes. Its adjusted p-values,
    ranks and symbols must agree with its raw statistics. Only the all-scope
    records supply raw comparisons for regeneration.
    """
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError(f"{path}: missing or duplicate CSV header fields")
        scoped = "comparison_scope" in reader.fieldnames
        input_rows = list(reader)

    records = {}
    raw_by_key = {}
    for line, original in enumerate(input_rows, start=2):
        context = f"{path}:{line}"
        if None in original or any(value is None for value in original.values()):
            raise ValueError(f"{context}: malformed CSV record")
        suite = original.get("suite")
        dim = integer_field(original, "dimension", context)
        budget = integer_field(original, "budget", context)
        fid = integer_field(original, "function", context)
        setting = (suite, dim, budget)
        if setting not in SETTINGS or fid not in FUNCTIONS[suite]:
            raise ValueError(f"{context}: unexpected setting or function")
        scope = original.get("comparison_scope", "all")
        if scope not in SCOPES or fid not in scope_functions(suite, scope):
            raise ValueError(f"{context}: invalid scope or function for scope")
        key = (*setting, scope, fid)
        if key in records:
            raise ValueError(f"{context}: duplicate comparison {key}")
        records[key] = original
        expected = base_row(suite, dim, budget, fid)
        for field in ("function_class", "competitor", "reference"):
            if original.get(field) != expected[field]:
                raise ValueError(f"{context}: unexpected {field}")
        for field in ("n_competitor", "n_reference"):
            if integer_field(original, field, context) != RUNS:
                raise ValueError(f"{context}: {field} must be {RUNS}")
        values = {field: finite_float(original, field, context) for field in RAW_FIELDS}
        u, p = values["u_competitor"], values["p_raw"]
        if not 0 <= u <= RUNS * RUNS or not (2 * u).is_integer():
            raise ValueError(f"{context}: U must be a half-integer in [0, {RUNS * RUNS}]")
        if not 0 <= p <= 1:
            raise ValueError(f"{context}: p_raw outside [0, 1]")
        probability = values["probability_nea2plus_lower"]
        if not 0 <= probability <= 1 or not math.isclose(
            probability, 1.0 - u / (RUNS * RUNS), rel_tol=0.0, abs_tol=1e-15,
        ):
            raise ValueError(f"{context}: probability inconsistent with U")
        if finite_float(original, "alpha", context) != ALPHA:
            raise ValueError(f"{context}: alpha must be {ALPHA}")
        family_field = "test_family_size" if scoped else "bonferroni_family_size"
        if integer_field(original, family_field, context) != len(scope_functions(suite, scope)):
            raise ValueError(f"{context}: incorrect family size")
        if scoped:
            if original.get("correction") != "holm-bonferroni":
                raise ValueError(f"{context}: expected holm-bonferroni correction")
            for field in ("mean_rank_nea2plus", "mean_rank_msc", "p_holm"):
                finite_float(original, field, context)
        else:
            p_bonf = finite_float(original, "p_bonferroni", context)
            if not math.isclose(p_bonf, min(1.0, len(FUNCTIONS[suite]) * p), rel_tol=1e-14, abs_tol=0.0):
                raise ValueError(f"{context}: inconsistent legacy Bonferroni p-value")
        expected.update({field: original[field] for field in RAW_FIELDS})
        expected["median_nea2plus"] = reporting_median(values["median_nea2plus"])
        expected["median_msc"] = reporting_median(values["median_msc"])
        if scope == "all":
            raw_by_key[(*setting, fid)] = expected

    expected_keys = {
        (suite, dim, budget, scope, fid)
        for suite, dim, budget in SETTINGS
        for scope in (SCOPES if scoped else ("all",))
        for fid in scope_functions(suite, scope)
    }
    if set(records) != expected_keys:
        missing = sorted(expected_keys - set(records))
        raise ValueError(f"{path}: incomplete function coverage; missing {missing}")

    raw_rows = [
        raw_by_key[(suite, dim, budget, fid)]
        for suite, dim, budget in SETTINGS for fid in FUNCTIONS[suite]
    ]
    if scoped:
        for generated in build_scoped_rows(raw_rows):
            key = tuple(generated[field] for field in (
                "suite", "dimension", "budget", "comparison_scope", "function",
            ))
            original = records[key]
            context = f"{path}: {key}"
            for field in RAW_FIELDS + ["mean_rank_nea2plus", "mean_rank_msc", "p_holm"]:
                expected_value = float(generated[field])
                actual_value = finite_float(original, field, context)
                # Reporting medians in scoped files must already use the convention.
                if not math.isclose(actual_value, expected_value, rel_tol=1e-14, abs_tol=0.0):
                    raise ValueError(f"{context}: inconsistent {field}")
            if original.get("mwu_symbol") != generated["mwu_symbol"]:
                raise ValueError(f"{context}: inconsistent mwu_symbol")
    return raw_rows


def build_scoped_rows(raw_rows):
    """Apply independent all-function and composition-only Holm families."""
    rows = []
    for suite, dim, budget in SETTINGS:
        setting_rows = [
            row for row in raw_rows
            if (row["suite"], row["dimension"], row["budget"]) == (suite, dim, budget)
        ]
        for scope in SCOPES:
            family = [
                row for row in setting_rows
                if scope == "all" or row["function_class"] == "composition"
            ]
            if sorted(row["function"] for row in family) != sorted(scope_functions(suite, scope)):
                raise ValueError(f"Incomplete or duplicate family: {suite} D={dim} B={budget} {scope}")
            adjusted = holm_adjust([float(row["p_raw"]) for row in family])
            for raw, p_holm in zip(family, adjusted):
                row = dict(raw)
                rank_nea, rank_msc = pooled_mean_ranks(float(row["u_competitor"]))
                row.update({
                    "comparison_scope": scope, "test_family_size": len(family),
                    "correction": "holm-bonferroni", "p_holm": format(p_holm, ".17g"),
                    "alpha": ALPHA,
                    "mean_rank_nea2plus": format(rank_nea, ".17g"),
                    "mean_rank_msc": format(rank_msc, ".17g"),
                    "mwu_symbol": mwu_symbol(p_holm, rank_nea, rank_msc),
                })
                rows.append(row)
    return rows


def summarize(rows):
    summary = []
    for suite, dim, budget in SETTINGS:
        for scope in SCOPES:
            family = [row for row in rows if (
                row["suite"], row["dimension"], row["budget"], row["comparison_scope"]
            ) == (suite, dim, budget, scope)]
            summary.append({
                "suite": suite, "dimension": dim, "budget": budget,
                "comparison_scope": scope, "n_functions": len(family),
                "n_lt": sum(row["mwu_symbol"] == "<" for row in family),
                "n_gt": sum(row["mwu_symbol"] == ">" for row in family),
                "n_eq": sum(row["mwu_symbol"] == "=" for row in family),
            })
    return summary


def write_csv(path, fields, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--experiments", type=Path, default=Path("experiments"))
    parser.add_argument("--output-dir", type=Path, default=Path("related_comparisons/nea2plus/mwu"))
    parser.add_argument("--from-details", type=Path, help="Regenerate from legacy or scoped full-precision details.csv")
    args = parser.parse_args(argv)
    try:
        raw_rows = read_raw_details(args.from_details) if args.from_details else calculate_raw_rows(args.experiments)
        rows = build_scoped_rows(raw_rows)
        summary = summarize(rows)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(args.output_dir / "details.csv", DETAIL_FIELDS, rows)
        write_csv(args.output_dir / "summary.csv", SUMMARY_FIELDS, summary)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    print(f"Wrote {len(rows)} scoped comparisons and {len(summary)} family summaries under {args.output_dir}")
    for scope in SCOPES:
        families = [row for row in summary if row["comparison_scope"] == scope]
        counts = [sum(row[field] for row in families) for field in ("n_lt", "n_gt", "n_eq")]
        print(f"{scope}: n_< / n_> / n_= = {' / '.join(map(str, counts))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
