---
# holon-agentic-coder-ref-metadata-0259
title: "`holon flow` never runs in the `main` worktree: provision a dedicated flow worktree off `origin/main`"
status: completed
type: bug
priority: high
tags:
  - flow
  - cli
  - worktree
  - holon-agentic-coder
created_at: 2026-11-09T06:00:00Z
updated_at: 2026-11-09T07:45:00Z
---

## Problem

`holon flow --target-worktree apps/<repo>/main` uses the path as it is whenever it is an attached working tree
(`ensure_worktree()` in `git_flow.py` returns early for any active working tree, and `_should_provision()` in
`cli/commands/flow.py` only provisions bare or absent targets). Stage 4 then checks out the execution branch in that
worktree (`_checkout_execution_branch`) and Stage 5 commits the calibration report and ledger rows there.

Result: every flow I ran against `main` (Beans 0254 and 0258, among others) left the `main` worktree checked out on an
`I-.../P-.../E-...` branch with extra commits and merges, until it was restored by hand. The `main` worktree must stay
on `main`, identical to `origin/main` including local files, and the editable `holon` install runs the code in it.

Naming `main` as the target is legitimate: it selects the repository and the base branch. The flow should then work in a
new worktree branched off `main`, not in the `main` worktree itself.

## Goal

1. **Redirect a default-branch worktree**: In `holon flow`, when the resolved target worktree is an attached working
   tree whose checked-out branch is the intent's target branch (normally `main`), provision or attach the derived
   `flow-<slug>` sibling worktree (`derive_worktree_layout`), branched off `origin/<target_branch>`, and use it as the
   target worktree for every stage, the checkpoint and the summary. Log the redirect. A target on any other branch is
   still used as it is.
2. **The default-branch worktree is never mutated**: No stage may check out, commit to, or write ledger or calibration
   files in it. Assert this in a hermetic test: after a flow over a fixture repository whose target is the
   default-branch worktree, its `HEAD`, branch and `git status` are unchanged.
3. **Checkpoints**: A new checkpoint records the provisioned worktree. Resuming from a checkpoint whose recorded
   worktree is a default-branch worktree fails fast with an actionable error naming the `flow-<slug>` worktree to use
   instead, rather than silently running there.
4. **Same guard for the other entry points** that write to the working tree (`holon review`, `holon review-loop` and
   `holon calibrate` run directly on a branch): refuse to run them with the default branch checked out in the target.
5. **Docs and tests**: Update the CLI help for `--target-worktree` and the flow documentation. Add hermetic tests for
   the redirect, an already-existing `flow-<slug>` worktree, a non-default-branch target, the checkpoint refusal and the
   unchanged-`main` assertion.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- Touches `cli/commands/flow.py` and `git_flow.py`, not the `flow/` package internals, so it can run alongside beans in
  the resolver lane or the calibration lane.
- Harness side (done): `AGENTS.md`, `.agents/workflows.md` and the `holon-flow` skill now require a `flow-<slug>`
  worktree, and `run_holon_flow.py` creates it from `origin/main` for a `main` target. This bean makes the CLI enforce
  it for everyone who calls `holon flow` directly.

## Resolution

Delivered via [PR #150](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/150) and merged into `main`
(`8000794`, 2026-11-09T07:31:08Z), 21 files, +1,994 / −171:

- **Redirect**: `holon flow` provisions or attaches the derived `flow-<slug>` worktree, branched off `origin/main`, when
  the target is a worktree with the target branch checked out, and runs every stage, the checkpoint and the summary
  there. Non-default-branch targets are still used as they are, and bare or absent targets still auto-provision.
- **Guards**: a checkpoint recording a default-branch worktree, and the direct `holon review`, `review-loop` and
  `calibrate` commands, refuse a default-branch worktree with an actionable error. Hermetic tests assert the `main`
  worktree's `HEAD`, branch and status are unchanged after a run.
- **Holon flow traversal**: all 5 stages on `claude-agent` / `claude-opus-5-5`, launched through the `holon-flow` skill
  script, which created the `flow-<slug>` worktree. Execute took 12.9 min. The resolver pushed fixes in iterations 1 and
  2 (no `uv` crash: Bean 0258 held), and 3/3 consensus with zero findings came at iteration 3. Calibration: predicted EV
  34.85, actual 64.43 (ΔEV +29.58; Clean and Observed EV agree, since Bean 0257 landed).
- **Calibration report not in the merged PR**: the PR was merged at head `84493a1` before the calibration merge commit
  could be pushed, so `plans/P-1794205494-860c0862-claude-agent-claude-opus-5-5_calibration.md` is only on the
  `.../E-1794205767-3c799dc6-claude-agent-claude-opus-5-5/calibrated` branch on `origin`. Keep that branch until the
  report is carried into `main` by a later flow.
- **Harness side**: the first launch of the `holon-flow` script created the worktree inside `main` (a relative-path
  bug); it was removed and the script now resolves absolute paths (`420e281`).
