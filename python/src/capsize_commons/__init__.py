"""Generic, selectively-installable building blocks shared across Capsize.

What this package deliberately does **not** do, because each one is what makes
in-repo copies hard to consolidate:

* **No application logic.** If a helper knows a domain noun, it belongs in the
  project, not here.
* **No required dependencies.** The base install is stdlib-only. Anything that
  needs a third-party package lives in a sub-package behind an extra and
  imports it lazily.
* **No import-time side effects.** Importing a module never reads the
  environment, opens a connection, or configures logging. You call
  :func:`capsize_commons.logging.configure_logging` when you want it.
* **No global mutable state** beyond explicitly cached, resettable settings.

The sub-packages:

``capsize_commons.logging``
    Structured JSON logging with the §14 field set, reversible by design.
``capsize_commons.config``
    A ``pydantic-settings`` base plus a per-class cached accessor.
``capsize_commons.db``
    SQLAlchemy engine/session factories and the §6 model conventions
    (time-ordered UUID keys, UTC timestamps).
``capsize_commons.web``
    FastAPI API-key auth and the ``/health`` + ``/ready`` routes.
``capsize_commons.http``
    Retry with exponential backoff, sync and async.
``capsize_commons.text``
    Case conversion for the fleet's naming rules (§3.1).
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.5"
