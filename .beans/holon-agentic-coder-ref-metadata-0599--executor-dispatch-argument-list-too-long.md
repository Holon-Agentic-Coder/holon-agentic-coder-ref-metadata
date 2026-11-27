---
# holon-agentic-coder-ref-metadata-0599
title: "Executor dispatch fails with 'exec role_dispatcher.sh: argument list too long' (exit 255)"
status: in-progress
type: bug
priority: high
tags:
  - holon-flow
  - executor
  - dispatch
created_at: 2026-11-27T01:49:20Z
updated_at: 2026-11-27T17:41:21Z
---

## Cause

- On 2026-11-26T23:47:17Z the Stage 3 executor dispatch of the module-budget-default-350 flow ran
  `docker run ... -e HOLON_REPLAN_FEEDBACK ...` and the container died at once with
  `exec /home/holon/entrypoint/role_dispatcher.sh: argument list too long`; the stage failed with executor exit code 255
  after 0.4 minutes (log line 215 of the flow log).
- Hypothesis, unconfirmed: the inherited environment (`HOLON_REPLAN_FEEDBACK` carries replan text, plus the intent and
  env-file values) exceeds the kernel exec argument and environment size limit inside the container.

## Fix

- Reproduce with a replan feedback value of realistic size and measure the environment size handed to the container.
- Pass large values (replan feedback, intent text) through a mounted file instead of an environment variable, as the
  intent file already is; keep the environment small.
- Fail early with a clear message naming the variable and its size when the environment would exceed the limit.

## Acceptance

- A replan feedback larger than the exec environment limit no longer fails the executor dispatch.
- A test covers the dispatch with an oversized feedback value.
- Self-explaining code invariant holds: no docstrings, and the only comments are `# why:` comments.

## Links

- holon-agentic-coder-ref-metadata-0489 (flow where it occurred)
- 2026-11-27 (`0519` `admission-remote-in-flight`, `8496396b1`): confirmed directly — Stage 2 re-plan merged
  `origin/main` across `3,908` paths (`233,058` bytes in `-e HOLON_REPLAN_FEEDBACK`), exceeding Linux's 128 KiB
  `MAX_ARG_STRLEN` and crashing container startup with
  `exec /home/holon/entrypoint/role_dispatcher.sh: argument list too long` (`exit 255`); reproduced via
  `docker run -e HOLON_REPLAN_FEEDBACK=...`.

## Flow & PR Status

- PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/434 (OPEN, `MERGEABLE` / `CLEAN`, head
  `4ebcdd35adf7e13a2d98584e0a2f02ba9f0d1f55`, awaiting maintainer merge)
- Worktree: `apps/holon-agentic-coder/flow-replan-feedback-file-dispatch`
- Branch: `I-1795797317-replan-feedback-file-dispatch/P-1795797350-ANA-G4N/E-1795797667-ANA-G4N/_`
- Checkpoint:
  `apps/holon-agentic-coder/flow-replan-feedback-file-dispatch/.holon/flow/checkpoint-replan-feedback-file-dispatch.json`
  (all 5 stages `intent`, `plan`, `execute`, `review`, `calibrate` completed)
- Consensus: APPROVED (3/3 across 3 iterations, `antigravity-agent` / `gemini-4-neon`)
- Calibration: `plans/I-1795797317-replan-feedback-file-dispatch/P-1795797350-ANA-G4N_calibration.md` included in PR
  diff (Predicted EV: `66.55`, Actual EV: `84.91`, delta `+18.36`)
- CI: 16/16 checks passed (`0` failing, `0` pending)
