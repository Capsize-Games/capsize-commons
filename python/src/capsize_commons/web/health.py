"""Liveness and readiness routes (§14).

Every service in the fleet hand-rolled ``GET /health``. This adds the
``GET /ready`` counterpart §14 also requires, with an optional readiness
predicate so a service can report "up but not able to serve" (for example,
still loading a model or warming a pool) as ``503``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import Enum

from fastapi import APIRouter, FastAPI, HTTPException, status

__all__ = ["health_router", "install_health_routes"]


def health_router(
    *,
    ready_check: Callable[[], bool] | None = None,
    tags: Sequence[str | Enum] | None = None,
) -> APIRouter:
    """Return a router exposing ``/health`` and ``/ready``.

    When ``ready_check`` is given and returns ``False``, ``/ready`` responds
    ``503`` so an orchestrator stops routing traffic to the instance.
    """
    router = APIRouter(tags=None if tags is None else list(tags))

    @router.get("/health")
    def health() -> dict[str, str]:
        """Report liveness (the process is running)."""
        return {"status": "ok"}

    @router.get("/ready")
    def ready() -> dict[str, str]:
        """Report readiness, consulting ``ready_check`` when supplied."""
        if ready_check is not None and not ready_check():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Not ready",
            )
        return {"status": "ready"}

    return router


def install_health_routes(
    app: FastAPI,
    *,
    ready_check: Callable[[], bool] | None = None,
) -> None:
    """Include the health router on ``app`` at the root path."""
    app.include_router(health_router(ready_check=ready_check))
