## Context

The selector currently treats `AccountState.reset_at` as the only recovery deadline for `rate_limited` and `quota_exceeded`. The load balancer already queries the latest primary usage row, but weekly-only primary rows are normalized into the long-window fields and lose their raw primary reset in `AccountState`. A blocked row with no persisted reset therefore remains excluded even when the two-minute usage observations contain the upstream deadline.

Fresh selection already has a 95% budget preference helper, but it is shared with sticky fallback, uses normalized/in-flight-adjusted pressure, and intentionally lets `burn_first` policy win first. Reusing or lowering it would change sticky behavior and would not enforce the requested fresh-allocation guard.

## Goals / Non-Goals

**Goals:**

- Preserve the latest raw primary usage observation in memory and use its reset only when the persisted block reset is absent.
- Bound recovery attempts for rows with no reset evidence, including legacy rows with no block marker.
- Keep at most one resetless recovery probe admitted per interval and restore the durable status only after its outcome is known.
- Protect only first-turn, non-sticky, non-preferred allocations from accounts at or above the configured raw primary usage threshold.
- Keep the defaults operator-configurable through the existing `CODEX_LB_` settings mechanism.

**Non-Goals:**

- Implementing the parked exhausted-session rebind design in `PLAN-exhausted-rebind.md`.
- Changing sticky reallocation thresholds, routing-policy precedence outside fresh allocation, or additional-quota contracts.
- Adding a database column, migration, dashboard setting, or background-recovery policy.

## Decisions

### Preserve raw primary usage separately from normalized routing windows

Add raw observed primary usage and reset fields to `AccountState`, populated before weekly-only and expired-window normalization. Existing `used_percent`, `primary_reset_at`, and secondary fields retain their current sorting and quota meanings. This avoids a new repository query or schema change and prevents the incident fix from changing established window normalization.

The effective blocked reset is `state.reset_at` when present, otherwise the raw observed primary reset. The persisted value remains authoritative even if the usage observation disagrees, preserving existing behavior for all set-reset states.

### Represent resetless admission as an outcome-bound probe

When both reset sources are absent, use `blocked_at + resetless_account_probe_interval_seconds` as the next probe deadline. If a legacy row has no `blocked_at`, the first selection inspection anchors it to the current time and leaves it blocked so normal state persistence creates a durable clock.

At the deadline the selector marks one chosen candidate as a recovery probe and advances its block marker, while persistence keeps the durable account status blocked. The detached account returned to the request path is active so existing proxy/session checks can use it. An in-memory per-account marker prevents concurrent selection from treating usage normalization as recovery. A successful request compare-and-swaps the still-blocked row to active and clears block fields; rate-limit, quota, and generic request failures clear the in-flight marker while retaining or re-establishing the blocked state and interval. Permanent failures clear the marker and retain the existing terminal status transition. This is more explicit than optimistic durable activation, which could admit multiple concurrent requests before the probe result.

### Gate only explicit fresh allocations

Add an explicit fresh-allocation flag to `LoadBalancer.select_account()`. `ProxyService` enables it only for general `first_turn` selection with no sticky key and no preferred account; follow-up, reattach, preferred, and sticky calls leave it false. The Codex-control fallback enables it only when no affinity key exists.

Before routing-policy and budget-safe ranking, try the pool whose raw observed primary usage is unknown or below `fresh_allocation_primary_usage_threshold_pct`. If that pool has no selectable account, retry the full pool. This makes an over-threshold `burn_first` account yield to a usable below-threshold alternative without creating a false `no_accounts` result when every alternative is blocked or over threshold.

### Use environment-backed tunables

Add `resetless_account_probe_interval_seconds` with a 900-second default and `fresh_allocation_primary_usage_threshold_pct` with a 90% default to `Settings`. Pydantic validation requires a positive interval and a threshold from 0 through 100. No dashboard or migration work is needed.

## Risks / Trade-offs

- [A process exits while a recovery probe is in flight] → The durable row remains blocked with the advanced `blocked_at`, so another process waits for the next bounded interval rather than opening the account immediately.
- [A successful probe races with an external status update] → Recovery uses compare-and-swap persistence; a newer durable status wins and invalidates the selection cache.
- [Raw primary usage is missing or stale] → Missing usage does not prove exhaustion and remains eligible; stale reset timestamps are used only for blocked recovery, where an elapsed deadline safely permits a probe rather than continuous admission.
- [All accounts exceed the allocation threshold] → Selection retries the original eligible pool so the guard cannot strand capacity.
- [The new defaults need incident-specific tuning] → Operators can override them with `CODEX_LB_RESETLESS_ACCOUNT_PROBE_INTERVAL_SECONDS` and `CODEX_LB_FRESH_ALLOCATION_PRIMARY_USAGE_THRESHOLD_PCT`.

## Migration Plan

Deploy the code with default environment values; no data migration or backfill is required. Existing resetless rows with `blocked_at` become probe-eligible when their interval has elapsed, while older rows without a marker acquire one on inspection. Roll back by deploying the previous code; the only durable side effect is a normal `blocked_at` update on legacy/resetless accounts.

## Open Questions

None.
