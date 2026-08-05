The fallback is a locality repair. The request is treated as fresh only when the existing durable count/fingerprint proof and the account-neutral replay validator prove that it carries no upstream account state.

The preferred selection remains the first attempt. Local stream and response-create capacity failures retain their wait behavior. Other preferred-selection failures trigger one unpinned bridge-local selection, with no shared selector policy change.

The fallback does not forward session, turn-state, or conversation affinity headers upstream. The bridge retains the canonical durable key so `claim_session` changes ownership and clears aliases in one transaction. A failed replacement write must leave the previous durable fields intact after rollback.

The WebSocket validator keeps its existing three tool-call families and behavior. The shared causal helper is generalized for the bridge predicate without storing a new fingerprint or compatibility field.
