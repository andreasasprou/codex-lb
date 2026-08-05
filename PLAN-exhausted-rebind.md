# Plan v5 (PARKED as upstream-PR candidate): soft-pin fallback for rebind-safe bridge requests

> **Status 2026-07-17:** after 3 dialectic rounds (Sol xhigh skeptic + Luna max
> refuter) the design below is sound in direction but still needs: stored
> input-prefix fingerprint proof for full resends (Sol r3 Critical), durable
> claim ordering that preserves proof fields until replacement completes, and
> a bridge-local two-call selection to avoid the single_account bypass.
> Andreas chose the KISS route instead: `lb-auto-unpin.timer` on the prod VM
> (see `codex-lb-infra/lb-auto-unpin.sh`) automates the proven manual unpin.
> This document is the starting point if/when an upstream PR is attempted.

## Problem (incident 2026-07-17)
Bridge sessions durable-pinned (hard session-header key) to an account that hit
100% weekly returned 503 `no_accounts` on every follow-up for days. Manual
durable-row delete proved rebind safe for full-resend clients.

## Design change from v1 (per skeptic round 1)
v1 read account status + reset threshold at the streaming site. Rejected:
status accessor doesn't exist there (S3), 1h threshold can't classify windows
(S4), raw `QUOTA_EXCEEDED`/`ignore_standard_quota` reasoning duplicates and
diverges from the selector (S5). v2 delegates ALL availability judgment to the
existing selector and merely stops *requiring* the pinned account when the
request is provably safe to serve elsewhere.

## Mechanism
1. **`_http_bridge_request_rebind_safe(payload, headers, request_state)`** —
   new pure helper. True iff ALL:
   - `request_state.previous_response_id` is None (body carries no upstream
     continuity ref)
   - `payload.conversation` is None (the other opaque upstream-context field,
     `requests.py:626-627`, `api_key_usage.py:64-65` — Lu-r2-1)
   - NO `x-codex-turn-state` header present at all. No synthesized-format
     allowance: format proves nothing about provenance; clients are told to
     echo returned turn state (`affinity.py:233-246`, ops.md — Lu-r2-3).
   - `extract_input_file_ids(payload.input)` is empty (categorical file
     exclusion — S2/L2)
   - self-contained replay: `_http_bridge_payload_looks_like_full_resend`
     AND `len(payload.input) >= durable_lookup.latest_input_item_count` (full
     history grows, trimmed/current-turn payloads shrink; fail closed when the
     stored count is absent — S-r2-1, defeats the single-large-message case)
     AND causal closure, generalized from the websocket replay-safety check
     (`websocket/helpers.py:443-489`): ≥1 `message` item and ANY input item
     whose type ends with `_call_output` (function/custom/apply_patch/
     computer/…, future-proof — Lu-r3-2) must have a matching earlier call
     item in the input. Extract into a shared helper; the ws validator keeps
     its current 3-family behavior unless separately reviewed.
   Fail-safe: any doubt → False → today's behavior.

   Scope clarification (Lu-r3-1 disposition): rebind_safe is evaluated ONLY
   at bridge-session create (the site where selection runs). Live-session
   reuse never consults it, so in-memory repair state
   (`last_pending_tool_calls`) is never bypassed while it exists; after
   session close that state is already lost on ANY account — production
   measurement (91/91 anchored fresh-bridge reattach failures, 2026-07-16)
   established fresh bridges start clean. Rebinding at create loses nothing
   that closure hasn't already lost.

   Live-proof obligation added: because the turn-state condition is now
   absolute, the canary must confirm real incident-shaped traffic (pi/codex
   full resends) actually carries no turn-state header and rebinds; if it
   does carry one, the patch is inert (safe but useless) and the condition
   needs provenance tracking instead.

2. **Soften the requirement** (`mixin.py:504-507`): `require_preferred_account`
   gains `and not rebind_safe` on the hard-key/fallback-disabled term. The
   `previous_response_id`-based term is untouched (rebind_safe is already false
   there). File-required pins are untouched (rebind_safe false). Compact and
   websocket paths untouched.

3. **Fallback gating by failure class — inverted and bridge-scoped**
   (S-r2-2/3/4): exhaustion produces `error_code=None` at the preferred
   lookup (`load_balancer.py:794`; `no_accounts` is synthesized later), so an
   exhaustion allowlist is impossible there. Instead: WAIT only on the local
   capacity codes (`account_stream_cap`, `account_response_create_cap`,
   `load_balancer.py:449`) which the 429 wait machinery already recognizes;
   fall back on every other failure (exhaustion, cooldown, paused, reauth,
   `quota_exhausted`, `no_plan_support_for_model` — all of which fallback
   should handle anyway).

   Scoping: do NOT change shared `service.py:1845` behavior for all callers.
   Add an optional `preferred_fallback_policy` parameter (default = legacy
   behavior) threaded only from the HTTP-bridge create path when rebind_safe.
   Websocket, retry, prompt-cache, model-transition callers see zero change.

   The selector remains the single authority on why the preferred account is
   unusable — no duplicated availability logic.

4. After fallback selection, fresh bridge goes unanchored for full resends
   (4aad503e, `streaming.py:779-812`); canonical durable row rewritten on
   claim, stale aliases cleared (`durable_bridge_repository.py:217`).

## Accepted residual risks (dispositions)
- S6/S8 (narrowed per round 2): a still-open session on the exhausted account
  can be reused (account-match passes once require is false) and can inject
  `session.last_completed_response_id` into the resend. Consequence bounded:
  that request fails upstream once, the session is penalized/retired, and the
  NEXT request runs selection → fallback → rebind. Accepted as
  one-failed-request-then-heal; regression test pins exactly this sequence.
  S8's no-anchor guarantee claimed only for fresh bridge creation
  (`streaming.py:796`).
- S7 concurrent requests during canonical replacement: fork machinery covers
  the session-header/no-turn-state case (which rebind_safe now guarantees).
  Partial failure (canonical fails, fork succeeds) leaves a stale canonical
  pin; next request re-runs the predicate and falls back again — converges.
  Tests must cover: account choices, both turn-state aliases, routing through
  each alias, and the partial-failure case (S-r2-7).
- S8 stale `durable_lookup` reinjection later in the request: anchor injection
  is skipped for full-resend payloads (which rebind_safe guarantees); covered
  by test, no provenance plumbing.
- Replacement account may be ineligible (scope/model/caps): selection then
  fails exactly as today — strictly no worse (L5).
- Multi-instance owner forwarding: prod is single-instance (L6).

## Proof obligations (tests)
- rebind_safe truth table: each condition alone false → False; all true → True.
- Hard-key + exhausted preferred + rebind_safe payload, no live session →
  fallback selection succeeds (200) and durable row rebinds.
- Same but live stale session → one failed request, then rebind on next (S6).
- Hard-key + trimmed payload (tool-output-only, or turn-state header, or
  file_id, or previous_response_id) → require stays true → today's 503.
- `account_stream_cap` / `account_response_create_cap` on preferred → wait
  plan (not rebind); every other failure code → fallback.
- Non-bridge callers (websocket, retry, compact, model-transition): selection
  behavior byte-identical to today (policy param defaulted).
- Active preferred account → selected as before (no behavior change).
- Concurrent double full-resend on same hard key → both complete, one canonical.

## Rollback
Redeploy previous image; no schema/settings changes.

## Follow-ups (parked)
- Exclude >90%-primary accounts from new-session allocation.
- Honest non-retriable error for truly-pinned (file/prev-id) sessions.
- lb-auto-heal alert on preferred_account_miss bursts.
