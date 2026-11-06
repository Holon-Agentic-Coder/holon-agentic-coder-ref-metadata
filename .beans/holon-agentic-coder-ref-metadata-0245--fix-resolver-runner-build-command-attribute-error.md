---
# holon-agentic-coder-ref-metadata-0245
title: "Fix resolver runner build_command AttributeError across agent runner classes"
status: todo
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - resolver
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-06T12:37:00Z
updated_at: 2026-11-06T12:37:00Z
---

## Problem

During the Stage 4 PR Review Loop for PR #133, the resolver was dispatched to remediate a CI check failure across 25
iterations. On every single iteration, the resolver container immediately crashed with:

```text
AttributeError: 'AntigravityAgentRunner' object has no attribute 'build_command'
```

Traceback point: In `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`:

```python
def _run_resolver_agent(
    repo_dir: str,
    agent_name: str,
    model_name: str,
    prompt: str,
    dispositions_path: str,
) -> list[dict[str, Any]]:
    """Run the resolver agent turn and parse its dispositions JSON file."""
    os.makedirs(os.path.dirname(dispositions_path), exist_ok=True)
    runner = get_runner(agent_name)
    cmd = runner.build_command(prompt, model_name)
    outcome = run_turn(cmd, cwd=repo_dir)
```

In [Bean 0240](holon-agentic-coder-ref-metadata-0240--fix-resolver-run-turn-signature-and-cmd-builder.md) /
[PR #131](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/131), `_run_resolver_agent()` was updated to
call `runner.build_command(prompt, model_name)` to supply a command list to `run_turn(cmd)`. However, neither
`AgentRunner`, `StandardAgentRunner`, nor `AntigravityAgentRunner` in
`apps/sandbox-executor/src/sandbox_executor/agent_runner.py` implemented a `build_command` method. Instead,
`AgentRunner` defines:

```python
def compose_cmd(self, model_name: str, full_prompt: str) -> list[str]:
    ...
```

The unit tests in `apps/sandbox-executor/tests/test_review_loop.py` passed because `mock_runner` was a mock object on
which `mock_runner.build_command` was dynamically assigned:

```python
mock_runner.build_command.return_value = ["my-agent", "-p", "prompt", "--model", "test-model"]
```

Because no test invoked `build_command` on a real `AgentRunner` subclass, the missing method escaped detection in CI and
broke real Docker container runs.

## Goal

1. **Implement `build_command` on `AgentRunner`**: In `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`, add
   `build_command(self, prompt: str, model_name: str) -> list[str]` to the base `AgentRunner` class:

   ```python
   def build_command(self, prompt: str, model_name: str) -> list[str]:
       """Assemble the agent argv with prompt and model name."""
       return self.compose_cmd(model_name, prompt)
   ```

   This ensures that all registered runners (`antigravity-agent`, `claude-agent`, `gemini`, `codex`, etc.) immediately
   inherit and support `build_command(prompt, model_name)` without individual subclass duplication.

2. **Validate Contract in `_run_resolver_agent`**: In
   `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`, ensure `_run_resolver_agent()` can build the
   command using `runner.build_command(prompt, model_name)` or fallback cleanly to
   `runner.compose_cmd(model_name, prompt)`.

3. **Hermetic Unit Tests with Real Runner Instances**: In `apps/sandbox-executor/tests/test_agent_runner.py`, add test
   cases iterating across all real registered runners in `runners` dictionary:
   - Assert `runner.build_command("prompt", "model")` is callable and returns a valid argv list matching
     `runner.compose_cmd("model", "prompt")`.
   - Assert `AntigravityAgentRunner` specifically produces the correct argv.
   - In `test_review_loop.py`, verify `_run_resolver_agent` works with real runner instances.

4. **Zero Lint / Hygiene Regressions**: Ensure all target repository tests pass cleanly via `uv run pytest` and
   formatting passes via `uv run ruff check .` and `uv run ruff format --check .`.
