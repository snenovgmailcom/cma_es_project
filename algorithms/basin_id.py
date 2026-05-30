"""Helpers for basin identifiers used by MSC-CMA-ES.

Phase-0 basins are identified by an integer sample index. Split children keep
that original id nested as tuples, e.g. ``(346, 922)`` or ``((346, 922), 101)``.
The helpers here make that legacy representation explicit without changing it.
"""

from __future__ import annotations

from typing import Any, Tuple, TypeAlias, Union

# Keep the runtime representation unchanged: int for Phase-0, nested tuples for
# split children. This alias documents the intended shape and removes scattered
# ad-hoc ``Tuple`` hints from the code.
BasinId: TypeAlias = Union[int, Tuple[Any, int]]


def root_basin_id(basin_id: BasinId) -> int:
    """Return the Phase-0 integer ancestor of a possibly split basin id."""
    while isinstance(basin_id, tuple):
        basin_id = basin_id[0]
    return int(basin_id)


def format_basin_id(basin_id: BasinId) -> str:
    """Human-readable basin id: ``346`` or ``346/922/101``."""
    if isinstance(basin_id, tuple):
        return f"{format_basin_id(basin_id[0])}/{basin_id[1]}"
    return str(basin_id)


def serialize_basin_id(basin_id: BasinId) -> str:
    """Stable string form for result serialization and golden traces."""
    return format_basin_id(basin_id)


def serialize_basin_pair(source: BasinId, destination: BasinId | None) -> str:
    """Stable string key for migration matrices."""
    dest = "None" if destination is None else serialize_basin_id(destination)
    return f"{serialize_basin_id(source)}->{dest}"
