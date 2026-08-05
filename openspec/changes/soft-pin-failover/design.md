## Decisions

1. `_http_bridge_request_rebind_safe(payload, headers, request_state, durable_lookup)` returns `False` on any missing or malformed proof. It requires no `previous_response_id`, no `conversation`, no `x-codex-turn-state` header, no input file id, a full-resend shape, input length at least the durable latest count, and shared causal closure.
2. The hard-key and fallback-disabled preferred-account requirement is softened only when `rebind_safe` is true. Previous-response and file-owner requirements remain hard.
3. `_create_http_bridge_session` makes one preferred selection first. If it returns no account for a code other than `account_stream_cap` or `account_response_create_cap`, it makes one unpinned selection with empty affinity only when `rebind_safe` is true.
4. The fallback connection removes all HTTP bridge affinity headers. The durable canonical row remains the session key and is claimed through the existing transaction.
5. Existing WebSocket and non-bridge selection callers retain their current call shape and defaults.
