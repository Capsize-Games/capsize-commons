# capsize-commons (Python)

The Python distribution of [`capsize-commons`](../README.md). It has **no
required dependencies**; each sub-package is pulled in through an extra and
imports its third-party dependency lazily, so importing one module never drags
in another module's stack.

## Install

```bash
uv add "capsize-commons[logging]"        # anything is optional
uv add "capsize-commons[web,db,config]"  # or pick several
uv add "capsize-commons[all]"            # or everything
```

| Extra | Enables | Third-party |
|---|---|---|
| `config` | `capsize_commons.config` | `pydantic`, `pydantic-settings` |
| `db` | `capsize_commons.db` | `sqlalchemy` |
| `web` | `capsize_commons.web` | `fastapi` |
| `http` | `capsize_commons.http` | none (stdlib only) |
| `all` | every sub-package | above |

`capsize_commons.text` and `capsize_commons.logging` are stdlib-only and ship
with the base install.

## Modules

```python
# Structured JSON logs matching §14
from capsize_commons.logging import configure_logging
configure_logging(json_mode=True, logger_name="myapp")

# Env-backed settings, cached per class
from capsize_commons.config import CapsizeSettings, get_settings
class Settings(CapsizeSettings):
    model_config = CapsizeSettings.model_config | {"env_prefix": "MYAPP_"}
    database_url: str = "sqlite:///./app.db"

# FastAPI auth + health
from capsize_commons.web import make_api_key_dependency, install_health_routes

# SQLAlchemy engine, sessions and the standard model mixin
from capsize_commons.db import make_engine, make_session_factory, TimestampedBase

# HTTP retry with backoff
from capsize_commons.http import Backoff, retry_async

# Naming (§3.1)
from capsize_commons.text import slugify, to_snake_case
```

## Development

```bash
cd python
uv sync --all-extras
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy src
```

Or from the repository root: `just test`, `just lint`, `just typecheck`.
