"""Shared-secret API-key authentication for service-to-service calls (§13).

``capsize-social`` and ``capsize-persona`` carried byte-identical copies of
``require_api_key``. This generalizes that function into a dependency factory
whose expected key is read lazily, so it can pull from settings or a secret
store without this module knowing which.

The security-relevant behaviours are preserved deliberately:

* an **empty** expected key rejects every request (fail closed — a service
  started without configuration must not be wide open);
* comparison uses :func:`secrets.compare_digest`, so a wrong key cannot be
  recovered by timing.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable

from fastapi import Header, HTTPException, status

__all__ = ["check_api_key", "make_api_key_dependency"]


def check_api_key(provided: str, expected: str) -> bool:
    """Return ``True`` when ``provided`` matches a non-empty ``expected``."""
    if not expected:
        return False
    return secrets.compare_digest(provided, expected)


def make_api_key_dependency(
    expected_key: Callable[[], str],
    *,
    header_name: str = "X-API-Key",
) -> Callable[..., None]:
    """Build a FastAPI dependency enforcing the shared API key.

    ``expected_key`` is called per request so the value can come from mutable
    or reloadable configuration. Raises ``401`` on any mismatch.
    """

    def require_api_key(
        x_api_key: str = Header(default="", alias=header_name),
    ) -> None:
        """Reject the request unless the presented key matches."""
        if not check_api_key(x_api_key, expected_key()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

    return require_api_key
