---
# holon-agentic-coder-ref-metadata-0602
title: "Readiness report to the maintainer shows per-head CI state; five PRs were merged with checks still pending"
status: todo
type: task
priority: high
tags:
  - harness
  - pr-merging
  - ci
  - reporting
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T04:33:33Z
---

## Evidence

`gh pr list --state merged` rollups taken at 04:32Z: #395, #397, #399, #400 and #401 show checks still not COMPLETED
(#397: integration, ledger-invariants, unit on both OS, build on macOS, CodeQL Python; #399: 12 jobs; #400: 11 jobs;
#401: macOS unit). They were merged between 04:26Z and 04:31Z, about 10 minutes after their heads were pushed. #373
(named in the brief) now shows all complete, so its pending state at merge time cannot be proven: **not measured**,
because nothing records the CI state at the moment of merge. All ten merged PRs had exactly one review each and none had
a failed check.

`pr-merging.md` already says a PR is ready only when CI is green; the failure is in what is reported. The maintainer
merges, so the readiness message is the only gate between a pending head and main.

## Goal

1. The readiness report for every PR that targets `main` carries one fixed block: head SHA, review verdict on that SHA,
   and the CI table (job, state, conclusion). Any job not COMPLETED/SUCCESS prints the PR as **not ready: CI pending**
   in the first line, never as ready with a footnote.
2. A small harness script (`gh pr checks` and the head SHA) generates the block, so the coordinator pastes it; the same
   script runs in `post-pr-merge` to record the merge-time CI state in the bean resolution.
3. Because CI is a post-review gate (bean 0235), the report says which of the two gates (consensus, pipeline) is
   outstanding.

## Expected gain and cost

Gain: removes the class of merge-on-pending without adding a wait; the merge-time record makes it measurable. Cost: one
script and a paragraph in the readiness checklist.

## Notes

- Source: self-improvement audit 2026-11-27.
- Related: 0235, 0160.
