# ADR 0002 — C++ target level is C++23 (for `std::expected`)

- **Status:** Accepted
- **Date:** 2026-09-19
- **Context standards:** CAPSIZE 1.x §4.3 (language levels), §0.4 (deviations)

## Context

§4.3 sets the fleet's C/C++ levels at **C17** and **C++20**. This library's
`capsize/commons/expected.h` is built on `std::expected`, which is only
available from **C++23**; GCC 14's libstdc++ refuses to expose it under
`-std=c++20` (`'expected' in namespace 'std' does not name a template type`).

Consolidating the fleet's Result type onto `std::expected` is worthwhile
because projects already reach for it: `curlee` sets
`CMAKE_CXX_STANDARD 23` and defines
`template <typename T> using Result = std::expected<T, std::vector<Diagnostic>>`.
Re-implementing `expected` to stay on C++20 would add a few hundred lines of
error-prone code to a repository whose entire purpose is to *remove* code.

## Decision

`capsize::commons` requires **C++23**:

- `target_compile_features(capsize_commons PUBLIC cxx_std_23)`
- `CXX_STANDARD 23`, `CXX_STANDARD_REQUIRED ON`, `CXX_EXTENSIONS OFF`
- `.clang-format` `Standard: c++23`

This is a documented deviation from §4.3, permitted by §0.4.

## Consequences

- Consumers need GCC 13+, Clang 17+ or MSVC 19.36+. The documentation states
  this explicitly so the requirement is not discovered at link time.
- The `PUBLIC` compile feature propagates the standard to consumers, so linking
  `capsize::commons` is sufficient to get the right `-std=` flag.
- Every other header is C++20-compatible and could be consumed from a C++20
  translation unit that does not include `expected.h`.

## Alternatives considered

1. **Stay on C++20 and hand-roll an `expected` replacement.** Rejected: it
   contradicts the repository's purpose and duplicates a standard facility.
2. **Drop `expected.h` from this repository.** Rejected: the Result type is
   exactly the kind of duplicated primitive this repository exists to absorb,
   and curlee already depends on it.
3. **Raise §4.3 fleet-wide to C++23 via its own ADR.** Reasonable, but that is
   a standards-level change and out of scope for this repository; this ADR only
   records the local exception.
