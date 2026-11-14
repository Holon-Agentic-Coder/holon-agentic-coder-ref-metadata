---
# holon-agentic-coder-ref-metadata-0208
title: "holon-coherence: a ProxyLifecycle class owns start-up, readiness and teardown of the proxy"
status: completed
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0203
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-14T14:10:00Z
---

## Problem

Spawned by Bean 0177. Measured on `68fdf67`: `commands/start.handle_start` **202 lines, CC 33**, `ensure_proxy_running`
171 lines, CC 30; `commands/agents.extract_runner_flags` CC 24 and `build_agent_env` CC 23. `start.py` was touched by 3
of the coherence PRs #24-#31 (#26 readiness polling, #27 mitmweb inspector, #29).

## Scope

1. `ProxyLifecycle` (docker or host-local mode chosen once) with `ensure_ca`, `start`, `wait_until_ready` (monotonic
   deadline), `stop`; `handle_start` becomes argument parsing plus one call.
2. Runner flag and env construction as a small `AgentLaunch` object in `commands/agents.py`.
3. All functions within the 0186 limits; readiness and inspector behaviour unchanged.

## Touch set

`commands/start.py`, `commands/agents.py`, `host_local.py` (call sites only), mirrored tests.

## Dependencies

Blocked by 0203. Parallel-safe with 0207.

## Notes

- Run through the Holon flow on holon-coherence.

## Progress (2026-11-01)

- Intent `I-1793438378-coherence-proxy-lifecycle-class-for-start/_` and plan
  `P-1793438393-antigravity-agent-gemini-3.8-flash-medium` generated and pushed.
- Stage 3 executed (`E-1793439253-antigravity-agent-gemini-3.8-flash-medium`, head `2f30d6e`) and Pull Request
  [#41](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/41) opened. Worktree
  `apps/holon-coherence/pr41-proxy-lifecycle`.
- CI is **red** on both unit jobs (`unit (ubuntu-latest)` and `unit (macos-latest)`; `docker-build`, `Run Make`,
  `hygiene` and `integration` pass): 9 tests fail — 5 in `tests/commands/test_start.py::TestMitmwebInspectorDefault`, 1
  in `tests/commands/test_web_token.py` and 3 in `tests/test_cli.py::TestCLIDispatchAndMain` — with `SystemExit: 1` in
  the in-container `start` path and `Expected 'stop_proxy_container' to be called once. Called 0 times.` in the new
  `stop` dispatch. The in-container start branch and the `stop` call site were moved without updating the mocks' patch
  targets.
- Stage 4 (review loop) has therefore not started and no review has been posted; `mergeStateStatus` is `UNSTABLE`.
- Next: resume from Stage 3/4 on the existing execution branch (`holon flow <intent.json> --from-stage review`) after
  fixing the three failing test modules, then review to consensus, calibrate, and request the merge.

## Resolution

Delivered via [PR #42](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/42) and merged into `main`
(`baf5c65`, holon-coherence `0.1.0`). It supersedes
[PR #41](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/41), which the maintainer closed in favour of #42
(its branches deleted).

- **Key Architectural Deliverables**: `ProxyLifecycle` (in `src/holon_coherence/container/lifecycle.py`) owns
  `ensure_ca`, `start`, `wait_until_ready` (monotonic deadline) and `stop`. The `start` and `stop` commands delegate to
  it (`commands/start.py`, `commands/stop.py`, `commands/docker_ops.py`). `ProxyLifecycleConfig` carries the docker or
  host-local settings.
- **Verification & Tests**: CI 7/7 green on the PR head; hermetic tests added in `tests/test_proxy_lifecycle.py` and
  `tests/commands/test_stop.py`.
- **Holon Flow Traversal**: Stage 3 execution `E-1794660196-e8e8027b-claude-agent-claude-opus-5-5`; Stage 4 review
  reached consensus 3/3 at iteration 5; Stage 5 calibration
  (`plans/P-1793438393-antigravity-agent-gemini-3.8-flash-medium_calibration.md`) is included in the PR diff. EV
  predicted 8.05 / actual 8.45.
- **Engine findings exposed**: (1) the `skip_review` / `skip_calibrate` checkpoint flags stick across resumes; (2) the
  flow halted for human review after consensus approval, skipping Stage 5, and needed a calibrate-only resume.
