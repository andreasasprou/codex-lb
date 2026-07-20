## Why

Persisted `rate_limited` and `quota_exceeded` accounts with `reset_at=NULL` can remain excluded from routing forever even when recent usage observations contain the missing reset deadline. During the 2026-07-20 production incident this stranded healthy capacity and caused thousands of pinned-session 503 responses, so account recovery and fresh-session allocation need bounded, explicit safeguards.

## What Changes

- Recover blocked accounts with no persisted reset deadline using the latest primary usage-window reset already loaded for selection.
- When neither source has a reset deadline, permit a bounded recovery probe at a configurable interval instead of excluding the account indefinitely.
- Preserve the existing persisted-reset recovery behavior when `reset_at` is present.
- Keep fresh, non-sticky session allocation away from accounts above a configurable primary-usage threshold when a below-threshold eligible account is available.
- Leave sticky and follow-up account selection semantics unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-routing`: define resetless blocked-account recovery and fresh-session primary-usage allocation guards.

## Impact

The change affects the pure balancer selector, proxy load-balancer state hydration and fresh-selection path, environment-backed balancer settings, and existing balancer unit tests. It does not change API schemas, database schemas, sticky-session contracts, images, or deployment procedures.
