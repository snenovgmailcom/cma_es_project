#!/usr/bin/env python3
"""
Create the Nguyen (2024) comparison pages.

One file only. Run from ~/cma_es_project:

    python analysis/build_nguyen_comparison.py --check-only
    python analysis/build_nguyen_comparison.py

It reads MSC-CMA-ES PKLs locally and contains the published
CMAES-NBC-qN mean/std values from Nguyen (2024), Tables 10 and 12.

Outputs:
  related_comparisons/nguyen/README.md
  related_comparisons/nguyen/cec2014/d30/budget_300000/README.md
  related_comparisons/nguyen/cec2017/d30/budget_300000/README.md

No MWU or DSC is computed for Nguyen because run-wise CMAES-NBC-qN
samples are not available.
"""

from pathlib import Path
import argparse
import math
import pickle
import numpy as np

from report_style import (
    class_label,
    format_budget,
    format_value,
)

DOI = "10.1016/j.asoc.2024.112361"
DOI_URL = "https://doi.org/10.1016/j.asoc.2024.112361"
BUDGET = 300_000
DIM = 30
RUNS = 51
ZERO = 1e-8

# Published CMAES-NBC-qN values: function -> (mean, std)
# Nguyen (2024), Table 10: CEC2014, D=30
NGUYEN_CEC2014 = {
 1:(0.00e0,0.00e0),  2:(0.00e0,0.00e0),  3:(0.00e0,0.00e0),
 4:(0.00e0,0.00e0),  5:(2.17e1,2.45e-2),  6:(3.06e0,7.62e0),
 7:(0.00e0,0.00e0),  8:(2.33e2,7.37e1),  9:(7.63e0,4.20e1),
10:(7.88e2,4.15e2), 11:(1.88e2,1.99e2), 12:(5.13e0,4.61e0),
13:(7.75e-1,8.26e-2),14:(6.79e-1,1.37e-1),15:(1.23e6,8.78e6),
16:(9.66e0,2.45e0), 17:(1.46e2,6.41e2), 18:(5.28e-1,1.43e-1),
19:(3.14e0,1.08e0), 20:(1.70e0,6.47e-1),21:(4.06e4,2.28e5),
22:(1.34e2,5.18e1), 23:(1.02e3,2.25e3), 24:(2.27e2,3.29e1),
25:(2.52e2,1.83e2), 26:(1.01e2,1.51e-1),27:(5.71e2,1.17e3),
28:(8.62e2,9.47e1), 29:(7.12e2,9.21e1), 30:(7.87e2,4.95e2),
}

# Nguyen (2024), Table 12: CEC2017, D=30
NGUYEN_CEC2017 = {
 1:(0.00e0,0.00e0),  2:(0.00e0,0.00e0),  3:(0.00e0,0.00e0),
 4:(6.47e1,1.25e1),  5:(2.55e1,7.17e1),  6:(0.00e0,0.00e0),
 7:(3.61e2,8.04e2),  8:(2.54e1,8.13e1),  9:(0.00e0,0.00e0),
10:(4.77e2,3.63e2), 11:(4.56e4,3.05e5), 12:(3.80e4,2.49e5),
13:(7.09e4,3.83e5), 14:(1.96e1,6.45e0), 15:(1.33e9,8.08e9),
16:(1.94e1,2.38e1), 17:(3.03e1,6.56e0), 18:(2.22e1,1.15e-2),
19:(4.52e0,9.56e-1),20:(4.82e1,3.32e1),21:(4.28e2,8.27e1),
22:(3.19e3,2.54e3),23:(5.25e2,1.15e2),24:(5.22e2,1.10e2),
25:(3.87e2,2.92e0),26:(1.85e3,2.32e3),27:(5.31e2,9.15e1),
28:(4.00e3,1.08e4),29:(4.24e2,3.87e1),30:(2.03e3,1.66e2),
}

CLASSES = {
    "cec2014": {
        "basic": set(range(1,17)),
        "hybrid": set(range(17,23)),
        "composition": set(range(23,31)),
    },
    "cec2017": {
        "basic": {1, *range(3,11)},
        "hybrid": set(range(11,21)),
        "composition": set(range(21,31)),
    },
}

def cls(suite, fid):
    for name, funcs in CLASSES[suite].items():
        if fid in funcs:
            return class_label(name)
    raise ValueError((suite, fid))

def fmt(x):
    return format_value(float(x), sig=6)

def load_msc(suite, functions):
    base = Path("experiments") / suite / "d30" / "MSC-CMA" / "maxevals_300000"
    if not base.is_dir():
        raise SystemExit(f"Missing directory: {base}")

    out = {}
    for fid in functions:
        p = base / f"f{fid}.pkl"
        if not p.is_file():
            raise SystemExit(f"Missing: {p}")
        with p.open("rb") as f:
            d = pickle.load(f)

        e = np.asarray(d["errors"], dtype=float)
        if e.shape != (RUNS,):
            raise SystemExit(f"{p}: expected 51 errors, got {e.shape}")
        if int(d.get("maxevals", BUDGET)) != BUDGET:
            raise SystemExit(f"{p}: wrong budget")

        out[fid] = (
            float(e.mean()),
            float(e.std(ddof=1)),
        )
    return out

def page(suite, table_no, nguyen, functions):
    msc = load_msc(suite, functions)

    lines = [
        f"# {suite.upper()}, D=30, B={format_budget(BUDGET)} — MSC-CMA-ES vs CMAES-NBC-qN",
        "",
        "This page compares MSC-CMA-ES with the numerical values reported by "
        "Nguyen for CMAES-NBC-qN:",
        "",
        f"> D. M. Nguyen, *Adapting the population size in CMA-ES using "
        f"nearest-better clustering method for multimodal optimization*, "
        f"*Applied Soft Computing* 167 (2024), 112361. "
        f"DOI [{DOI}]({DOI_URL}).",
        "",
        f"Nguyen reports 51 runs per function and `maxFEs = 10,000 × D`; "
        f"therefore D=30 corresponds to **{format_budget(BUDGET)} NFE**. "
        f"CMAES-NBC-qN mean/std values below are taken from **Table {table_no}**.",
        "",
        "MSC-CMA-ES mean/std values are computed from the repository's 51 "
        "terminal-error runs at the same suite, dimension and budget. "
        "The MSC values are computed from the stored terminal errors without "
        "flooring or clipping; std uses `ddof=1`.",
        "",
        "**No MWU or DSC is computed for CMAES-NBC-qN**, because its run-wise "
        "samples are not available in the paper.",
        "",
    ]

    if suite == "cec2017":
        lines += [
            "CEC2017 `f2` is omitted here to remain consistent with the project's "
            "29-function CEC2017 evaluation set.",
            "",
        ]

    lines += [
        "| Function | Class | MSC-CMA-ES Mean | CMAES-NBC-qN Mean | MSC-CMA-ES Std. | CMAES-NBC-qN Std. |",
        "|:--|:--|--:|--:|--:|--:|",
    ]

    for fid in functions:
        mm, ms = msc[fid]
        nm, ns = nguyen[fid]

        if math.isclose(mm, nm, rel_tol=1e-12, abs_tol=1e-15):
            sm, sn = f"**{fmt(mm)}**", f"**{fmt(nm)}**"
        elif mm < nm:
            sm, sn = f"**{fmt(mm)}**", fmt(nm)
        else:
            sm, sn = fmt(mm), f"**{fmt(nm)}**"

        lines.append(
            f"| f{fid} | {cls(suite,fid)} | {sm} | {sn} | "
            f"{fmt(ms)} | {fmt(ns)} |"
        )

    lines += [
        "",
        "*Bold marks the minimum of the two mean values. This is descriptive and is not a significance test.*",
        "",
        f"Source for CMAES-NBC-qN: Nguyen (2024), Table {table_no}.",
        "",
    ]
    return "\n".join(lines)

def index_page():
    return f"""# CMAES-NBC-qN (Nguyen 2024) — published-value comparison

Nguyen reports CEC2014 and CEC2017 results for CMAES-NBC-qN in D=30 and D=50.
The two D=30 cells correspond directly to MSC-CMA-ES experiments at the same
budget, **{format_budget(BUDGET)} NFE**.

Reference:

> D. M. Nguyen, *Adapting the population size in CMA-ES using nearest-better
> clustering method for multimodal optimization*, *Applied Soft Computing*
> 167 (2024), 112361. DOI [{DOI}]({DOI_URL}).

| Suite | D | Budget | Published source | Comparison |
|:--|--:|--:|:--|:--|
| CEC2014 | 30 | {format_budget(BUDGET)} | Nguyen Table 10 | [MSC-CMA-ES vs CMAES-NBC-qN](cec2014/d30/budget_300000/README.md) |
| CEC2017 | 30 | {format_budget(BUDGET)} | Nguyen Table 12 | [MSC-CMA-ES vs CMAES-NBC-qN](cec2017/d30/budget_300000/README.md) |

Only published **mean and standard deviation** values are used for
CMAES-NBC-qN. No MWU or DSC is reported because the run-wise CMAES-NBC-qN
samples are not available.
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    f14 = tuple(range(1,31))
    f17 = (1, *range(3,31))

    # Validate embedded source data.
    if set(NGUYEN_CEC2014) != set(range(1,31)):
        raise SystemExit("CEC2014 Nguyen table incomplete")
    if set(NGUYEN_CEC2017) != set(range(1,31)):
        raise SystemExit("CEC2017 Nguyen table incomplete")

    p14 = page("cec2014", 10, NGUYEN_CEC2014, f14)
    p17 = page("cec2017", 12, NGUYEN_CEC2017, f17)
    idx = index_page()

    if args.check_only:
        print("CHECK PASSED")
        print("CEC2014 D30: 30 functions, Nguyen Table 10")
        print("CEC2017 D30: 29 functions (f2 excluded), Nguyen Table 12")
        print("Would write 3 README files.")
        return

    root = Path("related_comparisons/nguyen")
    p1 = root / "cec2014/d30/budget_300000/README.md"
    p2 = root / "cec2017/d30/budget_300000/README.md"
    p3 = root / "README.md"

    for path, text in ((p1,p14),(p2,p17),(p3,idx)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("WROTE", path)

if __name__ == "__main__":
    main()
