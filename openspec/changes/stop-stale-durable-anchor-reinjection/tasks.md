## 1. Suspect-anchor bookkeeping

- [x] 1.1 Add a bounded, TTL-pruned suspect durable-anchor map on the proxy service.
- [x] 1.2 Record the injected anchor as suspect when the `response.created` progress
  deadline fires for a proxy-injected request.

## 2. Injection guard

- [x] 2.1 Skip durable-anchor injection for full-resend payloads while the anchor is
  suspect, logging `stale_anchor_injection_skipped`.
- [x] 2.2 Keep injection unchanged for valid anchors and for short follow-up
  payloads that cannot carry their own continuity.

## 3. Regression coverage

- [x] 3.1 Progress timeout records the injected anchor and stays retryable.
- [x] 3.2 Client-provided anchors are never recorded suspect.
- [x] 3.3 Full resend skips a suspect anchor; non-suspect anchors still inject.
- [x] 3.4 Suspect map TTL expiry and size bound.
