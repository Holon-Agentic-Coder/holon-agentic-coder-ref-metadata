---
# holon-agentic-coder-ref-metadata-0516
title: "Review ensemble fails with 'Prompt is too long' on a pull request that deletes thousands of files"
status: todo
type: bug
priority: high
tags:
  - flow
  - review
  - prompt-size
created_at: 2026-11-26T12:45:00Z
updated_at: 2026-11-26T12:45:00Z
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
