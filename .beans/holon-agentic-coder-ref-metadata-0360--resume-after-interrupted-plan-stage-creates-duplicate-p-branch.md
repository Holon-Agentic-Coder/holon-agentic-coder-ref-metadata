---
# holon-agentic-coder-ref-metadata-0360
title: "Resume after an interrupted plan stage creates a duplicate P- branch"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - checkpoint
  - stage-2
  - holon-agentic-coder
created_at: 2026-11-23T00:10:00Z
updated_at: 2026-11-23T12:20:00Z
---

## Problem

When `holon flow` is killed after Stage 2 has pushed its `P-.../_` branch but before the checkpoint advances past
`plan`, resuming with `--from-stage plan --checkpoint <path>` runs planning again. That creates a second `P-.../_`
branch under the same intent, and the plan stage then refuses with "ambiguous P-branches". Seen on 2026-11-23 for the
`resume-flags-override-checkpoint` flow (PR #239): the stale plan branch `P-1795388515` remains on origin, and the flow
only continued after a hand edit of the checkpoint (advance to `execute` with `plan_branch` set to the newer
`P-1795390638`).

## Goal

Stage 2 records its pushed plan branch in the checkpoint atomically with the push, or a resume from `plan` detects an
existing pushed plan branch for the intent and adopts it instead of planning again. No duplicate P- branch, and no hand
edit of the checkpoint.

## Notes

- About a dozen flows were stopped mid Stage 2 on 2026-11-23 (machine load), so each resume may hit this.
