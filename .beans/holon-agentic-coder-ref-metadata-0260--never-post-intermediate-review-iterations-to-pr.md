---
# holon-agentic-coder-ref-metadata-0260
title: "Never post intermediate review iterations or aborted review passes to GitHub PR"
status: todo
type: bug
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - github
  - holon-agentic-coder
created_at: 2026-11-09T07:41:00Z
updated_at: 2026-11-09T07:41:00Z
---

## Problem

In `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py` (`_run_review_loop_iterations`, around line 765):

```python
    # Dual-post review consensus to GitHub and handle self-approval restriction
    posting_res: dict[str, Any] = {}
    post_error: str | None = None
    if effective_dry_run or skip_post:
        suppressed_ledger_records += 1
    elif pr_refusal_error or infra_error:
        context.log(f"[Review Loop] Not posting a review consensus for '{review_target}': the review failed.")
    elif not any(result.status is ReviewerStatus.COMPLETED for result in reviewers):
        context.log(f"[Review Loop] Not posting a review consensus for '{review_target}': no reviewer completed.")
    else:
        posting_res = post_pr_review_consensus(...)
```

When an individual reviewer turn crashes, times out, or stalls (for example, `Reviewer 3` in PR #151 encountering
`root agent idle; waiting for 1 background task(s) to finish`), `decide_consensus()` evaluates the ensemble verdict as
`ConsensusVerdict.FAILED`.

In `loop.py` (lines 582–587):

```python
if ensemble_verdict is not ConsensusVerdict.CHANGES_REQUESTED:
    context.log(f"[Review Loop] Halting review loop at iteration {iteration}: verdict {ensemble_verdict or ConsensusVerdict.FAILED}.")
    break
```

This causes the review loop to break immediately. Because some reviewers completed (e.g. 2 out of 3), `loop.py` executes
`post_pr_review_consensus()`, posting a failed iteration report to GitHub PR! When the outer orchestrator subagent
catches the failure and resumes from checkpoint, the next iteration also posts its comment, polluting the PR with noise
and intermediate failure reports.

This violates `AGENTS.md` Invariant 11:

> _"Intermediate review iterations stay local in `.subagent/` — never post premature review comments to GitHub until all
> findings are fully resolved or consensus approved."_

## Decision

Review consensus posting to GitHub PR must be reserved strictly for the terminal conclusion of Stage 4:

1. **Only Post on Consensus Approval or Budget Exhaustion**:
   - `post_pr_review_consensus()` must never post intermediate iterations or aborted runs.
   - It should post to GitHub PR **only if**:
     - `consensus_reached is True` (unanimous consensus approval achieved), OR
     - `iteration >= last_label` (the review iteration budget has been completely exhausted).
2. **Transient Failures Stay Local**:
   - If an iteration halts due to `ConsensusVerdict.FAILED`, infrastructure error, or transient reviewer timeout/crash,
     log the failure locally and record it in `executions.jsonl`, but **do not post anything to GitHub**.
   - Resuming `holon flow` from checkpoint should not leave behind orphaned, misleading review comments on the PR.
3. **Tests**:
   - Add hermetic pytest unit tests in `apps/sandbox-executor/tests/flow/test_loop.py` asserting that:
     - An iteration with a failed reviewer turn does not call `post_pr_review_consensus`.
     - An aborted loop does not post to GitHub PR.
     - Only `APPROVED` or final exhausted iterations invoke posting.

## Scope

- `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py`
- `apps/sandbox-executor/tests/flow/test_loop.py`
