---
# holon-agentic-coder-ref-metadata-0416
title: "Fix relative quota reset tail scanning, seconds parsing, and watcher keychain lookup"
status: todo
type: bug
priority: high
tags:
  - harness
  - holon-flow
  - run-247
  - credentials
  - reliability
created_at: 2026-11-24T11:05:00Z
updated_at: 2026-11-24T11:05:00Z
---

## Why

The harness flow wrapper and limit watcher parse quota reset messages inconsistently and `watch_limits.py` still reads a
deleted plaintext secret file after Bean 0225 moved the Claude OAuth token to the OS keychain.

## Evidence

Inspected in the self-improvement audit of `2026-11-24T11:05Z`:

1. **Full-output vs tail scan mismatch (`.agents/skills/holon_flow/scripts/run_holon_flow.py`)**:
   `is_quota_error(output)` scans only the last `QUOTA_SCAN_TAIL_LINES = 200` lines (to ignore intent prose, commit
   `90fe069`), whereas `parse_limit_reset(output)` and `parse_relative_limit_reset(output)` (lines 362–400) run
   `re.search` over the **entire** `output` from the start. An earlier reset string in intent prose or a previous
   attempt overrides the latest error at the tail.
2. **Seconds dropped in `limit_reset.py` (`.agents/skills/run_247/scripts/limit_reset.py`, lines 86–98)**: `parse_reset`
   uses `re.search` from the start of the message and its relative regex `in ... h ... m` omits seconds (`s`).
   Antigravity messages like `"Resets in 51m58s"` drop `58s`, and `"Resets in 45s"` returns `None` (misclassified as
   credit exhaustion).
3. **Stale plaintext token path & Claude-only relaunch (`.agents/skills/run_247/scripts/watch_limits.py`, lines 10,
   46, 133)**: `TOKEN_FILE` still reads `~/.holon/secrets/claude-oauth-token` directly (deleted at `2026-11-24T09:56Z`
   when PR #271 / Bean 0225 moved it to the OS keychain; Bean 0406 fixed only `flow_env.py`), and `watch_limits.py`
   still excludes `antigravity-agent` flows from automatic relaunch.

## Proposed change

1. Make `parse_limit_reset` in `run_holon_flow.py` scan only the tail (matching `QUOTA_SCAN_TAIL_LINES`) and take the
   **last** matching reset expression.
2. Add seconds (`s`/`sec`/`seconds`) support and last-match semantics to `limit_reset.py`'s `parse_reset`.
3. Reuse `flow_env.py`'s OS-keychain-aware token resolution in `watch_limits.py`, support `antigravity-agent` relaunch
   alongside `claude-agent`, and add unit tests in `tests/test_flow_fallback.py` and `limit_reset.py --self-test`.

## Expected gain

Prevents early/missed quota wakeups and broken `watch_limits.py` relaunches after the keychain migration.

## Cost

Small harness-only change in `.agents/skills/holon_flow/scripts/run_holon_flow.py`, `.agents/skills/run_247/scripts/`,
and `tests/`.
