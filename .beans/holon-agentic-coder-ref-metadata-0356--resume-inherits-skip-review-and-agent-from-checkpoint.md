---
# holon-agentic-coder-ref-metadata-0356
title: "A resumed flow inherits skip_review and the agent from its checkpoint instead of the run's own flags"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - checkpoint
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-21T23:30:00+11:00
updated_at: 2026-11-22T22:55:00Z
---

## Problem

On 2026-11-21, PR #228 (`intent-plan-stage-decomposition`) was calibrated without a completed review:

- An antigravity run (about 09:21-09:35Z) saved `skip_review: true` into the flow checkpoint's context.
- A later resume at 10:01Z (`holon flow ... --agent claude-agent --model claude-opus-5-5 --checkpoint ...`), run without
  `--skip-review`, read the stored value. It logged "Stage 4 (REVIEW) skipped due to --skip-review flag" and went
  straight to Stage 5.
- The same resume logged `Agent runner resolved to claude-agent (source: flag, --agent)`, but its calibration report
  names `antigravity-agent/gemini-3.8-flash-medium` as the evaluating agent. The checkpoint's agent and model won over
  the flags for at least part of the run.

## Action

Through the Holon flow on `holon-agentic-coder`:

- **Per-run switches are not checkpoint state.** `skip_review`, `skip_calibrate`, `skip_push` and `dry_run` apply only
  to the run that passes them. A resume uses only its own flags, and logs it when it drops a stored skip that differs.
- **Flags win over the checkpoint.** On resume, `--agent` and `--model` override the checkpoint's agent and model for
  every stage and role in that run: Stage 4 reviewers and resolver, and the Stage 5 evaluating agent. The checkpoint
  records the new values, and the summary shows the agent and model actually used.
- Never skip Stage 4 for a PR that has no consensus approval unless the current run passes `--skip-review` explicitly.
- Hermetic tests:
  - a checkpoint with `skip_review: true` resumed without the flag runs Stage 4;
  - a resume with `--agent claude-agent` on a checkpoint saved by antigravity uses claude for review and calibration,
    and the report names it;
  - the old checkpoint format still loads.

## Notes

- Harness side, done 2026-11-21: `run_holon_flow.py` no longer switches runner on its own and reads hour-only reset
  times. A resume that clears a stored `skip_review` by hand edits the checkpoint, as was done for #228.
- Related: Bean 0341 (resume keeps the checkpoint intact), Bean 0355 (holon calibrate runs the full Stage 5).

## Flow (2026-11-23)

- Intent: `todo/intent-0356-resume-flags-override-checkpoint.json`. PR:
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/239 (`resume-flags-override-checkpoint`). Stage 4
  consensus approved at iteration 1 (3/3); Stage 5 calibrated and the calibration report is in the PR diff. Awaiting
  human merge.
- Overlap: ran with `--allow-overlap` alongside PRs #230 and #238 (shared `cli/commands/flow.py`).

## Audit (2026-11-23)

Bean `0357` removes `--skip-review` entirely, superseding the `skip_review` inheritance clause here while the
agent/model override and per-run switch rules remain. Bundle with `0357` or run right after it; waits for PR #230
(overlaps `flow/checkpoint.py`, `flow/context.py`, `flow/pipeline.py`).
