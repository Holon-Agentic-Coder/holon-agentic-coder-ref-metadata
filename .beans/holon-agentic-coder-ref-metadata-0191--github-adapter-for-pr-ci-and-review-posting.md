---
# holon-agentic-coder-ref-metadata-0191
title: "One GitHub adapter owns every gh call (PR create/update, CI probe, mergeability, review posting)"
status: in-progress
type: task
priority: high
tags:
  - refactor
  - ports-and-adapters
  - github
  - holon-agentic-coder
blocked_by:
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-23T12:50:00+11:00
---

## Problem

Spawned by Bean 0177. `flow.py` (`993b686`) issues 14 raw `gh` invocations spread over `create_or_update_pr`,
`probe_ci_checks` (CC 24), `check_pr_mergeability` (192 lines, CC 28), `post_pr_review_consensus` (185 lines, CC 40),
`generate_semantic_pr_metadata` (CC 46), `_wait_for_ci_registration` and `_wait_for_pending_ci`. GitHub I/O, polling
policy and domain decisions are interleaved, so tests must patch module globals and every review-loop change edits the
same functions.

## Scope

1. `adapters/github.py`: a `GitHubPullRequests` class (repo-scoped) with intention-revealing methods (`open_or_update`,
   `ci_checks`, `mergeability`, `post_review`), the only place that runs `gh`. It keeps the existing write guard and
   token redaction.
2. Pure decision functions (CI verdict, mergeability verdict, consensus body, semantic PR title/body) move to
   `flow/review_policy.py`-style modules with no I/O; the adapter returns plain data.
3. A `FakeGitHub` in `tests/` replaces `patch` on `subprocess`/module globals in the affected tests.
4. Every function in the touched code within the 0185 limits.

## Touch set

`flow/github.py` (becomes `adapters/github.py` plus pure modules), call sites in `flow/review_loop.py` and
`flow/stages/review.py` (call lines only), `review_target.py` if it shells out to `gh`, matching tests.

## Dependencies

Blocked by 0187. Blocks 0192. Sequence with 0160 (CI polling) and 0179.

## Notes

- Run through the Holon flow on holon-agentic-coder. Tests never call real `gh`.

## Audit (2026-11-20)

Blocker Bean 0187 was scrapped (the `flow/` split landed via #147/#163); the `flow.py` references above are stale. The
`gh` calls now sit under `flow/github/` plus `review_target.py`, `calibration.py` and `flow/review/loop.py`; there is
still no single adapter.

## Audit (2026-11-21)

Touch set refreshed against `origin/main`: the `gh` calls live in
`flow/github/{pr,ci,ci_wait,ci_final_head,ci_reverify,merge,merge_method,review_post}.py`, `flow/in_flight.py`
(`gh pr list`/`pr diff`), `review_target.py` and `calibration.py`; call sites in `flow/review/loop.py` and
`flow/stages/review.py`. Tests mirror under `tests/flow/github/` and `tests/flow/review/`. `flow/github/pr.py` is 515
lines, so the module budget (Beans 0264, 0340) applies to any new adapter module.

## Flow progress (2026-11-23)

- Intent `todo/intent-0191-github-adapter-pr-ci-review.json` ran through Stage 2 (plan, resumed after a Stage 2
  ambiguous-P-branch stop; the stale empty P- branch from the earlier attempt was bypassed by checkpoint edit to execute
  on the newest pushed P- branch).
- Planner decomposed the bean into 3 sub-intents. Child 1 (`extract-the-pure-ci-verdict`) executed and opened PR #242
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/242). Children 2 and 3 have not run.
- Blocked at Stage 4 (review) on child 1: the review container raised `ConflictResolutionError` because the execution
  branch conflicts with `origin/main` in `flow/__init__.py` (plus ledger rows) after main moved (#235-#240). Stage 4
  does not resolve code conflicts; a hand-merge would bypass the flow, so the run is halted pending a maintainer
  decision.

- 2026-11-23: Child 3 (inject one GitHubAdapter at flow entry) recovered manually on maintainer instruction. Removed 47
  sidecar scratch files committed under todo/ (moved to todo/recovered-0191-sidecar-scratch/), base (parent plan branch)
  already contained, lint plus module budgets green, full suite 5914 passed. Opened PR #255 against the parent plan
  branch (siblings #242, #245 used the same base). Review loop pending.

## Progress note (2026-11-23, parent flow resume)

Split parent resumed from checkpoint without re-running children (children 1 and 2 merged as #242 and #245; child 3
recorded merged as #255 / a9fe10c8, origin wins). Parent Stage 3 integration of plan branch
`I-1795388456-github-adapter-pr-ci-review/P-1795397463-CLA-CO5.5/_` into the parent execution branch failed with merge
conflicts in code files (flow/**init**.py, flow/pipeline.py, tests/flow/helpers.py, docs/git_flow.md,
.agents/holon_flow.md) and ledgers/KB (intents, plans, executions jsonl, kb/failure_modes/index.json). The engine
aborted the merge; worktree is clean, no merge in progress. Plan branch vs origin/main: 40+ conflicting files
(flow/**init**.py, lazy_exports.py, pipeline.py, review/loop.py, stage5.py, launcher/*). Parent PR not opened. Blocked
on a code-conflict decision; needs a higher-tier resolve-conflict subagent (not run). No merge into main performed.

## 2026-11-23 conflict resolution (plan branch vs main, uncommitted)

Merged origin/main into the plan branch in worktree flow-github-adapter-pr-ci-review (local branch plan-merge-0191,
merge left uncommitted). The squashed children carried main content, so apps/ was rebuilt as main plus the bean's own
patch (diff of the plan branch against main's #249 head, applied with 3-way). Ledgers and KB via resolve_known.py; KB
index.json stays deleted; KB entries and the #249 calibration report take main's copy. Lint is clean; the suite passes
except the adapter AST boundary test: main's new flow/github/ci_head_reruns.py spawns `gh run rerun <run-id>` (whole
run) outside adapter.py. Needs a decision: add a whole-run rerun method to the adapter, or allowlist it like
approval_invalidation. Two test fixes were applied (test_conflict_gate carried-approval test moved to FakeGitHub;
test_calibrate_final_head_ci passes a FakeGitHub to _FinalHeadCheck).

2026-11-23 update: the boundary test was resolved by adding GitHubAdapter.rerun_run (whole-run rerun) and routing
gh_run_rerunner through it. Lint and the full suite pass (6354 passed). Merge commit 5f3076dc pushed to the plan branch.
