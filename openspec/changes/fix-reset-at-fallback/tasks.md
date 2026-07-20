## 1. Regression feedback loops

- [x] 1.1 Add selector tests for raw-primary reset fallback, persisted-reset precedence, and weekly-only hydration.
- [x] 1.2 Add bounded resetless-probe tests covering the wait interval, failed re-probe delay, and successful durable recovery.
- [x] 1.3 Add fresh-allocation tests covering a below-threshold alternative, all-pressured fallback, unavailable alternatives, and sticky/follow-up isolation.

## 2. Blocked-account recovery

- [x] 2.1 Preserve raw primary usage/reset observations in `AccountState` and hydrate them before usage-window normalization.
- [x] 2.2 Implement persisted-reset precedence and raw-primary reset fallback for both recoverable blocked statuses.
- [x] 2.3 Implement the configurable, single in-flight resetless recovery probe and success/failure settlement paths without a schema change.

## 3. Fresh allocation guard

- [x] 3.1 Add validated environment-backed defaults for the resetless probe interval and fresh-allocation primary-usage threshold.
- [x] 3.2 Add a fresh-allocation candidate guard that excludes at-or-above-threshold accounts only while a below-threshold candidate is selectable.
- [x] 3.3 Thread explicit first-turn allocation intent from proxy request staging and keep preferred, sticky, follow-up, and reattach calls unchanged.

## 4. Verification

- [x] 4.1 Run focused balancer regression tests and confirm the original null-reset reproduction no longer fails.
- [x] 4.2 Run strict OpenSpec validation plus the repository-configured Python lint and test gates without the prohibited typecheck.
- [x] 4.3 Review the final diff for parked-plan exclusion, concurrency safety, and accidental sticky-selection changes.
