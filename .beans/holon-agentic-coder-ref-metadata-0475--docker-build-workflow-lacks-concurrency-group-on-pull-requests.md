---
# holon-agentic-coder-ref-metadata-0475
title: "Docker Build workflow lacks a concurrency group and completes on every cancelled PR head"
status: completed
type: bug
priority: high
tags:
  - ci
  - pipeline
  - github-actions
  - performance
  - holon-agentic-coder
created_at: 2026-11-26T03:50:00Z
updated_at: 2026-11-26T10:12:00Z
---

# Docker Build workflow lacks a concurrency group and completes on every cancelled PR head

## Problem

Five of the six core `holon-agentic-coder` CI workflows (`.github/workflows/test-unit.yml`, `test-stress.yml`,
`test-hygiene.yml`, `test-integration.yml`, `make.yml`) declare a `concurrency` stanza with
`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`. `.github/workflows/docker-build.yml` declares no
`concurrency` block at all.

Whenever a Stage 4 resolver commit or target-sync merge is superseded 10–20 s later by a `chore(review)` ledger push
(Bean `0443`) or another push on a pull request branch, the five test/lint workflows cancel the superseded head
immediately, whereas `Docker Build` runs to completion (`success`) on the stale SHA, burning Ubuntu runner minutes on a
head that can never merge.

## Evidence (2026-11-26T03:50Z fifth-merge audit, 5 h window `2026-11-25T22:49:00Z..2026-11-26T03:50:09Z`)

- Across `48` distinct `holon-agentic-coder` SHAs in the window (`298` workflow runs total), **`26` SHAs** had their
  five test/lint workflows cancelled as superseded (`median 1.82 min` wall).
- **`Docker Build` ran to `success` on all `26` of those `26` cancelled SHAs** (`median 1.78 min`, `max 2.23 min`),
  wasting **`2,396.0 s` (`39.93 runner-min`)** on commits already superseded (e.g., `PR #310` `e8fc7e43`, `0a9cbc98`,
  `02c1d8e7`, `8dc91384`, `366ade8c`, `e311727d`, `ac5d2056`; `PR #311` `bac5dd73`, `feafb760`, `40c9d4ad`; `PR #312`
  `f04266bf`, `4c8d25a5`; `PR #313` `937eef73`, `0c8fa6c7`; `PR #314` `6248e983`; `PR #308` `55df1efb`, `5a813110`).

## Proposed Change

1. Add a `concurrency` block to `.github/workflows/docker-build.yml` that cancels superseded `pull_request` heads while
   keeping every `push` to `main` commit distinct (avoiding Bean `0461`'s `main`-push eviction bug):
   ```yaml
   concurrency:
     group:
       ${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.head_ref || format('{0}-{1}',
       github.ref, github.sha) }}
     cancel-in-progress: ${{ github.event_name == 'pull_request' }}
   ```
2. Update `.github/workflows/README.md` or workflow trigger tests if concurrency coverage requires it.

## Expected Gain

Eliminates `~40 runner-minutes` per 5-hour window (`26` cancelled heads in this window) and removes unnecessary
`Docker Build` queue contention on GitHub-hosted runners.

## Cost

Small: 4-line `concurrency` block in `.github/workflows/docker-build.yml` (+ test/doc check) via `holon flow`
(`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0461` (`main`-push concurrency across the other 5 workflows), Bean `0443` (Stage 4 double-push race).

## Progress

- 2026-11-26: in-progress. Flow `flow-docker-build-concurrency-group` launched from
  `todo/intent-0475-docker-build-concurrency-group.json` (claude-agent, claude-opus-5-5); scope is
  `.github/workflows/docker-build.yml` only, disjoint from the live flows.

## Resolution

Delivered via [PR #329](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/329) and merged into `main`
(`883a5d6`):

- **Key Architectural Deliverables**: top-level `concurrency` block added to `.github/workflows/docker-build.yml`. Pull
  request runs group by workflow and head branch and cancel in progress; push and `workflow_dispatch` runs group by
  workflow, ref and SHA and are never cancelled (main-push eviction avoided, per bean 0461). The diff touches that one
  workflow file only.
- **Verification & Tests**: affected tests, lint, prettier and the full suite passed in the flow's execution record.
  Live cancellation was not observable at merge time, so it is verified by construction, not by a live run.
- **Holon Flow Traversal**: intent, plan, execution and calibration artifacts were all committed for
  `I-1795685858-docker-build-concurrency-group`. The bean's optional README or trigger-test update was not needed.
- **Post-merge**: flow worktree and its `I-1795685858-docker-build-concurrency-group` branches removed locally and on
  origin. No install-holon run was needed (workflow-only change).
- 2026-11-26 10:10Z: flow `flow-docker-build-concurrency-group` completed. PR #329 (`.github/workflows/docker-build.yml`
  only) was approved 3/3 at review, calibration report included (EV 37.57, final head CI success) and the PR reached
  MERGEABLE/CLEAN. The maintainer (thomashan) merged PR #329 at 09:54Z while the flow was in calibration. Post-merge
  closure (bean to completed, worktree and branch prune) is pending via the post-pr-merge skill.
- Bug logged: bean 0504 (run log stays empty while the flow runs).
