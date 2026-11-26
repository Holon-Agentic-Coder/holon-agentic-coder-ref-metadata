---
# holon-agentic-coder-ref-metadata-0426
title: "Fix run_holon_flow slug truncation, bean-progress truncated-slug attribution, and subagent intent rewrites"
status: todo
type: bug
priority: high
tags:
  - harness
  - holon-flow
  - bean-progress
  - attribution
created_at: 2026-11-24T13:00:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Why

During the `2026-11-24T11:05Z–12:47Z` fifth-merge audit window, three interacting harness defects broke bean
attribution, completion notifications, and worktree hygiene across `run_holon_flow.py`, `bean_progress.py`, and
`holon-flow` subagents:

1. **Uncommitted slug truncation & hardcoded `0380` hack in `.agents/skills/holon_flow/scripts/run_holon_flow.py`**:
   - Lines 184–189 and 495–510 truncate `slug` > 32 chars and write `todo/intent-modified-<truncated_slug>.json`
     (stripping the `<bean-id>` from the filename!). For Bean `0380`
     (`todo/intent-0380-coherence-module-line-budget-all-packages.json`, 41-char slug), this launched
     `holon-coherence#55` on branch `I-1795521016-coherence-module-line-budget-all/...` while leaving
     `todo/intent-modified-coherence-module-line-budget-all.json` in `todo/`.
   - Lines 501–504 hardcode a one-off Bean `0380` mutation
     (`if "0380" in intent_path.name ...: intent_data["module_budget_change"] = ...`) inside the shared flow wrapper.
   - Line 754 in `main()` calls `parse_intent_file(args.intent)["slug"]` (untruncated) when passing `slug` to
     `_notify_outcome`, so `_calibration_done` and `find_flow_pr` fail to match the checkpoint or PR whenever slug
     truncation ran.
2. **Broken truncated-slug attribution in `.agents/skills/bean_progress/scripts/bean_progress.py`**:
   - `INTENT_FILE_RE` (`^intent-((?:\d{4}-)+)(.+)\.json$`) ignores `intent-modified-*` and `intent-truncated-*` files,
     and `build_in_flight_rows` indexes only `intent.slug` and `intent.file_slug` — not the 32-char truncated slug used
     on the git branch (`coherence-module-line-budget-all`). As a result `holon-coherence#55` rendered with `Bean # = —`
     in `bean_progress` output.
3. **`flash_lite` subagents rewriting/copying `todo/intent-*.json` files**:
   - `todo/intent-0393-preflight-ok-reply-slow-exit-and-retry.json` (38-char slug) was overwritten in place with
     `"slug": "preflight-retry"` after an initial attempt created
     `apps/holon-agentic-coder/flow-preflight-ok-reply-slow-exit-and-retry`, then launched a second worktree
     `flow-intent-0393-preflight-retry` (with `intent-0393-` in the worktree name) that delivered
     `holon-agentic-coder#274`, leaving `bean_progress` reporting a stale Stage 1 attempt.
   - `todo/intent-truncated-coherence-module-line-budget-all.json` was also left behind as an unattributed copy.

## Proposed change

1. Remove the hardcoded `"0380"` injection from `run_holon_flow.py`; validate `len(slug) <= 32` cleanly or preserve
   `<bean-id>` in any derived intent filename, and pass the effective (truncated) `slug` to `resolve_flow_worktree`,
   `verify_pr_and_calibration`, and `_notify_outcome` in `main()`.
2. In `bean_progress.py` (`scan_intents` / `build_in_flight_rows`), index `truncate_slug(intent.slug, 32)` and
   `truncate_slug(intent.file_slug, 32)` alongside the full slug so truncated flow branches and PRs always attribute to
   their bean ID.
3. Update `.agents/skills/holon_flow/SKILL.md` to forbid `holon-flow` subagents from editing, copying, or rewriting
   `todo/intent-*.json` files or adding `intent-<id>-` prefixes to `flow-<slug>` worktree names.
4. Add regression tests in `tests/test_bean_progress.py` and `tests/test_flow_fallback.py`.

## Expected gain

Eliminates `Bean # = —` misattribution on truncated-slug PRs (like `holon-coherence#55`), ensures `ntfy` completion
notifications work on truncated slugs, removes one-off bean hacks from `run_holon_flow.py`, and stops `flash_lite`
subagents from creating duplicate/stale worktrees and mutated intent files.

## Cost

Small harness-only change in `.agents/skills/holon_flow/scripts/run_holon_flow.py`,
`.agents/skills/bean_progress/scripts/bean_progress.py`, `.agents/skills/holon_flow/SKILL.md`, and `tests/`.
