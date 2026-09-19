"""SQLAlchemy model conventions from CAPSIZE_PROJECT_STANDARDS.md §6.

Two things every model re-implemented, now shared:

* :class:`UtcDateTime` — SQLite has no native timezone-aware storage, so the
  stock ``DateTime`` reads back naive even when written aware. This reattaches
  UTC on the way out and rejects naive values on the way in.
* :class:`TimestampedBase` — the mandated ``id`` + ``created_at`` +
  ``updated_at`` columns, with a time-ordered UUIDv7 primary key.
"""

from __future__ import annotations

import datetime
import os
import time
import uuid

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

__all__ = ["Base", "TimestampedBase", "UtcDateTime", "uuid7"]


def uuid7() -> uuid.UUID:
    """Return a time-ordered UUIDv7 (§6 primary-key preference).

    Layout: 48-bit Unix milliseconds, 4-bit version, 12-bit ``rand_a``,
    2-bit variant, 62-bit ``rand_b``.
    """
    milliseconds = int(time.time() * 1000) & ((1 << 48) - 1)
    random_bits = int.from_bytes(os.urandom(10), "big") >> 6  # 74 random bits
    rand_a = random_bits >> 62
    rand_b = random_bits & ((1 << 62) - 1)
    value = (
        (milliseconds << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0x2 << 62)
        | rand_b
    )
    return uuid.UUID(int=value)


def utcnow() -> datetime.datetime:
    """Return the current time as a timezone-aware UTC ``datetime``."""
    return datetime.datetime.now(datetime.UTC)


class UtcDateTime(TypeDecorator[datetime.datetime]):
    """A ``DateTime`` that round-trips as timezone-aware UTC through SQLite."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self, value: datetime.datetime | None, dialect: object
    ) -> datetime.datetime | None:
        """Require and normalize an aware value on the way into storage."""
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("UtcDateTime requires a timezone-aware value")
        return value.astimezone(datetime.UTC)

    def process_result_value(
        self, value: datetime.datetime | None, dialect: object
    ) -> datetime.datetime | None:
        """Reattach UTC to a value SQLite returned as naive."""
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC)


class Base(DeclarativeBase):
    """Declarative base for every Capsize SQLAlchemy model."""


class TimestampedBase(Base):
    """Abstract base adding the standard ``id`` and UTC timestamps (§6)."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid7
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        UtcDateTime, default=utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        UtcDateTime, default=utcnow, onupdate=utcnow
    )
