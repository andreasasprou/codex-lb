## ADDED Requirements

### Requirement: Warm Responses bridges recover from transport and protocol stalls
The proxy MUST preserve the HTTP Responses session bridge while bounding failure
modes that retain its response-create gate. A stalled holder MUST settle and release
its gate before a follower reaches response-create admission timeout.

#### Scenario: half-open upstream WebSocket is detected
- **GIVEN** a warm upstream Responses WebSocket becomes half-open
- **WHEN** heartbeat acknowledgement is not received within the configured liveness
  interval
- **THEN** the proxy closes the stale upstream transport
- **AND** existing bridge cleanup settles the pending request and gate
- **AND** a later request can create a fresh bridge

#### Scenario: legacy heartbeat behavior remains configurable
- **GIVEN** upstream WebSocket heartbeat is configured as zero
- **WHEN** the HTTP Responses bridge opens a direct or proxy-routed aiohttp
  upstream WebSocket
- **THEN** aiohttp heartbeat is disabled for compatibility

#### Scenario: ambiguous pre-created replay is bounded
- **GIVEN** an upstream transport closes before `response.created`
- **AND** the request is safe to replay
- **WHEN** bridge recovery runs repeatedly
- **THEN** the proxy submits at most one replay for that request
- **AND** a second ambiguous recovery attempt fails through normal cleanup

#### Scenario: submitted request makes no protocol progress
- **GIVEN** `response.create` was submitted on a healthy upstream WebSocket
- **AND** no `response.created` or explicit account-capacity wait is observed
- **WHEN** the dedicated progress deadline expires
- **THEN** the downstream stream receives retryable `stream_incomplete`
- **AND** the request settles through the existing detach/finalization path
- **AND** the stale bridge is retired before follower admission expires
- **AND** the deadline remains effective when SSE keepalives are long or disabled

#### Scenario: reasoning after response creation is unaffected
- **GIVEN** the upstream emitted `response.created`
- **WHEN** model reasoning continues longer than the pre-create progress deadline
- **THEN** the pre-create deadline MUST NOT terminate the request
- **AND** existing stream idle and total request budgets remain authoritative

#### Scenario: explicit account-capacity wait is unaffected
- **GIVEN** the bridge reports that the request is waiting for account capacity
- **WHEN** the pre-create progress deadline passes
- **THEN** the proxy MUST continue the bounded capacity-wait behavior
- **AND** MUST NOT classify the wait as a stalled `response.create`
