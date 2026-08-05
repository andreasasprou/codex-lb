## 1. Replay safety

- [x] 1.1 Add the pure HTTP bridge rebind-safe predicate with fail-closed checks.
- [x] 1.2 Extract shared causal closure and preserve WebSocket validator behavior.
- [x] 1.3 Add the rebind-safe truth table and unsafe-payload tests.

## 2. Bridge selection and durable ownership

- [x] 2.1 Soften only hard-key preferred selection for rebind-safe bridge requests.
- [x] 2.2 Add one bridge-local unpinned fallback selection for non-capacity failures.
- [x] 2.3 Strip stale affinity headers on fallback and verify canonical durable rebind.
- [x] 2.4 Add stale live-session and concurrent double-resend coverage.
- [x] 2.5 Add crash-between-write durable claim coverage.

## 3. Validation

- [x] 3.1 Run focused bridge, replay-safety, durable, balancer, and integration suites.
- [x] 3.2 Validate OpenSpec artifacts with the repository’s available tooling or report unavailable tooling.

## Validation notes

- The `openspec` CLI is unavailable in this environment, so the change artifacts were reviewed directly.
- Balancer integration failures remain outside this change:
  `test_load_balancer_reactivates_after_secondary_reset` and
  `test_legacy_rate_limited_row_recovers_after_floor_elapses`.

## 4. Adversarial review remediation

- [x] 4.1 Require strict account-neutral replay validation and cover account-scoped input types.
- [x] 4.2 Require the stored input-prefix count and fingerprint to match.
- [x] 4.3 Unanchor rebind-safe account switches after refresh or WebSocket-open failures.
- [x] 4.4 Preserve durable replay proof across account-change claims and post-claim failures.
- [x] 4.5 Rerun affected unit, integration, lint, format, and diff checks.
