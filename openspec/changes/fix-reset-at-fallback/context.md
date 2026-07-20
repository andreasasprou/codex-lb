# Resetless balancer recovery context

## Purpose and scope

This change addresses the 2026-07-20 production incident in which three weekly-exhausted accounts were persisted as `rate_limited` with `reset_at=NULL`. The selector only recovered blocked states when the persisted reset existed and had elapsed, so the affected accounts were excluded indefinitely while healthy capacity sat idle. Roughly 4,300 pinned sessions received 503 responses. The parked `PLAN-exhausted-rebind.md` proposal concerns a different sticky-session rebind policy and is explicitly out of scope.

## Decisions and constraints

The latest primary usage observation is the preferred fallback because two-minute usage probes already persist its `reset_at`, and the selection input loader already queries that row. `_state_from_account()` can normalize a weekly primary row into the long-window fields and clear `primary_reset_at`, so `AccountState.observed_primary_reset_at` preserves the raw reset before normalization. A persisted account reset remains authoritative whenever it exists, preserving current cooldown behavior.

If both reset sources are absent, the selector uses a bounded recovery interval from the persisted or runtime block marker. This prevents permanent exclusion without turning an unknown reset into continuous traffic. The interval and the fresh-session allocation threshold follow the existing `CODEX_LB_` environment-backed settings pattern.

The allocation guard applies only when `LoadBalancer.select_account()` is performing the initial non-sticky selection. Sticky lookups, preferred-account follow-ups, retries that carry affinity, and sticky fallback retain their existing thresholds and ordering.

## Failure modes and recovery

A usage-derived reset in the future keeps the account blocked; once elapsed, normal selector recovery reactivates it. A resetless account without an elapsed block interval remains excluded. If a bounded probe fails with another rate-limit or quota response, the existing failure handlers write a new block marker and begin another interval. If it succeeds, compare-and-swap persistence restores only the still-owned blocked row to `active`; a concurrent terminal status update wins instead.

If every otherwise eligible account is at or above the fresh-allocation threshold, the guard falls back to the full eligible pool so it cannot manufacture a `no_accounts` outage. Unknown usage is not treated as over threshold because no observation proves the account is near exhaustion.

## Concrete example

At 12:00, account A is `rate_limited` with `accounts.reset_at=NULL`, while its latest primary usage row has `reset_at=12:05`. Selection at 12:04 excludes A; selection after 12:05 may recover it. If account B has 92% primary usage and account C has 40%, a new non-sticky session uses C, but a sticky follow-up pinned to B continues to evaluate B under the existing sticky rules.

## Operational notes

No migration or backfill is required. Operators can tune the defaults with environment settings, and rollback is a code rollback because no durable contract changes are introduced.
