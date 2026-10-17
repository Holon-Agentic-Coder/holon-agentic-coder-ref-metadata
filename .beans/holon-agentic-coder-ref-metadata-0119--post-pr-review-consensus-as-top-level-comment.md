---
# holon-agentic-coder-ref-metadata-0119
title: "Post PR review consensus as top-level discussion comment and handle author self-review restrictions"
status: completed
type: task
priority: normal
tags:
  - pr-review-loop
  - holon-flow
  - cli
  - github
  - devex
  - holon-agentic-coder
created_at: 2026-10-17T11:00:00Z
updated_at: 2026-10-17T14:00:00Z
---

## Summary

In both the `pr-review-loop` agent skill and the native `holon review-loop` CLI engine (Bean 0118), ensure the final
consensus review summary is always posted as a top-level Pull Request discussion comment
(`gh pr comment <pr> --body "..."`) in addition to submitting the Pull Request Review object (`gh pr review`). This
guarantees the consensus report is immediately visible in the main PR conversation tab and external notifications,
bypassing GitHub's restriction against PR authors approving their own PRs.

## Context & Problem Statement

When the multi-agent consensus review passes unanimously, the current implementation attempts to submit the review via:

```bash
gh pr review <pr> --approve --body "<consensus_report>"
```

However, two operational issues occur in practice:

1. **GitHub Author Self-Approval Restriction**:
   - If the agent runs with credentials matching the PR author (e.g. `thomashan`), the GitHub API rejects `--approve`
     with:
     ```text
     HTTP 422: Unprocessable Entity - Can not approve your own pull request
     ```
   - The CLI/skill falls back to `--comment` (`state: "COMMENTED"`), meaning GitHub never renders the green approval
     checkmark or updates `reviewDecision`.

2. **Invisibility in Main Conversation Feed**:
   - Submitting via `gh pr review --comment` posts to `/repos/:owner/:repo/pulls/:number/reviews` rather than
     `/repos/:owner/:repo/issues/:number/comments`.
   - On GitHub, a review without line-level diff comments is collapsed into an activity timeline item ("_user left a
     review_") and the PR conversation comments count remains **0**.
   - As a result, maintainers checking the PR conversation or receiving email/Slack webhooks do not see the consensus
     table and verification matrix unless they expand review activities.

## Proposed Solution

1. **Dual-Post Pattern**:
   - Always post the consensus summary markdown as a top-level PR conversation comment via:
     ```bash
     gh pr comment <pr> --body "<consensus_report>"
     ```
   - This ensures 100% visibility in the main PR conversation timeline and increments the comment counter.

2. **Graceful PR Review Submission**:
   - Attempt `gh pr review <pr> --approve --body "<summary>"`.
   - If rejected with "Can not approve your own pull request" (or author == viewer), catch the error gracefully, log an
     informative notice, and submit with `--comment` so the official review record is still registered.

3. **Port Across Harness and Native CLI**:
   - Update `.agents/skills/pr_review_loop/` orchestrator scripts.
   - Update `sandbox_executor/flow.py` (`run_review_loop` and helper `post_consensus_review`).

## Tasks & Scope

- [x] Audit `sandbox_executor/flow.py` review loop GitHub posting logic.
- [x] Implement dual-posting (`gh pr comment` for conversation visibility + `gh pr review` for review state).
- [x] Add explicit detection/handling for the PR author self-review restriction.
- [x] Update `.agents/skills/pr_review_loop/` to match.
- [x] Add unit tests in `apps/sandbox-executor/tests/test_flow.py` asserting `gh pr comment` invocation on consensus.
- [x] Route `holon-agentic-coder` changes through the 5-stage Holon flow.

## Resolution

Implemented via 5-stage Holon flow on `holon-agentic-coder` in PR
[#82](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/82).

- Added `post_pr_review_consensus` in `sandbox_executor/flow.py` implementing the dual-posting pattern: top-level
  discussion comment via `gh pr comment` plus official review submission via `gh pr review`.
- Handles HTTP 422 author self-approval restriction by gracefully falling back to `--comment`.
- Added timeout guards (`timeout=60`) on all subprocess calls and hermetic unit tests in `test_flow.py`.
- 3-agent ensemble consensus approved (0 Critical, 0 Important, 0 Nit). Calibration executed and included in PR.
