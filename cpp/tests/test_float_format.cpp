// SPDX-License-Identifier: MIT
#include "test_harness.h"

#include <capsize/commons/float_format.h>
#include <cmath>
#include <cstdlib>
#include <string>

void run_float_format_tests()
{
    using namespace capsize::commons;

    CHECK_EQ(f64_text(0.5), std::string("0.5"));
    CHECK_EQ(f32_text(0.5F), std::string("0.5"));

    // An integral value still carries a '.', so it can never be mistaken for
    // an integer literal.
    CHECK_EQ(f64_text(1.0), std::string("1.0"));

    // Non-finite values keep their spelling and gain no ".0".
    CHECK(f64_text(std::nan("")).find("nan") != std::string::npos);
    CHECK(f64_text(INFINITY).find("inf") != std::string::npos);

    // Round-trip: the emitted text parses back to exactly the same value.
    CHECK_EQ(std::strtod(f64_text(0.1).c_str(), nullptr), 0.1);
    CHECK_EQ(std::strtod(f64_text(3.141592653589793).c_str(), nullptr),
             3.141592653589793);
}
