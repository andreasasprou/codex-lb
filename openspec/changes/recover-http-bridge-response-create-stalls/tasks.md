## 1. Liveness and replay bounds

- [x] 1.1 Add a configurable upstream WebSocket heartbeat and apply it to both
  WebSocket construction paths.
- [x] 1.2 Refuse a second ambiguous pre-`response.created` replay.

## 2. Protocol progress

- [x] 2.1 Record monotonic `response.create` submission time on each attempt.
- [x] 2.2 Add an auto/configurable `response.created` deadline that always expires
  before follower admission.
- [x] 2.3 Emit retryable `stream_incomplete`, settle through existing detach cleanup,
  and retire stale sessions using submission age.

## 3. Regression coverage

- [x] 3.1 Prove heartbeat configuration reaches direct public/manual and proxy-routed
  aiohttp WebSocket paths, including disabled compatibility behavior.
- [x] 3.2 Prove ambiguous pre-created replay occurs once and not twice.
- [x] 3.3 Prove a swallowed `response.created` emits a terminal retryable event and
  detaches the request before follower admission even with long or disabled SSE
  keepalives.
- [x] 3.4 Prove account-capacity waits and long reasoning after `response.created` are
  unaffected.

## 4. Validation

- [ ] 4.1 Run strict OpenSpec validation.
- [x] 4.2 Run focused proxy unit tests, ruff, and type checking for touched modules.
