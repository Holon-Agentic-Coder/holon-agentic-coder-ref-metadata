---
# holon-agentic-coder-ref-metadata-0462
title: "Epoch-second stage and plan IDs collide across concurrent flows"
status: todo
type: bug
priority: normal
tags:
  - flow
  - architecture
  - ledgers
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-25T06:05:00Z
updated_at: 2026-11-25T06:05:00Z
---

# Epoch-second stage and plan IDs collide across concurrent flows

## Problem

Multiple ID generators in `apps/sandbox-executor/src/sandbox_executor/` still derive IDs purely from `int(time.time())`
without a per-flow disambiguator (despite Bean `0278` fixing `build_review_id` and adding `build_stage_disambiguator` in
`ledger/rows.py:116-119`):

1. **Intent ID / branch (`entrypoint/intent_creator.py:86`):**
   `resolve_root_intent_branch(intent_data, slug_clean, int(time.time()), "", "")` embeds the same `I-<epoch>` prefix
   across two concurrent flows launched in the same second (`I-1795584436-ledger-fragments-and-promotion` and
   `I-1795584436-calibration-merge-adapted-file`; earlier `#300` & `#302` shared `I-1795567884-*`).
2. **Plan ID (`entrypoint/planner.py:348`, `ledger/rows.py:122-131`):** `plan_seq = int(time.time())` builds
   `P-<epoch>-<AGENT>-<MODEL>` checked only against `taken_plan_ids` _within `intent_branch_prefix`_. Because two
   concurrent flows with different slugs check disjoint branch prefixes, if Stage 1 finishes in the same second (both
   take `~15-20 s` -> Stage 2 starts in the same second), they mint the exact same globally non-unique `plan_id` in
   `holon-knowledge/ledger/plans.jsonl`.
3. **Review iteration and Stage 5 calibration IDs (`flow/review/loop.py:463`, `calibration.py:1316`):** `execution_id`
   still uses bare `f"REV-ITR-{iteration}-{int(time.time())}"` and `f"CAL-{plan_id}-{int(time.time())}"` without hex
   disambiguation, inheriting any `plan_id` collision or same-second completion across concurrent flows.

## Evidence (2026-11-25T06:05Z audit, live & main ledger)

- **`main` `holon-knowledge/ledger/plans.jsonl`:** contains **5 duplicate `plan_id` values** (`P-1795154100-CLA-CO5.5`
  x2, `P-1795167432-CLA-CO5.5` x3, `P-1795184234-CLA-CO5.5` x2, `P-1795246947-CLA-CO5.5` x2, `P-1795567904-ANA-G4N` x2).
  In particular, `#300` (`decomposition-rule-self-doc`, Stage 1 `00:51:32Z`, plan `00:54:24Z`) and `#302`
  (`review-report-self-doc`, Stage 1 `00:51:32Z`, plan `00:54:26Z`) both minted `I-1795567884-*` and the identical
  `plan_id` `P-1795567904-ANA-G4N`, merging duplicate `plan_id` rows into `main`.
- **Concurrent active flows (`0371` & `0438`/`#309` at `05:27:16Z`):** both started in the same second
  (`todo/flow-ledger-fragments-and-promotion.log:14`, `checkpoint-calibration-merge-adapted-file.json:846`), both
  received `I-1795584436-*`, and both Stage 2 planners minted the identical **`P-1795584464-CLA-CO5.5`**
  (`todo/flow-ledger-fragments-and-promotion.log:57`, `checkpoint-calibration-merge-adapted-file.json:99`), so
  `calibration_predicted` / `calibration` ledger lookups and `CAL-P-1795584464-CLA-CO5.5-...` labels collide.

## Proposed Change

1. Include a short disambiguator (reusing `build_stage_disambiguator` or short hash of `slug`/intent/worktree) in root
   `intent_id` / `plan_id` (`build_plan_id`, keeping branch segment within `ensure_stage_segment_fits`), `execution_id`
   (`REV-ITR-...` in `flow/review/loop.py:463`), and `CAL-...` (`calibration.py:1316`).
2. Add regression tests verifying two same-second calls with different slugs/branches produce globally distinct
   `intent_id`, `plan_id`, `REV-ITR-*`, and `CAL-*` IDs while preserving branch-length limits and existing row schemas.

## Expected Gain

Eliminates duplicate `plan_id`, `CAL-...`, and `REV-ITR-...` identifiers across concurrent flows (`5` duplicate
`plan_id`s already on `main`, plus live `0371`/`0438` `P-1795584464-CLA-CO5.5` collision), preventing silent cross-flow
misattribution in calibration lookups and ledger queries once Bean `0371` lands.

## Cost

Small: reuse existing `build_stage_disambiguator` helper across 4 ID construction sites + unit tests via `holon flow`
(`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0278` (completed for `build_review_id`), Bean `0371` (per-flow pending ledger fragments keyed by root
  intent id).
