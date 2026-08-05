## Why

An HTTP bridge can keep a hard locality pin to an account that is exhausted while a full, self-contained resend carries no account-owned continuity. Returning `503/no_accounts` for that request strands the bridge until an operator removes the pin.

## What Changes

- Define a fail-closed HTTP-bridge-only `rebind_safe` predicate for full resends with no upstream continuity, file references, or turn-state header.
- Allow one fresh account selection after a non-capacity preferred-account selection failure when the predicate is true.
- Open the fallback bridge without stale downstream affinity headers and let the existing durable claim transaction rebind the canonical row and clear old aliases.
- Keep previous-response, file-owned, WebSocket, retry, compact, prompt-cache, model-transition, and configured single-account behavior unchanged.

## Capabilities

### Modified Capabilities

- `responses-api-compat`: self-contained HTTP bridge full resends may recover from a failed hard locality pin.

## Impact

- Affected code: HTTP bridge request preparation and session creation, shared replay-safety helpers, and durable bridge regression tests.
- No schema, setting, public request field, migration, or new fingerprint storage is added.
