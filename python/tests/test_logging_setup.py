"""Tests for capsize_commons.logging.setup."""

import io
import json
import logging

import pytest

from capsize_commons.logging import (
    configure_logging,
    logging_enabled,
    reset_logging,
)


def test_disabled_without_environment_or_force(monkeypatch) -> None:
    monkeypatch.delenv("CAPSIZE_LOG_JSON", raising=False)
    monkeypatch.delenv("CAPSIZE_LOG_LEVEL", raising=False)
    assert not logging_enabled()
    assert configure_logging() is None


def test_force_installs_a_json_handler() -> None:
    stream = io.StringIO()
    handler = configure_logging(json_mode=True, force=True, stream=stream)
    assert handler is not None
    logging.getLogger("capsize").info("ping")
    payload = json.loads(stream.getvalue().strip())
    assert payload["message"] == "ping"
    reset_logging()


def test_reset_restores_previous_state() -> None:
    logger = logging.getLogger("capsize")
    before = (logger.level, logger.propagate)
    configure_logging(force=True, json_mode=True, stream=io.StringIO())
    assert logger.propagate is False
    reset_logging()
    assert (logger.level, logger.propagate) == before
    assert logger.handlers == []


def test_level_and_json_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("CAPSIZE_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("CAPSIZE_LOG_JSON", "1")
    assert logging_enabled()
    stream = io.StringIO()
    handler = configure_logging(stream=stream)
    assert handler is not None
    assert logging.getLogger("capsize").level == logging.DEBUG
    logging.getLogger("capsize").debug("dbg")
    assert json.loads(stream.getvalue().strip())["level"] == "DEBUG"
    reset_logging()


def test_custom_logger_name_is_isolated(monkeypatch) -> None:
    monkeypatch.delenv("CAPSIZE_LOG_JSON", raising=False)
    stream = io.StringIO()
    handler = configure_logging(
        force=True, logger_name="svc", stream=stream, json_mode=False
    )
    assert handler is not None
    logging.getLogger("svc").info("human")
    assert "human" in stream.getvalue()
    reset_logging("svc")


@pytest.mark.parametrize("flag", ["", "0", "false", "no", "off"])
def test_falsey_flags(monkeypatch, flag: str) -> None:
    monkeypatch.setenv("CAPSIZE_LOG_JSON", flag)
    monkeypatch.delenv("CAPSIZE_LOG_LEVEL", raising=False)
    assert not logging_enabled()
