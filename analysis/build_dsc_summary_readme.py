#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from report_style import (
    P_FRIEDMAN,
    P_HOLM,
    display_name,
    format_budget,
    format_p,
)


BASE_ALGORITHMS = (
    "MSC-CMA",
    "BIPOP-CMA",
    "ARRDE",
    "LSRTDE",
    "NLSHADE-RSP",
    "j2020",
    "jSO",
)

FUNCTION_SUBSETS = {
    "cec2014": ("f1–f30", "f23–f30"),
    "cec2017": ("f1, f3–f30", "f21–f30"),
    "cec2020": ("f1–f10", "f8–f10"),
    "cec2022": ("f1–f12", "f9–f12"),
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--table",
        type=Path,
        default=Path("dsc/dsc_results_final_table.csv"),
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("dsc/README.md"),
    )
    p.add_argument("--check", action="store_true")
    return p.parse_args()


def budget_slug(budget: int) -> str:
    """Stable anchor used by the already-generated MWU READMEs."""
    if budget >= 1_000_000 and budget % 1_000_000 == 0:
        return f"{budget // 1_000_000}m"
    if budget >= 1_000 and budget % 1_000 == 0:
        return f"{budget // 1_000}k"
    return str(budget)


def optional_p(value: str) -> str:
    return "—" if value == "" else format_p(float(value))


def validate(rows):
    if len(rows) != 17:
        raise ValueError(f"Expected 17 settings, found {len(rows)}")

    keys = {
        (r["suite"], int(r["dimension"]), int(r["budget"]))
        for r in rows
    }
    if len(keys) != 17:
        raise ValueError("Duplicate suite/dimension/budget row")

    for r in rows:
        for scope in ("all", "composition"):
            if r[f"{scope}_label"] not in {"★", "≈", "↓", "O"}:
                raise ValueError(
                    f"Unknown {scope} label: {r[f'{scope}_label']}"
                )

            if not r[f"{scope}_best_algorithm"]:
                raise ValueError(
                    f"Missing {scope} lowest-mean-rank algorithm"
                )

            float(r[f"{scope}_friedman_p_value"])

            holm = r[f"{scope}_holm_p_best_vs_msc"]
            if holm:
                float(holm)


def render(rows):
    rows = sorted(
        rows,
        key=lambda r: (
            r["suite"],
            int(r["dimension"]),
            int(r["budget"]),
        ),
    )

    n = len(rows)

    all_labels = Counter(r["all_label"] for r in rows)
    comp_labels = Counter(r["composition_label"] for r in rows)

    all_lowest = sum(
        r["all_best_algorithm"] == "MSC-CMA"
        for r in rows
    )
    comp_lowest = sum(
        r["composition_best_algorithm"] == "MSC-CMA"
        for r in rows
    )

    all_reject = n - all_labels["O"]
    comp_reject = n - comp_labels["O"]

    comp_significant = [
        r for r in rows
        if r["composition_label"] == "↓"
    ]
    if len(comp_significant) != 1:
        raise ValueError(
            "Expected exactly one significant composition comparison, "
            f"found {len(comp_significant)}"
        )
    comp_sig = comp_significant[0]

    lines = [
        "# Deep Statistical Comparison — summary",
        "",
        "This page summarizes the Deep Statistical Comparison (DSC) results for",
        f"the {n} suite–dimension–budget settings used in the study. Detailed",
        "per-function DSC ranks and statistical comparisons are linked from the",
        "table below.",
        "",
        "DSC is applied to the 51 run-wise terminal errors for each function using",
        "Anderson–Darling comparisons (`alpha=0.05`, `epsilon=0`,",
        "`monte_carlo_iterations=0`). The resulting per-function ranks are",
        "analyzed with the Friedman omnibus test. When the omnibus null",
        "hypothesis is rejected, Holm-adjusted post-hoc comparisons are",
        "performed against the algorithm with the lowest mean DSC rank.",
        "",
        "## Overall summary",
        "",
        f"**All functions.** MSC-CMA-ES has the lowest mean DSC rank in "
        f"**{all_lowest}/{n}** settings. The Friedman test rejects the null "
        f"hypothesis in **{all_reject}/{n}** settings. Among these, the "
        f"Holm-adjusted comparison with MSC-CMA-ES is significant in "
        f"**{all_labels['↓']}** settings and not significant in "
        f"**{all_labels['≈']}** settings. In the remaining "
        f"**{all_labels['O']}/{n}** settings, the Friedman test does not reject "
        "the null hypothesis.",
        "",
        f"**Composition functions.** MSC-CMA-ES has the lowest mean DSC rank in "
        f"**{comp_lowest}/{n}** settings. The Friedman test rejects the null "
        f"hypothesis in **{comp_reject}/{n}** settings. MSC-CMA-ES has the "
        f"lowest mean DSC rank in **{comp_labels['★']}** of these rejected "
        f"settings. In **{comp_labels['≈']}** other rejected settings, the "
        "Holm-adjusted comparison between MSC-CMA-ES and the "
        "lowest-mean-rank algorithm is not significant. The only significant "
        "Holm-adjusted comparison occurs for **"
        f"{comp_sig['suite'].upper()}, D={int(comp_sig['dimension'])}, "
        f"B={format_budget(int(comp_sig['budget']))}**, where the "
        "lowest-mean-rank algorithm is **"
        f"{display_name(comp_sig['composition_best_algorithm'])}** "
        "(`p_Holm = "
        f"{format_p(float(comp_sig['composition_holm_p_best_vs_msc']))}`). "
        f"In the remaining **{comp_labels['O']}/{n}** settings, the Friedman "
        "test does not reject the null hypothesis.",
        "",
        "### Symbols",
        "",
        "- **★** — MSC-CMA-ES has the lowest mean DSC rank and the Friedman "
        "test rejects the null hypothesis.",
        "- **≈** — the Friedman test rejects the null hypothesis, but the "
        "Holm-adjusted comparison between MSC-CMA-ES and the "
        "lowest-mean-rank algorithm is not significant.",
        "- **↓** — the lowest-mean-rank algorithm has a smaller mean DSC rank "
        "than MSC-CMA-ES and the Holm-adjusted comparison is significant.",
        "- **O** — the Friedman test does not reject the null hypothesis; no "
        "post-hoc interpretation is made.",
        "",
        f"`{P_HOLM}` is shown only when the lowest-mean-rank algorithm is not "
        "MSC-CMA-ES and the Friedman test rejects the null hypothesis.",
        "",
        f"## All {n} settings",
        "",
        "| Suite | D | Budget | All: lowest-mean-rank algorithm | "
        f"MSC position | {P_FRIEDMAN} | {P_HOLM} | Result | "
        "Composition: lowest-mean-rank algorithm | MSC position | "
        f"{P_FRIEDMAN} | {P_HOLM} | Result |",
        "|:--|--:|--:|:--|:--:|--:|--:|:--:|:--|:--:|--:|--:|:--:|",
    ]

    for r in rows:
        suite = r["suite"]
        dim = int(r["dimension"])
        budget = int(r["budget"])

        link = (
            f"../mwu/{suite}/d{dim}/README.md"
            f"#dsc-budget-{budget_slug(budget)}"
        )

        lines.append(
            "| "
            + " | ".join(
                [
                    suite.upper(),
                    str(dim),
                    f"[{format_budget(budget)}]({link})",
                    display_name(r["all_best_algorithm"]),
                    r["all_msc_position"],
                    format_p(float(r["all_friedman_p_value"])),
                    optional_p(r["all_holm_p_best_vs_msc"]),
                    f"**{r['all_label']}**",
                    display_name(r["composition_best_algorithm"]),
                    r["composition_msc_position"],
                    format_p(float(r["composition_friedman_p_value"])),
                    optional_p(r["composition_holm_p_best_vs_msc"]),
                    f"**{r['composition_label']}**",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Function subsets",
            "",
        ]
    )

    for suite in ("cec2014", "cec2017", "cec2020", "cec2022"):
        all_set, comp_set = FUNCTION_SUBSETS[suite]
        lines.append(
            f"- **{suite.upper()}:** All: `{all_set}`; "
            f"Composition: `{comp_set}`."
        )

    lines.extend(
        [
            "",
            "All settings compare the same seven algorithms:",
            ", ".join(display_name(a) for a in BASE_ALGORITHMS) + ".",
            "",
            "The numerical source for this page is "
            "[`dsc_results_final_table.csv`](dsc_results_final_table.csv). "
            "The detailed per-scope values are stored in "
            "[`dsc_results_final_long.csv`](dsc_results_final_long.csv).",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    args = parse_args()

    with args.table.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    validate(rows)
    text = render(rows)

    if args.check:
        print("CHECK PASSED")
        print("settings:", len(rows))
        print(
            "all labels:",
            dict(Counter(r["all_label"] for r in rows)),
        )
        print(
            "composition labels:",
            dict(Counter(r["composition_label"] for r in rows)),
        )
        print("Would write:", args.output)
        return

    args.output.write_text(text, encoding="utf-8")
    print("WROTE:", args.output)


if __name__ == "__main__":
    main()
