# Capsize canonical task interface for the capsize-commons polyglot library.
# Thin wrappers only: no business logic lives here (standards §2.1).
set shell := ["bash", "-euo", "pipefail", "-c"]
set dotenv-load := true

default:
    @just --list

# Install/repair the dev environment and dependencies.
setup:
    cd python && uv sync --all-extras
    cd typescript && pnpm install
    cd cpp && cmake --preset dev

# Produce build artifacts for every language.
build:
    cd python && uv build
    cd typescript && pnpm build
    cd cpp && cmake --build --preset dev

# Run the full test suite for every language.
test:
    cd python && uv run pytest
    cd typescript && pnpm test
    cd cpp && ctest --preset dev

# Static analysis across every language.
lint:
    cd python && uv run ruff check .
    cd typescript && pnpm lint
    cd cpp && find include src tests -name '*.cpp' -o -name '*.h' | xargs -r clang-tidy -p build

# Auto-format sources.
format:
    cd python && uv run ruff format .
    cd typescript && pnpm format
    cd cpp && find include src tests -name '*.cpp' -o -name '*.h' | xargs -r clang-format -i

# Run the type checker(s).
typecheck:
    cd python && uv run mypy src
    cd typescript && pnpm typecheck

# A library has nothing to run; list recipes instead.
run:
    @just --list

clean:
    rm -rf python/dist python/build python/.mypy_cache python/.ruff_cache python/.pytest_cache
    rm -rf typescript/dist typescript/coverage
    rm -rf cpp/build

# Documentation is Markdown under docs/.
docs:
    @echo "See docs/README.md and docs/ARCHITECTURE.md"

ci: lint typecheck test

# Regenerate every derived AI-instruction file from capsize.json (§12.6).
sync-rules:
    bash scripts/sync-rules.sh
