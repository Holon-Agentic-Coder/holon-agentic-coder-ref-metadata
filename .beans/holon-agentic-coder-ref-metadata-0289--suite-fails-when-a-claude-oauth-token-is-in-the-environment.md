---
# holon-agentic-coder-ref-metadata-0289
title:
  "Four test_cli.py credential tests fail whenever CLAUDE_CODE_OAUTH_TOKEN is in the environment, so the credentialed
  review container's pre-push gate fails"
status: completed
type: bug
priority: critical
tags:
  - flow
  - tests
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-12T07:00:00Z
updated_at: 2026-11-12T07:00:00Z
---

## Problem

The Stage 4 resolver's pre-push gate runs the suite in the review-loop container, whose environment carries the runner's
credential (`CLAUDE_CODE_OAUTH_TOKEN`, applied from the agent settings). The suite's ambient-credential scrub
(`tests/conftest.py`: `_AMBIENT_CREDENTIAL_NAMES = ("GITHUB_TOKEN", "GH_TOKEN")` plus `HOLON_*`) does not clear it, so
four `tests/test_cli.py` tests see a real token instead of the one they plant:
`test_claude_container_gets_the_discovered_secrets_file_value_by_type` (both parameters),
`test_secrets_travel_in_an_owner_only_env_file_that_is_removed` and
`test_line_break_in_a_secret_aborts_before_docker_runs`. Diagnosed 2026-11-12 on the `stubfetch` flow (Bean 0286) from
the first untruncated gate log (Bean 0285): the full suite gave `4 failed, 3669 passed`; re-running those tests in the
review-loop image reproduces exactly four failures with a dummy token in the environment and four passes without it.
This is also why earlier gate halts showed four `F`s that never reproduced in an uncredentialed container run.

## Action

Run through the Holon flow. Scrub every credential variable the code under test reads (`CLAUDE_CODE_OAUTH_TOKEN`,
`ANTHROPIC_API_KEY`, and any other the credential discovery consults) in the suite-wide isolation fixture, and add a
guard test that runs the four named tests (or a representative one) with each variable set in the real environment and
asserts they still pass. Test code only; no production change; no new dependencies.

## Notes

Touches `tests/conftest.py`, which Bean 0286 also edits, so the two run one after the other.

## Resolution

Delivered via [PR #176](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/176) and merged into `main`
(`7464836`):

- **Fix**: the suite-wide isolation fixture in `tests/conftest.py` now scrubs `CLAUDE_CODE_OAUTH_TOKEN` and
  `ANTHROPIC_API_KEY`, so the four `test_cli.py` credential tests no longer see the credentialed review container's
  token. A guard test sets each variable in the real environment and asserts the tests still pass. Test code only.
- **Review**: 3/3 ensemble consensus approval after 6 resolver iterations, posted as a comment (`--approve` is refused
  on the maintainer's own PR). Head at calibration `516b7da`.
- **Calibration**: `plans/P-1794464849-2a9a4a6b-claude-agent-claude-sonnet-5-5_calibration.md` in the PR; EV predicted
  47.95 vs actual 56.06.
- **Flow**: all five stages traversed through `holon flow`.
- **Unblocks**: Bean 0286 (stubfetch, PR #174), then Bean 0280 (calci, PR #173).
