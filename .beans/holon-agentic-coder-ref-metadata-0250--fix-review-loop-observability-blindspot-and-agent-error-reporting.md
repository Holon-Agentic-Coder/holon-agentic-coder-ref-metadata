---
# holon-agentic-coder-ref-metadata-0250
title:
  "Fix review loop observability blindspots: surface agent exit code and stderr, and pass file-based prompts for large
  inputs"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - observability
  - error-handling
  - agent-runner
  - holon-agentic-coder
created_at: 2026-11-07T13:05:00Z
updated_at: 2026-11-07T13:05:00Z
---

## Problem

During Stage 4 Review Loop execution in `holon flow` (as observed during Bean 0249), all 3 reviewers in the ensemble
failed within 7 seconds with:

```text
Ensemble : FAILED
  Reviewer 1: antigravity-agent / gemini-3.8-flash-medium: FAILED (the reviewer wrote no report)
  Reviewer 2: antigravity-agent / gemini-3.8-flash-medium: FAILED (the reviewer wrote no report)
  Reviewer 3: antigravity-agent / gemini-3.8-flash-medium: FAILED (the reviewer wrote no report)
```

Investigation revealed two intertwined flaws:

### 1. Complete Diagnostic Blindspot in `review_ensemble.py`

When an agent fails to start (e.g. `OSError 7: Argument list too long`), crashes with a non-zero exit code (e.g. exit
127, signal termination), or outputs fatal errors on `stderr`:

1. `turns.py:run_turn()` catches the failure and records it accurately in `TurnResult`:
   ```python
   TurnResult(
       returncode=127,
       stderr="Failed to start agent: [Errno 7] Argument list too long: 'agy'",
   )
   ```
2. `review_ensemble._turn_failure()` inspects **only** `outcome.breach` (budget breaches); because no timeout occurred,
   it returns `None`.
3. When `_read_report()` returns `None` (because the agent crashed before creating `report.md`),
   `_result_from_outcome()` falls back to a hardcoded string:
   ```python
   if text is None:
       return ReviewerResult.failed(index, agent, model, report_rel, "the reviewer wrote no report")
   ```
4. The actual process exit code and `stderr` diagnostics are **completely swallowed and discarded**. The operator and
   flow engine only see the generic `"the reviewer wrote no report"`, requiring manual container reproduction to uncover
   the real failure.
5. Furthermore, reviewer turns execute silently without logging command lines or agent process exit statuses (unlike
   `planner.py` and `executor.py`, which log command lines and failure details).

### 2. Large Diff Inlining Triggers Linux `MAX_ARG_STRLEN` (128 KB)

1. When a change touches many files (such as Bean 0249 modifying 36 files), the PR diff inlined into the reviewer prompt
   reaches 140+ KB.
2. `review_ensemble._write_turn_inputs()` already writes the complete prompt to `scratch/prompt.md`.
3. However, `AntigravityAgentRunner.build_cmd()` ignores `prompt_file` and appends `full_prompt` directly to the CLI
   `argv`:
   ```bash
   agy --dangerously-skip-permissions --model gemini-3.8-flash-medium --effort medium -p "<145KB prompt>"
   ```
4. On Linux systems (inside Docker containers), the Linux kernel strictly enforces `MAX_ARG_STRLEN = 131,072 bytes` (128
   KB / 32 pages) per individual command-line argument in `execve()`. Any argument exceeding 128 KB immediately fails
   with `[Errno 7] Argument list too long: 'agy'`.
5. `agy` already natively supports file-based prompts via `@<path>` syntax (e.g. `agy -p "@/path/to/prompt.md"`), but
   the runner was not utilising it.

## Goal

Provide full observability into reviewer agent failures so errors are never swallowed, and utilize file-based prompt
passing for `AntigravityAgentRunner` to prevent `MAX_ARG_STRLEN` command-line overflows.

### 1. Surface Agent Return Code and Stderr in `review_ensemble.py`

In `apps/sandbox-executor/src/sandbox_executor/review_ensemble.py`:

- Update `_turn_failure(outcome: AuthoringOutcome) -> str | None`:
  - Inspect `outcome.turns`. If any turn failed to launch or exited non-zero (`turn.returncode != 0`), return a clear,
    redacted failure description (e.g.
    `f"agent process failed with exit code {turn.returncode}: {turn.stderr.strip()}"`).
- In `_result_from_outcome()`:
  - If `text is None` (no report found on disk), check the last turn's `returncode` and `stderr`.
  - If `turn.returncode != 0` or `turn.stderr`:
    ```python
    err_detail = turn.stderr.strip() or f"exit code {turn.returncode}"
    return ReviewerResult.failed(
        index,
        agent,
        model,
        report_rel,
        f"agent failed without writing report ({redact_agent_secrets(err_detail)})",
    )
    ```
- Add logging in `_supervise_reviewer_turn()`:
  - Log agent invocation command (with secrets masked) and log warning on non-zero exit code or captured stderr.

### 2. File-Based Prompt Support in `AntigravityAgentRunner`

In `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`:

- Update `AntigravityAgentRunner.build_cmd()`:
  - When `prompt_file` is provided and exists on disk (or when `len(full_prompt) > 32768`), pass `f"@{prompt_file}"` to
    `compose_cmd()` rather than inlining the entire prompt string directly into `argv`:
    ```python
    if prompt_file and os.path.isfile(prompt_file):
        prompt_arg = f"@{prompt_file}"
    else:
        prompt_arg = full_prompt
    return self.compose_cmd(model_name, prompt_arg)
    ```
  - This reduces the CLI argument from 140+ KB to ~35 bytes, avoiding kernel `MAX_ARG_STRLEN` limits.

### 3. Preflight Safety & Truncation Guard for Review Diff

In `apps/sandbox-executor/src/sandbox_executor/review_ensemble.py`:

- In `build_reviewer_prompt()`, if the diff or combined prompt exceeds a safe threshold (e.g. 500 KB), truncate the
  inlined diff and add an explicit note instructing the agent to run `git diff <base_ref>...<head_sha>` directly in its
  workspace.

### 4. Hermetic Unit Tests

- In `apps/sandbox-executor/tests/test_review_loop.py`:
  - Test that an agent turn with `returncode=127` and `stderr="Failed to start agent: ..."` results in a
    `ReviewerResult` whose `failure_reason` includes the actual exit code and stderr, not
    `"the reviewer wrote no report"`.
  - Test that a non-zero exit code with no report produces a failure reason naming the exit code and stderr.
- In `apps/sandbox-executor/tests/test_agent_runner.py`:
  - Test that `AntigravityAgentRunner.build_cmd()` produces `f"@{prompt_file}"` when `prompt_file` is provided and
    exists.
  - Test that `AntigravityAgentRunner.build_cmd()` falls back to `full_prompt` when `prompt_file` is empty or None.

## Constraints

- Australian English in documentation and code comments.
- Zero synthetic benchmarks.
- No new external dependencies.
- Strict test execution with `uv run pytest`.
- Linting passes cleanly with `uv run task lint`.
