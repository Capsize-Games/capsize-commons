"""Opt-in, reversible structured logging.

Nothing here runs at import time and no entry point *must* call it, so a
library consumer's default logging behaviour is untouched. Call
:func:`configure_logging` to attach one handler to a named logger (never the
root logger) and :func:`reset_logging` to restore the exact prior state — which
is what makes this safe to use in tests.

``SPIKEFORGE_LOG_JSON`` / ``SPIKEFORGE_LOG_LEVEL`` and their copies across the
fleet become one implementation with a configurable prefix; the default prefix
here is ``CAPSIZE``.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Final, TextIO

from capsize_commons.logging.json_formatter import JsonFormatter

__all__ = [
    "DEFAULT_LEVEL",
    "DEFAULT_LOGGER_NAME",
    "configure_logging",
    "logging_enabled",
    "reset_logging",
]

#: Logger structured logging attaches to when no name is given.
DEFAULT_LOGGER_NAME: Final = "capsize"
#: Level used when neither the argument nor the environment supplies one.
DEFAULT_LEVEL: Final = "INFO"
#: Human-readable format used when JSON output is not requested.
HUMAN_FORMAT: Final = "%(asctime)s %(levelname)s %(name)s %(message)s"

_FALSEY: Final = ("", "0", "false", "no", "off")

# logger name -> (installed handler, previous level, previous propagate)
_installed: dict[str, tuple[logging.Handler, int, bool]] = {}


def _truthy(value: str | None) -> bool:
    """Return ``True`` when an environment flag is set to a truthy value."""
    return value is not None and value.strip().lower() not in _FALSEY


def _env_names(prefix: str) -> tuple[str, str]:
    """Return the ``(json_var, level_var)`` names for ``prefix``."""
    return f"{prefix}_LOG_JSON", f"{prefix}_LOG_LEVEL"


def logging_enabled(prefix: str = "CAPSIZE") -> bool:
    """Return ``True`` when the environment asks for logging to be set up."""
    json_var, level_var = _env_names(prefix)
    return _truthy(os.environ.get(json_var)) or bool(os.environ.get(level_var))


def _resolve_level(name: str | None, level_var: str) -> int:
    """Resolve a level from the argument, the environment, or the default."""
    resolved = name or os.environ.get(level_var) or DEFAULT_LEVEL
    candidate = getattr(logging, str(resolved).upper(), None)
    return candidate if isinstance(candidate, int) else logging.INFO


def _resolve_json(json_mode: bool | None, json_var: str) -> bool:
    """Resolve the JSON decision from the argument or the environment."""
    if json_mode is not None:
        return json_mode
    return _truthy(os.environ.get(json_var))


def _build_handler(use_json: bool, stream: TextIO | None) -> logging.Handler:
    """Return a stream handler carrying the JSON or human formatter."""
    handler = logging.StreamHandler(stream)
    formatter: logging.Formatter = (
        JsonFormatter() if use_json else logging.Formatter(HUMAN_FORMAT)
    )
    handler.setFormatter(formatter)
    return handler


def configure_logging(
    level: str | None = None,
    json_mode: bool | None = None,
    *,
    force: bool = False,
    stream: TextIO | None = None,
    logger_name: str = DEFAULT_LOGGER_NAME,
    env_prefix: str = "CAPSIZE",
) -> logging.Handler | None:
    """Attach the opt-in handler, or return ``None`` when logging is disabled.

    ``level`` / ``json_mode`` override ``<prefix>_LOG_LEVEL`` /
    ``<prefix>_LOG_JSON``. ``force`` configures even when no environment
    variable is set, and ``stream`` redirects output (used by tests). Repeating
    the call is safe: any previously installed handler is removed first.
    """
    json_var, level_var = _env_names(env_prefix)
    if not force and not logging_enabled(env_prefix):
        return None
    reset_logging(logger_name)
    logger = logging.getLogger(logger_name)
    handler = _build_handler(_resolve_json(json_mode, json_var), stream)
    _installed[logger_name] = (handler, logger.level, logger.propagate)
    logger.addHandler(handler)
    logger.setLevel(_resolve_level(level, level_var))
    logger.propagate = False
    return handler


def reset_logging(logger_name: str = DEFAULT_LOGGER_NAME) -> None:
    """Remove the installed handler and restore the previous logger state."""
    saved: Any = _installed.pop(logger_name, None)
    if saved is None:
        return
    handler, level, propagate = saved
    logger = logging.getLogger(logger_name)
    logger.removeHandler(handler)
    handler.close()
    logger.setLevel(level)
    logger.propagate = propagate
