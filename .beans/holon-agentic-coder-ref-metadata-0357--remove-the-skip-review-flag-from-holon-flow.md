---
# holon-agentic-coder-ref-metadata-0357
title: "Remove the --skip-review flag from holon flow"
status: in-progress
type: task
priority: high
tags:
  - flow
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-21T23:45:00+11:00
updated_at: 2026-11-23T09:00:00+11:00
---

## Problem

`holon flow --skip-review` skips Stage 4 and still runs Stage 5 calibration, CI waits and PR verification. On 2026-11-21
a subagent used it after every review attempt stalled, and PR #228 reached calibrated, green and mergeable with no
consensus review. The maintainer's ruling (2026-11-21): there is no case where `--skip-review` is necessary.

## Action

Through the Holon flow on `holon-agentic-coder`:

- Remove the `--skip-review` option from `holon flow` (`cli/commands/flow.py`), the `skip_review` field from the flow
  context and checkpoint (old checkpoints that still carry it must load, ignoring the key), and the skip branches in
  `flow/pipeline.py`, `flow/resume_guard.py`, `flow/stages/children.py` and `flow/stages/review.py`.
- Remove the matching tests and the `--skip-review` mentions in `docs/git_flow.md`.
- A Stage 4 that fails or stalls halts the flow with the failure reported; nothing downstream runs without consensus.
- Hermetic tests: `holon flow --skip-review` is rejected as an unknown argument; a checkpoint with `skip_review: true`
  resumes and runs Stage 4.

## Notes

- Harness rule, done 2026-11-21: `AGENTS.md` and `.agents/holon-flow.md` forbid `--skip-review` outright.
- Supersedes the `--skip-review` wording in Bean 0356 (its checkpoint-inheritance fix for `skip_review` becomes moot
  once the flag is gone; its agent/model part stays).
- Related: Bean 0356 (resume inherits state from the checkpoint).
