---
# holon-agentic-coder-ref-metadata-0167
title: "Turn supervisor test relies on a real 50 ms reader-join timeout and flakes on slow CI runners"
status: todo
type: bug
priority: high
tags:
  - tests
  - flaky
  - ci
  - holon-agentic-coder
created_at: 2026-10-27T01:44:38Z
updated_at: 2026-10-28T10:04:33Z
---

## Problem

`unit (macos-latest)` failed on holon-agentic-coder PR #97 head `837cb02` (2026-10-27), where the change does not touch
the code under test:

```text
FAILED tests/test_turn_supervisor.py::TestRunTurn::test_lingering_pipe_holder_group_is_terminated_after_exit
AssertionError: Lists differ: [(4242, SIGTERM), (4242, SIGKILL)] != [(4242, SIGTERM)]
```

The test (from #94, on `main`) drives `run_turn` with a fake clock and sleeper. It also patches
`turns.READER_JOIN_TIMEOUT_SECONDS` to **0.05 s of real time**. After SIGTERM, `killpg` closes the fake stream, and the
reader thread must notice and join within 50 ms. On a loaded macOS runner it doesn't, so the supervisor correctly
escalates to SIGKILL and the assertion fails. 2329 other tests passed, and ubuntu unit passed on the same head.

## Scope

- Make the reader join deterministic in tests: inject the join timeout or the thread-join primitive the same way the
  clock and sleeper are injected, or have the fake stream signal an event that the test waits on. The test must not
  depend on wall-clock scheduling.
- Audit `test_turn_supervisor.py` (and other tests that patch real timeouts to tiny values) for the same pattern.
- Verify by running the affected tests repeatedly under CPU load. A stress loop is enough; no synthetic performance
  claims.

## Notes

- **Global git config dependence (found 2026-10-27, PR #97 iteration 30):**
  `tests/test_workspace_survival_stress.py::...preserves_workspace_and_history` (stress-marked) fails when the
  developer's global git config sets `core.hooksPath`. PR #97 fixed the same dependence in its own executor tests: the
  test origin pins its own hooks directory, and client git commands set `core.hooksPath` to an empty directory. Apply
  that pattern here, and audit every test that creates repositories or hooks so none reads the developer's global git
  config. One option is a session-wide `GIT_CONFIG_GLOBAL=/dev/null` in the test environment.

- Run through the Holon flow on holon-agentic-coder. Related: Bean 0154 (another CI flake), Bean 0163 (CI timing gate).

## Status (2026-10-28)

Fixed inside PR #99 (Bean 0168, intent item 4): the lingering-pipe-holder test now joins its readers inside the fake
`killpg` after an end-of-stream sentinel (no real-time 50 ms dependency), and the stress suite passes with a hostile
global `core.hooksPath` because tests now use a hermetic test-only git config. 50/50 runs under load passed. Mark
`completed` when PR #99 merges.
