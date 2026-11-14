---
# holon-agentic-coder-ref-metadata-0300
title: "CI runs once per change, on the pull request only, not also on push"
status: scrapped
type: bug
priority: medium
tags:
  - ci
  - github-actions
  - token-cost
  - holon-agentic-coder
created_at: 2026-11-14T11:30:00Z
updated_at: 2026-11-14T13:00:00Z
---

## Problem

The maintainer sees duplicate CI pipelines, one triggered by a push and one by the pull request, and wants CI to run for
the pull request only.

## Findings so far (2026-11-14)

- Every workflow under `.github/workflows/` (`make`, `docker-build`, `test-hygiene`, `test-unit`, `test-integration`,
  `test-stress`) triggers on `push` to `main` only, plus `pull_request` and `workflow_dispatch`. No workflow triggers on
  push to other branches.
- The run list for PR #196's branch shows `pull_request` events only, one run per workflow per head, so duplicates were
  not reproduced on a flow branch. The `.github/workflows/README.md` states this is deliberate: a commit on an intent
  branch is checked once, by its pull request, and a push to `main` once, by `push`.
- The remaining push runs are the ones on `main` after a merge. The timing gate runs in `record` mode on a push to
  `main` and writes the baselines that every pull request compares against, so removing `push` outright would stop the
  baselines from updating.

## Confirmed (2026-11-14)

`Docker Build / build (push)` runs only on `main` (latest push runs `e556a0c`, `721cd36`, 12:26 and 12:28 UTC), so it
shows beside the merged pull request's `build (pull_request)` check on the merge commit. Maintainer decision: CI runs
for the pull request only, so the `push` trigger goes from every workflow. The timing baselines on `main` must then be
recorded another way, for example `pull_request: closed` with `merged == true` into `main`, or a scheduled job.

## Scope

1. Drop the `push` trigger from every workflow (reproduced: see Confirmed).
2. Record the timing baselines on `main` another way, as above.
3. Change the workflows and `.github/workflows/README.md`, keeping the timing gate's `main` baselines working.
4. A workflow lint that fails if any workflow regains a `push` trigger.

## Notes

Run through the Holon flow on holon-agentic-coder. Related: the all-branch CI for stacked PRs (PR #153) and the CI
timing gate (PRs #109, #114).

## Resolution

Scrapped by the maintainer on 2026-11-14: there is no duplicate. `build (push)` runs only on `main`, after a merge, and
`build (pull_request)` runs on the pull request before it, so each change is tested once before the merge and once as
the commit that lands. The push run on `main` also records the timing baselines, so the `push` trigger stays.
