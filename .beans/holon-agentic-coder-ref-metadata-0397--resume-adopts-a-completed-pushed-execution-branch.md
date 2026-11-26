---
# holon-agentic-coder-ref-metadata-0397
title: "A resume adopts a completed, pushed execution branch instead of executing Stage 3 again"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - resume
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

When a run is killed after its executor finished and pushed, the checkpoint still says `execute` with no execution
branch, and a resume dispatches a new executor. Bean 0387's flow executed Stage 3 four times on 2026-11-24
(`E-1795500528`, `E-1795504454`, `E-1795504981`, `E-1795505480`); only the last was used, and three complete execution
branches remain on origin.

## Goal

- On resume at Stage 3, the engine looks for execution branches of this plan (and the recovery ref
  `refs/holon/recovery/E-*`) that completed: the executor's final commit and ledger row are present. It adopts the
  newest complete one, records the adoption in the checkpoint and goes to Stage 4.
- An incomplete branch is not adopted; the engine says which branches it found and why each was or was not used.
- Superseded execution branches are listed in the flow summary so they can be cleaned up.

## Notes

- Overlap: Bean 0375 (resume ignores an interrupted execution branch with commits but no ledger row) covers the unpushed
  or ledger-less case; this bean covers a completed, pushed branch. Both change the Stage 3 resume lookup, so Bean 0375
  owns the shared branch-adoption code and this bean follows it.
- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Mirrors Bean 0360 (a resume adopts a pushed plan branch).
- Related: Bean 0390 (the ambiguity guard that fired when two branches appeared during one dispatch).
