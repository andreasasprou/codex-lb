## Why

The HTTP Responses session bridge serializes `response.create` through one gate per
warm upstream WebSocket. A half-open socket, an ambiguous pre-`response.created`
replay, or a healthy socket that never acknowledges the submitted request can retain
that gate until follower admission expires. Followers then receive
`http_bridge_response_create_gate` overload even though the account pool has capacity.

Disabling the bridge avoids the gate but also discards warm upstream continuity and
materially reduces prompt-cache reuse. Recovery must retire only the stalled bridge
while keeping the bridge enabled for healthy sessions.

## What Changes

- Enable configurable aiohttp heartbeat detection on every HTTP Responses bridge
  upstream path, including direct and proxy-routed connections, with zero retaining
  the legacy disabled behavior.
- Bound ambiguous pre-`response.created` transport replay to one attempt.
- Record when each `response.create` submission starts and terminate a request that
  receives no `response.created` before a dedicated progress deadline.
- Derive/clamp that progress deadline below response-create admission so holder
  cleanup wins before a follower can emit a gate-overload error.
- Key stale-gate retirement from submission time rather than total request age.

## Non-goals

- Do not disable the HTTP session bridge or change its one-request-at-a-time ordering.
- Do not time out model reasoning after `response.created`.
- Do not change account selection, prompt-cache affinity, or durable-anchor semantics.

## Risks

- A progress deadline that is too short could replay a request whose acknowledgement
  is merely delayed, so explicit account-capacity waits are excluded and the deadline
  remains configurable.
- aiohttp heartbeat behavior must be identical on direct public/manual construction
  paths and proxy-routed connections.
- Cleanup must preserve the existing shielded detach/finalization path so gates,
  account leases, and request logs settle exactly once.
