---
# holon-agentic-coder-ref-metadata-0624
title: "Stage 4 touch_set_violation strands unpushed commits and lacks bounded re-plan recovery"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - resolver
  - holon-agentic-coder
created_at: 2026-11-27T10:55:04Z
updated_at: 2026-11-27T10:56:02Z
---

## Notes

### Evidence (2026-11-27T07:49Z–10:49Z fifth-merge audit)

- Since `0596` (`#410`) enforced resolver touch-set checks in Stage 4, two flows halted immediately on
  `touch_set_violation` with stranded local commits:
  1. **`holon-coherence#70` (`0528`, `coherence-translation-sse-finish`, `CF-0054`, `08:24:11Z`):** Passed `3/3` review,
     then Stage 5 merged `#64` (`sse_tap.py`), exposing an EOF trailing-line flush mismatch
     (`test_bridged_sse_flushes_trailing_line_without_newline_on_eof`). On resume, the carried-finding resolver edited
     `src/holon_coherence/proxy/steps/sse_tap.py:79` outside `#70`'s touch set (`providers/translation.py`,
     `tests/providers/test_translation.py`). Stage 4 raised `touch_set_violation`, left unpushed local commit
     `eb9a91bd97e7` plus ledger commit `00ce18ac`
     (`Warning: pushing ledger commit 00ce18ac refused: it sits on unpushed non-ledger commits`), and halted without
     resetting or recovering.
  2. **`holon-agentic-coder#413` (`0611`, `promote-ledger-debounce-alert`, `CF-0055`, `08:44:21Z`):** All `3/3`
     reviewers requested updating `.github/workflows/README.md` to match `.github/workflows/promote-ledger.yml`. The
     resolver edited `.github/workflows/README.md` outside `intent.scope`, raising `touch_set_violation`
     (`ac8f76db3dda`) and refusing ledger commit push (`6365fa72`).
- Unlike Stage 3 (which automatically returns to Stage 2 to widen the touch set up to `MAX_REPLAN_ATTEMPTS`), Stage 4
  resolver halts leave unpushed local non-ledger commits on the branch that block ledger pushes and require manual
  `git reset`/re-scope.

### Proposed Change

1. Before committing ledger rows or halting on `touch_set_violation` in Stage 4, save the offending resolver commit's
   diff as a patch under `.holon/flow/` (or `executions/` diagnostics) and cleanly reset the unpushed violation commit
   so review ledger rows can still commit and push onto the valid branch head.
2. Provide a bounded Stage 4 escalation path (mirroring Stage 3's bounded re-plan or recording `blocked_on` /
   `unresolvable_out_of_scope` with the rejected path list) when unanimous reviewer findings or post-merge contract
   mismatches cannot be resolved inside the existing plan touch set.

### Expected Gain & Cost

- Eliminates stranded unpushed commits and manual git cleanup on Stage 4 `touch_set_violation` halts (`CF-0054`,
  `CF-0055`) and keeps review ledger pushes unblocked.
- Cost: small rollback/patch-archive guard in `flow/review/resolver.py` / `flow/review/loop.py` + hermetic tests.

## Acceptance Criteria

- [ ] When Stage 4 detects `touch_set_violation` on a resolver commit, the violating unpushed commit's patch is saved
      and reset off the branch before the review ledger commit/push runs, leaving zero stranded non-ledger commits.
- [ ] The ledger commit pushes cleanly and records the rejected out-of-scope file path(s) and finding outcome.
- [ ] Hermetic tests cover both a Stage 4 `touch_set_violation` rollback + clean ledger push and bounded escalation/halt
      behavior; `uv run pytest` passes.

## Resolution
