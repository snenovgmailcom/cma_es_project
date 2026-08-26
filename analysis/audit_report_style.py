#!/usr/bin/env python3
"""
Audit generated README presentation style.

This checks reader-visible text. It deliberately ignores:
- fenced code blocks;
- inline code;
- Markdown link destinations;
- the formal term "nearest-better".
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


RULES = [
    (
        "naked FBTC; use FBTC(B)",
        re.compile(r"\bFBTC\b(?!\(B\))"),
    ),
    (
        'comparative "better"; describe the measured direction instead',
        re.compile(r"\bbetter\b", re.I),
    ),
    (
        'comparative "worse"; describe the measured direction instead',
        re.compile(r"\bworse\b", re.I),
    ),
    (
        'use "Lowest-mean-rank algorithm", not "Best-ranked ..."',
        re.compile(r"\bbest-ranked\b", re.I),
    ),
    (
        'use "Friedman p"',
        re.compile(r"\bFriedman p-value\b", re.I),
    ),
    (
        'use p_raw',
        re.compile(r"\bRaw two-sided p-value\b", re.I),
    ),
    (
        'use p_Bonferroni',
        re.compile(r"\bBonferroni-adjusted p-value\b", re.I),
    ),
    (
        'use p_Holm',
        re.compile(r"\bHolm p-value\b", re.I),
    ),
    (
        'use full display name MSC-CMA-ES',
        re.compile(r"\bMSC-CMA\b(?!-ES)"),
    ),
    (
        'use full display name BIPOP-CMA-ES',
        re.compile(r"\bBIPOP-CMA\b(?!-ES)"),
    ),
    (
        'use NL-SHADE-RSP',
        re.compile(r"\bNLSHADE-RSP\b"),
    ),
    (
        'use L-SRTDE',
        re.compile(r"\bLSRTDE\b"),
    ),
    (
        'use NEA2+',
        re.compile(r"\bNEA2PLUS-PY\b"),
    ),
    (
        'use scientific budget notation, not K/M abbreviations',
        re.compile(
            r"(?<![A-Za-z0-9_])"
            r"(?:50K|100K|200K|300K|1M|3M|10M|20M)"
            r"(?![A-Za-z0-9_])"
        ),
    ),
    (
        'remove floating HTML TOC',
        re.compile(r"float\s*:\s*right", re.I),
    ),
]


def visible_text(text: str) -> str:
    # Fenced code.
    text = re.sub(r"```.*?```", "", text, flags=re.S)

    # Inline code.
    text = re.sub(r"`[^`\n]*`", "", text)

    # Keep Markdown link label, remove destination.
    text = re.sub(r"\]\([^)\n]*\)", "]()", text)

    # Formal technical term; do not treat its "better" as evaluative prose.
    text = re.sub(
        r"nearest[\-\u2011\u2013\u2014 ]better",
        "nearest_based",
        text,
        flags=re.I,
    )

    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        type=Path,
        default=Path("."),
    )
    ap.add_argument(
        "--report-only",
        action="store_true",
        help="print violations but exit successfully",
    )
    args = ap.parse_args()

    files = sorted(args.root.rglob("README.md"))

    violations = []

    for path in files:
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        text = visible_text(raw)

        for lineno, line in enumerate(text.splitlines(), 1):
            for description, pattern in RULES:
                if pattern.search(line):
                    violations.append(
                        (path, lineno, description, line.strip())
                    )

    for path, lineno, description, line in violations:
        print(f"{path}:{lineno}: {description}")
        print(f"    {line}")

    print()
    print("README files checked:", len(files))
    print("Style violations    :", len(violations))

    if violations and not args.report_only:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
