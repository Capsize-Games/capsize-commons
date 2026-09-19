"""Structured JSON logging that matches CAPSIZE_PROJECT_STANDARDS.md §14.

Stdlib-only: part of the base install.
"""

from __future__ import annotations

from capsize_commons.logging.json_formatter import JsonFormatter
from capsize_commons.logging.setup import (
    DEFAULT_LEVEL,
    DEFAULT_LOGGER_NAME,
    configure_logging,
    logging_enabled,
    reset_logging,
)

__all__ = [
    "DEFAULT_LEVEL",
    "DEFAULT_LOGGER_NAME",
    "JsonFormatter",
    "configure_logging",
    "logging_enabled",
    "reset_logging",
]
