# Responses API Compatibility Delta

## Requirement: Safe HTTP bridge hard-pin rebinding

An HTTP bridge MUST mark a request rebind-safe only when all of these conditions hold: the request has no `previous_response_id`, no non-empty `conversation`, no `x-codex-turn-state` header, no input file reference, a self-contained full-resend input, an input item count at least as large as the durable latest input count, and causal closure for every call-output item.

When the preferred account selection returns no account for a failure other than `account_stream_cap` or `account_response_create_cap`, a rebind-safe bridge session creation MUST perform one unpinned selection. Capacity failures MUST retain the existing wait behavior.

The fallback bridge MUST send no stale session, turn-state, or conversation affinity headers upstream. Its durable canonical session claim MUST rebind the account and clear stale aliases atomically. A failed replacement write MUST leave the prior durable owner and replay proof fields intact.

#### Scenario: exhausted hard locality pin falls back

- **GIVEN** a hard HTTP bridge pin whose preferred account is unavailable
- **AND** the request satisfies the complete rebind-safe predicate
- **WHEN** the bridge creates a fresh session
- **THEN** it selects another eligible account and sends the request without stale affinity headers
- **AND** the canonical durable row points to the selected account

#### Scenario: unsafe bridge continuation stays pinned

- **GIVEN** a hard HTTP bridge pin
- **AND** the request has a previous response, conversation, turn-state header, file reference, trimmed input, or open causal output
- **WHEN** preferred selection fails
- **THEN** the bridge does not perform the rebind-safe fallback

#### Scenario: local capacity still waits

- **GIVEN** a rebind-safe request whose preferred selection fails with `account_stream_cap` or `account_response_create_cap`
- **WHEN** the bridge handles the failure
- **THEN** it follows the existing capacity wait behavior
