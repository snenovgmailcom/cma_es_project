#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path("dsc")
ALPHA = 0.05

LONG = ROOT / "dsc_results_final_long.csv"
TABLE = ROOT / "dsc_results_final_table.csv"

SCOPES = ("all", "composition")


def close(a, b, *, rel=1e-12, abs_=1e-14):
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=abs_)


def optional_float(x):
    if x is None or x == "":
        return None
    return float(x)


def avg_position(means, algorithm):
    """
    Position among algorithms ordered by increasing mean DSC rank.
    Ties occupy the average of their position interval.
    """
    target = means[algorithm]
    ordered = sorted(means.items(), key=lambda kv: kv[1])

    positions = [
        i + 1
        for i, (_, value) in enumerate(ordered)
        if close(value, target)
    ]

    lo = min(positions)
    hi = max(positions)
    avg = sum(positions) / len(positions)
    k = len(means)

    if float(avg).is_integer():
        pos = f"{int(avg)}/{k}"
    else:
        pos = f"{avg:g}/{k}"

    if lo == hi:
        interval = f"{lo}/{k}"
    else:
        interval = f"{lo}-{hi}/{k} (tie)"

    return pos, interval


def holm_map(response):
    for block in response["result"]:
        if block["name"] == "Holm":
            return {
                x["algorithm"]: float(x["value"])
                for x in block["algorithms"]
            }
    raise AssertionError("Holm block not found")


def compare_optional_numeric(label, expected, actual):
    e = optional_float(expected)
    a = optional_float(actual)

    if e is None or a is None:
        assert e is None and a is None, (
            label, expected, actual
        )
    else:
        assert close(e, a), (
            label, e, a, a - e
        )


long_rows = list(csv.DictReader(
    LONG.open(newline="", encoding="utf-8")
))
table_rows = list(csv.DictReader(
    TABLE.open(newline="", encoding="utf-8")
))

assert len(long_rows) == 34, len(long_rows)
assert len(table_rows) == 17, len(table_rows)

long_by_key = {
    (
        r["suite"],
        int(r["dimension"]),
        int(r["budget"]),
        r["scope"],
    ): r
    for r in long_rows
}

assert len(long_by_key) == 34


# ------------------------------------------------------------------
# 1. final_long.csv vs raw DSCTool omnibus/posthoc responses
# ------------------------------------------------------------------

checked_omnibus = 0
checked_posthoc = 0

for key in sorted(long_by_key):
    suite, dim, budget, scope = key
    row = long_by_key[key]

    cell = ROOT / suite / f"d{dim}" / f"budget_{budget}"

    omni_path = cell / f"omnibus_{scope}_response.json"
    assert omni_path.exists(), omni_path

    omni = json.loads(omni_path.read_text())
    assert omni["success"] is True, omni_path

    result = omni["result"]

    p = float(result["p_value"])
    t = float(result["t"])

    means = {
        x["algorithm"]: float(x["mean"])
        for x in result["algorithm_means"]
    }

    k = int(row["k"])
    n_functions = int(row["n_functions"])

    assert len(means) == k, (key, len(means), k)
    assert "MSC-CMA" in means, key

    # Friedman statistic and p-value
    assert close(t, row["friedman_statistic"]), (
        key, "friedman statistic",
        t, row["friedman_statistic"]
    )

    assert close(p, row["friedman_p_value"]), (
        key, "friedman p",
        p, row["friedman_p_value"]
    )

    # Lowest mean rank
    expected_control = row["best_algorithm"]
    min_mean = min(means.values())

    assert expected_control in means, (
        key, expected_control, sorted(means)
    )
    assert close(means[expected_control], min_mean), (
        key,
        "summary control is not at minimum mean rank",
        expected_control,
        means[expected_control],
        min_mean,
    )

    assert close(
        means[expected_control],
        row["best_mean_dsc_rank"]
    ), (
        key,
        "control mean rank",
        means[expected_control],
        row["best_mean_dsc_rank"],
    )

    # MSC mean and position
    assert close(
        means["MSC-CMA"],
        row["msc_mean_dsc_rank"]
    ), (
        key,
        "MSC mean rank",
        means["MSC-CMA"],
        row["msc_mean_dsc_rank"],
    )

    pos, interval = avg_position(means, "MSC-CMA")

    assert pos == row["msc_position"], (
        key, "MSC position", pos, row["msc_position"]
    )

    assert interval == row["msc_position_interval"], (
        key,
        "MSC position interval",
        interval,
        row["msc_position_interval"],
    )

    # Statistical interpretation
    stored_holm = optional_float(
        row["holm_p_best_vs_msc"]
    )

    if p >= ALPHA:
        expected_label = "O"
        assert stored_holm is None, (
            key,
            "Holm value present although Friedman did not reject",
            stored_holm,
        )

    elif expected_control == "MSC-CMA":
        expected_label = "★"
        assert stored_holm is None, (
            key,
            "Holm value present although MSC is control",
            stored_holm,
        )

    else:
        req_path = cell / f"posthoc_{scope}_request.json"
        res_path = cell / f"posthoc_{scope}_response.json"

        assert req_path.exists(), req_path
        assert res_path.exists(), res_path

        req = json.loads(req_path.read_text())
        res = json.loads(res_path.read_text())

        assert res["success"] is True, res_path

        # Post-hoc request must use the minimum-mean-rank control.
        assert req["base_algorithm"] == expected_control, (
            key,
            "wrong posthoc control",
            req["base_algorithm"],
            expected_control,
        )

        assert int(req["k"]) == k, (
            key, "posthoc k", req["k"], k
        )
        assert int(req["n"]) == n_functions, (
            key, "posthoc n", req["n"], n_functions
        )

        req_means = {
            x["algorithm"]: float(x["mean"])
            for x in req["algorithm_means"]
        }

        assert set(req_means) == set(means), (
            key,
            "posthoc/omnibus algorithm sets differ",
        )

        for alg in means:
            assert close(req_means[alg], means[alg]), (
                key,
                "posthoc/omnibus mean differs",
                alg,
                req_means[alg],
                means[alg],
            )

        hm = holm_map(res)
        assert "MSC-CMA" in hm, (
            key,
            "MSC-CMA missing from Holm response",
        )

        raw_holm = hm["MSC-CMA"]

        assert stored_holm is not None, (
            key,
            "summary Holm value missing",
        )

        assert close(raw_holm, stored_holm), (
            key,
            "Holm p mismatch",
            raw_holm,
            stored_holm,
        )

        expected_label = (
            "↓" if raw_holm < ALPHA else "≈"
        )

        checked_posthoc += 1

    assert row["label"] == expected_label, (
        key,
        "label mismatch",
        row["label"],
        expected_label,
    )

    checked_omnibus += 1


# ------------------------------------------------------------------
# 2. final_table.csv vs final_long.csv
# ------------------------------------------------------------------

for trow in table_rows:
    suite = trow["suite"]
    dim = int(trow["dimension"])
    budget = int(trow["budget"])

    for scope in SCOPES:
        lrow = long_by_key[(suite, dim, budget, scope)]

        prefix = f"{scope}_"

        assert (
            trow[prefix + "best_algorithm"]
            == lrow["best_algorithm"]
        ), (
            suite, dim, budget, scope,
            "best_algorithm"
        )

        assert (
            trow[prefix + "msc_position"]
            == lrow["msc_position"]
        ), (
            suite, dim, budget, scope,
            "msc_position"
        )

        compare_optional_numeric(
            (suite, dim, budget, scope, "friedman p"),
            trow[prefix + "friedman_p_value"],
            lrow["friedman_p_value"],
        )

        compare_optional_numeric(
            (suite, dim, budget, scope, "Holm p"),
            trow[prefix + "holm_p_best_vs_msc"],
            lrow["holm_p_best_vs_msc"],
        )

        assert (
            trow[prefix + "label"]
            == lrow["label"]
        ), (
            suite, dim, budget, scope,
            "label",
        )


# ------------------------------------------------------------------
# 3. Global invariants
# ------------------------------------------------------------------

assert {int(r["k"]) for r in long_rows} == {7}

labels_all = Counter(
    r["label"]
    for r in long_rows
    if r["scope"] == "all"
)

labels_comp = Counter(
    r["label"]
    for r in long_rows
    if r["scope"] == "composition"
)

assert labels_all == Counter({
    "↓": 7,
    "≈": 4,
    "O": 6,
}), labels_all

assert labels_comp == Counter({
    "★": 5,
    "↓": 1,
    "≈": 6,
    "O": 5,
}), labels_comp


print("DSC CONSISTENCY AUDIT OK")
print("settings             :", len(table_rows))
print("scope rows           :", len(long_rows))
print("omnibus responses    :", checked_omnibus)
print("posthoc comparisons  :", checked_posthoc)
print("algorithms per scope : 7")
print("all labels           :", dict(labels_all))
print("composition labels   :", dict(labels_comp))
