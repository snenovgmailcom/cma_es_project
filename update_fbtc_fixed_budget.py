#!/usr/bin/env python3
"""Update MSC-CMA-ES repository README/generators for raw fixed-budget FBTC(B).

This script does NOT run git and does NOT contact GitHub.
It updates the three README generators and all README files linked from the two
root README tables.  With PKL files present, it also regenerates only the
budget-scaling PNGs using raw FBTC(B), never a running maximum.

Usage from repository root:
    python /path/to/update_fbtc_fixed_budget.py

For a text/code-only dry application (no plots):
    python /path/to/update_fbtc_fixed_budget.py --no-plots
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib
import os
from pathlib import Path
import py_compile
import re
import sys
import tarfile

SUITE_DIMS = {
    "cec2014": (10, 30),
    "cec2017": (10, 30),
    "cec2020": (5, 10, 15, 20),
    "cec2022": (10, 20),
}

SOURCE_FILES = (
    Path("analysis/cell_report.py"),
    Path("analysis/suite_report.py"),
    Path("analysis/run_mwu_all_functions.py"),
)


def _replace(text: str, old: str, new: str) -> tuple[str, int]:
    n = text.count(old)
    if n:
        text = text.replace(old, new)
    return text, n


def patch_cell_report(text: str) -> str:
    # Documentation / labels.
    replacements = [
        ("FBTC vs budget, MONOTONE ENVELOPE\n     (running maximum over budgets; see paper, sec:budget).",
         "raw FBTC(B) vs fixed evaluation budget.\n     Each point is a separate fixed-budget experiment; no running maximum is applied."),
        ("FBTC vs budget, MONOTONE ENVELOPE\n     (running maximum over budgets; see paper, sec:budget).",
         "raw FBTC(B) vs fixed evaluation budget.\n     Each point is a separate fixed-budget experiment; no running maximum is applied."),
        ("# Budget-scaling figures (monotone envelope, per-class budget axis)",
         "# Budget-scaling figures (raw FBTC(B), per-class budget axis)"),
        ("('FBTC', 'FBTC', True)", "('FBTC(B)', 'FBTC', True)"),
        ("aggregate metrics (worst-SUM, median-SUM, FBTC, best-SUM)",
         "aggregate metrics (worst-SUM, median-SUM, FBTC(B), best-SUM)"),
        ("ax.plot(x, _envelope(raw), label=DISPLAY.get(a, a), **STYLE[a])",
         "ax.plot(x, raw, label=DISPLAY.get(a, a), **STYLE[a])"),
        ("ax.set_xlabel('Budget (MaxFES)', fontsize=11)",
         "ax.set_xlabel('Fixed evaluation budget B (NFE)', fontsize=11)"),
        ("ax.set_ylabel(f'FBTC (sum over {nmax} functions)', fontsize=11)",
         "ax.set_ylabel(f'SUM(FBTC(B)) over {nmax} functions', fontsize=11)"),
    ]
    for old, new in replacements:
        text, _ = _replace(text, old, new)

    # Also match the original untouched prose exactly.
    old_block = """o.append(f'FBTC by budget, monotone envelope (running maximum over '
                 f'budgets). Higher is better. The budget axis is per class: a '
                 f'budget is shown only where all {len(data)} algorithms cover '
                 f'the whole class. MSC-CMA in red.')"""
    new_block = """o.append(f'Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. '
                 f'Each point is a separate fixed-budget experiment. Higher is better. '
                 f'The budget axis is per class: a budget is shown only where all '
                 f'{len(data)} algorithms cover the whole class. MSC-CMA in red.')"""
    text = text.replace(old_block, new_block)

    # Remove the old helper if present; raw values are plotted directly.
    text = re.sub(
        r"\ndef _envelope\(vals\):\n(?:    .*\n)+?    return out\n",
        "\n",
        text,
        count=1,
    )

    # Table display label: underlying key remains FBTC.
    old = "rows.append(f'| {cat} | {metric} | ' + ' | '.join(cells) + ' |')"
    new = "display_metric = 'FBTC(B)' if metric == 'FBTC' else metric\n            rows.append(f'| {cat} | {display_metric} | ' + ' | '.join(cells) + ' |')"
    text = text.replace(old, new)

    # README definition: explicitly fixed-budget and explicitly not anytime.
    old_footer = """o.append('*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform '
             'targets in [10²…10⁻⁸] per function); fixed-budget analogue of '
             'the COCO/BBOB ECDF. Higher is better.*')"""
    new_footer = """o.append('*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: '
             'for each function, the mean attainment rate over 51 log-uniform targets '
             'in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors '
             'at that budget. Class and SUM rows add the per-function FBTC(B) values. '
             'Each budget is evaluated separately; FBTC(B) is not an anytime measure. '
             'Higher is better.*')"""
    text = text.replace(old_footer, new_footer)

    return text


def patch_suite_report(text: str) -> str:
    replacements = [
        ("where <cov> = FBTC if ANY algorithm has FBTC>0 for that (dim,class) at",
         "where <cov> = FBTC(B) if ANY algorithm has FBTC>0 for that (dim,class) at"),
        ("* Budget metric per class: FBTC (monotone envelope) if any algorithm has\n    FBTC>0 at any budget; else median-SUM (lower-better, no envelope).",
         "* Budget metric per class: raw FBTC(B) at each evaluated fixed budget.\n    No running maximum and no metric substitution are applied."),
        ("cov_label, cov_key = ('FBTC', 'FBTC') if use_fbtc else ('mean-SUM', 'mean')",
         "cov_label, cov_key = ('FBTC(B)', 'FBTC') if use_fbtc else ('mean-SUM', 'mean')"),
        ("(worst-SUM, median-SUM, FBTC, best-SUM)",
         "(worst-SUM, median-SUM, FBTC(B), best-SUM)"),
        ("ax.set_xlabel('Budget (MaxFES)', fontsize=11)",
         "ax.set_xlabel('Fixed evaluation budget B (NFE)', fontsize=11)"),
        ("ylab = f'FBTC (sum over {nmax} functions)'",
         "ylab = f'SUM(FBTC(B)) over {nmax} functions'"),
        ("## FBTC — Fixed-Budget Target Coverage (higher is better)",
         "## FBTC(B) — Fixed-Budget Target Coverage (higher is better)"),
    ]
    for old, new in replacements:
        text, _ = _replace(text, old, new)

    # Always use raw FBTC for budget scaling; do not silently switch to median.
    block_re = re.compile(
        r"    # FBTC unless all-zero at every budget -> median\n"
        r"    any_fbtc = any\(series\[b\]\[a\]\['FBTC'\] > 1e-12\n"
        r"                   for b in budgets for a in algos\)\n"
        r"    # Metric switching is restricted to the composition class: elsewhere a\n"
        r"    # flat-zero FBTC panel is preferred over a silent change of metric\.\n"
        r"    metric = 'FBTC' if \(any_fbtc or cls != 'composition'\) else 'median'\n"
    )
    text = block_re.sub(
        "    # Raw fixed-budget coverage is shown even when it is identically zero.\n"
        "    # This intentionally avoids both a running maximum and metric substitution.\n"
        "    metric = 'FBTC'\n",
        text,
        count=1,
    )
    text = text.replace(
        "        y = _env(raw) if metric == 'FBTC' else raw\n        ax.plot(x, y, label=DISPLAY.get(a, a), **STYLE[a])",
        "        ax.plot(x, raw, label=DISPLAY.get(a, a), **STYLE[a])",
    )
    old_axis_block = r"""    if metric == 'FBTC':
        if cls != 'composition':
            ax.axhline(nmax, ls=':', color='gray', lw=1)
            ax.text(x[-1], nmax, f' max={nmax}', va='center', ha='left',
                    color='gray', fontsize=9)
            ax.set_ylim(0, nmax * 1.06)
        else:
            ax.set_ylim(0, None)
        ylab = f'SUM(FBTC(B)) over {nmax} functions'
        title = f'{suite.upper()}  D={dim}\n{CLASS_TITLE[cls]} class'
    else:
        ylab = f'Median error, summed over {nmax} functions (lower is better)'
        title = (f'{suite.upper()}  D={dim}\n'
                 f'{CLASS_TITLE[cls]} class (median error)')"""
    new_axis_block = r"""    if cls != 'composition':
        ax.axhline(nmax, ls=':', color='gray', lw=1)
        ax.text(x[-1], nmax, f' max={nmax}', va='center', ha='left',
                color='gray', fontsize=9)
        ax.set_ylim(0, nmax * 1.06)
    else:
        ax.set_ylim(0, None)
    ylab = f'SUM(FBTC(B)) over {nmax} functions'
    title = f'{suite.upper()}  D={dim}\n{CLASS_TITLE[cls]} class'"""
    text = text.replace(old_axis_block, new_axis_block)
    # Remove the now-unused envelope helper if present.
    old_env = """
def _env(v):
    o, m = [], -np.inf
    for x in v:
        m = max(m, x)
        o.append(m)
    return o
"""
    text = text.replace(old_env, "\n")


    # README budget prose: no envelope, no median fallback.
    old_note = """note = ('FBTC by budget, monotone envelope; higher is better.')
            # composition may be median
            if budget_metric.get((dim, 'composition')) == 'median':
                note += (' Composition is shown as *median error* '
                         '(lower is better): no algorithm reaches even the '
                         'easiest target, so FBTC is zero for all.')"""
    new_note = """note = ('Raw FBTC(B) at each evaluated fixed budget; no running maximum '
                    'is applied. Each point is a separate fixed-budget experiment; '
                    'higher is better.')"""
    text = text.replace(old_note, new_note)

    old_footer = """o.append('*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform '
             'targets in [10²…10⁻⁸] per function); fixed-budget analogue of '
             'the COCO/BBOB ECDF. Higher is better.*')"""
    new_footer = """o.append('*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B: '
             'for each function, the mean attainment rate over 51 log-uniform targets '
             'in [10²…10⁻⁸] and 51 runs, computed from the terminal best-so-far errors '
             'at that budget. The tables sum per-function FBTC(B) within each class. '
             'Each budget is evaluated separately; FBTC(B) is not an anytime measure. '
             'Higher is better.*')"""
    text = text.replace(old_footer, new_footer)
    return text


def patch_mwu_generator(text: str) -> str:
    old = """        "functions separately for each budget and competitor.",
            "",
            "The U statistic in [`details.csv`](details.csv) is for the competitor","""
    new = """        "functions separately for each budget and competitor.",
            "The test is evaluated with SciPy's asymptotic Mann–Whitney U method",
            "(`method=\\\"asymptotic\\\"`) with continuity correction (`use_continuity=True`).",
            "",
            "The U statistic in [`details.csv`](details.csv) is for the competitor","""
    text = text.replace(old, new)

    old_dsc = """        "Following the fixed-budget analysis workflow described by",
        "[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied",
        "Deep Statistical Comparison through",
        "[DSCTool](https://doi.org/10.1016/j.asoc.2019.105977) to the 51",
        "run-wise terminal errors for each function.","""
    new_dsc = """        "Following the fixed-budget analysis workflow described by",
        "[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied",
        "[Deep Statistical Comparison (Eftimov et al., 2017)](https://doi.org/10.1016/j.ins.2017.07.015)",
        "through [DSCTool (Eftimov et al., 2020)](https://doi.org/10.1016/j.asoc.2019.105977)",
        "to the 51 run-wise terminal errors for each function.","""
    text = text.replace(old_dsc, new_dsc)
    return text


def patch_experiment_readme(text: str) -> str:
    # Descriptive labels.
    text = text.replace(
        "(worst-SUM, median-SUM, FBTC, best-SUM)",
        "(worst-SUM, median-SUM, FBTC(B), best-SUM)",
    )
    text = text.replace(
        "FBTC by budget, monotone envelope (running maximum over budgets). Higher is better.",
        "Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment. Higher is better.",
    )
    text = text.replace(
        "FBTC by budget, monotone envelope; higher is better.",
        "Raw FBTC(B) at each evaluated fixed budget; no running maximum is applied. Each point is a separate fixed-budget experiment; higher is better.",
    )
    # Remove the old composition-only median substitution explanation if it follows the old note.
    text = text.replace(
        " Composition is shown as *median error* (lower is better): no algorithm reaches even the easiest target, so FBTC is zero for all.",
        "",
    )
    text = text.replace(
        "## FBTC — Fixed-Budget Target Coverage (higher is better)",
        "## FBTC(B) — Fixed-Budget Target Coverage (higher is better)",
    )
    # Metric column labels in cell README tables.
    text = re.sub(r"(\|\s*(?:\*\*[^|]+\*\* \(n=\d+\)|)\s*\|\s*)FBTC(\s*\|)", r"\1FBTC(B)\2", text)
    text = re.sub(r"(\|\s*\|\s*)FBTC(\s*\|)", r"\1FBTC(B)\2", text)

    old_footer = "*FBTC = Fixed-Budget Target Coverage (sum across 51 log-uniform targets in [10²…10⁻⁸] per function); fixed-budget analogue of the COCO/BBOB ECDF. Higher is better.*"
    new_footer = ("*FBTC(B) = Fixed-Budget Target Coverage at evaluation budget B. For each function, "
                  "it is the mean attainment rate over 51 log-uniform targets in [10²…10⁻⁸] and 51 runs, "
                  "computed from the terminal best-so-far errors at that budget. Class and SUM values add "
                  "the per-function FBTC(B) values. Each budget is evaluated separately; FBTC(B) is not an "
                  "anytime measure. Higher is better.*")
    text = text.replace(old_footer, new_footer)
    return text


def patch_mwu_readme(text: str) -> str:
    marker = ("Bonferroni adjustment is applied over all\n"
              "functions separately for each budget and competitor.\n")
    addition = (marker +
                "The test is evaluated with SciPy's asymptotic Mann–Whitney U method "
                "(`method=\"asymptotic\"`) with continuity correction "
                "(`use_continuity=True`).\n")
    if marker in text and "use_continuity=True" not in text:
        text = text.replace(marker, addition, 1)

    old = ("Following the fixed-budget analysis workflow described by\n"
           "[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied\n"
           "Deep Statistical Comparison through\n"
           "[DSCTool](https://doi.org/10.1016/j.asoc.2019.105977) to the 51\n"
           "run-wise terminal errors for each function.")
    new = ("Following the fixed-budget analysis workflow described by\n"
           "[Wang et al. (2022)](https://doi.org/10.1145/3510426), we applied\n"
           "[Deep Statistical Comparison (Eftimov et al., 2017)](https://doi.org/10.1016/j.ins.2017.07.015)\n"
           "through [DSCTool (Eftimov et al., 2020)](https://doi.org/10.1016/j.asoc.2019.105977)\n"
           "to the 51 run-wise terminal errors for each function.")
    text = text.replace(old, new)
    return text


def linked_readmes(root: Path) -> tuple[list[Path], list[Path]]:
    exp = []
    mwu = []
    for suite, dims in SUITE_DIMS.items():
        exp.append(root / "experiments" / suite / "README.md")
        for dim in dims:
            exp.append(root / "experiments" / suite / f"d{dim}" / "README.md")
            mwu.append(root / "mwu" / suite / f"d{dim}" / "README.md")
    return exp, mwu


def make_backup(root: Path, files: list[Path]) -> Path:
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path("/tmp") / f"msc_cma_fbtc_readme_backup_{stamp}.tar.gz"
    with tarfile.open(out, "w:gz") as tf:
        for p in files:
            if p.exists():
                tf.add(p, arcname=str(p.relative_to(root)))
    return out


def write_if_changed(path: Path, new: str) -> bool:
    old = path.read_text(encoding="utf-8")
    if new == old:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def regenerate_budget_plots(root: Path) -> None:
    analysis = root / "analysis"
    sys.path.insert(0, str(analysis))
    sys.path.insert(0, str(root / "benchmark"))
    cr = importlib.import_module("cell_report")
    sr = importlib.import_module("suite_report")

    # The current tracked generators save directly to .png.  A local variant
    # may expose save_fig and expect an extensionless basename; support both.
    cell_extensionless = hasattr(cr, "save_fig")
    suite_extensionless = hasattr(sr, "save_fig") or cell_extensionless

    for suite, dims in SUITE_DIMS.items():
        for dim in dims:
            base = root / "experiments" / suite / f"d{dim}"
            if not base.is_dir():
                continue
            algos = [a for a in cr.ALGO_ORDER if (base / a).is_dir()]
            if len(algos) != len(cr.ALGO_ORDER):
                missing = sorted(set(cr.ALGO_ORDER) - set(algos))
                raise RuntimeError(f"{base}: missing core algorithm directories: {missing}")
            # cell_report uses this global in titles.
            cr.dimlabel = f"D={dim}"
            for cls in cr.CLASSES:
                png = base / f"budget_{cls}.png"
                out = str(png.with_suffix("")) if cell_extensionless else str(png)
                cr.fig_budget(str(base), algos, suite, cls, out)

            # Suite-level budget figures have distinct filenames but the same
            # underlying raw fixed-budget data.
            salgos = [a for a in sr.ALGO_ORDER if (base / a).is_dir()]
            for cls in sr.CLASSES:
                png = base / f"budget_d{dim}_{cls}.png"
                out = str(png.with_suffix("")) if suite_extensionless else str(png)
                sr.fig_budget(str(base), salgos, suite, dim, cls, out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    ap.add_argument("--no-plots", action="store_true", help="do not regenerate budget PNGs")
    args = ap.parse_args()
    root = args.root.resolve()

    required = [root / p for p in SOURCE_FILES]
    exp_readmes, mwu_readmes = linked_readmes(root)
    missing = [p for p in required + exp_readmes + mwu_readmes if not p.is_file()]
    if missing:
        print("ERROR: required files are missing:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        return 2

    plot_files = []
    for suite, dims in SUITE_DIMS.items():
        for dim in dims:
            base = root / "experiments" / suite / f"d{dim}"
            plot_files.extend(base.glob("budget*.png"))
    backup = make_backup(root, required + exp_readmes + mwu_readmes + list(plot_files))
    print(f"Backup: {backup}")

    changed = []
    transforms = {
        root / "analysis/cell_report.py": patch_cell_report,
        root / "analysis/suite_report.py": patch_suite_report,
        root / "analysis/run_mwu_all_functions.py": patch_mwu_generator,
    }
    for p, fn in transforms.items():
        old = p.read_text(encoding="utf-8")
        if write_if_changed(p, fn(old)):
            changed.append(p)

    for p in exp_readmes:
        old = p.read_text(encoding="utf-8")
        if write_if_changed(p, patch_experiment_readme(old)):
            changed.append(p)
    for p in mwu_readmes:
        old = p.read_text(encoding="utf-8")
        if write_if_changed(p, patch_mwu_readme(old)):
            changed.append(p)

    # Syntax validation before touching plots.
    for p in required:
        py_compile.compile(str(p), doraise=True)

    if not args.no_plots:
        # Require at least one PKL so a no-PKL archive cannot accidentally be
        # presented as fully regenerated.
        if not any((root / "experiments").rglob("*.pkl")):
            raise RuntimeError("No PKL files found; rerun without --no-plots on the full local repository")
        regenerate_budget_plots(root)

    print(f"Updated source/README files: {len(changed)}")
    print("Experiment README targets:", len(exp_readmes))
    print("MWU/DSC README targets:", len(mwu_readmes))
    print("Plots:", "skipped" if args.no_plots else "raw FBTC(B) budget plots regenerated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
