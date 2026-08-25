#!/usr/bin/env python3
"""
B-only phi ablation for MSC-CMA-ES.

Purpose
-------
Diagnostic ablation of the B configuration, primarily for the hybrid
functions.

Modes
-----
    --phi staircase
        B configuration only, original automatic staircase phi selection.

    --phi 2.0
        B configuration only, staircase disabled, fixed phi = 2.0.

    --phi 1.3
        B configuration only, staircase disabled, fixed phi = 1.3.

Everything else is inherited from the tuned B configuration:
    - Phase-0 sample size and sampling method
    - NBC Rule 1 / Rule 2 parameters
    - basin-dependent sigma0
    - basin-dependent CMA population size
    - k-NN convergence tracking / exclusion
    - CMA stopping criteria
    - final refinement

Because this is a single-configuration run:
    mode_schedule = None

there is no C/B alternation and no cross-cycle Phase-0 reuse.

Outputs
-------
ablations/experiments/<suite>/d<dim>/
    B-ONLY-STAIR/maxevals_<N>/
    B-ONLY-PHI2/maxevals_<N>/
    B-ONLY-PHI13/maxevals_<N>/

Each directory contains f<k>.pkl and summary.csv.
"""

import argparse
import dataclasses
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed


# -------------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------------

_ABL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_ABL_DIR)

for _p in (
    os.path.join(_ROOT, "algorithms"),
    os.path.join(_ROOT, "benchmark"),
):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)


# -------------------------------------------------------------------------
# Project imports
# -------------------------------------------------------------------------

from _common import (  # noqa: E402
    ImprovementRecorder,
    build_outdir,
    parse_functions,
    print_func_result,
    print_header,
    suite_config,
    suite_default_maxevals,
    summary_row,
    write_function_pkl,
    write_summary_csv,
)

from auto_config import get_B  # noqa: E402
from basin_detector import NBCDetector  # noqa: E402
from msc_cma import MSC_CMA  # noqa: E402


# =========================================================================
# Fixed-phi detector
# =========================================================================

class FixedPhiDetector(NBCDetector):
    """NBCDetector with staircase phi selection replaced by a constant."""

    def __init__(self, dim, bounds, cfg, seed, phi_fixed):
        super().__init__(dim, bounds, cfg, seed)
        self.phi_fixed = float(phi_fixed)

    def _staircase_phi(self, n_target):
        return self.phi_fixed, []


class MSC_BOnlyFixedPhi(MSC_CMA):
    """B-only MSC with a fixed NBC cutting threshold."""

    def __init__(
        self,
        func,
        bounds,
        maxevals,
        seed,
        config,
        phi_fixed,
        disp=False,
    ):
        self.phi_fixed = float(phi_fixed)

        # Single configuration:
        # mode_schedule=None => B only, no alternation, no Phase-0 reuse.
        super().__init__(
            func,
            bounds,
            maxevals,
            seed=seed,
            config=config,
            mode_schedule=None,
            disp=disp,
        )

    def _make_detector_for_cycle(self, cycle, cfg):
        cycle_seed = self.seed + cycle * 10000

        detector = FixedPhiDetector(
            self.dim,
            self.bounds,
            cfg,
            cycle_seed,
            self.phi_fixed,
        )

        return detector, cfg.sampling_method


# =========================================================================
# Helpers
# =========================================================================

def phi_mode(value):
    """Parse CLI --phi."""
    s = str(value).strip().lower()

    if s == "staircase":
        return "staircase", None

    try:
        x = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "--phi must be staircase, 2.0, or 1.3"
        )

    if x == 2.0:
        return "fixed", 2.0

    if x == 1.3:
        return "fixed", 1.3

    raise argparse.ArgumentTypeError(
        "--phi must be staircase, 2.0, or 1.3"
    )


def algo_name(phi_kind, phi_fixed):
    if phi_kind == "staircase":
        return "B-ONLY-STAIR"

    if phi_fixed == 2.0:
        return "B-ONLY-PHI2"

    if phi_fixed == 1.3:
        return "B-ONLY-PHI13"

    raise RuntimeError("Unsupported phi configuration")


# =========================================================================
# Worker: one seed
# =========================================================================

def _run_seed(
    suite,
    fnum,
    dim,
    maxevals,
    seed,
    cfg_B,
    phi_kind,
    phi_fixed,
    disp=False,
):
    cec_cls, bias, bounds = suite_config(suite, fnum, dim)
    cec = cec_cls(fnum, dim)

    recorder = ImprovementRecorder(
        cec,
        f_opt=bias,
        maxevals=maxevals,
    )

    if phi_kind == "staircase":
        # Original detector, B configuration only.
        solver = MSC_CMA(
            recorder,
            bounds,
            maxevals,
            seed=seed,
            config=cfg_B,
            mode_schedule=None,
            disp=disp,
        )
    else:
        # Same B-only solver, but staircase replaced by fixed phi.
        solver = MSC_BOnlyFixedPhi(
            recorder,
            bounds,
            maxevals,
            seed=seed,
            config=cfg_B,
            phi_fixed=phi_fixed,
            disp=disp,
        )

    result = solver.solve()
    recorder.finalize()

    cycles_dicts = [c.as_dict() for c in result.cycles]

    pre_refine_err = (
        float(result.best_f_pre_refine) - float(bias)
    )

    nfev_pre_refine = (
        int(result.cycles[-1].nfev_end)
        if result.cycles
        else 0
    )

    nfev_total = int(solver.nfev)

    return (
        seed,
        recorder.best_err,
        recorder.improvements,
        dict(solver.popsize_hist),
        cycles_dicts,
        pre_refine_err,
        nfev_pre_refine,
        nfev_total,
    )


# =========================================================================
# CLI
# =========================================================================

def build_parser():
    p = argparse.ArgumentParser(
        description=(
            "B-only MSC-CMA-ES phi ablation: "
            "staircase, fixed phi=2.0, or fixed phi=1.3."
        )
    )

    p.add_argument(
        "--suite",
        required=True,
        choices=[
            "cec2014",
            "cec2017",
            "cec2019",
            "cec2020",
            "cec2022",
        ],
    )

    p.add_argument("--dim", type=int, required=True)

    p.add_argument(
        "--functions",
        type=str,
        required=True,
        help="Comma-separated: 11,12,...,20 or f11,f12,...,f20",
    )

    p.add_argument(
        "--phi",
        required=True,
        help="staircase | 2.0 | 1.3",
    )

    p.add_argument("--runs", type=int, default=51)
    p.add_argument("--seed-start", type=int, default=0)

    p.add_argument(
        "--maxevals",
        type=int,
        default=0,
        help="0 = suite default",
    )

    p.add_argument("--jobs", type=int, default=1)

    p.add_argument(
        "--outdir",
        type=str,
        default="",
        help="Optional explicit output directory",
    )

    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing f*.pkl files",
    )

    p.add_argument(
        "--logs",
        action="store_true",
        help="Verbose per-cycle output; use mainly with --runs 1 --jobs 1",
    )

    p.add_argument(
        "--popsize-hist",
        action="store_true",
        help="Print aggregate CMA population-size histogram",
    )

    return p


# =========================================================================
# Main
# =========================================================================

def main():
    args = build_parser().parse_args()

    phi_kind, phi_fixed = phi_mode(args.phi)
    algo = algo_name(phi_kind, phi_fixed)

    fnums = parse_functions(args.functions)

    seeds = list(
        range(
            args.seed_start,
            args.seed_start + args.runs,
        )
    )

    maxevals = (
        args.maxevals
        or suite_default_maxevals(args.suite, args.dim)
    )

    # ONLY the tuned B configuration.
    cfg_B = get_B(args.dim)

    outdir = (
        args.outdir
        or build_outdir(
            args.suite,
            args.dim,
            algo,
            maxevals,
            base=os.path.join(_ABL_DIR, "experiments"),
        )
    )

    # Prevent accidental overwrite.
    if not args.force:
        for fnum in fnums:
            path = os.path.join(
                outdir,
                f"f{fnum}.pkl",
            )

            if os.path.exists(path):
                print(
                    f"ERROR: {path} already exists. "
                    f"Use --force to overwrite.",
                    file=sys.stderr,
                )
                sys.exit(1)

    print_header(
        args.suite,
        args.dim,
        algo,
        maxevals,
        args.runs,
        args.jobs,
    )

    if phi_kind == "staircase":
        phi_description = "automatic staircase"
    else:
        phi_description = f"fixed phi={phi_fixed}"

    print(
        f"Variant: B-only | {phi_description} | "
        f"single config | no C/B alternation | "
        f"no cross-cycle Phase-0 reuse"
    )

    print(f"B[{cfg_B.summary()}]")

    params_record = {
        "cli_args": vars(args),
        "variant": algo,
        "mode": "B-only",
        "phi_mode": phi_kind,
        "phi_fixed": phi_fixed,
        "config_B": dataclasses.asdict(cfg_B),
        "config_C": None,
        "phase0_reuse": False,
    }

    summary_rows = []

    for fnum in fnums:
        func_name = f"f{fnum}"

        print(
            f"-- {func_name} --",
            flush=True,
        )

        t0 = time.time()

        results = Parallel(n_jobs=args.jobs)(
            delayed(_run_seed)(
                args.suite,
                fnum,
                args.dim,
                maxevals,
                seed,
                cfg_B,
                phi_kind,
                phi_fixed,
                disp=args.logs,
            )
            for seed in seeds
        )

        elapsed = time.time() - t0

        results.sort(key=lambda t: t[0])

        ret_seeds = np.array(
            [r[0] for r in results],
            dtype=np.int64,
        )

        errors = np.array(
            [r[1] for r in results],
            dtype=np.float64,
        )

        improvements = [
            r[2] for r in results
        ]

        cycles_per_seed = [
            r[4] for r in results
        ]

        pre_refine_errors = np.array(
            [r[5] for r in results],
            dtype=np.float64,
        )

        nfev_pre_refine_arr = np.array(
            [r[6] for r in results],
            dtype=np.int64,
        )

        nfev_total_arr = np.array(
            [r[7] for r in results],
            dtype=np.int64,
        )

        # Aggregate popsize histogram.
        agg_hist = {}

        for r in results:
            for k, v in r[3].items():
                agg_hist[k] = (
                    agg_hist.get(k, 0) + v
                )

        _, bias, _ = suite_config(
            args.suite,
            fnum,
            args.dim,
        )

        path = write_function_pkl(
            outdir=outdir,
            suite=args.suite,
            dim=args.dim,
            func_name=func_name,
            f_opt=bias,
            algorithm=algo,
            maxevals=maxevals,
            seeds=ret_seeds,
            errors=errors,
            improvements=improvements,
            params=params_record,
            force=args.force,
            cycles_per_seed=cycles_per_seed,
            pre_refine_errors_per_seed=pre_refine_errors,
            nfev_pre_refine_per_seed=nfev_pre_refine_arr,
            nfev_total_per_seed=nfev_total_arr,
        )

        print_func_result(
            func_name,
            errors,
            elapsed,
        )

        print(
            f"       -> {path}",
            flush=True,
        )

        if args.popsize_hist and agg_hist:
            hist = " ".join(
                f"{k}:{v}"
                for k, v in sorted(
                    agg_hist.items()
                )
            )
            print(
                f"       popsize_hist: {hist}",
                flush=True,
            )

        summary_rows.append(
            summary_row(
                func_name,
                errors,
                elapsed,
                maxevals,
            )
        )

    csv_path = write_summary_csv(
        outdir,
        summary_rows,
    )

    print()
    print(f"Summary -> {csv_path}")


if __name__ == "__main__":
    main()
