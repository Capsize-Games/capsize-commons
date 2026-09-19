# Architecture

## Goal

Reduce total fleet code volume by giving many projects one shared home for the
generic primitives they each re-implemented. This repository is a **library**:
it holds no application logic and knows no domain nouns.

## Repository layout

```
capsize-commons/
├── capsize.json            # the manifest (§1): identity + command map
├── justfile                # the only task interface (§2)
├── AGENTS.md               # the one hand-edited instruction file (§12)
├── CLAUDE.md, .roo/, …     # generated shims (never hand-edited)
├── python/                 # distribution: capsize-commons (src layout)
├── typescript/             # package: @capsize/commons (subpath exports)
├── cpp/                    # library: capsize::commons (header-first)
├── docs/                   # this guide + ADRs
└── scripts/sync-rules.sh   # regenerates the shims, drift-checked in CI
```

Each language directory owns its native manifest (`pyproject.toml`,
`package.json`, `CMakeLists.txt`); the root `capsize.json` classifies all three.
See [ADR 0001](adr/0001-polyglot-commons-layout.md) for why the repository is
polyglot and why this deviates from the root-level `src/<package>/` layout.

## The selective-install mechanism

"Selectively installable" means a project pays only for the slices it uses, and
that is implemented differently in each ecosystem:

| Language | Mechanism |
|---|---|
| Python | **Optional extras.** The base wheel has zero dependencies; each sub-package imports its third-party package lazily and is enabled by an extra (`config`, `db`, `web`, `http`, `all`). |
| TypeScript | **Subpath exports + tree-shaking.** `exports` maps one subpath per module; `sideEffects: false` lets a bundler drop what is not imported. |
| C++ | **Header-first + one compiled unit.** Everything but the logging sink is header-only; `capsize::commons` links only what is referenced, and `find_package`/`FetchContent` both work. |

A consequence of the Python approach: importing `capsize_commons.text` must
never import FastAPI or SQLAlchemy. That is why `capsize_commons/__init__.py`
exports nothing but `__version__`, and why every sub-package `__init__.py`
imports only its own dependency.

## Module map and cross-language parity

| Concern | Python | TypeScript | C++ |
|---|---|---|---|
| Structured logging (§14) | `logging` | `logging` | `logging.h` |
| Env/config (§7) | `config` | `env` | —¹ |
| DB conventions (§6) | `db` | —¹ | —¹ |
| Web auth + health (§13, §14) | `web` | —¹ | —¹ |
| Retry/backoff | `http` | `http`² | —¹ |
| Result / error handling | *(exceptions)*³ | `result` | `expected.h` |
| Case conversion (§3.1) | `text` | `string` | `string_utils.h` |
| Misc utilities | `sentinel` | `object` | `scope_guard.h`, `float_format.h` |

¹ Deliberately absent: these concerns are runtime/framework-specific to one
language (there is no SQLAlchemy in C++, no FastAPI in TypeScript). The rule in
`AGENTS.md` §2.5 is "equivalent **or** a documented reason for absence".

² The TypeScript `http` module provides `fetchJson` only; its backoff
equivalent is not yet written. Tracked as follow-up work.

³ Python uses exceptions for control flow; the `Result` type exists in the
languages where a value-returning error channel is idiomatic.

## Consolidation targets

Each module was chosen from an observed duplication, not invented:

| Module | Duplication it replaces |
|---|---|
| `logging.json_formatter` / `.setup` | `JsonFormatter` + `configure_logging` copied across three `spikeforge` trees and two `airunner` trees; `SPIKEFORGE_LOG_*` env handling re-implemented each time. |
| `web.auth` | `require_api_key` byte-identical in `capsize-social` and `capsize-persona` (and mirrored by `airunner`'s fastsearch extension). |
| `config.base` | `Settings(BaseSettings)` + `@lru_cache get_settings()` duplicated in every FastAPI service. |
| `db.engine` | Per-project `make_engine` / `make_session_factory`, with the SQLite foreign-key pragma usually missing. |
| `db.base.UtcDateTime` | The timezone-aware SQLite `DateTime` decorator written in `capsize-persona`. |
| `db.base.{uuid7,TimestampedBase}` | §6's `id` + `created_at` + `updated_at` conventions, hand-written per model. |
| `web.health` | Hand-rolled `GET /health`, with no `/ready`. |
| `text.case` / `string.case` | A different `slugify` in every project. |
| `cpp/*` | Generic helpers from `curlee/include/curlee/base` and similar. |

## Design rules (enforced in review and by `just ci`)

1. No domain nouns; no application logic.
2. No import-time side effects; no global state except resettable caches.
3. No required Python dependencies; third-party imports are lazy and guarded by
   an extra.
4. Every module independently importable.
5. Explicit public surface (`__all__`, barrels, `namespace capsize::commons`).
6. Typed and documented; Python is `mypy --strict` clean.
7. Tests in the same change; 80% coverage (a `library`, §9).

## Deviations from CAPSIZE 1.x

- **Polyglot layout** (language directories instead of a root `src/<package>/`):
  permitted by §0.4, recorded in [ADR 0001](adr/0001-polyglot-commons-layout.md).
- **C++ target is C++23**, not the §4.3 default of C++20, because
  `expected.h` is built on `std::expected`. Recorded in
  [ADR 0002](adr/0002-cpp23-std-expected.md), with `curlee` as precedent.
- **C++ tests use a header-only harness** rather than Catch2 v3. §4.3 says
  Catch2 is *preferred*; the harness keeps the test target buildable with no
  network fetch. The checks map one-to-one onto Catch2's `REQUIRE`/`CHECK`.
