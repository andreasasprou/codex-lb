## Why

After a stalled HTTP bridge is retired with `stream_incomplete`, the client resends
its complete context. The fresh bridge injects the durable response anchor recorded
by the previous (dead) upstream connection and trims the full resend down to a few
items behind it. When upstream never acknowledges that anchored `response.create`,
the pre-`response.created` progress deadline fires — but the durable record still
holds the same anchor, so every client retry repeats the identical injection and
stall. Sessions burn their whole client retry budget on one stale anchor.

## What Changes

- Record a durable anchor as suspect when a request that carried a proxy-injected
  anchor hits the `response.created` progress timeout.
- Skip injecting a suspect anchor into a full-resend request; the complete payload
  is its own source of continuity, and a successful turn stores a fresh anchor.
- Keep injecting anchors into short follow-up payloads (they cannot carry their own
  continuity) and rely on the existing progress deadline for those.
- Suspicion is in-memory, time-bounded, and size-bounded; a valid anchor that never
  times out is injected exactly as before.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: Bound stale durable-anchor stalls on fresh HTTP bridges to
  a single progress timeout while retaining anchor-based continuity for valid
  anchors and short follow-ups.

## Impact

- Affected code: HTTP bridge durable-anchor injection and the pre-`response.created`
  progress-timeout path.
- Affected tests: HTTP bridge progress-timeout, durable full-resend anchor
  injection, and suspect-anchor bookkeeping coverage.
- Compatibility: no API or configuration change; unrecoverable attempts retain the
  existing retryable `stream_incomplete` contract.
