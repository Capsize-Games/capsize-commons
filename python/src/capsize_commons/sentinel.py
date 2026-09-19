"""A single shared ``UNSET`` sentinel.

Projects keep re-declaring ``_UNSET = object()`` so that ``None`` can be a
legitimate value distinct from "not supplied". This gives that sentinel one
identity across the fleet.
"""

from __future__ import annotations

from typing import Final

__all__ = ["UNSET", "is_unset"]


class _Unset:
    """The type of :data:`UNSET`. Instantiate only through the singleton."""

    __slots__ = ()

    def __bool__(self) -> bool:
        """Return ``False`` so ``if not value`` reads as "nothing given"."""
        return False

    def __repr__(self) -> str:
        """Return a stable, unambiguous spelling."""
        return "UNSET"


#: Sentinel for "no value was supplied", distinct from ``None``.
UNSET: Final[_Unset] = _Unset()


def is_unset(value: object) -> bool:
    """Return ``True`` when ``value`` is the shared :data:`UNSET` sentinel."""
    return value is UNSET
