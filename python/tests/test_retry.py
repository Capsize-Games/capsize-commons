"""Tests for capsize_commons.http.retry."""

import random

import pytest

from capsize_commons.http import Backoff, retry_async, retry_sync


def test_delay_curve_without_jitter() -> None:
    backoff = Backoff(base_delay=1.0, factor=2.0, max_delay=3.0, jitter=False)
    rng = random.Random(0)
    assert backoff.delay_for(0, rng) == 1.0
    assert backoff.delay_for(1, rng) == 2.0
    assert backoff.delay_for(2, rng) == 3.0  # capped


def test_delay_with_jitter_stays_within_bounds() -> None:
    backoff = Backoff(base_delay=1.0, factor=2.0, max_delay=10.0, jitter=True)
    rng = random.Random(42)
    for attempt in range(4):
        assert (
            0.0
            <= backoff.delay_for(attempt, rng)
            <= min(1.0 * (2.0**attempt), 10.0)
        )


def test_retry_sync_returns_on_first_success() -> None:
    assert retry_sync(lambda: 7) == 7


def test_retry_sync_recovers_after_failures() -> None:
    calls = {"count": 0}

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("transient")
        return "ok"

    result = retry_sync(
        flaky,
        backoff=Backoff(attempts=5, jitter=False),
        sleep=lambda _delay: None,
    )
    assert result == "ok"
    assert calls["count"] == 3


def test_retry_sync_reraises_after_exhausting_attempts() -> None:
    def always_fails() -> None:
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        retry_sync(
            always_fails,
            backoff=Backoff(attempts=2, jitter=False),
            sleep=lambda _delay: None,
        )


def test_retry_sync_does_not_catch_unlisted_exceptions() -> None:
    def boom() -> None:
        raise KeyError("boom")

    with pytest.raises(KeyError):
        retry_sync(
            boom,
            backoff=Backoff(attempts=3, jitter=False, retry_on=(ValueError,)),
            sleep=lambda _delay: None,
        )


async def test_retry_async_recovers_after_failures() -> None:
    calls = {"count": 0}

    async def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("transient")
        return "ok"

    async def no_sleep(_delay: float) -> None:
        return None

    result = await retry_async(
        flaky,
        backoff=Backoff(attempts=3, jitter=False),
        sleep=no_sleep,
    )
    assert result == "ok"
    assert calls["count"] == 2
