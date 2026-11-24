---
# holon-agentic-coder-ref-metadata-0433
title:
  "Stage 3 in-flight PR discovery fails when an open PR diff exceeds 20,000 lines (HTTP 406 PullRequest.diff too_large)"
status: todo
type: bug
priority: high
tags:
  - flow
  - admission
  - github
  - holon-agentic-coder
created_at: 2026-11-24T18:33:00Z
updated_at: 2026-11-24T18:33:00Z
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
