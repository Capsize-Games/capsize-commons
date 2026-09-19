"""FastAPI integration helpers: API-key auth (§13) and health routes (§14).

Requires the ``web`` extra (``fastapi``).
"""

from __future__ import annotations

from capsize_commons.web.auth import check_api_key, make_api_key_dependency
from capsize_commons.web.health import health_router, install_health_routes

__all__ = [
    "check_api_key",
    "health_router",
    "install_health_routes",
    "make_api_key_dependency",
]
