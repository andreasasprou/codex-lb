## ADDED Requirements

### Requirement: Stale durable anchors do not repeatedly stall fresh bridges
When a proxy-injected durable anchor causes a pre-`response.created` progress
timeout, the proxy MUST NOT inject that anchor into subsequent full-resend requests
while it remains suspect. A full resend MUST proceed with its complete payload as
the source of continuity.

#### Scenario: injected anchor times out and is recorded suspect
- **GIVEN** a request whose `previous_response_id` was injected by the proxy from a
  durable record
- **WHEN** the `response.created` progress deadline expires for that request
- **THEN** the proxy records that response id as a suspect durable anchor
- **AND** the request fails with the existing retryable `stream_incomplete` event

#### Scenario: full resend skips a suspect anchor
- **GIVEN** a durable record whose latest response id is recorded suspect
- **WHEN** a full-resend request would otherwise receive that anchor on a fresh
  bridge
- **THEN** the proxy submits the complete payload without injecting the anchor

#### Scenario: valid anchors keep the prompt-cache path
- **GIVEN** a durable record whose latest response id is not suspect
- **WHEN** a full-resend request arrives on a fresh bridge with a matching stored
  prefix
- **THEN** the proxy injects the anchor and trims the payload exactly as before

#### Scenario: client-provided anchors are not affected
- **GIVEN** a request whose `previous_response_id` was supplied by the client
- **WHEN** the `response.created` progress deadline expires for that request
- **THEN** the proxy does not record that response id as suspect

#### Scenario: suspicion expires
- **GIVEN** a suspect durable anchor older than the suspicion window
- **WHEN** a later full-resend request consults the suspect set
- **THEN** the expired anchor is eligible for injection again
