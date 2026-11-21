---
# holon-agentic-coder-ref-metadata-0349
title: "Mount writable tmpfs for Antigravity brain/conversations and surface agent output on empty_diff"
status: in-progress
type: bug
priority: high
tags:
  - holon-agentic-coder
  - antigravity
  - sandbox
  - docker
  - observability
created_at: 2026-11-21T11:55:00+11:00
updated_at: 2026-11-21T11:55:00+11:00
---

## Problem

1. **Antigravity background-task reactive wakeup drops when `brain/` and `conversations/` are read-only**:
   `get_agent_session_mounts()` in `apps/sandbox-executor/src/sandbox_executor/cli/__init__.py` mounts
   `/home/holon/.gemini/antigravity-cli:ro` and adds writable `--tmpfs` overlays only for `config`, `log`, and `cache` —
   omitting `brain` and `conversations`. Whenever `agy` backgrounds a shell command exceeding `WaitMsBeforeAsync` (10s)
   and the model ends its turn to wait, `agy`'s `OnTaskCompleted` handler fails to create its namespace directory under
   `/home/holon/.gemini/antigravity-cli/brain/...` (`read-only file system`), dropping the reactive wakeup and causing
   `agy -p` to shut down with exit code `0` and premature `"Waiting for background task..."` output. Empirically
   verified via A/B probe on `holon/agent-antigravity` (`agy 1.5.13`): `:ro` drops the wakeup (`EXIT_A=0` without
   output), while `--tmpfs` on `brain` and `conversations` restores wakeup cleanly (`EXIT_B=0` with `WAKEUP_OK_42`).
2. **Exit-0 `empty_diff` failures discard `agent_output_text`**:
   `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` computes `agent_output_text` on exit `0` but only
   writes `agent_output_bytes` to `holon-knowledge/ledger/executions.jsonl`, never printing a bounded, secret-redacted
   excerpt to stderr on `empty_diff`, leaving operators blind to premature exits.

## Goal & Acceptance Criteria

1. In `apps/sandbox-executor/src/sandbox_executor/cli/__init__.py` (`get_agent_session_mounts()`), add
   `--tmpfs /home/holon/.gemini/antigravity-cli/brain:uid=1000,gid=1000` and
   `--tmpfs /home/holon/.gemini/antigravity-cli/conversations:uid=1000,gid=1000` across all three Antigravity mount
   branches (macOS dedicated session dir, Linux dedicated session dir, and Linux host `~/.gemini/antigravity-cli`
   fallback) via a shared constant/helper, keeping `/home/holon/.gemini/antigravity-cli:ro` read-only.
2. In `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py`, when
   `failure_reason == EMPTY_DIFF_FAILURE_REASON` and `agent_output_text` is non-empty, emit a bounded secret-redacted
   excerpt (tail up to 500 characters of the already-redacted `agent_output_text`, noting `agent_output_bytes`) to
   `sys.stderr` alongside `Error: {summary}`, without writing raw output into `holon-knowledge/ledger/executions.jsonl`.
3. Update/add unit tests in `apps/sandbox-executor/tests/test_cli.py`, `apps/sandbox-executor/tests/test_pi_mounts.py`,
   and `apps/sandbox-executor/tests/test_executor.py`.
4. Do not modify `holon-config/hygiene/module_budgets.json`; `uv run task lint`, `uv run task check`, and targeted
   pytest suites pass cleanly.
