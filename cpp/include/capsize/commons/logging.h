// SPDX-License-Identifier: MIT
#pragma once

#include <functional>
#include <iosfwd>
#include <string>
#include <string_view>

namespace capsize::commons
{

/**
 * @file logging.h
 * @brief Minimal leveled logging with the §14 JSON shape.
 *
 * Deliberately small: a process-wide level and sink, one record type, and both
 * a JSON and a human formatter. Nothing is configured until you call
 * @ref set_log_level or @ref set_log_sink; the default sink writes JSON lines
 * to stdout.
 */

/** @brief Severity, ordered from most to least verbose. */
enum class LogLevel
{
    trace,
    debug,
    info,
    warn,
    error,
    off
};

/** @brief One structured log record. */
struct LogRecord
{
    LogLevel level{LogLevel::info};
    std::string logger;
    std::string message;
};

/** @brief Receives one already-formatted line at a time. */
using LogSink = std::function<void(std::string_view)>;

/** @brief Uppercase name of @p level (e.g. `"INFO"`). */
[[nodiscard]] std::string_view level_name(LogLevel level);

/** @brief Parse a case-insensitive level name; unknown names map to info. */
[[nodiscard]] LogLevel level_from_name(std::string_view name);

/** @brief The current process-wide minimum level. */
[[nodiscard]] LogLevel log_level();

/** @brief Set the process-wide minimum level. */
void set_log_level(LogLevel level);

/** @brief Replace the process-wide sink. */
void set_log_sink(LogSink sink);

/** @brief Format @p record as one JSON object on a single line. */
[[nodiscard]] std::string format_json(const LogRecord& record);

/** @brief Format @p record as a human-readable line. */
[[nodiscard]] std::string format_text(const LogRecord& record);

/** @brief Emit a record at @p level when it passes the threshold. */
void log(LogLevel level, std::string_view logger, std::string_view message);

/** @brief A sink that appends a newline after writing to @p stream. */
[[nodiscard]] LogSink ostream_sink(std::ostream& stream);

} // namespace capsize::commons
