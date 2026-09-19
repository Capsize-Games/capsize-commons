// SPDX-License-Identifier: MIT
#include "test_harness.h"

#include <capsize/commons/logging.h>
#include <iostream>
#include <string>
#include <string_view>

void run_logging_tests()
{
    using namespace capsize::commons;

    CHECK_EQ(std::string(level_name(LogLevel::info)), std::string("INFO"));
    CHECK(level_from_name("debug") == LogLevel::debug);
    CHECK(level_from_name("WARNING") == LogLevel::warn);
    CHECK(level_from_name("bogus") == LogLevel::info);

    const LogRecord record{LogLevel::warn, "svc", "hello"};
    const auto json = format_json(record);
    CHECK(json.find("\"level\":\"WARN\"") != std::string::npos);
    CHECK(json.find("\"logger\":\"svc\"") != std::string::npos);
    CHECK(json.find("\"message\":\"hello\"") != std::string::npos);
    CHECK(json.find("\"timestamp\":\"") != std::string::npos);

    const LogRecord quoted{LogLevel::info, "svc", "a\"b\nc"};
    CHECK(format_json(quoted).find("\\\"") != std::string::npos);
    CHECK(format_json(quoted).find("\\n") != std::string::npos);

    CHECK_EQ(format_text(record), std::string("WARN svc hello"));

    std::string captured;
    set_log_sink([&captured](std::string_view line) { captured.assign(line); });
    set_log_level(LogLevel::warn);
    CHECK_EQ(log_level(), LogLevel::warn);

    log(LogLevel::info, "svc", "hidden");
    CHECK(captured.empty());
    log(LogLevel::error, "svc", "shown");
    CHECK(captured.find("shown") != std::string::npos);

    // Restore defaults so later suites see a clean process.
    set_log_level(LogLevel::info);
    set_log_sink([](std::string_view line) { std::cout << line << '\n'; });
}
