"""Text and naming helpers that implement the fleet's casing rules (§3.1)."""

from __future__ import annotations

from capsize_commons.text.case import (
    slugify,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)

__all__ = ["slugify", "to_kebab_case", "to_pascal_case", "to_snake_case"]
