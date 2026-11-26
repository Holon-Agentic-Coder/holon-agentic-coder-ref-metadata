---
# holon-agentic-coder-ref-metadata-0514
title: "Main-push tree gate skips nothing when merges arrive back to back; coalesce a burst to the newest tip"
status: todo
type: task
priority: normal
tags:
  - ci
  - pipeline
  - holon-agentic-coder
created_at: 2026-11-26T12:20:00Z
updated_at: 2026-11-26T12:20:00Z
---

## Evidence

Self-improvement audit 2026-11-26T12:20Z, question (1).

- #333 (per-SHA concurrency, merged 10:51Z): in order. No cancelled run on `main` after it; the last cancellations are
  `903aafe` (08:47Z) and five on 11-25. Every main push since ran unit, survival, integration and stress to success (9
  pushes, 0 failures).
- #337 (skip tested tree, merged 12:06Z): one main push has run since it landed, `5440e92` (#338). The gate logged
  `decision=RUN rule=main-push-tree-mismatch detail=pushed tree 2c7c301d0741, head tree 6bee257e74e8`, so survival (207
  s) and both unit legs ran in full. `762642a` (#337 itself) has no run at all because GitHub fires one push event for
  the two commits merged together.
- Cause: #339, #335, #338 and #337 merged at 12:04:42, 12:05:00 and 12:06:00 (twice). Each PR head had been tested on
  the base it was cut from; once the previous merge lands, the pushed tree can never equal the head tree. Three full CI
  sets started in 2 minutes (`f0d6c56`, `8ef1bfb`, `5440e92`): macOS unit 292 s, 425 s and still running, survival 291,
  269 and 207 s, ubuntu unit 156, 122 and 162 s, about 25 runner-minutes for trees that are each a superset of the
  previous one.

So the gate helps for an isolated merge and does nothing for a burst, which is how the maintainer merges (4 PRs in 80 s
here).

## Proposed fix

- A push whose commit is no longer the tip of `main` when the job starts (`git ls-remote origin main`) records a skip
  with rule `main-push-superseded` and relies on the newest tip's run, which tests a superset tree. Only the tip of a
  burst runs the full suite.
- Keep the daily scheduled full run. If the tip run fails, the failing merge is found by the existing per-PR green heads
  plus a bisect job, which this bean does not build.
- Log the rule and the skipped/ran count per day in the workflow summary so the saving is measured (relates to 0509).

## Expected gain

A burst of N merges costs one run instead of N: about 17 runner-minutes saved per extra merge (0510 figures). Cost:
attribution of a red tip to one of N merges needs a bisect; mitigated because PR heads were already green.

## Notes

Related: 0510 (completed, the exact-tree rule), 0461 (per-SHA concurrency, deliberately keeps every push), 0403, 0454.
The 0461 reason (never evict a pending push) is kept by skipping, not cancelling.
