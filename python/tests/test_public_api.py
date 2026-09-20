"""Compatibility checks for the public Python consumer surfaces."""

from __future__ import annotations

import importlib

import pytest

PUBLIC_MODULES = (
    ("capsize_commons.config", "CapsizeSettings", "get_settings"),
    ("capsize_commons.db", "Base", "UtcDateTime", "make_engine"),
    ("capsize_commons.http", "Backoff", "retry_sync", "retry_async"),
    ("capsize_commons.logging", "JsonFormatter", "configure_logging"),
    ("capsize_commons.text", "slugify", "to_snake_case"),
    ("capsize_commons.web", "health_router", "install_health_routes"),
)


@pytest.mark.parametrize("surface", PUBLIC_MODULES)
def test_public_symbols_remain_importable(surface: tuple[str, ...]) -> None:
    module_name, *symbols = surface
    module = importlib.import_module(module_name)

    assert set(symbols).issubset(set(module.__all__))
    for symbol in symbols:
        assert getattr(module, symbol)
