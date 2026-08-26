#!/usr/bin/env python3
"""
Canonical presentation style for generated repository reports.

IMPORTANT
---------
This module controls DISPLAY/PRESENTATION only.

It must not change:
- experiment directory names;
- algorithm IDs stored in data files;
- CSV schemas unless explicitly intended;
- statistical calculations;
- PKL data;
- benchmark definitions.

Repository prose should describe measured quantities and statistical
directions, rather than algorithms as "better" or "worse".
"""

from __future__ import annotations

import math


# ----------------------------------------------------------------------
# Algorithm display names
# ----------------------------------------------------------------------

DISPLAY_NAME = {
    "MSC-CMA": "MSC-CMA-ES",
    "MSC-CMA-Conly": "MSC-CMA-ES (C-only)",
    "BIPOP-CMA": "BIPOP-CMA-ES",
    "LSRTDE": "L-SRTDE",
    "NLSHADE-RSP": "NL-SHADE-RSP",
    "NEA2PLUS-PY": "NEA2+",
    "ARRDE": "ARRDE",
    "j2020": "j2020",
    "jSO": "jSO",
}


def display_name(name: str) -> str:
    """Return manuscript/repository display name for an algorithm ID."""
    return DISPLAY_NAME.get(name, name)


# ----------------------------------------------------------------------
# Function-class display names
# ----------------------------------------------------------------------

CLASS_LABEL = {
    "basic": "Unimodal and simple multimodal",
    "simple": "Unimodal and simple multimodal",
    "unimodal": "Unimodal and simple multimodal",
    "hybrid": "Hybrid",
    "composition": "Composition",
    "all": "All",
}


def class_label(name: str) -> str:
    return CLASS_LABEL.get(name.lower(), name)


# ----------------------------------------------------------------------
# Metric display names
# ----------------------------------------------------------------------

METRIC_LABEL = {
    "mean": "Mean",
    "median": "Median",
    "best": "Minimum",
    "worst": "Maximum",
    "std": "Std.",
    "fbtc": "FBTC(B)",
    "FBTC": "FBTC(B)",
}


def metric_label(name: str) -> str:
    return METRIC_LABEL.get(name, name)


# ----------------------------------------------------------------------
# Budget formatting
# ----------------------------------------------------------------------

def format_budget(budget: int) -> str:
    """
    Human-readable scientific notation used in README files.

    Examples
    --------
    50_000     -> 5×10^4
    100_000    -> 10^5
    200_000    -> 2×10^5
    1_000_000  -> 10^6
    3_000_000  -> 3×10^6
    10_000_000 -> 10^7
    20_000_000 -> 2×10^7
    """
    b = int(budget)
    if b <= 0:
        raise ValueError(f"Budget must be positive: {budget}")

    exponent = int(math.floor(math.log10(b)))
    power = 10 ** exponent

    if b % power == 0:
        coefficient = b // power
        if coefficient == 1:
            return f"10^{exponent}"
        if 1 < coefficient < 10:
            return f"{coefficient}×10^{exponent}"

    return f"{b:,}"


# ----------------------------------------------------------------------
# Numerical presentation
# ----------------------------------------------------------------------

def format_value(value: float, sig: int = 6) -> str:
    """
    Compact README presentation.

    Raw CSV files should retain full numerical precision.
    """
    x = float(value)

    if not math.isfinite(x):
        return str(x)

    if x == 0:
        return "0"

    return f"{x:.{sig}g}"


def format_p(value: float, sig: int = 6) -> str:
    """Canonical p-value presentation in README tables."""
    x = float(value)

    if not math.isfinite(x):
        return str(x)

    if x == 0:
        return "0"

    return f"{x:.{sig}g}"


# ----------------------------------------------------------------------
# Canonical labels used in statistical tables
# ----------------------------------------------------------------------

P_RAW = "p_raw"
P_BONFERRONI = "p_Bonferroni"
P_HOLM = "p_Holm"
P_FRIEDMAN = "Friedman p"

DIRECTION_LABEL = "Direction"

ARROW_LOWER = "↓"
ARROW_HIGHER = "↑"
ARROW_NS = "—"


# ----------------------------------------------------------------------
# Canonical FBTC(B) wording
# ----------------------------------------------------------------------

FBTC_NAME = "FBTC(B)"

FBTC_NOTE = (
    "FBTC(B) denotes Fixed-Budget Target Coverage at evaluation budget B. "
    "Each budget is evaluated separately; FBTC(B) is not an anytime measure."
)


# ----------------------------------------------------------------------
# Canonical descriptive-table note
# ----------------------------------------------------------------------

DESCRIPTIVE_BOLD_NOTE = (
    "Bold marks the minimum value for error-based metrics and standard "
    "deviation, and the maximum value for FBTC(B). "
    "These values are descriptive and are not significance tests."
)
