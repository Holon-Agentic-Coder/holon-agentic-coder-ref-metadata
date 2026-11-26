---
# holon-agentic-coder-ref-metadata-0510
title: "Main-push CI re-runs every workflow for merges whose tree the PR head already tested"
status: in-progress
type: task
priority: medium
tags:
  - ci
  - pipeline
  - holon-agentic-coder
created_at: 2026-11-26T10:50:00Z
updated_at: 2026-11-26T10:50:00Z
---

## Problem

Self-improvement audit 2026-11-26T10:50Z. Every merge to `main` runs all seven workflows again. Merges between `09:25Z`
and `10:39Z` ran macOS unit (445 s), ubuntu unit (about 165 s), Workspace survival (about 270 s), integration and stress
each, about 17 runner-minutes of tests per merge, with 0 failures on the main pushes. #329 changed only
`.github/workflows/docker-build.yml` and still ran the full unit suite on two OSes and survival (`09:54Z`: ubuntu 153 s,
macOS 445 s, survival 278 s). The PR heads had already passed the same jobs: 0 failed unit runs on 44 heads of #325,
#326, #327, #329, #330 and #331.

## Proposed fix

- On `push` to `main`, skip the test jobs when the pushed tree equals the tree of the PR head that passed (squash merge
  of an up-to-date branch), and always run them when `main` moved since the last green head (compare
  `git rev-parse <sha>^{tree}`).
- Cheaper alternative: path filters so workflow-only, docs-only and ledger-only merges run hygiene only (extends 0454).

## Expected gain

Up to about 17 runner-minutes and the macOS timing-gate flake exposure per merge; no effect on the PR gate. Risk: an
interaction between two merges is only caught on the next PR, so keep one scheduled full run per day. Related: 0403,
0454, 0461, 0400.

- In progress (2026-11-26): flow main-push-ci-skip-tested-tree (claude-agent, claude-opus-5-5), log
  todo/flow-main-push-ci-skip-tested-tree.log.
