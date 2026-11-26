---
# holon-agentic-coder-ref-metadata-0463
title: "Stage 2 planner collapses file-scoped intents into directory touch-set entries that broaden Stage 3 overlap"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-2
  - planner
  - stage-3
  - admission
  - holon-agentic-coder
created_at: 2026-11-25T06:05:00Z
updated_at: 2026-11-25T06:05:00Z
---

# Stage 2 planner collapses file-scoped intents into directory touch-set entries that broaden Stage 3 overlap

## Problem

Even when an input `intent.json` explicitly lists concrete file paths in `scope` (and zero directories), Stage 2
(`planner.py` + `planner.template.md`) frequently collapses those files into a broad trailing-`/` directory entry in
`## Touch Set`:

- `apps/holon-agentic-coder/main/holon-config/prompts/planner.template.md:109-113` explicitly invites directory globs
  (`one backticked repository-relative path or glob per top-level bullet (a trailing '/' means a whole directory, '*' stays within one path segment and '**' spans directories)`).
- `apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/entrypoint/planner.py:302-307` only prints
  an stderr
  `Warning: the touch set has folder or wildcard entries (...); they match every existing file below them at Stage 3 admission, so prefer module paths.`
  after creating and committing the plan branch.

At Stage 3 admission, any folder entry matches **every** existing file beneath that directory across all open PRs and
active flows, artificially magnifying admission blocking (distinct from Bean `0459`, which validates `intent.json`
`scope` before Stage 1, and Bean `0446`, which covers `SPLIT` parent admission before decomposition).

## Evidence (2026-11-25T06:05Z audit, Bean 0371 flow)

- **`0371` (`ledger-fragments-and-promotion`):** `todo/intent-0371-ledger-fragments-and-promotion.json:7-27` carefully
  specified **19 concrete file paths** (`fragments.py`, `promote.py`, `rows.py`, `query.py`, `order.py`, `__init__.py`,
  etc.) and **0 directories**.
- Despite this, the Stage 2 planner emitted `- apps/sandbox-executor/src/sandbox_executor/ledger/` on line `197` of
  `plans/I-1795584436-ledger-fragments-and-promotion/P-1795584464-CLA-CO5.5.md`, triggering the non-fatal stderr warning
  in `todo/flow-ledger-fragments-and-promotion.log:47`
  (`Warning: the touch set has folder or wildcard entries (apps/sandbox-executor/src/sandbox_executor/ledger/); they match every existing file below them at Stage 3 admission, so prefer module paths.`)
  and widening the plan's touch set across the entire `ledger/` package (`git_refs.py` overlap with `#305` came from the
  broader module list, while any folder collapse blocks unrelated siblings under `ledger/` like `sync.py` or future
  flows).

## Proposed Change

1. Update `holon-config/prompts/planner.template.md:109-113` to prohibit collapsing concrete paths into trailing-`/`
   directories or wildcards (`*`, `**`) whenever concrete module/file paths exist (and explicitly when the intent
   `scope` lists files).
2. In `apps/sandbox-executor/src/sandbox_executor/entrypoint/planner.py` (or touch-set validation helper), either:
   - fail Stage 2 plan validation (`_fail_plan_attempt`, triggering a prompt retry/correction turn within Stage 2) when
     `broad_entries(touch_set)` is non-empty for a concrete-file intent scope, OR
   - cleanly disallow directory/glob wildcards unless explicitly justified and bounded, matching `0459`'s wrapper guard
     on `intent.json` `scope`.
3. Add unit tests verifying Stage 2 rejects or expands collapsed directory touch-set entries produced from file-scoped
   intents.

## Expected Gain

Prevents Stage 2 from silently undoing careful file-level touch scoping in `intent.json`, eliminating avoidable
false-positive Stage 3 overlap blocking across unrelated files inside shared packages (`sandbox_executor/flow/`,
`ledger/`, `calibration/`, `tests/`).

## Cost

Small: prompt rule + Stage 2 `broad_entries` enforcement/retry check in `entrypoint/planner.py` + unit tests via
`holon flow` (`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0459` (wrapper rejects directory entries in `intent.json` `scope`), Bean `0446` (`SPLIT` parent plans
  blocked before decomposition), Bean `0371`.
