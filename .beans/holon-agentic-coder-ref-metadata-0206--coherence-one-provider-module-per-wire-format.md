---
# holon-agentic-coder-ref-metadata-0206
title:
  "holon-coherence: one provider module per wire format (Anthropic, OpenAI, Gemini) for cleaning, parsing and cache keys"
status: in-progress
type: task
priority: normal
tags:
  - refactor
  - complexity
  - open-closed
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0204
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. Provider branching is repeated in four modules on `68fdf67`:

| Function                                               | Lines | CC  |
| ------------------------------------------------------ | ----- | --- |
| `parsers/sse.extract_sse_token_counts`                 | 192   | 85  |
| `parsers/sse.extract_sse_content`                      | -     | 44  |
| `translate_gemini_to_openai_request` (`mitm_addon`)    | 153   | 45  |
| `translate_openai_sse_chunk_to_gemini` (`mitm_addon`)  | 111   | 37  |
| `payload_cleaner.JSONContextCleaner._clean_openai`     | -     | 32  |
| `payload_cleaner.JSONContextCleaner._clean_gemini`     | -     | 32  |
| `hybrid_cache.HybridCacheStore._extract_system_prompt` | -     | 31  |
| `hybrid_cache.HybridCacheStore._extract_user_content`  | -     | 30  |
| `parsers/tokens.extract_token_counts`                  | -     | 28  |

Adding or changing a provider edits all of them.

## Scope

1. `providers/{anthropic,openai,gemini}.py`, each implementing a `ProviderFormat` protocol: `clean(payload)`,
   `token_counts(sse_events)`, `content(sse_events)`, `cache_key_parts(payload)`; translation between formats in
   `providers/translation.py`.
2. `JSONContextCleaner`, the SSE/token parsers and `HybridCacheStore` select the provider object once and delegate.
3. Can be delivered as one PR per provider if the diff is large (each is independently mergeable after the protocol
   lands).
4. All functions within the 0186 limits; existing cleaner, SSE and cache tests green.

## Touch set

`payload_cleaner.py`, `parsers/{sse,tokens}.py`, `hybrid_cache.py`, `proxy/translation/` (after 0204), new `providers/`,
mirrored tests.

## Dependencies

Blocked by 0204. Do 0200 (removing holon-agentic-coder's copy) first or alongside, so the duplicate is not refactored
twice.

## Notes

- Run through the Holon flow on holon-coherence.

## Progress (2026-10-31)

- Created dedicated worktree `apps/holon-coherence/pr39-provider-modules` from `origin/main` (`e3dcc1a`).
- Verified baseline unit tests (1,107 passed cleanly via `uv run pytest`).
- Prepared intent file `todo/intent-0206-coherence-one-provider-module-per-wire-format.json`.
- Executed `holon flow`:
  - Stage 1 completed: intent branch `I-1793405506-coherence-one-provider-module-per-wire-format/_` established and
    pushed.
  - Stage 2 completed: planner produced `plans/P-1793405520-antigravity-agent-gemini-3.8-flash-medium.md` (EV 79.52).
  - Stage 3 completed: executor produced `E-1793405842-antigravity-agent-gemini-3.8-flash-medium` changing 23 files
    (+3,263/-1,291 lines), all 1,130 unit tests passing (+23 new tests).
- Opened Pull Request [#39](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/39) on `holon-coherence`.
- Spawned background PR Review Loop Orchestrator subagent (`4aa0f164-aa5a-48b3-aa68-5f3484fc29f1`) for Stage 4 review
  loop and Stage 5 calibration.
