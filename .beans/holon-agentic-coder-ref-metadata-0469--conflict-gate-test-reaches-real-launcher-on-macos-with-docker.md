---
# holon-agentic-coder-ref-metadata-0469
title: "test_conflict_gate code-conflict test reaches the real launcher and exits on macOS when docker is on PATH"
status: completed
type: bug
priority: normal
tags:
  - tests
  - hermetic
  - macos
created_at: 2026-11-25T23:10:00Z
updated_at: 2026-11-26T22:35:00Z
---

## Problem

`apps/sandbox-executor/tests/flow/review/test_conflict_gate.py::test_a_code_conflict_still_aborts_with_a_fingerprinted_approval`
fails on a clean checkout of origin/main (a144e65c) on a developer Mac that has `docker` on PATH, so local
`uv run pytest` is red on main. The two stress tests that re-run the suite in a child (`test_sandbox_hermetic_guard.py`
canary and `test_workspace_survival_stress.py`) fail only as a consequence.

## Cause (confirmed)

The test merges main into a conflicting branch, so `sync_with_target` calls the conflict resolver role. The chain is
`conflict_resolver_role._dispatch` -> `dispatch_role_agent` -> `containers.run_docker_container` -> `mounts()` ->
`launcher/mounts.py::_antigravity_mounts`. The default agent is `antigravity-agent` and the autouse fixture
`isolated_claude_home` sets HOME to an empty tmp dir, so `~/.holon/sessions/antigravity` is missing. On darwin without
HOLON_AGENT_KEY, `_abort_missing_macos_antigravity_session` calls `sys.exit(1)`. `_dispatch` only catches `Exception`,
and `SystemExit` is a `BaseException`, so it kills the test. The test never mocks the dispatch/launcher.

Why CI is green: with docker absent from PATH (what CI macos-latest effectively provides) the launch aborts earlier,
before `mounts()`. Verified locally: the same test with `PATH=<uv dir>:/usr/bin:/bin` passes; with the normal PATH it
fails, with or without GITHUB_TOKEN, CI=true, or GITHUB_ACTIONS=true. The failure is not tied to the real ~/.holon
session dir (it exists on this Mac but the fixture hides it), only to docker being installed. Ubuntu is unaffected
because the abort is darwin-only.

## Introduced by

Latent since PR #280 (131c3b42, 2026-11-25, launcher refactor that moved the macOS abort into mounts.py; the abort
itself dates from #229/#241). The test is from PR #283 (ce2c4c7a, resolver tiers), which made the gate reach the
dispatch. Neither PR's CI caught it because CI runners lack docker. Main's latest Test - Unit run (45716718961,
a144e65c) is green on ubuntu and macos.

## Evidence

- Detached worktree of origin/main a144e65c: 1 failed, 25 passed in that file; SystemExit at mounts.py:84.
- CI log: that test PASSED on both unit (macos-latest) and unit (ubuntu-latest).

## Proposed fix

1. In the test (or an autouse conftest fixture), monkeypatch the role dispatch (`conflict_resolver_role._dispatch_role`)
   or `containers.run_docker_container` so no unit test reaches the real launcher; assert it is not called for the
   code-conflict path unless the test expects it.
2. Make `_dispatch` catch `SystemExit` too (`except (Exception, SystemExit)`) so a launcher abort becomes an
   `agent_failed` verdict instead of killing the flow.
3. Add a hermetic guard that fails fast if a test spawns docker or reaches `run_docker_container` unmocked.

## Flow

Launched 2026-11-27 as flow-conflict-gate-launcher-abort (claude-agent, claude-opus-5-5); intent
todo/intent-0469-conflict-gate-launcher-abort.json. Scope: flow/conflict_resolver_role.py plus its two tests; the
conftest guard from proposed fix 3 is left out.

## Resolution

Delivered via [PR #355](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/355) and merged into `main`
(`c5435c1e`):

- **Key Architectural Deliverables**: the conflict resolver role dispatch treats a `SystemExit` from the container
  launcher as an `agent_failed` verdict (same as any other exception), so a launcher abort no longer kills the flow. The
  code-conflict test replaces the role dispatch with a stub, so it never reaches the real launcher on a macOS host with
  docker on PATH.
- **Verification & Tests**: `test_conflict_gate.py` and `test_conflict_resolver_role.py` updated; passes on a macOS host
  with docker on PATH and an empty home directory.
- **Scope left out**: the conftest guard from proposed fix 3 (hermetic guard that fails fast on unmocked
  `run_docker_container`) was not delivered here; it is left for the conftest split, bean 0540.
- **Holon Flow Traversal**: flow `conflict-gate-launcher-abort` (intent, plan, execute, review, calibrate) completed;
  the PR was merged by the maintainer.
