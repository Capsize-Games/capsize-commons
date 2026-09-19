"""SQLAlchemy engine and session factories.

Consolidates the per-project ``make_engine`` / ``make_session_factory`` pair.
The SQLite branch is the part every copy got subtly wrong or left out: it
disables the thread check (so a single file-backed database can be shared) and
turns on ``PRAGMA foreign_keys`` (which SQLite leaves off by default, so every
``ON DELETE CASCADE`` in a project silently did nothing).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["make_engine", "make_session_factory"]


def make_engine(
    database_url: str,
    *,
    echo: bool = False,
    pool_pre_ping: bool = True,
    **engine_kwargs: Any,
) -> Engine:
    """Create an :class:`Engine`, applying SQLite-safe defaults.

    ``pool_pre_ping`` defaults to ``True`` so a pooled connection that a
    database or proxy has since dropped is detected and replaced (standards
    §6: pooling must be explicit, never unbounded).
    """
    connect_args: dict[str, Any] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=pool_pre_ping,
        connect_args=connect_args,
        **engine_kwargs,
    )
    if database_url.startswith("sqlite"):
        _enable_sqlite_foreign_keys(engine)
    return engine


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    """Turn on foreign-key enforcement for every SQLite connection."""

    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_connection: Any, _record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory with the fleet's standard flags."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
