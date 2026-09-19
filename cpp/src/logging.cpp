// SPDX-License-Identifier: MIT
#include <capsize/commons/logging.h>
#include <capsize/commons/string_utils.h>
#include <chrono>
#include <cstdio>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>

namespace capsize::commons
{
namespace
{

/// Process-wide state, built on first use so static-initialization order can
/// never leave it half-constructed.
struct State
{
    LogLevel level{LogLevel::info};
    LogSink sink;
};

State& state()
{
    static State instance = []
    {
        State created;
        created.sink = [](std::string_view line) { std::cout << line << '\n'; };
        return created;
    }();
    return instance;
}

std::string timestamp_now()
{
    const auto now = std::chrono::system_clock::now();
    const auto seconds = std::chrono::system_clock::to_time_t(now);
    std::tm broken_down{};
#if defined(_WIN32)
    gmtime_s(&broken_down, &seconds);
#else
    gmtime_r(&seconds, &broken_down);
#endif
    std::ostringstream out;
    out << std::put_time(&broken_down, "%Y-%m-%dT%H:%M:%SZ");
    return out.str();
}

bool needs_unicode_escape(unsigned char c)
{
    return c < 0x20;
}

std::string json_escape(std::string_view text)
{
    std::string out;
    out.reserve(text.size() + 2);
    for (const char raw : text)
    {
        const auto c = static_cast<unsigned char>(raw);
        switch (raw)
        {
        case '"':
            out += "\\\"";
            break;
        case '\\':
            out += "\\\\";
            break;
        case '\n':
            out += "\\n";
            break;
        case '\r':
            out += "\\r";
            break;
        case '\t':
            out += "\\t";
            break;
        default:
            if (needs_unicode_escape(c))
            {
                char buffer[7];
                std::snprintf(buffer, sizeof(buffer), "\\u%04x", c);
                out += buffer;
            }
            else
            {
                out += raw;
            }
            break;
        }
    }
    return out;
}

} // namespace

std::string_view level_name(LogLevel level)
{
    switch (level)
    {
    case LogLevel::trace:
        return "TRACE";
    case LogLevel::debug:
        return "DEBUG";
    case LogLevel::info:
        return "INFO";
    case LogLevel::warn:
        return "WARN";
    case LogLevel::error:
        return "ERROR";
    case LogLevel::off:
        break;
    }
    return "OFF";
}

LogLevel level_from_name(std::string_view name)
{
    const auto lowered = to_lower(name);
    if (lowered == "trace")
    {
        return LogLevel::trace;
    }
    if (lowered == "debug")
    {
        return LogLevel::debug;
    }
    if (lowered == "warn" || lowered == "warning")
    {
        return LogLevel::warn;
    }
    if (lowered == "error")
    {
        return LogLevel::error;
    }
    if (lowered == "off" || lowered == "none")
    {
        return LogLevel::off;
    }
    return LogLevel::info;
}

LogLevel log_level()
{
    return state().level;
}

void set_log_level(LogLevel level)
{
    state().level = level;
}

void set_log_sink(LogSink sink)
{
    state().sink = std::move(sink);
}

std::string format_json(const LogRecord& record)
{
    std::ostringstream out;
    out << "{\"timestamp\":\"" << timestamp_now() << "\",\"level\":\""
        << level_name(record.level) << "\",\"logger\":\""
        << json_escape(record.logger) << "\",\"message\":\""
        << json_escape(record.message) << "\"}";
    return out.str();
}

std::string format_text(const LogRecord& record)
{
    return std::string(level_name(record.level)) + " " + record.logger + " " +
           record.message;
}

void log(LogLevel level, std::string_view logger, std::string_view message)
{
    auto& current = state();
    if (current.level == LogLevel::off || level < current.level)
    {
        return;
    }
    if (!current.sink)
    {
        return;
    }
    const LogRecord record{level, std::string(logger), std::string(message)};
    current.sink(format_json(record));
}

LogSink ostream_sink(std::ostream& stream)
{
    return [&stream](std::string_view line) { stream << line << '\n'; };
}

} // namespace capsize::commons
