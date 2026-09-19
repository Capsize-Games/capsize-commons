"""The §14 JSON log shape, in one place.

Standards §14 requires structured JSON on stdout with at least ``timestamp``,
``level``, ``logger`` and ``message``. This module has no dependency beyond the
standard library and no import-time side effects.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

__all__ = ["JsonFormatter"]

#: Optional correlation fields copied onto the record when present.
_IDENTIFIER_FIELDS = ("service", "request_id", "trace_id", "span_id", "event")


class JsonFormatter(logging.Formatter):
    """Render a log record as one compact JSON object on a single line."""

    def format(self, record: logging.LogRecord) -> str:
        """Return ``record`` serialized as a JSON line."""
        return json.dumps(
            self.build_payload(record), default=str, ensure_ascii=False
        )

    def build_payload(self, record: logging.LogRecord) -> dict[str, Any]:
        """Return the standards-shaped mapping for ``record``.

        The base fields are always present; correlation fields are added only
        when the caller supplied them via ``extra=``. An optional ``fields``
        mapping is nested under ``"fields"`` rather than spread into the
        payload, so a field can never overwrite a base field.
        """
        created = datetime.fromtimestamp(record.created, UTC)
        payload: dict[str, Any] = {
            "timestamp": created.isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for name in _IDENTIFIER_FIELDS:
            value = getattr(record, name, None)
            if value is not None:
                payload[name] = value
        fields = getattr(record, "fields", None)
        if isinstance(fields, Mapping):
            payload["fields"] = dict(fields)
        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)
        return payload
