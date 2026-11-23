---
# holon-agentic-coder-ref-metadata-0376
title: "The flow resolves file conflicts itself at every stage: an in-flow conflict resolver"
status: todo
type: feature
priority: critical
tags:
  - flow
  - merge-conflicts
  - resolver
  - cost
  - holon-agentic-coder
created_at: 2026-11-23T08:40:00Z
updated_at: 2026-11-23T08:40:00Z
---

## Problem

When a flow branch conflicts with its target branch, the flow engine resolves only ledger files. Any other conflicting
file stops the stage, and the conflict is then fixed outside the flow (the `resolve-conflict` skill in a harness
subagent, or by hand). On 2026-11-23 every code conflict was handled that way: PR #248 (twice), bean 0191 child 3, PR
#253 (`flow/stages/calibrate.py`), PR #251, PR #252 (16 KB entry files).

What each stage does today (`flow/stage_conflicts.py`, `flow/stage_conflict_resolution.py`,
`flow/review/conflict_gate.py`, `flow/stages/sync_conflict.py`):

| Where                                                | Ledger conflict                                  | Any other file                                                                                                                           |
| :--------------------------------------------------- | :----------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| Before a stage (`check_and_resolve_stage_conflicts`) | append-merged automatically                      | raises `ConflictResolutionError`; the stage fails (bean 0191 at Stage 3 `prepare_workspace`, bean 0369 at Stage 4 entry)                 |
| End of Stage 3                                       | —                                                | records a `sync_conflict` row and reports success ("a resolver or the maintainer must resolve it"); no resolver runs, Stage 4 then fails |
| Stage 4 conflict gate                                | merges the target and pushes; approval re-earned | aborts the merge and blocks                                                                                                              |
| Stage 5                                              | —                                                | refuses to calibrate; PR #248 was refused for ledger and KB index conflicts reported as "code conflicts"                                 |

The handling differs per stage (raise, record a row, abort, refuse), none of it resolves a code conflict, and each halt
costs a harness subagent, a manual resume and often a repeated review.

## Goal

At any stage of the flow, a file conflict with the target branch is taken care of inside the flow: the engine merges the
target branch, resolves the conflicts, proves the result with lint and tests, and continues. A stage fails on a conflict
only when the resolver cannot produce a passing tree, and then it says exactly which files and why.

## Design

1. **One conflict routine for every stage.** Replace the per-stage variants with a single
   `sync_with_target(context, stage)` used before Stages 2 to 5, at the end of Stage 3, at the Stage 4 conflict gate and
   before Stage 5: fetch, merge the target branch with a normal merge commit (never a rebase or force-push), classify
   conflicts, resolve, verify, commit, push.
2. **Mechanical classes, no agent** (extend `classify_conflicts`):
   - ledgers: append-merge (as today);
   - KB/WB entry files that differ only in timestamps (add/add): keep the target branch's copy;
   - files deleted on the target and only touched mechanically on the branch (for example a removed generated index):
     keep the deletion;
   - lists both sides appended to (lazy-export maps, `__all__`, changelog-style files): union, keeping order rules.
3. **Conflict resolver role for code conflicts.** A containerised resolver agent (same runner, agent and model ladder as
   the Stage 4 resolver) receives the conflicted files, both sides' diffs since the merge-base, and the intent and plan
   of this flow. It resolves each file, runs `uv run task lint` and the affected tests, then the full suite, and commits
   the merge. It may not change files outside the conflict set except tests whose setup the merge invalidated, may not
   touch the frozen module budgets (an over-budget file is split, as elsewhere), and has a bounded number of attempts.
4. **Approval and calibration after a resolved conflict.**
   - Mechanical-only merge: the approval carries over when the PR's own diff fingerprint is unchanged (Bean 0372); only
     CI on the new head must pass (PR #250's merged-head gate).
   - Agent-resolved code conflict: the fingerprint changes, so Stage 4 re-reviews, scoped to the resolved files and the
     tests the resolver changed, not the whole PR.
   - Stage 5 calibrates after a clean merge instead of refusing; the report's diff base and evaluated SHA follow
     Bean 0369.
5. **Ledger and provenance.** Each sync appends one row to `executions.jsonl` (stage, target SHA, conflicted paths,
   class per path, how resolved, resolver attempt count, test result). `sync_conflict` rows are superseded by a later
   resolved row (as Bean 0369 treats them).
6. **Resume.** A resume that finds a merge in progress in the flow worktree adopts it (verifies, completes or aborts and
   redoes) rather than failing on a dirty tree (related: Bean 0375).
7. **Fail closed, clearly.** If the resolver exhausts its attempts or the suite stays red, the stage fails with the
   conflicted paths, the failing tests and the resolver's last diff saved in the worktree; nothing is pushed.

## Acceptance criteria

- For each of Stages 2, 3, 4 and 5: a fixture where the target branch gains a conflicting change to a code file the flow
  also changed; the flow resolves it through the resolver role, tests pass, and the stage completes without a human or
  an outside agent.
- Mechanical classes (ledgers, timestamp-only KB entries, delete-vs-touch, both-appended lists) resolve with no agent
  call; a test per class.
- After a mechanical-only merge no reviewer is dispatched again; after an agent-resolved conflict only the resolved
  files are re-reviewed.
- Stage 5 no longer refuses for conflicts the routine can resolve; a ledger-only conflict never produces the message
  "code conflicts".
- A resolver that cannot reach a green tree fails the stage with paths, failing tests and saved diff; nothing is pushed;
  the checkpoint allows `--from-stage` resume.
- Every sync is recorded as one append-only ledger row; no earlier row is edited.
- Never rebases or force-pushes a flow branch; never edits the module budget file.
- All tests pass via `uv run pytest`; `uv run task lint` and `uv run task lint-docs` pass.

## Related and ordering

- Builds on Bean 0372 (approval survives a merge of main; PR #254) and Bean 0369 (calibration diff base; merged as PR
  #253): run after #254 merges.
- Bean 0371 (per-flow ledger fragments) and Bean 0373 (KB index, merged) reduce how often conflicts occur; this bean
  handles the ones that remain.
- Beans 0374 and 0375 (interrupted-run defects) share the resume path.
- Large: likely a split flow (shared routine and mechanical classes; resolver role; per-stage wiring and scoped
  re-review). Once it lands, the harness `resolve-conflict` skill is needed only for hand-authored harness branches.
