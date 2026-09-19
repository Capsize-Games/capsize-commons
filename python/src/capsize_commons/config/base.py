"""A shared ``pydantic-settings`` base and a per-class cached accessor.

Every FastAPI service in the fleet re-declared ``class Settings(BaseSettings)``
plus a ``@lru_cache get_settings()``. The base here fixes the common
conventions (``.env`` loading, unknown keys ignored) and the factory caches one
instance per settings class, so tests can clear it in one call.

The cache is a plain dict rather than ``functools.cache`` on purpose: wrapping
a generic function in ``@cache`` erases its ``TypeVar`` as far as mypy is
concerned, so every adopter's thin ``get_settings()`` wrapper reported
``no-any-return`` under ``--strict``. A dict keeps the generic signature
intact while behaving identically at runtime.
"""

from __future__ import annotations

from typing import TypeVar, cast

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["CapsizeSettings", "clear_settings_cache", "get_settings"]

_T = TypeVar("_T", bound=BaseSettings)

_CACHE: dict[type[BaseSettings], BaseSettings] = {}


class CapsizeSettings(BaseSettings):
    """Base class for Capsize runtime settings.

    Subclasses override ``model_config`` to set their own ``env_prefix``
    (``CAPSIZE_`` by default). Real ``.env`` files stay gitignored; ship an
    ``.env.example`` alongside them (§7).
    """

    model_config = SettingsConfigDict(
        env_prefix="CAPSIZE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


def get_settings(settings_cls: type[_T]) -> _T:
    """Return the process-wide, cached instance of ``settings_cls``."""
    if settings_cls not in _CACHE:
        _CACHE[settings_cls] = settings_cls()
    return cast(_T, _CACHE[settings_cls])


def clear_settings_cache() -> None:
    """Drop every cached settings instance (used by tests)."""
    _CACHE.clear()
