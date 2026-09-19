# Adoption plan — reducing project footprint with `capsize-commons`

**Status:** proposal · **Date:** 2026-09-19 · **Scope:** `~/Projects` and `~/PrivateProjects`

This document is the audit behind the plan. It is deliberately written down so
the reductions are measurable and each step is reversible.

---

## 1. Audit findings

Measured across `~/Projects` + `~/PrivateProjects` (build/cache/venv directories
excluded from file scans, but included in size scans):

### Scale

| Metric | Value |
|---|---|
| Total tree size | **196 GB** (78 GB `~/Projects`, 118 GB `~/PrivateProjects`) |
| Python manifests (`pyproject.toml` / `requirements*.txt`) | **83** |
| … using **FastAPI** | **24** |
| … using **Django** | **14** |
| … using **SQLAlchemy** | **8** |
| Virtualenvs | **33** |
| `node_modules` trees | **28** (4.4 GB total) |
| Vite frontends (`vite.config.*`) | **22** |
| Dockerfiles / compose files | **135** |
| Django `settings*.py` modules (some are pydantic, not Django) | 22 |

Virtualenv sizes range from 6.5 MB to **13 GB**. The large ones are
ML/data projects (`airunnerdesktop` 13 GB, `snn_interpreter` 6.4 GB, `999`
5.8 GB, `joeos_finetune_data` 5.3 GB, `WXRQ…` 2.7 GB) — their bulk is models
and datasets, **not** framework duplication. Django-site venvs are a much
tighter band: `Capsize-Games.github.io` 90 MB → `social-manager/backend`
330 MB.

### The repeated Django signature

Six projects carry a near-identical Django dependency set
(`django-distill==3.2.7`, DRF, `django-ratelimit`, `django-cors-headers`,
`django-cookie-consent`, `django-celery-beat`, `Django>=4.2`):

```
~/Projects/capsize-online/requirements.txt
~/PrivateProjects/joecurlee.com/requirements.txt
~/PrivateProjects/freakcomics/requirements.txt
~/PrivateProjects/homeserver/sites/capsizegames/requirements-docker.txt
~/PrivateProjects/homeserver/sites/freakcomics/requirements-docker.txt
~/PrivateProjects/homeserver/sites/joecurlee/requirements-docker.txt
```

`capsize-online/requirements.txt` says it outright:

> Local authoring + static compilation only. Production serves the compiled
> static output from `build/` and never runs Django.

**Django is a build-time tool for these sites, not a runtime.** That is the
single most important finding: for that family, production has no Django
process at all.

Its app (`capsize-online/pages/`) is a textbook repeated content-site app:
`models.py`, `views.py`, `urls.py`, `sitemaps.py`, `context_processors.py`,
`management/`, `migrations/`.

### Version drift in the same framework

| Package | Versions found |
|---|---|
| Django | 5.1.3, 5.1.4 ×3, 5.1.12, 5.2.10 ×2, 5.2.17, `>=4.2` ×6, `>=5.2.8` |
| djangorestframework | `>=3.15`, 3.16.1, `>=3.16.1` |
| django-csp | 3.8, `>=3.8`, 4.0 |
| django-distill | 3.2.7 ×6, 4.0.4 |
| djangorestframework-simplejwt | 5.5.1, `>=5.5.1` |
| django-storages[s3] | 1.14.6, `>=1.14.4` |

Six different Django pins, two DRF majors, two CSP majors. A security fix
lands six times, or (more likely) five times out of six.

### Other duplication found

- `fastsearch/.worktrees/{w1..w4,fix-api-key-test-layout}` each have their own
  `requirements.txt` and venv.
- `~/PrivateProjects/homeserver/sites/{capsizegames,freakcomics,joecurlee}`
  are deployment copies of the same three sites that exist as their own repos.
- `23andme_pdf_ingest` has **both** `venv` (134 MB) and `.venv` (149 MB).
- 135 Dockerfiles/compose files for ~50 deployables.
- `capsize-platform/packages/capsize_core` already exists as a 16-line
  `Settings` model — a proto-commons that `capsize-commons` now supersedes.

---

## 2. Answering "do we need a new Django installation for every project?"

Mostly **no** — but the fix is not "share one `site-packages`". Three separate
problems get conflated:

**(a) Disk cost of N installs — mostly already a non-problem.**
`uv` hardlinks from a single global cache, so the *marginal* disk cost of the
30th Django venv is small. The 33 venvs are not 33 fresh copies of Django. The
real disk is ML models/data. **Action:** standardise every Python project on
`uv` (standards §4.1 already mandates it) and stop using ad-hoc `venv`+`pip`,
which *does* copy naively.

**(b) N runtime installs — solvable for the static-site family by merging.**
The six `django-distill` sites do not need Django in production at all. They
are content repos compiled to static output. They can share **one authoring
toolchain** (a single `uv tool` / one workspace), which collapses six Django
installs into one build-time install and six runtime installs into zero.

For genuine *runtime* Django apps (`uwuchat/backend`, `llm_service/web`,
`WXRQ…/admin_site`, `fastsearch_web`), one install per deployable is correct
and Django does not offer a supported "one installation, many isolated
projects" model — isolation would be lost. The right lever there is (a) and
(c), not collapsing installs.

**(c) N copies of the same application code — the actual waste.**
Settings modules, security headers, cookie-consent/CSP/ratelimit wiring,
health endpoints, sitemaps, context processors, base templates and static
branding are re-written per site. This *is* shareable, as a Django reusable
app package, and it is where the code-volume reduction comes from.

So: **don't share the framework; share the application layer and the dependency
contract, and merge same-family static sites.**

---

## 3. Where new code should live

`capsize-commons` must stay dependency-free (Python base wheel has zero deps).
Django-specific work therefore goes in a **separate distribution**:

| Repository / package | Contains | Depends on |
|---|---|---|
| `capsize-commons` (exists) | logging, config, db, web, http, text — framework-agnostic | nothing (Python) |
| `capsize-django` (new) | `build_settings()`, health, security/SES wiring, reusable content-site app | Django, DRF, capsize-commons |
| `capsize-site-kit` (new) | the static-site authoring toolchain (distill pipeline, livereload, markdown) | Django (build-time only) |
| `capsize-api` (new) | FastAPI app factory, routers, deps, contract tests | FastAPI, capsize-commons |
| `@capsize/ui` (extend `capsize-web/packages/ui`) | shared React components/tokens | React, Vite |

---

## 4. Phased plan

Each phase is independently valuable and independently reversible. Nothing in
a later phase is required to justify an earlier one.

### Phase 0 — Baseline and freeze (no code moves)
1. Run `capsize migrate` (standards §21) on the 8 live Django sites and the top
   FastAPI services: add `capsize.json`, `justfile`, `AGENTS.md` + shims.
2. Record a footprint baseline: tree sizes, venv sizes, manifest dependency
   versions. Commit it so every later phase is measured, not asserted.
3. Land CI (`capsize-ci` reusable workflows) and get `just ci` green **before**
   changing any code. A migration with no green baseline cannot be verified.
4. Delete pure redundancy first (zero code risk): the duplicate `venv` in
   `23andme_pdf_ingest`, the `fastsearch/.worktrees/*` venvs, and the
   `homeserver/sites/*` deployment copies if they are not independently edited.

### Phase 1 — One dependency contract (kills the drift)
1. Publish a canonical constraints file / `capsize-django` metapackage pinning
   one Django (target 5.2 LTS line), one DRF, one CSP, one distill.
2. Replace per-project ranges with `uv` constraints
   (`[tool.uv] constraint-dependencies`) so resolution is central and upgrades
   happen once.
3. Enforce `uv` everywhere (no hand-made `venv` + `pip`).

**Win:** one security upgrade instead of six; drift becomes a CI failure.

### Phase 2 — Extract the Django application layer
Move the repeated, non-domain code out of each site into `capsize-django`:
- `settings`: a `build_settings()` that produces `INSTALLED_APPS`,
  `MIDDLEWARE`, logging (built on `capsize_commons.logging`), security headers,
  CORS and DB config from environment + a small per-site dataclass.
- `health`: `/health` + `/ready`, mirroring `capsize_commons.web.health`.
- `content_site`: the repeated `pages` app (models, views, sitemaps, context
  processors, management commands) as a reusable app.
- `security`: CSP, cookie consent, rate limiting, OTP wiring.

**Migration technique — extract, delegate, then delete.** For each site:
introduce the shared app, have the site's own module re-export from it, ship,
confirm parity, *then* delete the local copy. Never big-bang rewrite.

### Phase 3 — Collapse the static-site fleet (biggest low-risk win)
Turn the six `django-distill` repos into thin content repos that depend on
`capsize-site-kit`, sharing one authoring toolchain. Production remains static
output, so runtime risk is zero. Optionally merge same-family sites into one
authoring project — this is the honest version of "one Django installation".

### Phase 4 — Mirror for FastAPI and React
- `capsize-api`: app factory, router conventions, `/v1` prefix, auth dependency
  (from `capsize_commons.web.auth`), SQLAlchemy sessions
  (`capsize_commons.db`), contract tests against the OpenAPI spec.
- Standardise the 22 Vite frontends onto the existing `@capsize/ui` package
  plus `@capsize/commons` (`result`, `env`, `http`, `logging`, `string`).

### Phase 5 — Consolidate the deploy surface
Collapse 135 Dockerfiles/compose files toward a few canonical base images
(`python:3.12-slim` + `capsize-api`, `node:22-alpine` + static builder), built
once in CI. Fewer, pinned, scanned images.

---

## 5. How to do this carefully

1. **One project per PR.** Trunk-based, short-lived branch, `just ci` green,
   no behaviour change, coverage not reduced.
2. **Canary first.** Start with `capsize-social` and `capsize-persona` — they
   already contain the exact duplicated `auth.py` and `config.py` that
   `capsize-commons` was built from, so they are the lowest-risk proofs.
3. **Extract-and-delegate, never rewrite.** Re-export, verify parity, delete.
4. **Freeze the ML-heavy projects** (`airunner*`, `snn_interpreter`,
   `joeos_finetune_data`, `999`, `WXRQ…`, `research`, `consciousness`) until
   Phases 1–3 are done. Their footprint is data, and touching them early adds
   risk without reducing duplication.
5. **Test the shared layer, not just the consumers.** `capsize-commons`,
   `capsize-django` and `capsize-site-kit` own the contract tests; consumer
   suites stay as they are.
6. **Version and release SemVer**, tag-driven from CI (§11). A breaking change
   to a public symbol is a major bump.
7. **Measure every phase** against the Phase 0 baseline; if a phase does not
   move the numbers, stop and re-scope.

---

## 6. Suggested order of attack

| # | Target | Why first |
|---|---|---|
| 1 | `capsize-social`, `capsize-persona` | exact copies of shipped commons code; instant proof |
| 2 | `capsize-online` + the 5 sibling distill sites | one shared authoring kit, zero runtime risk |
| 3 | `capsize-auth`→`capsize-commons` interop | already a clean library; align conventions |
| 4 | `uwuchat/backend`, `llm_service/web`, `fastsearch_web`, `WXRQ…/admin_site` | real runtime Django apps → `capsize-django` |
| 5 | The 24 FastAPI manifests | `capsize-api` after the Django pattern is proven |
| 6 | The 22 Vite frontends | `@capsize/ui` + `@capsize/commons` |
| 7 | Deploy surface (135 Docker/compose) | last — only worth it once the code is consolidated |
