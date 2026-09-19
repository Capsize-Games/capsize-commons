// SPDX-License-Identifier: MIT
#pragma once

#include <iostream>

/**
 * @file test_harness.h
 * @brief A tiny dependency-free assertion harness.
 *
 * Keeps the C++ tests buildable with no network fetch. Swap in Catch2 v3 when
 * the build environment allows it; the checks below map one-to-one.
 */

namespace capsize_test
{

inline int checks = 0;
inline int failures = 0;

inline void check(bool condition, const char* expression, const char* file,
                  int line)
{
    ++checks;
    if (!condition)
    {
        ++failures;
        std::cerr << file << ":" << line << ": CHECK failed: " << expression
                  << '\n';
    }
}

template <typename Actual, typename Expected>
inline void check_equal(const Actual& actual, const Expected& expected,
                        const char* expression, const char* file, int line)
{
    ++checks;
    if (!(actual == expected))
    {
        ++failures;
        std::cerr << file << ":" << line << ": CHECK_EQ failed: " << expression
                  << '\n';
    }
}

} // namespace capsize_test

#define CHECK(condition)                                                       \
    ::capsize_test::check((condition), #condition, __FILE__, __LINE__)

#define CHECK_EQ(actual, expected)                                             \
    ::capsize_test::check_equal((actual), (expected), #actual, __FILE__,       \
                                __LINE__)
