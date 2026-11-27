---
# holon-agentic-coder-ref-metadata-0628
title: "Pre-launch overlap guard scans all parked flow Touch Sets on disk"
status: todo
type: feature
priority: high
tags:
  - harness
  - overlap-scheduling
  - slot-keeper
created_at: 2026-11-27T11:52:42Z
updated_at: 2026-11-27T11:55:26Z
---

## Notes

### Evidence (2026-11-27T11:52Z fifth-merge audit)

- `overlap-scheduling` has **15 entries** in `.agents/ledger/coordinator-failures.jsonl`, including repeats `CF-0046`
  (`0590`), `CF-0050` (`0599`), `CF-0056` (`0535` on `loop.py`), and `CF-0057` (`0610` parked at `11:18:45Z` for
  `4.8 min` wasted Stage 1–2 run on `0216`'s `flow/stages/plan.py`).
- Parked flow `0216` (`apps/holon-agentic-coder/flow-flow-references-github-issues/`, blocked since
  `2026-11-26T21:23:42Z`) has now blocked both `0590` (`CF-0046`) and `0610` (`CF-0057`) because:
  1. `.agents/scripts/slot_keeper.py:253-260` (`parked_holders`) only inspects entries with `kind == "resume"` inside
     `queue.json`, ignoring non-completed `apps/*/flow-*/` worktrees on disk that are not in `queue.json`.
  2. Direct launches via `.agents/skills/holon_flow/scripts/run_holon_flow.py` do not scan all on-disk
     `apps/*/flow-*/plans/*/P-*.md ## Touch Set` files before starting Stage 1, so coordinators relied on grepping
     `checkpoint-*.json` (`CF-0057`) and missed `plan.py` in `0216`'s `P-1795727982-CLA-CO5.5.md`.

### Proposed Change

1. Extract a shared harness helper (e.g. in `.agents/scripts/slot_keeper.py` or a small module imported by
   `run_holon_flow.py`) that scans every non-completed `apps/<repo>/flow-*/` worktree's `.holon/flow/checkpoint-*.json`,
   reads the latest `plans/*/P-*.md ## Touch Set` (falling back to intent `scope`), and also inspects open PR changed
   files.
2. Invoke this check automatically in `slot_keeper.py` (`parked_holders`) and `run_holon_flow.py` pre-flight (unless
   explicitly overridden), failing fast before Stage 1 with the exact overlapping parked worktree/PR, conflicting file,
   and oldest unblocked chain head (`CF-0046`).

### Expected Gain & Cost

- Prevents recurring `overlap-scheduling` wastes (`~3–5 min` per parked Stage 1–2 launch: `CF-0046`, `CF-0056`,
  `CF-0057`) and enforces `CF-0046`/`CF-0057` rules mechanically instead of relying on coordinator memory.
- Cost: ~60 lines in `.agents/scripts/` and `.agents/skills/holon_flow/scripts/run_holon_flow.py` + harness pytest.

## Acceptance Criteria

- [ ] A shared helper scans all on-disk non-completed `apps/<repo>/flow-*/` worktrees' `plans/*/P-*.md ## Touch Set`
      (and intent scopes) regardless of `queue.json` membership.
- [ ] Both `slot_keeper.py` and `run_holon_flow.py` pre-flight block or refuse overlapping launches against any parked
      on-disk flow worktree and print the blocking flow/file plus oldest unblocked chain head.
- [ ] Harness unit tests verify parked on-disk `## Touch Set` detection and pre-flight refusal; `uv run pytest` passes.

## Resolution
