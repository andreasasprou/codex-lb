# Responses API Compatibility Delta

## Requirement: Safe HTTP bridge hard-pin rebinding

An HTTP bridge MUST mark a request rebind-safe only when all of these conditions hold: the request has no `previous_response_id`, no non-empty `conversation`, no `x-codex-turn-state` header, no input file reference, a self-contained full-resend input, the strict account-neutral replay validator accepts the complete payload, the durable input count and fingerprint are present, the stored input prefix matches that fingerprint, and every call-output item has causal closure.

When the preferred account selection returns no account for a failure other than `account_stream_cap` or `account_response_create_cap`, a rebind-safe bridge session creation MUST perform one unpinned selection. Capacity failures MUST retain the existing wait behavior.

Any rebind-safe bridge that selects an account other than the original preferred account MUST use empty affinity and send no stale session, turn-state, or conversation affinity headers upstream, including switches after refresh or WebSocket-open failures. Its durable canonical session claim MUST rebind the account and clear stale aliases atomically. Account-change claims MUST preserve the durable input count and fingerprint until a later completed response replaces them. A failed replacement write MUST leave the prior durable owner and replay proof fields intact.

#### Scenario: exhausted hard locality pin falls back

- **GIVEN** a hard HTTP bridge pin whose preferred account is unavailable
- **AND** the request satisfies the complete rebind-safe predicate
- **WHEN** the bridge creates a fresh session
- **THEN** it selects another eligible account and sends the request without stale affinity headers
- **AND** the canonical durable row points to the selected account

#### Scenario: unsafe bridge continuation stays pinned

- **GIVEN** a hard HTTP bridge pin
- **AND** the request has a previous response, conversation, turn-state header, file reference, account-scoped input state, missing or mismatched prefix proof, trimmed input, or open causal output
- **WHEN** preferred selection fails
- **THEN** the bridge does not perform the rebind-safe fallback

#### Scenario: local capacity still waits

- **GIVEN** a rebind-safe request whose preferred selection fails with `account_stream_cap` or `account_response_create_cap`
- **WHEN** the bridge handles the failure
- **THEN** it follows the existing capacity wait behavior

#### Scenario: preferred connection failure falls back unanchored

- **GIVEN** a rebind-safe request whose preferred account selection succeeds
- **AND** refresh or WebSocket connection attempts fail on the preferred account
- **WHEN** the bridge selects another account
- **THEN** the fallback selection uses empty affinity
- **AND** the upstream connection sends no stale affinity headers

#### Scenario: post-claim crash retains replay proof

- **GIVEN** a rebind-safe request changes the durable canonical row to another account
- **AND** the process fails after the durable claim commits but before request completion
- **WHEN** the same full resend is evaluated again
- **THEN** the preserved durable input count and fingerprint allow the predicate to verify the stored prefix
