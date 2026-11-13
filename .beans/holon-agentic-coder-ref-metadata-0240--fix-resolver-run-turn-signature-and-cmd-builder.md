---
# holon-agentic-coder-ref-metadata-0240
title: "Fix resolver run_turn argument signature by building agent CLI command line via runner.build_command"
status: completed
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - resolver
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-06T06:01:17Z
updated_at: 2026-11-06T08:56:00Z
---

## Problem

In `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`, the resolver runner helper
`_run_resolver_agent()` invokes `run_turn()` with an invalid argument signature:

```python
runner = get_runner(agent_name)
outcome = run_turn(runner, prompt, model_name, cwd=repo_dir)
```

This crashes at runtime with:

```
TypeError: run_turn() takes 1 positional argument but 3 positional arguments (and 1 keyword-only argument) were given
```

In `apps/sandbox-executor/src/sandbox_executor/turns.py`:

```python
def run_turn(
    cmd: list[str],
    *,
    turn_budgets: TurnBudgets | None = None,
    ...
    cwd: str | None = None,
    ...
) -> TurnResult:
```

`run_turn()` takes only a single positional argument: the command list `cmd: list[str]`. All other arguments are
keyword-only (`*`).

Because `_run_resolver_agent()` passes `(runner, prompt, model_name)` directly to `run_turn()` instead of constructing
the command line via `runner.build_command(prompt, model_name)`, every Stage 4 resolver pass crashes before spawning the
LLM agent.

Furthermore, in `_run_resolver_mode()`:

```python
lint_ok = True
tests_ok = True
```

Verification defaults are optimistic by default. When the resolver crashes or fails before `_verify_before_push()` can
execute, the JSON outcome payload records `lint_passed: true` and `tests_passed: true` without ever running linters or
tests. This violates the fail-closed zero-trust principle: everything must be assumed broken until proven to be working
by verified execution.

## Goal

1. **Build Runner Command Line**: In `sandbox_executor.entrypoint.review_loop._run_resolver_agent()`, obtain the command
   line list by calling:
   ```python
   runner = get_runner(agent_name)
   cmd = runner.build_command(prompt, model_name)
   outcome = run_turn(cmd, cwd=repo_dir)
   ```
2. **Fail-Closed Verification Defaults**: In `_run_resolver_mode()`, initialize `lint_ok = False` and
   `tests_ok = False`. Never report `lint_passed: true` or `tests_passed: true` unless `_verify_before_push()` actually
   executed `uv run task lint` and `uv run task test` and both returned exit code 0.
3. **Propagate Turn Budgets / Timeouts**: Pass appropriate turn budgets or timeout parameters if configured in the
   environment.
4. **Hermetic Unit Tests**: Add test cases in `apps/sandbox-executor/tests/test_review_loop.py` verifying that:
   - `_run_resolver_agent()` correctly invokes `runner.build_command()` and forwards `cmd` to `run_turn()`.
   - When resolver execution fails or is skipped, `lint_passed` and `tests_passed` fail closed as `False`.

## Resolution

Delivered via [PR #131](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/131) and merged into `main`
(`3c752e6`):

- In `sandbox_executor.entrypoint.review_loop._run_resolver_agent()`, constructed the runner command list via
  `runner.build_command(prompt, model_name)` and invoked `run_turn(cmd, cwd=repo_dir)` with the single required
  positional argument.
- In `_run_resolver_mode()`, flipped optimistic defaults to fail-closed (`lint_ok = False`, `tests_ok = False`). They
  only evaluate to `True` when `_verify_before_push()` runs both linters and tests and both exit with code 0.
- Added comprehensive hermetic unit tests in `test_review_loop.py` asserting correct command construction, fail-closed
  defaults, and error outcome reporting.
- Traversed all 5 stages of the Holon flow, passed 3/3 ensemble review, calibrated, and merged into `main`.
