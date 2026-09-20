"""Liveness and readiness routes (§14).

Every service in the fleet hand-rolled ``GET /health``. This adds the
``GET /ready`` counterpart §14 also requires, with an optional readiness
predicate so a service can report "up but not able to serve" (for example,
still loading a model or warming a pool) as ``503``.

Contract
--------

``GET /health`` — **liveness**: the process is running. It must be cheap and
must not touch a dependency, because a failing liveness probe restarts the
container. Always ``200`` with ``{"status": "ok"}``.

``GET /ready`` — **readiness**: can this instance serve traffic *now*? It
consults the optional ``ready_check`` and returns ``503`` while it is false.
A ``ready_check`` **may only observe** — read a flag, probe a connection,
ask a pool whether it is warm. It must **not** write, mutate state, take an
auth dependency, or perform work that has side effects, because orchestrators
call it frequently and may call it concurrently. No authentication is applied
to either route: they are infrastructure probes, and a probe that needs a
credential is a probe that will fail closed in the wrong direction.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from enum import Enum

from fastapi import APIRouter, FastAPI, HTTPException, status

__all__ = ["health_router", "install_health_routes"]


def health_router(
    *,
    ready_check: Callable[[], bool] | None = None,
    health_body: Mapping[str, object] | None = None,
    ready_body: Mapping[str, object] | None = None,
    tags: Sequence[str | Enum] | None = None,
) -> APIRouter:
    """Return a router exposing ``/health`` and ``/ready``.

    When ``ready_check`` is given and returns ``False``, ``/ready`` responds
    ``503`` so an orchestrator stops routing traffic to the instance. The
    optional body mappings preserve an existing service's response shape
    while moving its route registration into this shared implementation.
    """
    router = APIRouter(tags=None if tags is None else list(tags))

    @router.get("/health")
    def health() -> dict[str, object]:
        """Report liveness (the process is running)."""
        body = {"status": "ok"} if health_body is None else health_body
        return dict(body)

    @router.get("/ready")
    def ready() -> dict[str, object]:
        """Report readiness, consulting ``ready_check`` when supplied."""
        if ready_check is not None and not ready_check():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Not ready",
            )
        body = {"status": "ready"} if ready_body is None else ready_body
        return dict(body)

    return router


def install_health_routes(
    app: FastAPI,
    *,
    ready_check: Callable[[], bool] | None = None,
    health_body: Mapping[str, object] | None = None,
    ready_body: Mapping[str, object] | None = None,
) -> None:
    """Include the health router on ``app`` at the root path."""
    app.include_router(
        health_router(
            ready_check=ready_check,
            health_body=health_body,
            ready_body=ready_body,
        )
    )
