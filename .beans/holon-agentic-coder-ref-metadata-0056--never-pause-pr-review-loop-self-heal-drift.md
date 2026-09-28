---
# holon-agentic-coder-ref-metadata-0056
title: "Make pr-review-loop never pause: self-heal drift, consolidate concurrent work, escalate non-convergence"
status: completed
type: task
priority: high
tags:
  - agents
  - pr-review-loop
  - governance
  - concurrency
created_at: 2026-09-27T15:52:00Z
updated_at: 2026-09-27T21:12:00Z
---

The `pr-review-loop` skill mandated stopping the run and asking the maintainer for input whenever reviewers disagreed or
whenever the branch state was not what the loop expected. Both triggers fired during a single run on PR #47 and both
were wrong: the loop is supposed to converge autonomously, and "the tree/PR moved" is work, not a blocker.

## Measured evidence (PR #47, 2026-09-27)

- Two agent sessions drove `pr-review-loop` against the same PR and the **same host worktree** (`actions/features`).
- 23:56 -- single-agent dry-run pass on `a14e631` returned `APPROVED` (0 Critical / 0 Important / 3 Nit).
- 00:15 -- the 3-agent ensemble consensus on the **identical commit** returned **2 Critical / 3 Important / 6 Nit**,
  `CHANGES_REQUESTED`, and correctly withheld the GitHub post. The loop rule then said _"pause and request guidance"_
  rather than arbitrating the disagreement.
- 00:17-00:18 -- that session's resolver edited `AGENTS.md`, `.agents/rules.md`, `.agents/workflows.md` and beans 0046 /
  0052 and stopped **before committing**. Five tracked files stayed dirty, one `git add -A` away from being swallowed
  into an unrelated commit by whichever resolver ran next.
- One of the dirty hunks (single-line YAML title in bean 0052) would have **broken CI**, because
  `.github/workflows/test-hygiene.yml` runs `npx prettier --check "**/*.md"` (`printWidth: 120`, `proseWrap: always`),
  which re-wraps the 150-character line. Adopting concurrent work therefore needs re-verification, not blind merge.

## Change

Rewritten in `.agents/skills/pr_review_loop/SKILL.md`:

- **Principle 3 -- Deterministic Convergence (Never Pause)**: the loop has no pause state and never requests guidance
  mid-flight. The only exits are a posted clean consensus approval or the max iteration cap with a final review posted.
- **Principle 4 -- Drift Self-Healing**: a commit pushed by someone else, a parallel session in the same worktree, a
  dirty tree, a stale cached diff, a rejected push, or CI flipping from `pending` to `failure` is reconciled and then
  worked. Consolidating another author's verified in-flight edits on top (with attribution) is the default; discarding
  them is not.
- **New Phase A0.5 -- Re-Sync & Consolidate Drifted State (every iteration)**: refresh `origin` +
  `gh pr view headRefOid`, drop cached diffs when the head moved, capture foreign edits to
  `.subagent/concurrent_iter_<iteration>_{sha}.patch` before touching them, adopt verified hunks as their own
  `fix: consolidate concurrent review fixes ...` commit, revert only hunks proven wrong or CI-breaking and only after
  the patch is on disk, integrate divergence with `git pull --rebase`, re-query CI/reviews for the current head, and log
  the reconciliation for the final report.
- **Principle 5 / Phase C**: drift is integrated with `git pull --rebase` + prettier + re-push. `--force` and
  `--force-with-lease` are never the answer to drift, and another author's commits are never dropped.
- **Phase B -- Convergence Escalation Ladder** replaces the "PAUSE THE LOOP" circuit breaker: (1) re-sync and re-review,
  (2) re-adjudicate the finding against primary sources (file contents, `.agents/rules.md`, `.beans/` status, CI log),
  (3) apply the union of the competing recommendations, (4) rule false or out-of-scope findings into
  `rejected_suggestions` in `.subagent/coordination.json` -- the ledger is what actually stops re-flagging, (5) re-scope
  oversized findings into a new sequentially numbered bean. Every rung runs inside the loop and is pushed.
- **Report template**: `PAUSED` is no longer a terminal status, and the cycle history table gained a
  `Drift & Sync Actions` column plus a `Drift Consolidated During Loop` line.
- **Principle 9 -- Runtime Attrition Is Absorbed, Never Propagated** (commit `a9e7018`): a pass death caused by anything
  other than the change under review -- a child wall-clock timeout, a model that spends its output budget on reasoning
  and returns no final message, a transport rejection that tears down the enclosing orchestration -- never ends the loop
  and never cancels the iteration. Passes write their `.subagent/` report early, answer briefly, and are re-run in
  salvage mode; increment review is gated on a prior report from the same loop that closes with the machine-readable
  trailer block (`VERDICT`, `CI`, `REPORT`, `CRITICAL`, `IMPORTANT`, `NIT`, `FINDINGS`, defined in
  `.agents/skills/pr_reviewer/SKILL.md` step 3.4 and mirrored into `.agents/prompts/pr_review_prompt.md`), so an aborted
  stub is never trusted as a baseline; and operators set a wall-clock budget per step type in the launch parameters
  (`HOLON_PR_LOOP_STEP_TIMEOUTS`, defaults 10 minutes for sync/posting and 25 for review/consensus -- a launcher-side
  name only: nothing in this repository reads it, so the budget is advisory) without introducing a pause state.

## Preserved invariants

- **PR merging stays human-only.** Principle 8 now states explicitly that the never-pause policy does **not** relax the
  `gh pr merge` / auto-merge / merge-queue prohibition.
- No destructive recovery primitives (`git stash`, `git reset --hard`, `git checkout --`, `git clean`) may be pointed at
  unverified in-flight work; foreign edits must stay recoverable via a captured patch.
- Reviewers still may not post while any Critical or Important finding survives.

## Verification

- `npx prettier --check .agents/skills/pr_review_loop/SKILL.md` passes.
- `grep -n "PAUSE\|request guidance" .agents/skills/pr_review_loop/SKILL.md` returns exactly one line -- the Step 3
  summary template's "There is no `PAUSED` status" note -- plus nothing in the escalation ladder, and no imperative
  pause instruction remains anywhere in the skill.
- Both new in-body anchors (`#phase-b-evaluate-exit-conditions--post-final-review`,
  `#phase-a05-re-sync--consolidate-drifted-state-every-iteration`) resolve to headings in the same file.

## Notes

- Harness-only change (`.agents/` is directly editable per the harness exception in `AGENTS.md`); no target-repository
  code is involved, so no flow run is required.
- Related: 0034 (prohibit autonomous PR merging) stays authoritative for the merge boundary; 0052 (consult ledger/KB per
  agent action) is where a `coordination.json` write in rung 4 would also be recorded as wisdom.

## Resolution

Implemented in `.agents/skills/pr_review_loop/SKILL.md` on `actions/features` (PR #47), alongside commit `de4f240`,
which consolidated the interrupted concurrent resolver output exactly as the new Phase A0.5 prescribes -- hunks kept
after re-verification (`Bean 0039 is completed` staleness fix, bean 0046 `created_at`) and the CI-breaking bean 0052
hunk dropped with the reason recorded in the commit message.

Principle 9 landed afterwards in commit `a9e7018`, which recorded the attrition rules but left two of them unnamed -- no
step ever set a wall-clock budget and no shipped document defined the trailer schema the salvage mode trusts. The
Iteration-1 resolver pass on the same PR pinned both down (named defaults plus `HOLON_PR_LOOP_STEP_TIMEOUTS`, and the
trailer block defined in `pr_reviewer/SKILL.md` step 3.4), which is why this record was advanced to describe them.
