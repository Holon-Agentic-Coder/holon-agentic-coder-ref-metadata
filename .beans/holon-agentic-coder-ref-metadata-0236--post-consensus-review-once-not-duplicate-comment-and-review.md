---
# holon-agentic-coder-ref-metadata-0236
title: "Post consensus review once per PR exit instead of duplicating via both gh pr comment and gh pr review"
status: completed
type: bug
priority: high
tags:
  - review-loop
  - stage-4
  - github
  - holon-agentic-coder
  - skills
created_at: 2026-11-06T00:12:00Z
updated_at: 2026-11-08T08:45:00Z
---

## Problem

On [PR #126](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/126), Stage 4 posted the exact same
`## ✅ Ensemble Consensus Review — APPROVED (3/3)` markdown body **twice** in the PR conversation timeline (5 seconds
apart):

1. `issuecomment-6672822852` (`2026-11-06T00:03:18Z`) via `gh pr comment <target> --body <report_text>`
2. `PRR_kwDORMmd1c8AAAABWVeR2A` (`2026-11-06T00:03:23Z`) via `gh pr review <target> --comment --body <report_text>`
   (triggered by the HTTP 422 self-approval fallback when `--approve` is rejected because the authenticated user is the
   PR author).

Because GitHub renders a `gh pr review` body directly in the PR Conversation timeline, executing both `gh pr comment`
and `gh pr review` with the full report body always produces two identical back-to-back posts on the PR.

## Decision

Post the consensus review report **exactly once** to the PR:

1. **Primary Submission (`gh pr review`)**:
   - When approved: run `gh pr review <target> --approve --body <report_text>`.
   - When changes requested (at budget exhaustion): run `gh pr review <target> --request-changes --body <report_text>`
     (or `--comment`).
2. **Self-Author Fallback (HTTP 422)**:
   - If GitHub rejects `--approve` or `--request-changes` with HTTP 422 (`Can not approve your own pull request` /
     `Can not request changes on your own pull request` / `PullRequestReviewAuthorError`), fall back to posting **one**
     review comment (`gh pr review <target> --comment --body <report_text>`), **not** both `gh pr comment` and
     `gh pr review --comment`.
3. **Retire Unconditional Dual-Posting**:
   - Remove the redundant unconditional `gh pr comment` step from `post_pr_review_consensus()` in
     `apps/sandbox-executor/src/sandbox_executor/flow.py` and from the harness skills
     (`.agents/skills/pr_reviewer/SKILL.md` and `.agents/skills/pr_review_loop/SKILL.md`).

## Scope

1. **Target (`holon-agentic-coder`)**:
   - Update `post_pr_review_consensus()` in `apps/sandbox-executor/src/sandbox_executor/flow.py` so it submits the
     consensus report once via `gh pr review` (with `--comment` fallback on HTTP 422 self-review restriction), rather
     than calling both `gh pr comment` and `gh pr review`.
   - Update unit tests in `apps/sandbox-executor/tests/test_flow.py` and `test_review_loop.py` to assert single posting
     (1 `gh` call when `--approve` succeeds; 2 `gh` calls total when `--approve` returns HTTP 422 and falls back to
     `--comment`, resulting in 1 posted review on GitHub).
2. **Harness Skills (`holon-agentic-coder-ref-metadata`)**:
   - Update `.agents/skills/pr_reviewer/SKILL.md` and `.agents/skills/pr_review_loop/SKILL.md` to post once via
     `gh pr review` (with `--comment` fallback on HTTP 422) rather than dual-posting.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow (`holon flow`).
- Supersedes the dual-posting requirement of Bean 0119.

## Resolution

Delivered via [PR #139](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/139) and merged into `main`
(`d0c1334`, 2026-11-08T08:34:14Z):

- **Key Architectural Deliverables**: `post_pr_review_consensus()` in
  `apps/sandbox-executor/src/sandbox_executor/flow.py` now submits the consensus report exactly once via
  `gh pr review --approve` (or `--request-changes`), falling back to a single `gh pr review --comment` on the HTTP 422
  self-review restriction; the unconditional duplicate `gh pr comment` step is retired. Harness skills
  (`.agents/skills/pr_reviewer/SKILL.md`, `.agents/skills/pr_review_loop/SKILL.md`) already post once — no
  `gh pr comment` dual-posting remains. Supersedes the dual-posting requirement of Bean 0119.
- **Verification & Tests**: Unit tests updated to assert single posting (1 `gh` call on successful `--approve`; 2 `gh`
  calls total on 422 fallback, yielding 1 posted review). All 15 CI checks passed; PR was MERGEABLE/CLEAN.
- **Holon Flow Traversal**: All 5 stages completed on claude-agent / claude-fable-5 (no model fallback). 3/3 ensemble
  consensus APPROVED on iteration 1 with zero findings. Stage 5 calibration included in the PR diff
  (`plans/P-1794124844-claude-agent-claude-fable-5_calibration.md`, EV predicted 50.76 vs actual 61.13, ΔEV +10.37).
