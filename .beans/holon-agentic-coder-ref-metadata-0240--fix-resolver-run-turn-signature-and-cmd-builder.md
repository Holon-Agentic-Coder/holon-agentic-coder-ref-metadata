---
# holon-agentic-coder-ref-metadata-0240
title: "Fix resolver run_turn argument signature by building agent CLI command line via runner.build_command"
status: todo
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - resolver
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-06T06:01:17Z
updated_at: 2026-11-06T06:01:17Z
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

## Goal

1. **Build Runner Command Line**: In `sandbox_executor.entrypoint.review_loop._run_resolver_agent()`, obtain the command
   line list by calling:
   ```python
   runner = get_runner(agent_name)
   cmd = runner.build_command(prompt, model_name)
   outcome = run_turn(cmd, cwd=repo_dir)
   ```
2. **Propagate Turn Budgets / Timeouts**: Pass appropriate turn budgets or timeout parameters if configured in the
   environment.
3. **Hermetic Unit Tests**: Add test cases in `apps/sandbox-executor/tests/test_review_loop.py` verifying that
   `_run_resolver_agent()` correctly invokes `runner.build_command()` and forwards `cmd` to `run_turn()`.
