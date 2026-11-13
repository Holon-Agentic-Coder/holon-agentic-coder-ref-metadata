---
# holon-agentic-coder-ref-metadata-0251
title: "Pass prompts to agent runners via files across all agent harnesses"
status: completed
type: feature
priority: high
tags:
  - agent-runner
  - prompts
  - harnesses
  - linux-limits
  - holon-agentic-coder
created_at: 2026-11-07T13:08:00Z
updated_at: 2026-11-08T07:47:00Z
---

## Problem

Currently, `StandardAgentRunner`, `AntigravityAgentRunner`, and all agent runner implementations in
`apps/sandbox-executor/src/sandbox_executor/agent_runner.py` pass the entire prompt string as a single command-line
argument:

```python
def compose_cmd(self, model_name: str, full_prompt: str) -> list[str]:
    cmd = [self.binary_name, *self.prefix, self.model_flag, model_name, *self.suffix]
    self._append_env_mappings(cmd)
    cmd.append(full_prompt)
    return cmd
```

Even though callers across all stages (`planner.py`, `executor.py`, and `review_ensemble.py`) already prepare and write
`prompt_file` (`scratch/prompt.md`) to disk and pass it into:

```python
runner.build_cmd(model_name, prompt_file, intent_file, full_prompt)
```

The runners currently discard `prompt_file` and append the raw `full_prompt` string directly to `argv`.

### The Linux Kernel Limitation

On Linux (including all Docker sandbox containers), `execve` enforces hard kernel limits:

1. **`MAX_ARG_STRLEN`**: Any individual argument in `argv` is limited to 128 KB (`32 * PAGE_SIZE = 131,072 bytes`).
2. **`ARG_MAX`**: Combined limit for all arguments and environment variables (typically 2 MB).

When prompts contain large diffs (e.g. 36 files modified in Bean 0249 resulting in a 140+ KB diff), extensive execution
logs, large plans, or substantial intent files, passing `full_prompt` in `argv` immediately crashes with:

```text
OSError: [Errno 7] Argument list too long
```

This breaks every agent runner when handling non-trivial repository changes.

## Goal

Refactor the agent runner architecture to pass prompts via file references or file input streams across **all**
supported agent runners (`antigravity`, `claude`, `pi`, `gemini`, `opencode`, `codex`), completely eliminating
command-line argument string overflow.

### 1. Runner Prompt Passing Strategies in `agent_runner.py`

Update `AgentRunner` and `StandardAgentRunner` to support file-based prompt mechanisms tailored to each CLI tool's
native capabilities:

1. **Antigravity (`agy`)**:
   - Natively supports `@<path>` syntax in `-p` (e.g. `agy -p "@path/to/prompt.md"`).
   - When `prompt_file` is provided and exists, pass `f"@{prompt_file}"` as the prompt argument.
2. **Claude Code (`claude`)**:
   - Claude CLI supports reading prompts from files or stdin.
   - When `prompt_file` exists, pass the prompt file or configure standard input redirection rather than inlining large
     strings in `argv`.
3. **Pi Agent (`pi`)**:
   - Support file-based prompt invocation or standard input streaming from `prompt_file`.
4. **Gemini / Codex / OpenCode**:
   - Configure prompt argument to reference the file path (or use stdin pipe in `run_turn()`) when supported by each
     binary.
5. **Universal Fallback via Stdin / File Guard**:
   - When a CLI binary does not have a native `@file` or `--file` flag, support piping `prompt_file` contents via
     `stdin` in `turns.py:run_turn()` if `argv` would exceed safe limits (e.g. > 32 KB).

### 2. Update `build_cmd` and `compose_cmd` Contracts

In `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`:

- Update `AgentRunner.build_cmd()` signature and implementations to make `prompt_file` a primary input rather than an
  unused parameter.
- Add helper `resolve_prompt_arg(runner, prompt_file, full_prompt) -> tuple[list[str], str | None]` to determine whether
  the prompt is supplied via CLI argument (e.g. `@file` or short string) or via stdin.
- Ensure that prompt files are always stored in standard, secured scratch directories (`.holon/scratch/` or container
  temp paths) accessible by the sandboxed process.

### 3. Stdin Streaming Support in `turns.py`

In `apps/sandbox-executor/src/sandbox_executor/turns.py`:

- Update `run_turn()` to accept an optional `stdin_file: str | None` or `stdin_bytes: bytes | None`:
  ```python
  def run_turn(
      cmd: list[str],
      *,
      stdin_file: str | None = None,
      ...
  )
  ```
- When `stdin_file` is provided, open and stream `stdin` directly from the file into the subprocess without buffering
  large strings in memory or in CLI `argv`.

### 4. Tests and Verification

- In `apps/sandbox-executor/tests/test_agent_runner.py`:
  - Test all runners (`antigravity`, `claude`, `pi`, `gemini`, `opencode`, `codex`) with prompts exceeding 130 KB to
    verify none trigger `[Errno 7] Argument list too long`.
  - Verify that each runner constructs the correct CLI flags / file arguments when `prompt_file` is provided.
  - Verify graceful fallback to `full_prompt` string when `prompt_file` is omitted or empty and prompt size is safe.
- In `apps/sandbox-executor/tests/test_turns.py`:
  - Test `run_turn()` with `stdin_file` input to confirm subprocess reads the full payload reliably.

## Constraints

- Australian English in documentation and code comments.
- Zero synthetic benchmarks.
- No new external dependencies.
- Strict test execution with `uv run pytest`.
- Linting passes cleanly with `uv run task lint`.

## Resolution

Delivered via PR #138 (`cfe3ddf69f50b6aaa7d937aacf162436e103f02b`) by traversing the full 5-stage Holon flow:

1. **Agent Runner Protocol Refactor (`agent_runner.py`)**:
   - Refactored `AgentRunner` and `StandardAgentRunner` hierarchy across all supported runners (`Claude`, `Pi`,
     `Gemini`, `OpenCode`, `Codex`, and `Antigravity`).
   - Configured `uses_stdin: bool = True` on standard runners to assemble promptless CLI commands when `prompt_file` is
     specified, eliminating prompt strings from `argv`.
   - Configured `uses_stdin: bool = False` on `AntigravityAgentRunner`, passing `@f"@{prompt_file}"` to leverage native
     file prompt input in `agy`.
   - Hardened `_sync_prompt_file()` to require absolute paths (`os.path.isabs(prompt_file)`), preventing test runs from
     writing untracked prompt artifacts to the repository root.
2. **Subprocess Stdin Streaming (`turns.py`)**:
   - Enhanced `run_turn()` with `stdin_file: str | None = None`. Streams prompts directly from disk into subprocess
     `stdin` via file handles, eliminating Linux `MAX_ARG_STRLEN` (128 KB) buffer limits and high memory pressure.
3. **Stage Caller Harmonisation**:
   - Updated `entrypoint/planner.py`, `entrypoint/executor.py`, and `review_ensemble.py` to consistently pass
     `prompt_file` and conditional `stdin_file` to `supervise_authoring_turn()`.
4. **Verification & Tests**:
   - Validated that large prompts (>130 KB) execute cleanly without `[Errno 7] Argument list too long`.
   - Removed stray `prompt.txt` file and verified all 3,047 unit/integration tests and `uv run task lint` pass with 100%
     success.
5. **Flow Provenance**:
   - Intent: `I-1794089603-pass-prompts-to-agent-runners-via-files/_`
   - Plan: `plans/P-1794089619-antigravity-agent-gemini-3.8-flash-medium.md`
   - Execution: `executions/E-1794090082-antigravity-agent-gemini-3.8-flash-medium.md`
   - Review: 3-agent ensemble consensus approved (3/3)
   - Calibration: `plans/P-1794089619-antigravity-agent-gemini-3.8-flash-medium_calibration.md` (Predicted EV: 78.86 |
     Actual EV: 84.78 | $\Delta\text{EV} = +5.92$)
   - Merged by maintainer into `main` (`cfe3ddf`).
