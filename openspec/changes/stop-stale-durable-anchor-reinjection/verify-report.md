## Validation

- `pytest tests/unit/test_proxy_http_bridge.py tests/unit/test_proxy_utils.py
  tests/unit/test_durable_bridge_sessions.py`: 986 passed (3 pre-existing unawaited
  `AsyncMock` warnings).
- `ruff check app tests`: pass.
- `ruff format app tests`: no drift beyond this change.
- `ty check` on the three changed application files: pass.
- `git diff --check`: clean.

## Production evidence motivating the change

On 2026-07-16 (image beta.3 + recover-http-bridge-response-create-stalls), the same
session repeated `retire_stale_pending detail=stream_incomplete` →
`durable_full_resend_anchor_injected` → `store_context_input_trimmed` →
`HTTP bridge response.created progress timeout timeout_seconds=45.0` every ~50
seconds; clients exhausted their five-retry budget on a single stale anchor.
