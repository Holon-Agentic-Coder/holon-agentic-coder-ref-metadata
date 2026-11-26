---
# holon-agentic-coder-ref-metadata-0360
title: "Resume after an interrupted plan stage creates a duplicate P- branch"
status: completed
type: bug
priority: high
tags:
  - flow
  - checkpoint
  - stage-2
  - holon-agentic-coder
created_at: 2026-11-23T00:10:00Z
updated_at: 2026-11-23T14:23:52Z
pr: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/264
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
- 2026-11-23: All 5 Holon flow stages completed on
  [PR #264](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/264) (`MERGEABLE`, `CLEAN`, 11/11 CI green,
  Stage 5 `calibrate` completed with calibration report in PR diff); awaiting human merge (`status: in-progress`).

## Resolution

Delivered via [PR #264](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/264) and merged into `main`
(`f49340f9`):

- **Key Architectural Deliverables**: Stage 2 now records pushed plan branches reliably and `plan` resume detects/adopts
  existing pushed `P-.../_` branches instead of generating duplicate plan branches.
- **Verification & Tests**: Unanimous `APPROVED (3/3)` ensemble consensus review posted (`2026-11-23T13:38:22Z`), all
  `11/11` CI checks passed, and `install_holon.py --holon-only` rebuilt all images and reinstalled `holon` against
  `main` (`f49340f9`).
- **Holon Flow Traversal**: All 5 stages completed cleanly (`antigravity-agent` / `gemini-4-argon` from existing Fable
  plan `P-1795436363-CLA-CF5.2`); Stage 5 calibration
  (`plans/I-1795436346-resume-adopts-pushed-plan-branch/P-1795436363-CLA-CF5.2_calibration.md`, EV predicted `42.34` /
  actual `58.86`, delta `+16.52`, Bug EV Drag `0.00`) included in PR diff.
