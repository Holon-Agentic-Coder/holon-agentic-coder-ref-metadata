---
# holon-agentic-coder-ref-metadata-0433
title:
  "Stage 3 in-flight PR discovery fails when an open PR diff exceeds 20,000 lines (HTTP 406 PullRequest.diff too_large)"
status: completed
type: bug
priority: high
tags:
  - flow
  - admission
  - github
  - holon-agentic-coder
created_at: 2026-11-24T18:33:00Z
updated_at: 2026-11-25T05:23:00Z
---

## Problem

During Stage 3 admission, `apps/sandbox-executor/src/sandbox_executor/flow/in_flight.py:125` runs
`gh pr diff <number> --name-only` for every open pull request. Once any open PR crosses GitHub REST API's 20,000-line
diff ceiling, `gh pr diff` fails with `HTTP 406: PullRequest.diff too_large`, and Stage 3 admission fails closed for
every new flow—even when the new flow's touch set is completely disjoint.

## Evidence (2026-11-24T18:31Z)

- Open PR `Holon-Agentic-Coder/holon-agentic-coder#283` (`0376`, `resolve-conflicts-in-flow`, 300 changed files,
  `17,856+ / 1,062-`) crossed the 20,000-line diff limit after Stage 5 calibration/merge.
- `core-helpers-self-doc` (Bean `0153`) completed Stages 1–2 cleanly (`overlap: []` verified independently via local
  3-dot `git diff origin/main...HEAD` and open PR inspection), then Stage 3 refused admission with exit code 1:

  ```text
  Stage 3 refused: the flows in flight could not be discovered: 'gh pr diff 283' failed: could not find pull request diff: HTTP 406: Sorry, the diff exceeded the maximum number of lines (20000) (https://api.github.com/repos/Holon-Agentic-Coder/holon-agentic-coder/pulls/283)
  PullRequest.diff too_large; or rerun with --allow-overlap to admit it anyway.
  ```

- Note also that `gh pr view <number> --json files` (GraphQL) silently truncates at 100 files, whereas the paginated
  REST `/pulls/{number}/files` endpoint returns up to 3,000 changed filenames without hitting the 20,000-line diff
  limit.

## Goal

1. In `in_flight.py`, fetch changed paths via paginated REST `pulls/{number}/files`
   (`gh api --paginate repos/{owner}/{repo}/pulls/{number}/files --jq '.[].filename'`) or fall back to it (and/or local
   3-dot `git diff --name-only origin/<base>...origin/<head>`) whenever `gh pr diff` returns `406` / `too_large`
   (avoiding GraphQL `files` 100-file truncation).
2. Add a hermetic unit test simulating a `406 PullRequest.diff too_large` response from `gh pr diff` and asserting Stage
   3 discovery succeeds and accurately computes overlap.

## Notes

- Target repo change through the Holon flow; wait until `PR #283` merges since both touch `flow/`.

## Audit evidence, 2026-11-25T00:28Z (self-improvement audit, fifth merge)

- Recurred at `2026-11-24T19:32:54Z` on `infra-helpers-self-doc`
  (`Stage 3 refused: the flows in flight could not be discovered: 'gh pr diff 283' failed: HTTP 406`) and again at
  `2026-11-24T23:26:48Z` on `workspace-survival-job-parallel` (also logged separately in companion Bean `0437` when PR
  #283 crossed 300 files). Both should be fixed together in `in_flight.py` via paginated REST `pulls/{number}/files`.

## Audit evidence, 2026-11-25T02:54Z (self-improvement audit, fifth merge)

- Recurred on **every single one of the 9 new flows** launched between `00:28Z` and `02:25Z` (`PR #299` itself, `#300`,
  `#301`, `#302`, `#303`, `#304`, `#305`, `#306`, `#307`) on `gh pr diff 283` HTTP 406 (`>300 files`), forcing `9`
  manual `--allow-overlap` resumes (`0.5–1.1 min` failed admission + `0.8–1.0 min` resume gap each), while
  `workspace-survival-job-parallel` idled `181.5 min` (`23:26:48Z`–`02:28:17Z`) waiting for `#283` to merge. `PR #299`
  (`in-flight-pr-files-fallback`, delivering this fix) reached consensus approval and Stage 5 calibration at `00:49:18Z`
  and awaits maintainer merge.

## Resolution

Delivered via [PR #299](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/299) and merged into `main`
(`599630f8`, `2026-11-25T05:20:56Z`):

- **Deliverables**: Added the HTTP 406 (`too_large`) paginated REST `/pulls/{number}/files` fallback in
  `apps/sandbox-executor/src/sandbox_executor/flow/pr_changed_files.py` and wired it into
  `apps/sandbox-executor/src/sandbox_executor/flow/in_flight.py`, with unit tests in
  `apps/sandbox-executor/tests/flow/test_in_flight.py`.
- **Holon Flow Traversal**: All 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed on
  `I-1795566347-in-flight-pr-files-fallback`.
