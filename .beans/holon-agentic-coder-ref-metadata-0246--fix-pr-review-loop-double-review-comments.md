---
# holon-agentic-coder-ref-metadata-0246
title: "Fix pr-review-loop skill to strictly post consensus review once and prohibit dual-posting via gh pr comment"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - stage-4
  - skills
  - github
  - pr-review-loop
created_at: 2026-11-06T15:00:00Z
updated_at: 2026-11-06T15:00:00Z
---

## Problem

On PR #126, PR #130, and [PR #133](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/133), duplicate
consensus review comments were posted to the GitHub PR timeline:

1. A formal review comment via `gh pr review <pr> --comment --body-file <file>`.
2. A separate issue comment via `gh pr comment <pr> --body-file <file>`.

Both comments contain the exact same markdown consensus report and appear back-to-back in the PR conversation tab within
seconds of each other.

This occurs because:

1. Legacy instructions in earlier iterations specified a "dual-post" pattern (posting to both the review thread and the
   issue timeline).
2. The `pr-review-loop` and `pr-reviewer` skills did not explicitly prohibit calling `gh pr comment` when `gh pr review`
   had already succeeded.
3. The HTTP 422 self-approval fallback (`Can not approve your own pull request`) led some agents to call `gh pr comment`
   in addition to `gh pr review --comment`.

## Goal

1. **Strict Single-Posting Rule in Skills**: In `.agents/skills/pr_review_loop/SKILL.md` and
   `.agents/skills/pr_reviewer/SKILL.md`:
   - State as an absolute invariant: **The consensus review report MUST be posted strictly once to GitHub**.
   - Use exclusively `gh pr review`:
     - `--approve` for consensus approval.
     - `--comment` as the single fallback if `--approve` fails with `Can not approve your own pull request`.
     - `--request-changes` (or `--comment`) if the maximum iteration cap is reached with unresolved issues.
   - Explicitly prohibit running `gh pr comment` to post or dual-post the review body.

2. **Remove All "Dual-Post" Terminology and Instructions**: Purge all references to "dual-post", "dual-posting", or
   parallel `gh pr comment` calls from:
   - `.agents/skills/pr_review_loop/SKILL.md`
   - `.agents/skills/pr_reviewer/SKILL.md`
   - `.agents/prompts/pr_review_prompt.md`

3. **Align with Target Engine (Bean 0236)**: Ensure the harness skill instructions align with
   [Bean 0236](holon-agentic-coder-ref-metadata-0236--post-consensus-review-once-not-duplicate-comment-and-review.md),
   which updates `post_pr_review_consensus()` in `apps/sandbox-executor/src/sandbox_executor/flow.py` to remove
   unconditional `gh pr comment` calls.
