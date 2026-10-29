---
# holon-agentic-coder-ref-metadata-0154
title: "Fix flaky URL fuzz leak check that can match random temp-file names"
status: completed
type: bug
priority: high
tags:
  - tests
  - flaky
  - redaction
  - holon-agentic-coder
created_at: 2026-10-25T08:01:22Z
updated_at: 2026-10-29T06:40:00Z
---

## Problem

On `main` (added by PR #96), `tests/test_url_message_fuzz.py`'s password-delimiter test fails intermittently inside the
sandbox-simulation path. The PR #94 sync resolver hit one failure in a full run on 2026-10-25. Sixty reruns and two
further full runs all passed.

The likely cause is that the leak check flags any fragment of the fake password of 4 or more characters that appears in
the captured output. The docker command line includes a randomly named env-file path (`tempfile`). When that random name
happens to share a 4-character run with the fake password, the check reports a leak that isn't one.

- **Second occurrence (2026-10-26, CI):** `unit (macos-latest)` on holon-agentic-coder PR #97 head `c479dd4` failed
  `test_every_delimiter_in_a_password_stays_off_argv_and_echo` with `["http/'[':main-argv", "http/'[':echo"]`. It failed
  only in the two texts that contain the random `--env-file` path under `.../pytest-of-runner/pytest-0/...`, and
  `env-item-echo` was clean. #97 touches no redaction code. This confirms the temp-name diagnosis and shows the flake
  turns real PRs' CI red, so the priority rises.

## Scope

- Reproduce deterministically by seeding the temp-file name or the fake value so they collide, and confirm this is the
  cause.
- Make the check exact. Either generate fake secrets from an alphabet or marker that temp names can't contain, or strip
  or allowlist the env-file path before matching, or match longer or whole tokens. It must still catch genuine partial
  leaks.
- Run the fuzz module many times in CI-like conditions (for example 200 iterations) to show the flake is gone.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Found by the PR #94 iteration-15 sync resolver (merge of #95).

## Resolution

Completed through the 5-stage Holon flow on `holon-agentic-coder`:

- **Flow**: `I-1793246367-url-fuzz-leak-check-ignores-random-temp-paths` → `P-1793246383-claude-agent-claude-opus-5-5` →
  `E-1793246576-claude-agent-claude-opus-5-5`.
- **PR #107** (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/107): resolved in 2 review-loop
  iterations (3/3 ensemble approval at `d017043`, review `5692855217`, 10/10 CI green), Stage 5 calibrated (`c7cd0e2`,
  EV 50.34 predicted / 62.89 actual, Prettier-formatted in `e306256`), ledger conflicts resolved in `7635240`, and
  merged by the maintainer as `81a12ee` (2026-10-29T05:48:44Z).
