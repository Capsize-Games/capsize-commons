// SPDX-License-Identifier: MIT
#pragma once

#include <concepts>
#include <utility>

namespace capsize::commons
{

/**
 * @file scope_guard.h
 * @brief Run a callable on scope exit, unless dismissed.
 *
 * The RAII counterpart to manual cleanup: acquire a resource and register its
 * release in one statement, so no early return can skip it.
 */

/**
 * @brief Invokes @p Fn on destruction unless dismissed.
 *
 * Move-only: moving transfers ownership of the action to the destination.
 */
template <typename Fn> class ScopeGuard
{
  public:
    static_assert(std::invocable<Fn&>,
                  "ScopeGuard requires a nullary callable");

    explicit ScopeGuard(Fn fn) : fn_(std::move(fn))
    {
    }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;
    ScopeGuard& operator=(ScopeGuard&&) = delete;

    ScopeGuard(ScopeGuard&& other) noexcept
        : fn_(std::move(other.fn_)),
          active_(std::exchange(other.active_, false))
    {
    }

    ~ScopeGuard()
    {
        if (active_)
        {
            fn_();
        }
    }

    /** @brief Cancel the deferred action. */
    void dismiss() noexcept
    {
        active_ = false;
    }

    /** @brief Whether the action will still run. */
    [[nodiscard]] bool active() const noexcept
    {
        return active_;
    }

  private:
    Fn fn_;
    bool active_{true};
};

/**
 * @brief Deduce the callable type and build a @ref ScopeGuard.
 */
template <typename Fn> [[nodiscard]] ScopeGuard<Fn> on_scope_exit(Fn fn)
{
    return ScopeGuard<Fn>(std::move(fn));
}

} // namespace capsize::commons
