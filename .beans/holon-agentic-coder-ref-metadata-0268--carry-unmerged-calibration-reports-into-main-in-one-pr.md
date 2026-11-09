---
# holon-agentic-coder-ref-metadata-0268
title: "Carry the calibration reports that missed their PRs into `main` in one pull request"
status: in-progress
type: task
priority: normal
tags:
  - calibration
  - flow
  - holon-agentic-coder
created_at: 2026-11-09T12:00:00Z
updated_at: 2026-11-09T12:00:00Z
---

## Problem

Stage 5 writes its calibration report to the `.../calibrated` branch, and the flow is supposed to merge that commit into
the PR head before the maintainer merges (`AGENTS.md`, "Ordering of the merge boundary"). Twice the PR was merged before
the calibration merge could be pushed, so the report stayed on its `calibrated` branch only:

- PR #150 (Bean 0259), report `plans/P-1794205494-860c0862-claude-agent-claude-opus-5-5_calibration.md`, branch
  `I-1794205479-flow-runs-in-dedicated-worktree-not-default-branch/.../E-1794205767-3c799dc6-claude-agent-claude-opus-5-5/calibrated`
  (`8689e81`).
- PR #153 (Bean 0266), report `plans/P-1794220535-37b66e75-claude-agent-claude-opus-5-5_calibration.md`, branch
  `I-1794220515-run-ci-on-pull-requests-into-any-branch/.../E-1794220711-a8d9ac38-claude-agent-claude-opus-5-5/calibrated`
  (`ea3466b`).

A survey of the seven `calibrated` branches left on `origin` found these two are the only ones whose report is missing
from `main`; the other five (the Stage 5 knowledge-commit flow and Beans 0249, 0254, 0258 and 0256) already have theirs.
Each branch carries two calibration commits: the report plus its ledger rows, and one stage-5 reconciliation row.

Older plans without a report in `main` (23 of 104, mostly August to mid-October 2026, plus the 2026-10-29 and 2026-10-30
runs) have no `calibrated` branch left, so they cannot be recovered this way and are out of scope.

## Action

One branch off `origin/main` carrying the four calibration commits by `cherry-pick -x`, in chronological order, with
ledger-only conflicts resolved by interleaving rows on `created_at` and removing duplicates. One pull request into
`main` for the maintainer to review and merge.

**Exception to the sole-change-path rule:** this was assembled by hand outside the Holon flow, at the maintainer's
explicit instruction (2026-11-09). It moves existing, flow-generated, already-audited artefacts and authors no new code.
The exception is named in the commit messages and the PR description.

## Follow-up

Bean 0253 (calibration branches from the origin PR head) and the flow's pre-merge ordering are what stop this recurring.
Do not delete the `calibrated` branches until this PR has merged.

## Progress (2026-11-09)

Branch `chore/0268-carry-unmerged-calibration-reports` (four `cherry-pick -x` commits off `origin/main` at `fe3b540`)
and [PR #154](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/154) opened. It adds the two reports and
+27 ledger rows (one existing row moved by the `created_at` sort; no row removed); all three ledgers parse and have no
duplicate lines. The exception is named in the last commit message and the PR description. Awaiting CI and the
maintainer's merge. After it merges: remove the worktree
`apps/holon-agentic-coder/chore-0268-carry-unmerged-calibration-reports` and the two `calibrated` branches, then close
this bean.

Observation: the shared repository's local git config carries the committer identity "Holon Review Loop Agent", set by
earlier flow runs, so commits made by hand in any worktree of the bare repository use it unless overridden.
