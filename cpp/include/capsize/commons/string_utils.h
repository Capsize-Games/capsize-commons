// SPDX-License-Identifier: MIT
#pragma once

#include <algorithm>
#include <cctype>
#include <string>
#include <string_view>
#include <vector>

namespace capsize::commons
{

/**
 * @file string_utils.h
 * @brief Header-only string helpers.
 *
 * Trim, split, join, case-fold and replace — the operations every project
 * re-implemented, header-only so nothing needs to be linked.
 */

namespace detail
{
inline constexpr std::string_view whitespace = " \t\n\r\f\v";
} // namespace detail

/** @brief Drop leading whitespace. */
[[nodiscard]] inline std::string_view trim_left(std::string_view text)
{
    const auto start = text.find_first_not_of(detail::whitespace);
    // Unlike std::string::substr, string_view::substr(pos) throws when
    // pos > size(), and find_first_not_of returns npos for all-whitespace
    // input, so the empty case must be handled explicitly.
    if (start == std::string_view::npos)
    {
        return {};
    }
    return text.substr(start);
}

/** @brief Drop trailing whitespace. */
[[nodiscard]] inline std::string_view trim_right(std::string_view text)
{
    const auto last = text.find_last_not_of(detail::whitespace);
    if (last == std::string_view::npos)
    {
        return {};
    }
    return text.substr(0, last + 1);
}

/** @brief Drop leading and trailing whitespace. */
[[nodiscard]] inline std::string_view trim(std::string_view text)
{
    return trim_right(trim_left(text));
}

/**
 * @brief Split @p text on @p delimiter.
 *
 * Empty fields are preserved, so `split("a,,b", ',')` has three parts.
 */
[[nodiscard]] inline std::vector<std::string> split(std::string_view text,
                                                    char delimiter)
{
    std::vector<std::string> parts;
    std::size_t start = 0;
    while (true)
    {
        const auto end = text.find(delimiter, start);
        if (end == std::string_view::npos)
        {
            parts.emplace_back(text.substr(start));
            break;
        }
        parts.emplace_back(text.substr(start, end - start));
        start = end + 1;
    }
    return parts;
}

/** @brief Join @p parts with @p separator. */
template <typename Range>
[[nodiscard]] inline std::string join(const Range& parts,
                                      std::string_view separator)
{
    std::string out;
    bool first = true;
    for (const auto& part : parts)
    {
        if (!first)
        {
            out.append(separator);
        }
        out.append(std::string_view(part));
        first = false;
    }
    return out;
}

/** @brief ASCII-lowercase a copy of @p text. */
[[nodiscard]] inline std::string to_lower(std::string_view text)
{
    std::string out(text);
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c)
                   { return static_cast<char>(std::tolower(c)); });
    return out;
}

/** @brief ASCII-uppercase a copy of @p text. */
[[nodiscard]] inline std::string to_upper(std::string_view text)
{
    std::string out(text);
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c)
                   { return static_cast<char>(std::toupper(c)); });
    return out;
}

/** @brief Replace every non-overlapping @p from with @p to. */
[[nodiscard]] inline std::string
replace_all(std::string_view text, std::string_view from, std::string_view to)
{
    if (from.empty())
    {
        return std::string(text);
    }
    std::string out;
    std::size_t pos = 0;
    while (true)
    {
        const auto found = text.find(from, pos);
        if (found == std::string_view::npos)
        {
            out.append(text.substr(pos));
            break;
        }
        out.append(text.substr(pos, found - pos));
        out.append(to);
        pos = found + from.size();
    }
    return out;
}

} // namespace capsize::commons
