"""Tests for capsize_commons.config."""

import pytest
from pydantic_settings import SettingsConfigDict

from capsize_commons.config import (
    CapsizeSettings,
    clear_settings_cache,
    get_settings,
)


class _Settings(CapsizeSettings):
    model_config = SettingsConfigDict(
        env_prefix="CAPSIZE_TEST_", extra="ignore"
    )

    value: str = "default"


@pytest.fixture(autouse=True)
def _clean_cache():
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_reads_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("CAPSIZE_TEST_VALUE", "from-env")
    assert get_settings(_Settings).value == "from-env"


def test_falls_back_to_default(monkeypatch) -> None:
    monkeypatch.delenv("CAPSIZE_TEST_VALUE", raising=False)
    assert get_settings(_Settings).value == "default"


def test_caches_one_instance_per_class() -> None:
    assert get_settings(_Settings) is get_settings(_Settings)


def test_clear_cache_drops_the_instance() -> None:
    first = get_settings(_Settings)
    clear_settings_cache()
    assert get_settings(_Settings) is not first


def test_cache_is_keyed_per_class() -> None:
    class _Other(CapsizeSettings):
        model_config = SettingsConfigDict(
            env_prefix="CAPSIZE_OTHER_", extra="ignore"
        )

    assert get_settings(_Settings) is not get_settings(_Other)
    assert isinstance(get_settings(_Settings), _Settings)
