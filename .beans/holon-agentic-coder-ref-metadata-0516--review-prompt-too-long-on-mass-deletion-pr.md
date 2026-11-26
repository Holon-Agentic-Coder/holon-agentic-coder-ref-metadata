---
# holon-agentic-coder-ref-metadata-0516
title: "Review ensemble fails with 'Prompt is too long' on a pull request that deletes thousands of files"
status: completed
type: bug
priority: high
tags:
  - flow
  - review
  - prompt-size
created_at: 2026-11-26T12:45:00Z
updated_at: 2026-11-26T22:33:03Z
---

## Problem

The flow for bean 0506 (prune-single-flow-kb-failures) executed in 4.4 min and changed 2,923 paths (a script, a test and
about 2,900 deleted `KB-failure-*.json` files). Stage 4 iteration 1 then failed in 1.2 min: all three reviewers
(claude-agent / claude-opus-5-5) exited with code 1, "Prompt is too long". A retry would fail the same way, so the flow
stopped at review (checkpoint kept in the flow-prune-single-flow-kb-failures worktree, PR created).

## Proposed change

- The review request lists a deleted or bulk-mechanical path set as a count plus a sample instead of inlining each path
  and its diff, and caps the diff section by size before it builds the prompt.
- Until then a mechanical deletion of this size is split into PRs of at most a few hundred paths, or the pruning script
  is run by the flow without committing its output.

## Update 2026-11-26 21:01Z: resumed after PR #334 still fails

- Resumed PR #344 from checkpoint (`--from-stage review`) after merging origin/main (merge 375dca35, pushed). Review
  iteration 2 ran in `full` mode ("last reviewed head unknown", since iteration 1 recorded no reviewed head), so the
  reviewers were still given the whole diff, including the mass deletion. The #334 own-diff keying did not help.
- Error, all three reviewers (claude-agent / claude-opus-5-5), 21:01Z, within seconds of dispatch: "Reviewer agent
  command failed with code 1 (stop reason: other). Runner output (redacted): Prompt is too long".
- Reviewer diff at that point (`git diff origin/main...HEAD`): 2,928 files changed, 1,020 insertions, 88,221 deletions,
  3.96 MB of patch text; 2,921 of the paths are deleted `holon-knowledge/kb/failure_modes/KB-failure-*.json`.
- Retry not done. Flow stopped at review; this flow's processes killed; checkpoint kept at stage review; worktree at
  375dca35 with an uncommitted flow-written `holon-knowledge/ledger/pending/executions/I-1795696249-*.jsonl` change.

## Progress 2026-11-27

in-progress: holon flow `flow-review-prompt-mass-deletion` (intent `todo/intent-0516-review-prompt-mass-deletion.json`,
log `todo/flow-review-prompt-mass-deletion.log`, claude-agent / claude-opus-5-5). The fix bounds the reviewers' diff in
`review_request.py` and `delta_review_request.py`: bulk deletions and generated files are summarised by count and
sample, and the inlined diff is capped at 400000 bytes with omitted sections listed by directory. Bean 0506 stays parked
until this lands, then resumes from its checkpoint.

Update 2026-11-27: flow `flow-review-prompt-mass-deletion` completed through Stage 5. PR #352 (head 15f6c660) is OPEN,
MERGEABLE/CLEAN, all CI checks green; Stage 4 consensus 3/3 APPROVED at iteration 1 (no review failures); calibration
report included in the PR diff (EV predicted 41.95, actual 60.70). Left in-progress until the maintainer merges PR #352.
Bean 0506 can resume from its checkpoint after that merge.

## Resolution

Delivered via [PR #352](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/352) and merged into `main`
(`2e28d79e`):

- **Key Architectural Deliverables**: `bound_review_diff` in `review_request.py` runs before any reviewer prompt is
  built, for both the full review and the own-diff delta review (`delta_review_request.py`). Deletions in a directory
  with 25 or more deleted files and generated files (`*.lock`, `package-lock.json`, `*.min.js`, `*.map`) are summarised
  by count and a five-path sample; other sections are inlined in git order until 400000 bytes, and the rest are listed
  by parent directory. A diff needing none of these rules is returned byte-identical.
- **Verification & Tests**: `test_review_request_bulk_diff.py` added; Stage 4 consensus 3/3 APPROVED at iteration 1.
- **Holon Flow Traversal**: Stages 1 to 5 completed in `flow-review-prompt-mass-deletion` (intent, plan, execute, review
  loop, calibration) with no review failures.
