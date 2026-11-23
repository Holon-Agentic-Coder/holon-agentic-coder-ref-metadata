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
   conflicts, resolve, verify, commit, push. 1a. **Check at the most granular place (maintainer, 2026-11-23): at the
   start, at every turn, and at the end.** The check itself is cheap and needs no agent (`git fetch` plus a
   `git merge-tree` probe against the target tip, keyed on the target SHA so an unchanged target costs nothing), so it
   runs at every boundary the engine controls:
   - **start of the flow** and **start of every stage** (Stages 1 to 5);
   - **every turn inside a stage**: each executor turn/step boundary in Stage 3, each planner turn in Stage 2 where
     there are several, each review iteration in Stage 4 (before the reviewers are dispatched and again before the
     consensus is posted), each resolver turn, and each calibration retry in Stage 5;
   - **end of every stage** before it pushes, and **end of the flow** (5a below). A conflict found at any of these
     points is resolved there by `sync_with_target`, while it is still small, instead of surfacing stages later. Inside
     a stage the merge happens only at a turn boundary, never while a role container is writing the worktree; the next
     turn's agent is told what the merge changed. **When the target is merged in (maintainer, 2026-11-23):** only when
     there is a conflict to resolve, or when a stage is about to start, end, push or calibrate. At a turn boundary
     inside a stage, a target that is unchanged, or changed without conflict, is not merged (no head move, no CI run, no
     lost approval); the merge waits for the next stage start or end.
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
   **Model ladder: lowest tier first, escalate on evidence, block last (maintainer question, 2026-11-23).** Resolve
   rather than raise or block. The order is: mechanical rules (no model) → resolver on the lowest tier → the same
   conflict one tier up when lint or tests fail, or when the resolver reports it cannot decide → fail the stage (block)
   only when the top tier is exhausted. The gate is the test suite, lint and the scoped re-review, not the model's
   confidence, so a cheap model is safe to try first. Evidence from 2026-11-23: the lowest tier settled every ledger and
   KB conflict and correctly escalated the code conflicts; its one attempted code merge (bean 0369, `calibrate.py`)
   broke a test, and one tier up produced a green tree (5948 passed). Each attempt and its tier are recorded in the
   ledger row.
4. **Approval and calibration after a resolved conflict.**
   - Mechanical-only merge: the approval carries over when the PR's own diff fingerprint is unchanged (Bean 0372); only
     CI on the new head must pass (PR #250's merged-head gate).
   - Agent-resolved code conflict: the fingerprint changes, so Stage 4 re-reviews, scoped to the resolved files and the
     tests the resolver changed, not the whole PR.
   - Stage 5 calibrates after a clean merge instead of refusing; the report's diff base and evaluated SHA follow
     Bean 0369.
5. **Ledger and provenance.** Each sync appends one row to `executions.jsonl` (stage, target SHA, conflicted paths,
   class per path, how resolved, resolver attempt count, test result). `sync_conflict` rows are superseded by a later
   resolved row (as Bean 0369 treats them). 5a. **End of the flow: a conflicting PR reruns the flow (maintainer,
   2026-11-23).** The pipeline's last step checks the PR against the target branch. If it is `CONFLICTING`/`DIRTY` (the
   target moved while Stage 4 or 5 ran), the flow does not finish at the merge boundary: it runs `sync_with_target` and
   re-enters Stage 4 and Stage 5 for the merged head (CI on the new head; review only if the PR's own diff changed;
   calibration redone), and repeats until the PR is mergeable and clean. "Completed successfully" is never printed for a
   conflicting PR (seen on PR #252 and PR #248). Until this lands, the harness `holon-flow` skill does the same from
   outside (Step 4.3).
6. **Resume.** A resume that finds a merge in progress in the flow worktree adopts it (verifies, completes or aborts and
   redoes) rather than failing on a dirty tree (related: Bean 0375).
7. **Fail closed, clearly.** If the resolver exhausts its attempts or the suite stays red, the stage fails with the
   conflicted paths, the failing tests and the resolver's last diff saved in the worktree; nothing is pushed.

## Acceptance criteria

- The conflict probe runs at flow start, at the start and end of every stage, at every turn boundary listed in 1a and at
  the end of the flow; a test per boundary injects a conflicting target change just before it and asserts the conflict
  is detected and resolved at that boundary, not later. With an unchanged target the probe makes no merge and no push.

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
