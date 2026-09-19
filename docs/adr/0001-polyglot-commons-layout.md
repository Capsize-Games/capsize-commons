# ADR 0001 — Polyglot `capsize-commons` layout

- **Status:** Accepted
- **Date:** 2026-09-19
- **Context standards:** CAPSIZE 1.x §3, §3.2, §4, §16, §20

## Context

The fleet duplicates a small set of generic primitives across many projects
(Python, TypeScript and C++). Consolidating them reduces the total code volume
— a stated goal of the normalisation effort — and gives the standards a single
place to evolve (structured logging, auth, health routes, DB conventions).

Capsize standards §3 describes a Python source layout at the repository root
(`src/<package>/`), and §3.2 allows multi-language repositories to split by
runtime, each part carrying its own native manifest under one root
`capsize.json`.

## Decision

`capsize-commons` is a **single polyglot repository** with one top-level
directory per language:

```
python/      -> python/pyproject.toml      (distribution: capsize-commons)
typescript/  -> typescript/package.json    (package: @capsize/commons)
cpp/         -> cpp/CMakeLists.txt         (target: capsize::commons)
```

The root holds exactly one `capsize.json`, one `justfile`, one `AGENTS.md`
with generated shims, and the standard hygiene files. This is a documented
deviation from the root-level `src/<package>/` Python layout, permitted by
§0.4 provided it is recorded here and referenced from the manifest's rule set.

## Consequences

- **Selective installation is natural.** Each language ecosystem installs
  only its own artifact: PyPI extra, npm subpath, or CMake target.
- **The Python `src/` layout is preserved**, just nested under `python/`.
- **One standard applies to all three.** The `justfile` fans `setup`, `build`,
  `test`, `lint`, `format`, `typecheck`, `clean`, `docs` and `ci` out to each
  language so `just ci` remains the single gate.
- **Versioning is per-artifact but released in lockstep** from one tag, so the
  Python, npm and CMake versions stay equal.

## Alternatives considered

1. **Three separate repositories.** Rejected: triples the manifest, CI and
   release surface, and cross-language parity would drift.
2. **Python at the repository root, others nested.** Rejected: it privileges
   one language and makes the other toolchains' manifests look second-class.
3. **Ship only Python now.** Rejected: the duplication exists in all three
   languages and the goal is fleet-wide reduction.
