---
# holon-agentic-coder-ref-metadata-0500
title: "bean-progress shows one row per bean, hiding parallel flows and their PRs"
status: completed
type: bug
priority: normal
tags:
  - harness
  - bean-progress
created_at: 2026-11-26T09:20:00Z
updated_at: 2026-11-26T09:30:00Z
---

## Problem

On 2026-11-26 bean 0405 had three flows running at once (test batches `tests-constant-time-tmp-dirs`,
`tests-cpu-bound-redaction-ledger`, `tests-fewer-git-worktree-exec`), each with its own PR (#325, #327, #323).
`bean_progress.py` showed one row for 0405 with one PR and listed the others only as "stale attempt" in the notes, so
the coordinator rebuilt the table by hand instead of returning the skill's output verbatim. Related stale rows the same
day: merged beans whose post-merge had not run yet showed "Stage 5 (Calibrated)" or "Not started" (0404, 0419, 0480),
and a decomposed flow showed "Stage 2 (Plan)" for its next child after earlier children merged into its plan branch.

## Fix

- One row per live flow (slug), grouped under its bean; a bean with no live flow keeps one row.
- Do not label a concurrent flow of the same bean as a "stale attempt" when its runner is live.
- Show a merged PR as merged (from `gh`) even before the post-merge skill updates the bean.
- For decomposed flows, show "child N of M" and the children's PRs.
- Related: Bean 0388 (stale halted stage), Bean 0488 (non-flow worktree row).

## Resolution

Implemented in `.agents/skills/bean_progress/` (2026-11-26, maintainer instruction). One row per live flow or PR of a
bean (same Bean # repeated, adjacent, notes prefixed with the flow slug); dead attempts without runner or PR still fold
into a `stale attempt` note. Merged PRs (read via `gh pr list --state merged|closed`) show `Merged — post-merge pending`
(beans with no flow are matched by bean number); closed-PR flows with a dead runner show `PR closed — dead worktree`.
Only `flow-*` or checkpoint-bearing worktrees count as flows (bean 0488). Decomposed flows show
`Stage N (child X of M: slug)` with the active and merged child PR numbers. SKILL.md documents the multi-row rule, split
flows and a Stale rows section; table columns unchanged. Hermetic tests added in `tests/test_bean_progress.py`.
