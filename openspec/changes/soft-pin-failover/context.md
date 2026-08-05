The fallback is a locality repair. The request is treated as fresh only when the strict account-neutral replay validator accepts the complete payload and the incoming prefix matches the existing durable count and fingerprint.

The preferred selection remains the first attempt. Local stream and response-create capacity failures retain their wait behavior. Other preferred-selection failures trigger one unpinned bridge-local selection, with no shared selector policy change.

Every rebind-safe path that leaves the preferred account clears selection affinity and does not forward session, turn-state, or conversation affinity headers upstream. The bridge retains the canonical durable key so `claim_session` changes ownership and clears aliases in one transaction. The claim preserves the input count and fingerprint so a crash after commit does not remove the proof needed for another rebind. A failed replacement write must leave the previous durable fields intact after rollback.

The WebSocket validator keeps its existing three tool-call families and behavior. The shared causal helper is generalized for the bridge predicate without storing a new fingerprint or compatibility field.
