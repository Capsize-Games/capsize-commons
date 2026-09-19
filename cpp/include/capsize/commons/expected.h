// SPDX-License-Identifier: MIT
#pragma once

#include <expected>
#include <type_traits>
#include <utility>

namespace capsize::commons
{

/**
 * @file expected.h
 * @brief Result aliases over @c std::expected.
 *
 * `curlee` defined `Result<T>` as `expected<T, vector<Diagnostic>>`; other
 * projects reached for `std::optional` plus an out-parameter. This gives the
 * fleet one vocabulary for "value or error" without forcing a specific error
 * type.
 */

/**
 * @brief A @p T on success or an @p E on failure.
 *
 * @tparam T The success value type.
 * @tparam E The failure value type.
 */
template <typename T, typename E> using Result = std::expected<T, E>;

/** @brief A result whose success carries no value. */
template <typename E> using Status = std::expected<void, E>;

/**
 * @brief Box a failure value so it can initialize a @c Result.
 *
 * Deduces the error type, so `return capsize::commons::err(MyError{...});`
 * works against any `Result<T, MyError>` without naming the type twice.
 */
template <typename E>
[[nodiscard]] constexpr std::unexpected<std::decay_t<E>> err(E&& error_value)
{
    return std::unexpected<std::decay_t<E>>(std::forward<E>(error_value));
}

} // namespace capsize::commons
