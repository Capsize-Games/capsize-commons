"""Tests for capsize_commons.db."""

import datetime
import uuid

import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from capsize_commons.db import (
    Base,
    TimestampedBase,
    UtcDateTime,
    make_engine,
    make_session_factory,
    uuid7,
)


class _Widget(TimestampedBase):
    __tablename__ = "widgets"

    name: Mapped[str] = mapped_column(String(50))


def test_uuid7_version_variant_and_ordering() -> None:
    first = uuid7()
    assert first.version == 7
    assert first.variant == uuid.RFC_4122

    import time

    time.sleep(0.002)
    second = uuid7()
    # Time-ordered: same-millisecond ties aside, later ids sort higher.
    assert second > first


def test_utc_datetime_rejects_naive_values() -> None:
    column = UtcDateTime()
    with pytest.raises(ValueError, match="timezone-aware"):
        column.process_bind_param(datetime.datetime(2026, 1, 1), None)


def test_utc_datetime_reattaches_utc_to_naive_reads() -> None:
    column = UtcDateTime()
    value = datetime.datetime(2026, 1, 1, 12, 0, 0)
    assert column.process_result_value(value, None).tzinfo is datetime.UTC


def test_engine_session_roundtrip_and_defaults() -> None:
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = make_session_factory(engine)()
    try:
        widget = _Widget(name="spin")
        session.add(widget)
        session.commit()
        session.refresh(widget)
        assert isinstance(widget.id, uuid.UUID)
        assert widget.id.version == 7
        assert widget.created_at.tzinfo is not None
        assert widget.updated_at.tzinfo is not None
    finally:
        session.close()


def test_sqlite_foreign_keys_are_enabled() -> None:
    engine = make_engine("sqlite://")
    with engine.connect() as connection:
        enabled = connection.exec_driver_sql("PRAGMA foreign_keys").scalar()
    assert enabled == 1
