// SPDX-License-Identifier: MIT
#include "test_harness.h"

#include <capsize/commons/string_utils.h>
#include <cstddef>
#include <string>
#include <vector>

void run_string_utils_tests()
{
    using namespace capsize::commons;

    CHECK_EQ(std::string(trim("  hi  ")), std::string("hi"));
    CHECK_EQ(std::string(trim_left("  hi")), std::string("hi"));
    CHECK_EQ(std::string(trim_right("hi  ")), std::string("hi"));
    CHECK_EQ(std::string(trim("   ")), std::string(""));
    CHECK_EQ(std::string(trim("no-trim")), std::string("no-trim"));

    const auto parts = split("a,b,,c", ',');
    CHECK_EQ(parts.size(), std::size_t{4});
    CHECK_EQ(parts[0], std::string("a"));
    CHECK_EQ(parts[2], std::string(""));
    CHECK_EQ(parts[3], std::string("c"));

    const std::vector<std::string> items{"a", "b", "c"};
    CHECK_EQ(join(items, "-"), std::string("a-b-c"));
    CHECK_EQ(join(std::vector<std::string>{}, ","), std::string(""));

    CHECK_EQ(to_lower("HeLLo"), std::string("hello"));
    CHECK_EQ(to_upper("HeLLo"), std::string("HELLO"));

    CHECK_EQ(replace_all("a.b.c", ".", "/"), std::string("a/b/c"));
    CHECK_EQ(replace_all("abc", "", "x"), std::string("abc"));
    CHECK_EQ(replace_all("aaa", "aa", "b"), std::string("ba"));
}
