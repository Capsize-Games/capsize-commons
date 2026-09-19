// SPDX-License-Identifier: MIT
#include "test_harness.h"

#include <capsize/commons/scope_guard.h>
#include <utility>

void run_scope_guard_tests()
{
    int runs = 0;
    {
        const auto guard = capsize::commons::on_scope_exit([&runs] { ++runs; });
        CHECK_EQ(runs, 0);
        CHECK(guard.active());
    }
    CHECK_EQ(runs, 1);

    int skipped = 0;
    {
        auto guard = capsize::commons::on_scope_exit([&skipped] { ++skipped; });
        guard.dismiss();
        CHECK(!guard.active());
    }
    CHECK_EQ(skipped, 0);

    int moved = 0;
    {
        auto outer = capsize::commons::on_scope_exit([&moved] { ++moved; });
        {
            auto inner = std::move(outer);
            CHECK_EQ(moved, 0);
            CHECK(inner.active());
        }
        CHECK_EQ(moved, 1);
    }
    CHECK_EQ(moved, 1);
}
