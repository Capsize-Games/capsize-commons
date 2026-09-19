// SPDX-License-Identifier: MIT
#include "test_harness.h"

#include <capsize/commons/expected.h>
#include <string>

namespace
{

using capsize::commons::Result;
using capsize::commons::Status;

Result<int, std::string> parse(bool good)
{
    if (good)
    {
        return 42;
    }
    return capsize::commons::err(std::string("bad"));
}

} // namespace

void run_expected_tests()
{
    const auto good = parse(true);
    CHECK(good.has_value());
    CHECK_EQ(good.value(), 42);

    const auto bad = parse(false);
    CHECK(!bad.has_value());
    CHECK_EQ(bad.error(), std::string("bad"));

    const Status<std::string> status;
    CHECK(status.has_value());
}
