# API governance

`capsize-commons` is the low-level authority for generic primitives. It is a
library, not a product runtime, and it must not acquire domain behavior merely
because a consumer has a similar-looking helper.

## Package boundaries

| Surface | Authority | May depend on | Must not depend on |
| --- | --- | --- | --- |
| Python `config`, `db`, `http`, `logging`, `text`, `web` | `capsize-commons` | stdlib and the named optional extra | product, domain, auth-policy, Django, or UI packages |
| `capsize-auth` | authentication domain package | `capsize-commons` primitives | reverse dependency from commons |
| `capsize-api` | FastAPI service contract | `capsize-commons` and FastAPI | product routes, provider policy, or reverse dependency from commons |
| `capsize-django` / `capsize-site-kit` | Django/site authoring | `capsize-commons` where generic | site content, deployment copies, or reverse dependency from commons |
| `@capsizellc/commons` | generic TypeScript utilities | platform-standard runtime only | UI components or product packages |
| C++ headers/library | generic C++ utilities | standard library | product/game/ML code |

The boundary check in `scripts/check_boundaries.py` runs in `just lint`. It
rejects known product/domain imports from the Python and TypeScript source
trees, and its regression tests demonstrate both the clean repository and a
rejected edge.

## Version authorities

| Artifact | Current version | Runtime floor | Release authority |
| --- | --- | --- | --- |
| `capsize-commons` Python | `0.1.4` candidate | Python `>=3.11` | `python/pyproject.toml`, PyPI package metadata |
| `@capsizellc/commons` | `0.1.4` candidate | Node `>=22` | `typescript/package.json`, npm package metadata |
| C++ library | `0.1.4` candidate | C++23, CMake `>=3.24` | `cpp/CMakeLists.txt` and tagged source release |

Consumers must depend on released versions, not a checkout or copied source.
The Python package uses extras (`config`, `db`, `web`, `http`); TypeScript
consumers use declared subpaths. A consumer may retain local behavior when its
provider, persistence, deployment, or compatibility contract is materially
different, but that exception belongs in its issue evidence.

## Compatibility and deprecation

- Public symbols are the names in Python `__all__`, TypeScript `exports`, and
  the C++ public include tree.
- Additions are minor releases; bug-compatible fixes are patch releases;
  removals or incompatible signatures require a major release.
- Deprecations are documented in the release notes, emit a runtime warning in
  the affected language where practical, and remain available for at least one
  minor release.
- Every public change adds or updates a focused compatibility test. The Python
  public-surface tests cover the current config, database, retry, logging,
  text, and web consumer imports.
- A consumer migration records its before/after status codes, response bodies,
  dependency probes, exception behavior, version used, and rollback path.

## Release path

The executable checklist is `just release-check`, implemented by
`scripts/release_check.py`. It validates both package identities and version
authorities, then runs the boundary check. The full pre-publish commands are
listed in [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

The Python artifact `0.1.2` is published and verified. The `0.1.4` candidate
keeps all three release surfaces in lockstep and is published only by the
tag-driven OIDC workflow described in `RELEASE_CHECKLIST.md`.
