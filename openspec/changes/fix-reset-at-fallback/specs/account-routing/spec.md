## ADDED Requirements

### Requirement: Blocked account selection uses observed primary resets as fallback
The account selector MUST preserve existing recovery semantics when a blocked account has a persisted `reset_at`. When a `rate_limited` or `quota_exceeded` account has no persisted reset, the selector MUST use the reset from its latest raw primary usage observation as the effective recovery deadline without changing the normalized usage-window contract.

#### Scenario: Usage-derived reset recovers a resetless blocked account
- **GIVEN** a blocked account whose persisted `reset_at` is absent
- **AND** its latest raw primary usage observation has a reset deadline
- **WHEN** selection runs at or after that observed deadline
- **THEN** the account becomes eligible for recovery

#### Scenario: Future usage-derived reset keeps an account blocked
- **GIVEN** a blocked account whose persisted `reset_at` is absent
- **AND** its latest raw primary usage observation has a reset deadline in the future
- **WHEN** selection runs before that deadline
- **THEN** the account remains excluded

#### Scenario: Persisted reset remains authoritative
- **GIVEN** a blocked account has a persisted `reset_at`
- **AND** a raw primary usage observation has a different reset deadline
- **WHEN** selection evaluates recovery
- **THEN** the selector uses the persisted reset and preserves existing set-reset behavior

### Requirement: Resetless blocked accounts receive bounded recovery probes
When a `rate_limited` or `quota_exceeded` account has neither a persisted reset nor an observed primary reset, the selector MUST permit at most one recovery probe after each configured resetless-probe interval. The durable account MUST remain blocked until the probe succeeds, a recoverable or transient probe failure MUST begin another bounded interval, and a successful probe MUST restore the account to `active` and clear its block markers. Permanent failures MUST preserve the existing terminal status transition semantics.

#### Scenario: Resetless account waits for the configured interval
- **GIVEN** a blocked account has no persisted or observed primary reset
- **AND** its block marker is newer than the configured probe interval
- **WHEN** account selection runs
- **THEN** the account remains excluded

#### Scenario: Legacy resetless account receives a durable probe clock
- **GIVEN** a blocked account has no reset evidence and no block marker
- **WHEN** account selection first inspects it
- **THEN** the selector anchors the bounded probe interval without admitting the account immediately

#### Scenario: Failed resetless probe remains bounded
- **GIVEN** a resetless blocked account is admitted for a recovery probe after the configured interval
- **WHEN** that probe receives a recoverable or transient failure
- **THEN** the account remains blocked
- **AND** another probe is not admitted until a new configured interval elapses

#### Scenario: Successful resetless probe restores the account
- **GIVEN** a resetless blocked account is admitted for a recovery probe
- **WHEN** the upstream attempt succeeds
- **THEN** the account becomes `active`
- **AND** its persisted reset and block markers are cleared

### Requirement: Fresh allocation avoids high primary usage when alternatives exist
For a first-turn allocation with no sticky or preferred account, the balancer MUST exclude accounts whose latest raw primary usage is at or above the configured threshold when at least one below-threshold eligible account is selectable. The default threshold MUST be 90%. If no below-threshold account is selectable, the balancer MUST retain the full eligible pool. Sticky, preferred, follow-up, and reattach selection MUST remain unaffected.

#### Scenario: Fresh allocation skips an over-threshold account
- **GIVEN** one eligible account has raw primary usage at or above the configured threshold
- **AND** another eligible account has raw primary usage below the threshold
- **WHEN** a first-turn non-sticky allocation runs
- **THEN** the below-threshold account is selected from the guarded pool

#### Scenario: Fresh allocation falls back when all accounts are pressured
- **GIVEN** every otherwise eligible account has raw primary usage at or above the configured threshold
- **WHEN** a first-turn non-sticky allocation runs
- **THEN** selection uses the full eligible pool instead of returning `no_accounts`

#### Scenario: Unavailable low-usage account does not strand capacity
- **GIVEN** a below-threshold account is not selectable for an existing eligibility reason
- **AND** an at-or-above-threshold account is otherwise eligible
- **WHEN** a first-turn non-sticky allocation runs
- **THEN** the eligible pressured account remains selectable

#### Scenario: Sticky follow-up keeps its existing account
- **GIVEN** a sticky or follow-up request is pinned to an account above the fresh-allocation threshold
- **WHEN** account selection runs
- **THEN** the fresh-allocation threshold does not change the pinned-account decision
