// SPDX-License-Identifier: MIT
#pragma once

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>

namespace capsize::commons
{

/**
 * @file float_format.h
 * @brief Shortest decimal text for F32/F64 values.
 *
 * Lifted from `curlee` (include/curlee/base/float_format.h) and generalized:
 * both a code emitter and a value-display path need a decimal spelling of a
 * float that parses back to exactly the same value.
 *
 * The emitted text always carries a '.', an exponent, or is the non-finite
 * spelling, so appending the `f` suffix for a `float` literal is always valid
 * C, and a finite value never looks like an integer literal.
 */

/**
 * @brief Shortest decimal text for @p value that round-trips.
 *
 * Tries `%.*g` at increasing precision and returns the first spelling that
 * round-trips through @c strtof (when @p as_float) or @c strtod.
 */
[[nodiscard]] inline std::string float_text(double value, int max_digits,
                                            bool as_float)
{
    auto finish = [](std::string text) -> std::string
    {
        const bool has_point = text.find_first_of(".eE") != std::string::npos;
        const bool is_non_finite =
            text.find_first_of("niNI") != std::string::npos;
        if (!has_point && !is_non_finite)
        {
            text += ".0";
        }
        return text;
    };

    // 512 exceeds the widest %g output (17-digit mantissa, 3-digit exponent,
    // signs) and keeps -Wformat-truncation quiet for a runtime precision.
    if (!std::isfinite(value))
    {
        char buffer[512];
        std::snprintf(buffer, sizeof(buffer), "%g", value);
        return finish(std::string(buffer));
    }

    for (int precision = 1; precision <= max_digits; ++precision)
    {
        char buffer[512];
        std::snprintf(buffer, sizeof(buffer), "%.*g", precision, value);
        const bool round_trips =
            as_float
                ? (std::strtof(buffer, nullptr) == static_cast<float>(value))
                : (std::strtod(buffer, nullptr) == value);
        if (round_trips)
        {
            return finish(std::string(buffer));
        }
    }

    char buffer[512];
    std::snprintf(buffer, sizeof(buffer), "%.*g", max_digits, value);
    return finish(std::string(buffer));
}

/** @brief Shortest round-tripping decimal text for an F64 value. */
[[nodiscard]] inline std::string f64_text(double value)
{
    return float_text(value, 17, false);
}

/** @brief Shortest round-tripping decimal text for an F32 value. */
[[nodiscard]] inline std::string f32_text(double value)
{
    return float_text(value, 9, true);
}

} // namespace capsize::commons
