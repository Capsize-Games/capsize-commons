# capsize::commons (C / C++)

The C++23 implementation of [`capsize-commons`](../README.md). It is
header-first: every utility other than the logging sink is header-only, so a
consumer pays for only what it includes.

## Requirements

- CMake **>= 3.24** with a preset (`CMakePresets.json` committed).
- A **C++23** compiler (GCC 13+, Clang 17+, MSVC 19.36+). The library pins
  C++23 rather than the standards-default C++20 because
  `capsize/commons/expected.h` is built on `std::expected` — the same choice
  `curlee` already makes. See
  [ADR 0002](../docs/adr/0002-cpp23-std-expected.md).

## Use

```cmake
find_package(capsize-commons CONFIG REQUIRED)
target_link_libraries(myapp PRIVATE capsize::commons)
```

Or vendored with `FetchContent`:

```cmake
FetchContent_Declare(
  capsize-commons
  GIT_REPOSITORY https://github.com/Capsize-Games/capsize-commons.git
  SOURCE_SUBDIR cpp
)
FetchContent_MakeAvailable(capsize-commons)
target_link_libraries(myapp PRIVATE capsize::commons)
```

## Headers

| Header | Provides |
|---|---|
| `capsize/commons/expected.h` | `Result<T, E>`, `Status<E>`, `err(...)` |
| `capsize/commons/scope_guard.h` | `ScopeGuard`, `on_scope_exit(...)` |
| `capsize/commons/string_utils.h` | `trim`, `split`, `join`, `to_lower`, `replace_all` |
| `capsize/commons/float_format.h` | `f32_text`, `f64_text` (round-tripping) |
| `capsize/commons/logging.h` | `LogLevel`, `LogRecord`, `log`, JSON/text formatters |

```cpp
#include <capsize/commons/scope_guard.h>
#include <capsize/commons/string_utils.h>

auto guard = capsize::commons::on_scope_exit([] { cleanup(); });
const auto parts = capsize::commons::split("a,b,c", ',');
```

## Development

```bash
cd cpp
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
```

Or from the repository root: `just test`, `just lint`, `just format`.

Tests use a tiny header-only harness (`tests/test_harness.h`) and are wired
through CTest, so no network fetch is required to build them.
