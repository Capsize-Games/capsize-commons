# capsize-commons

**What it is.** A single repository of the small, *generic* building blocks
that Capsize projects keep re-writing: structured logging, API-key auth,
health/readiness routes, database engine + timestamped models, HTTP retry
with backoff, case conversion, and the equivalent primitives in TypeScript
and C++.

**Why it exists.** The fleet currently duplicates this code. Reconnaissance
found, for example:

- `JsonFormatter` + `configure_logging` copied byte-for-byte across three
  `spikeforge` trees and two `airunner` trees.
- `require_api_key` identical in `capsize-social` and `capsize-persona`.
- `Settings` / `@lru_cache get_settings` duplicated across every FastAPI
  service.
- `make_engine` / `make_session_factory` re-derived per project.

Consolidating them here means a fix or a standards change lands once, and each
project installs only the slice it needs.

## Selective installation

Nothing is mandatory. The Python package has **no required dependencies**;
each sub-package is pulled in through an extra. The TypeScript package is
tree-shakeable and exposes one subpath per module. The C++ library is
header-first and links only what you use.

| Need | Python | TypeScript | C++ |
|---|---|---|---|
| Structured JSON logging | `capsize-commons[logging]` | `@capsizellc/commons/logging` | `capsize/commons/logging.h` |
| Env-backed settings | `capsize-commons[config]` | `@capsizellc/commons/env` | — |
| FastAPI auth + health | `capsize-commons[web]` | — | — |
| SQLAlchemy engine/models | `capsize-commons[db]` | — | — |
| HTTP retry/backoff | `capsize-commons[http]` | `@capsizellc/commons/http` | — |
| Case conversion | core | `@capsizellc/commons/string` | `capsize/commons/string_utils.h` |
| Result / error handling | core | `@capsizellc/commons/result` | `capsize/commons/expected.h` |

```bash
# Python — install only what a service uses
uv add "capsize-commons[web,db]"      # or [all]
# TypeScript
pnpm add @capsizellc/commons
# C++ (CMake FetchContent or find_package)
find_package(capsize-commons CONFIG REQUIRED)
target_link_libraries(myapp PRIVATE capsize::commons)
```

## Quickstart

```python
from capsize_commons.logging import configure_logging
from capsize_commons.web import make_api_key_dependency, install_health_routes

configure_logging(json_mode=True)
app = FastAPI()
install_health_routes(app)
app.dependency_overrides = {}
```

```ts
import { createLogger } from "@capsizellc/commons/logging";
import { fetchJson } from "@capsizellc/commons/http";

const log = createLogger({ name: "web", json: true });
log.info("starting");
```

```cpp
#include <capsize/commons/string_utils.h>
auto parts = capsize::commons::split("a,b,c", ',');
```

## Canonical `just` commands

| Recipe | Contract |
|---|---|
| `just setup` | Install uv env, pnpm deps, configure CMake |
| `just build` | Build wheel, TS bundle, C++ library |
| `just test` | pytest + vitest + ctest |
| `just lint` | ruff + eslint + clang-tidy |
| `just format` | ruff format + prettier + clang-format |
| `just typecheck` | mypy + tsc |
| `just clean` | Remove build/caches |
| `just docs` | Point at `docs/` |
| `just ci` | `lint` + `typecheck` + `test` |
| `just sync-rules` | Regenerate derived AI instruction shims |

## Configuration

There is deliberately **no global configuration state**. Each helper takes its
inputs as arguments; environment access is confined to the opt-in `config`
extras. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Testing

```bash
just test          # all languages
cd python && uv run pytest
cd typescript && pnpm test
cd cpp && ctest --preset dev
```

Coverage target: **80%** (this repo is a `library`, standards §9).

## Layout

```
python/      # the capsize-commons Python distribution (src layout)
typescript/  # the @capsizellc/commons pnpm package
cpp/         # the capsize::commons CMake library
docs/        # guides + ADRs
scripts/     # helper scripts (rules sync)
```

## License

MIT — see [`LICENSE`](LICENSE).
