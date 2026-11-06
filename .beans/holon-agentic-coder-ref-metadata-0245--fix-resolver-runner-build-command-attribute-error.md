---
# holon-agentic-coder-ref-metadata-0245
title: "Fix resolver runner build_command AttributeError across agent runner classes"
status: completed
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - resolver
  - stage-4
  - holon-agentic-coder
  - testing
  - minimise-mocking
created_at: 2026-11-06T12:37:00Z
updated_at: 2026-11-06T23:07:00Z
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

### Root Cause: Over-Mocking Masked Real Contract Violations

The unit tests in `apps/sandbox-executor/tests/test_review_loop.py` passed because `mock_runner` was a free-form
`MagicMock` on which `mock_runner.build_command` was dynamically assigned:

```python
mock_runner.build_command.return_value = ["my-agent", "-p", "prompt", "--model", "test-model"]
```

**Mocking hides calls to real implementations.** Because the test mocked the runner object completely without
specification, it validated an invented fantasy contract rather than the actual `AgentRunner` interface. The missing
method was completely invisible in CI and only broke once running against real code in the Docker container.

## Architectural Rule: Minimise Mocking

Unit and integration tests must strictly **minimise the use of mocks**:

1. **Never mock data structures or internal collaborators that can be instantiated cheaply.** Use real `AgentRunner`,
   `StandardAgentRunner`, and `AntigravityAgentRunner` instances.
2. **Never use free-form `MagicMock()` on classes.** When process execution or network I/O must be stubbed (e.g.,
   `run_turn`), use real runner objects or pass `autospec=True` / `spec=AgentRunner` so any call to a non-existent
   method raises an `AttributeError` during test execution.
3. **Assert against real contracts**: Tests must verify the actual outputs of real objects (e.g. verifying that
   `runner.build_command()` produces genuine argv arrays matching `runner.compose_cmd()`).

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

3. **Hermetic Unit Tests with Real Runner Instances (Zero Free-Form Mocks)**: In
   `apps/sandbox-executor/tests/test_agent_runner.py`, add test cases iterating across all real registered runners in
   `runners` dictionary:
   - Instantiate and test real runner instances directly without mocks.
   - Assert `runner.build_command("prompt", "model")` is callable and returns a valid argv list matching
     `runner.compose_cmd("model", "prompt")`.
   - Assert `AntigravityAgentRunner` specifically produces the correct argv.
   - In `test_review_loop.py`, replace free-form mock runners with real `AgentRunner` / `AntigravityAgentRunner`
     instances (or `create_autospec(AgentRunner)`) so calling an unmapped method fails immediately.

4. **Zero Lint / Hygiene Regressions**: Ensure all target repository tests pass cleanly via `uv run pytest` and
   formatting passes via `uv run ruff check .` and `uv run ruff format --check .`.

## Resolution

Delivered via [PR #134](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/134) and merged into `main`
(`4113f0d`):

- **Implemented `build_command` on Base `AgentRunner`**: Added
  `build_command(self, prompt: str, model_name: str) -> list[str]` to `AgentRunner` in
  `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`, delegating to `self.compose_cmd(model_name, prompt)`.
  All runner subclasses (`StandardAgentRunner`, `AntigravityAgentRunner`, etc.) inherit and provide the method.
- **Robustness in Review Loop Resolver**: In `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`,
  ensured `_run_resolver_agent()` invokes `runner.build_command()` cleanly or falls back to `runner.compose_cmd()`.
- **Minimised Mocking in Tests**: In `apps/sandbox-executor/tests/test_agent_runner.py` and `test_review_loop.py`,
  eliminated free-form mock runners in favour of real `AgentRunner` and `AntigravityAgentRunner` instances, verifying
  genuine command construction and contract fidelity.
- Traversed all 5 stages of the Holon flow, passed 3/3 ensemble review approval, calibrated, and merged into `main`.
