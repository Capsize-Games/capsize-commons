"""Tests for capsize_commons.logging.json_formatter."""

import json
import logging

from capsize_commons.logging import JsonFormatter


def _record() -> logging.LogRecord:
    return logging.LogRecord(
        name="svc",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )


def test_base_fields_match_the_standards_shape() -> None:
    payload = json.loads(JsonFormatter().format(_record()))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "svc"
    assert payload["message"] == "hello world"
    assert "timestamp" in payload
    # ISO-8601 with an explicit UTC offset.
    assert payload["timestamp"].endswith("+00:00")


def test_identifier_fields_and_nested_fields() -> None:
    record = _record()
    record.request_id = "req-1"
    record.fields = {"attempt": 2}
    payload = json.loads(JsonFormatter().format(record))
    assert payload["request_id"] == "req-1"
    assert payload["fields"] == {"attempt": 2}


def test_message_key_can_reproduce_a_legacy_shape() -> None:
    record = _record()
    record.run_id = "run-1"
    formatter = JsonFormatter(
        message_key="event",
        identifier_fields=("run_id", "config_id", "config_hash"),
    )
    payload = json.loads(formatter.format(record))
    assert payload["event"] == "hello world"
    assert payload["run_id"] == "run-1"
    assert "message" not in payload
    # Fields outside the configured set are not copied.
    record.request_id = "req-1"
    assert "request_id" not in json.loads(formatter.format(record))


def test_exception_is_rendered() -> None:
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        import sys

        record = _record()
        record.exc_info = sys.exc_info()
    payload = json.loads(JsonFormatter().format(record))
    assert "RuntimeError: boom" in payload["exception"]
