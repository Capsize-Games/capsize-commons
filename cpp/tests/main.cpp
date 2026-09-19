// SPDX-License-Identifier: MIT
#include "test_harness.h"

#include <iostream>

void run_expected_tests();
void run_scope_guard_tests();
void run_string_utils_tests();
void run_float_format_tests();
void run_logging_tests();

int main()
{
    run_expected_tests();
    run_scope_guard_tests();
    run_string_utils_tests();
    run_float_format_tests();
    run_logging_tests();

    std::cout << capsize_test::checks << " checks, " << capsize_test::failures
              << " failures\n";
    return capsize_test::failures == 0 ? 0 : 1;
}
