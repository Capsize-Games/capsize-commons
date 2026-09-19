"""Retry helpers with exponential backoff and jitter.

Stdlib-only. Callers supply the operation as a zero-argument callable and the
sleep function, which is what makes these testable without real delays and
usable from both sync and async code.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

__all__ = ["Backoff", "retry_async", "retry_sync"]

_T = TypeVar("_T")


@dataclass(frozen=True)
class Backoff:
    """Retry tuning: attempt count and the delay curve between attempts."""

    attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 5.0
    factor: float = 2.0
    jitter: bool = True
    retry_on: tuple[type[BaseException], ...] = (Exception,)

    def delay_for(self, attempt: int, rng: random.Random) -> float:
        """Return the delay to wait before retrying zero-based ``attempt``.

        With ``jitter`` enabled the delay is drawn uniformly from
        ``[0, raw]``, which spreads out retries from many clients instead of
        letting them all return at the same instant.
        """
        raw = min(self.base_delay * (self.factor**attempt), self.max_delay)
        if self.jitter:
            return rng.uniform(0.0, raw)
        return raw


def retry_sync(
    func: Callable[[], _T],
    *,
    backoff: Backoff | None = None,
    sleep: Callable[[float], None] = time.sleep,
    rng: random.Random | None = None,
) -> _T:
    """Call ``func`` until it returns, retrying the configured exceptions.

    Re-raises the final exception once attempts are exhausted.
    """
    config = backoff or Backoff()
    generator = rng or random.Random()
    last_error: BaseException | None = None
    for attempt in range(config.attempts):
        try:
            return func()
        except config.retry_on as error:
            last_error = error
            if attempt == config.attempts - 1:
                break
            sleep(config.delay_for(attempt, generator))
    if last_error is None:  # pragma: no cover - only when attempts < 1
        raise ValueError("Backoff.attempts must be at least 1")
    raise last_error


async def retry_async(
    func: Callable[[], Awaitable[_T]],
    *,
    backoff: Backoff | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    rng: random.Random | None = None,
) -> _T:
    """Await ``func`` until it returns, retrying the configured exceptions.

    Re-raises the final exception once attempts are exhausted.
    """
    config = backoff or Backoff()
    generator = rng or random.Random()
    last_error: BaseException | None = None
    for attempt in range(config.attempts):
        try:
            return await func()
        except config.retry_on as error:
            last_error = error
            if attempt == config.attempts - 1:
                break
            await sleep(config.delay_for(attempt, generator))
    if last_error is None:  # pragma: no cover - only when attempts < 1
        raise ValueError("Backoff.attempts must be at least 1")
    raise last_error
