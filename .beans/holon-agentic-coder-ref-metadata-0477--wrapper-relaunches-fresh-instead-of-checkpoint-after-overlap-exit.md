---
# holon-agentic-coder-ref-metadata-0477
title: "Overlap-exit relaunch without --checkpoint restarts split-calibration-package from intent four times"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - checkpoint
  - harness
created_at: 2026-11-26T05:15:00Z
updated_at: 2026-11-26T05:15:00Z
---

# Overlap-exit relaunch without --checkpoint restarts the flow from intent

## Problem

Bean 0197 (slug `split-calibration-package`) was launched with
`run_holon_flow.py <intent> --target-worktree apps/holon-agentic-coder/main --agent claude-agent --model claude-opus-5-5`.
Each relaunch after a Stage 3 overlap exit (local flow `no-unneeded-full-review`, touching calibration.py) and each
relaunch after a planner failure ran intent and plan again from scratch instead of resuming from
`.holon/flow/checkpoint-split-calibration-package.json`. The holon child command line carried no `--checkpoint`.

Evidence (local intent branches, all pushed to origin, all cut from origin/main):

- `I-1795665972-split-calibration-package` (plan P-1795665995)
- `I-1795666365-split-calibration-package` (plan P-1795666397)
- `I-1795668981-split-calibration-package` (plan P-1795669003; planner refused:
  `mounted workspace ... has uncommitted changes`, caused by untracked `plans/I-1795668981-split-calibration-package/`)
- `I-1795669744-split-calibration-package` (plan P-1795669767, current run)

Each fresh start also appended another intent row to the flow branch's ledger, so the eventual PR would carry duplicate
intent rows.

## Expected

After an overlap exit or a resumable failure, the wrapper relaunches with
`--checkpoint <worktree>/.holon/flow/checkpoint-<slug>.json` and resumes at the stage recorded there (for Stage 3
admission, `execute`). It never restarts from intent while a checkpoint exists.

## Related

- Bean 0468 (wrapper exits on a Stage 3 overlap instead of waiting). Still open. This bean is the resume half.
- Bean 0476 (overlap polling relaunches every minute).
- Untracked `plans/I-*/` left in the flow worktree by the intent stage blocks the planner's clean-workspace check.
  Logged as a separate observation in the same run.

## Workaround in use

Hand-relaunch with `--checkpoint` (same intent, worktree, agent, model) after the overlapping flow's PR merges or
closes. Do not relaunch without it.
