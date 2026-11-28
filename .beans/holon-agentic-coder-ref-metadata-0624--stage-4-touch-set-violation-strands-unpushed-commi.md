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
updated_at: 2026-11-28T00:03:58Z
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
  3. **`holon-agentic-coder#420` (`0601`, `self-doc-ast-behavior-gate`, `CF-0058`, `11:41:15Z`):** Resolver edited
     `apps/sandbox-executor/tests/test_ci_bookkeeping_wiring.py` outside the 3-file touch set, stranding unpushed commit
     `1906a1b8deea` and refusing ledger commit `19d339c9`.
  4. **`holon-agentic-coder#421` (`0617`, `stage5-fail-closed-calibrate`, `CF-0059`, `11:45:56Z`):** Resolver edited
     `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py` and `flow/stages/calibrate.py` outside the touch
     set, stranding unpushed commit `adcb4b6bcf9f` and refusing ledger commit `df001ca8`.
- Unlike Stage 3 (which automatically returns to Stage 2 to widen the touch set up to `MAX_REPLAN_ATTEMPTS`), Stage 4
  resolver halts leave unpushed local non-ledger commits on the branch that block ledger pushes and require manual
  `git reset`/re-scope (related prevention: Bean `0627`).
- **Audit update (`2026-11-28T00:01Z`):** `8` additional Stage 4 `touch_set_violation` halts occurred across `CF-0070`
  (`#429`), `CF-0074` (`COH #89`), `CF-0075` (`#435`, which already had `3/3 APPROVED`), `CF-0076` (`#436`), `CF-0077`
  (`#441`), `CF-0079` (`#445`), `CF-0080` (`#450`), and `CF-0082` (`#457`, stranding unpushed local commits `82b32b211`
  and `a0fde65c2` in `flow-hac-restore-why-cli-entrypoint`). Note `PR #437` (`stage4-resolver-touch-set`, merged
  `23:41:02Z`) now passes the plan Touch Set to the Stage 4 resolver input, while clean rollback/patch archival on
  violation (`0624`) remains unimplemented.

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
