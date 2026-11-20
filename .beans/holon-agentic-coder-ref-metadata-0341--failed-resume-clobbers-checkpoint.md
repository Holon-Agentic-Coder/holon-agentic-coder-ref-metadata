---
# holon-agentic-coder-ref-metadata-0341
title: "A flow resumed with --from-stage and no context fails and overwrites the good checkpoint with empty branches"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - checkpoint
  - resume
  - holon-agentic-coder
created_at: 2026-11-20T20:40:00+11:00
updated_at: 2026-11-20T20:40:00+11:00
---

## Problem

Seen on the `freeze-module-budgets-split` flow (Bean 0264, PR #214), 2026-11-20. After a conflict resolution the flow
was rerun with `holon flow <intent> --from-stage review` and no `--checkpoint`. It failed at once with "Cannot run
Review stage without an active execution_branch" and saved a checkpoint with empty intent, plan, execution and
calibrated branch fields over the completed one. The subagent had to rebuild the branch names by hand (damaged copy kept
as `checkpoint-freeze-module-budgets-split.json.clobbered.bak`). After the resumed run the checkpoint also showed
`current_stage: intent` with only review and calibrate listed as completed.

## Action

Through the Holon flow on `holon-agentic-coder`:

- `--from-stage` without `--checkpoint` loads the existing checkpoint for the intent's slug in the target worktree when
  there is one, instead of starting from an empty context.
- A run that fails before its first stage does any work never overwrites an existing checkpoint; it leaves it as it was.
- A resumed run keeps the earlier completed stages and the correct `current_stage` in the checkpoint.
- Hermetic tests for all three.

## Notes

- Harness side: `run_holon_flow.py` can also pass the existing checkpoint itself when only `--from-stage` is given.

## Progress

- 2026-11-20: Flow `resume-keeps-checkpoint-intact` started (claude-agent, claude-opus-5-5) in worktree
  `apps/holon-agentic-coder/flow-resume-keeps-checkpoint-intact`.
- 2026-11-20: Flow completed all 5 stages. PR #217 (3/3 consensus at review iteration 1), calibration in the PR diff,
  predicted EV 43.47, actual 59.47 (+16.00); MERGEABLE/CLEAN, checks green; awaiting human merge.
