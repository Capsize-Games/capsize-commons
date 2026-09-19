# AGENTS.md — capsize-commons

Canonical, tool-neutral instructions for this repository. This is the **only**
hand-edited instruction file; `CLAUDE.md`, `.roo/`, `.github/copilot-instructions.md`
and `.cursor/` are generated shims (standards §12).

**Manifest:** [`capsize.json`](capsize.json) · **Standards:** CAPSIZE 1.x

---

## 1. What this repo is

A **library** (`type: library`) shipping selectively-installable generic
building blocks in **Python, TypeScript and C++**. It is a consumer of the
Capsize standards, not an authority over them.

Rules composed for this repo (deterministic order, §12.3):
`capsize/base` → `capsize/library` → `capsize/lang/python` →
`capsize/lang/typescript` → `capsize/lang/cpp`.

## 2. Hard rules

1. **No application logic.** Only generic, reusable primitives. If a helper
   knows a domain noun (a "persona", an "account"), it does not belong here.
2. **No global state, no import-time side effects.** Nothing reads the
   environment or touches I/O at import. Configuration is constructor/explicit.
3. **No required dependencies in Python.** New third-party imports must be
   placed behind an optional extra and imported lazily inside their module.
4. **Every module is independently importable.** Importing
   `capsize_commons.text` must not require FastAPI, SQLAlchemy or httpx.
5. **Parity across languages.** A primitive added in one language should have
   an equivalent (or a documented reason for absence) in the others.
6. **Public surface is explicit.** Python `__all__`, TS barrel exports, and
   C++ `namespace capsize::commons` are the API; everything else is private.
7. **Typed and documented.** Python: `mypy --strict`, `from __future__ import
   annotations`, docstrings on every public symbol. TS: `strict`, no `any`.
8. **Backward compatibility.** This is a library: a breaking change to a
   public symbol requires a major version bump (SemVer, §11).

## 3. Layout

```
python/src/capsize_commons/    # Python package (src layout)
typescript/src/                # @capsize/commons sources
cpp/include/capsize/commons/   # public C++ headers
cpp/src/                       # C++ out-of-line implementations
docs/adr/                      # decision records
```

## 4. Task interface

`just` is the only entry point. Canonical recipes: `setup, build, test, lint,
format, typecheck, run, clean, docs, ci` (plus `sync-rules`). A recipe is a
thin wrapper — never put logic in the `justfile`.

- `just ci` must pass before any commit.
- Python: `uv`, `ruff`, `mypy --strict`, `pytest` (80% coverage gate).
- TypeScript: `pnpm`, `prettier`, `eslint`, `tsc --noEmit`, `vitest`.
- C++: CMake presets, **C++23** (not the §4.3 default C++20 — see
  `docs/adr/0002-cpp23-std-expected.md`), `-Wall -Wextra -Wpedantic`,
  `clang-format`, `clang-tidy`, CTest.

## 5. Cross-language conventions

- Naming: repos/files `kebab-case`; Python modules `snake_case`; TS files
  `kebab-case.ts`; C++ files `snake_case.h` / `.cpp` with
  `CAPSIZE_COMMONS_<PATH>_H` guards.
- Config/data keys `snake_case`; timestamps UTC; JSON logs to stdout with
  `timestamp`, `level`, `logger`, `message` (§14).
- Commits: Conventional Commits. No secrets in the repo.

## 6. Working agreement for agents

- Read `capsize.json` first to learn classification, then this file.
- Prefer editing the single shared primitive over copying it into a project.
- When adding a primitive, add its test in the same change.
- Keep derived instruction files in sync: run `just sync-rules`; CI fails on
  any drift.
- Do not reformat vendored or third-party code.
