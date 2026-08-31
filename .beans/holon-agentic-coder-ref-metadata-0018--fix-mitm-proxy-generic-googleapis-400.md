---
id: holon-agentic-coder-ref-metadata-0018
title: Fix MITM Proxy 400 Bad Request on Generic googleapis Endpoints
status: done
type: task
created_at: 2026-08-31T20:34:00+10:00
updated_at: 2026-08-31T20:37:00+10:00
---

# Fix MITM Proxy 400 Bad Request on Generic googleapis Endpoints

## Context

Addressed HTTP 400 Bad Request errors encountered when running `mitmproxy` against internal Google APIs (such as
`daily-cloudcode-pa.googleapis.com/v1internal:loadCodeAssist`, `setUserSettings`, `listExperiments`,
`www.googleapis.com/oauth2/v2/userinfo`, and `play.googleapis.com/log`).

Work executed via Holon CLI `./holon intent` on Holon flow intent branch `I-1788172624-fix-mitm-proxy-400/_` inside
worktree `holon-agentic-coder-ref/I-1788172624-fix-mitm-proxy-400`.

## Resolution Summary

1. **Created Holon Flow Intent**:
   - Created intent file `todo/fix-mitm-proxy-400.json`.
   - Executed `./holon intent todo/fix-mitm-proxy-400.json` from `holon-agentic-coder-ref/develop`.
   - Initialized Holon flow intent branch `I-1788172624-fix-mitm-proxy-400/_` and logged intent to
     `holon-knowledge/ledger/intents.jsonl`.
   - Set up worktree `holon-agentic-coder-ref/I-1788172624-fix-mitm-proxy-400`.

2. **Refined Provider Detection (`mitm_addon.py`)**:
   - Updated `MITMProxyInterceptor.detect_provider()` to restrict URL-based Gemini detection to
     `generativelanguage.googleapis.com`, `gemini`, `generatecontent`, or `streamgeneratecontent`.
   - Prevented generic `.googleapis.com` endpoints (e.g. `daily-cloudcode-pa.googleapis.com`, `www.googleapis.com`,
     `play.googleapis.com`) from being misclassified as Gemini LLM endpoints.

3. **Guarded Gemini Context Cleaner (`payload_cleaner.py`)**:
   - Updated `JSONContextCleaner._clean_gemini()` to verify that `contents` exists in the payload before attempting
     cleaning.
   - Prevented non-LLM payloads from being mutated with injected `"contents": []` fields that triggered backend
     `400 Bad Request` schema validation failures.

4. **Testing & Verification**:
   - Added unit test `test_mitm_interceptor_generic_googleapis_unaffected` to
     `apps/sandbox-executor/tests/test_token_reduction.py`.
   - Verified all 59 unit tests pass 100% clean using
     `uv run pytest apps/sandbox-executor/tests/test_token_reduction.py`.
