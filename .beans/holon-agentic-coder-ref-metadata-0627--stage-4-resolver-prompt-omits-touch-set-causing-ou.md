---
# holon-agentic-coder-ref-metadata-0627
title: "Stage 4 resolver prompt omits Touch Set causing out-of-scope halts"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-4
  - resolver
  - holon-agentic-coder
created_at: 2026-11-27T11:52:42Z
updated_at: 2026-11-27T23:48:13Z
---

## Notes

### Evidence (2026-11-27T11:52Z fifth-merge audit)

- Four consecutive flows across `holon-coherence` and `holon-agentic-coder` halted at Stage 4 on `touch_set_violation`
  after the resolver edited files outside the plan Touch Set:
  1. `holon-coherence#70` (`0528`, `CF-0054`, `08:24:11Z`): resolver edited
     `src/holon_coherence/proxy/steps/sse_tap.py:79`.
  2. `holon-agentic-coder#413` (`0611`, `CF-0055`, `08:44:21Z`): resolver edited `.github/workflows/README.md`.
  3. `holon-agentic-coder#420` (`0601`, `CF-0058`, `11:41:15Z`, `15.0 min` Stage 4 + `10.9 min` Stages 1–3): resolver
     edited `apps/sandbox-executor/tests/test_ci_bookkeeping_wiring.py`.
  4. `holon-agentic-coder#421` (`0617`, `CF-0059`, `11:45:56Z`, `15.9 min` Stage 4 + `41.5 min` prior Stage 3 re-plans):
     resolver edited `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py` and
     `apps/sandbox-executor/src/sandbox_executor/flow/stages/calibrate.py`.
  5. `holon-agentic-coder#423` (`0607`, `CF-0060`, `12:00:07Z`, `15.0 min` Stage 4 + `13.9 min` Stages 1–3): resolver
     edited `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports_review.py`.
- Inspecting `apps/sandbox-executor/src/sandbox_executor/flow/review/resolver.py:112-135` (`_dispatch_review_resolver`)
  and `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py:323-375` (`_build_resolver_prompt`) at
  `2a83e4cc7` confirms that the plan's Touch Set is **never passed** into `input_payload`, container args, or the
  resolver prompt. Line 356 even warns the resolver that ``"`out of scope` alone is not accepted"`` without telling it
  which paths are in the Touch Set or that any edit outside the Touch Set triggers a fatal `touch_set_violation`.
- Distinct from Bean `0624`: `0624` handles _post-violation_ rollback and bounded re-plan recovery once a
  `touch_set_violation` commit has already happened; this bean prevents the resolver from editing out-of-set files
  upfront and returns structured `unresolvable_out_of_touch_set` dispositions naming the required path.

### Proposed Change

1. Resolve the effective plan Touch Set in `flow/review/resolver.py` and pass it in the resolver `input_payload` (and
   through `entrypoint/review_loop.py` into `_build_resolver_prompt`).
2. State the allowed Touch Set paths explicitly in `_build_resolver_prompt`, forbid modifying files outside that list,
   and specify a structured rejection/escalation disposition (`out-of-touch-set` / `open` with the required external
   path) when a finding or CI check genuinely requires an unlisted file.
3. Add a pre-commit guard in `entrypoint/review_loop.py:_commit_resolution` (and hermetic tests) so out-of-set edits are
   caught before committing on the branch.

### Expected Gain & Cost

- Eliminates avoidable `~5 min` wasted resolver turns and `11.6–15.9 min` Stage 4 halts (`4` flows in ~3.5 h).
- Cost: ~50 lines across `flow/review/resolver.py`, `entrypoint/review_loop.py`, and hermetic tests.

## Acceptance Criteria

- [ ] `_dispatch_review_resolver` passes the effective plan Touch Set to the Stage 4 resolver container payload, and
      `_build_resolver_prompt` renders the allowed paths and instructs the resolver never to edit files outside them.
- [ ] When a finding requires editing a file outside the Touch Set, the resolver records a structured disposition naming
      the required external path instead of committing an out-of-set edit.
- [ ] Hermetic unit tests verify Touch Set propagation, prompt rendering, and pre-commit refusal; `uv run pytest`
      passes.

## Flow

- **Launched (`2026-11-27`, `stage4-resolver-touch-set`):** Propagates optional `touch_set` from
  `flow/review/resolver.py` to `entrypoint/review_loop.py` prompt and pre-commit guard with unit tests in
  `tests/flow/review/test_resolver_touch_set.py` (`todo/intent-0627-stage4-resolver-touch-set.json`).
- **Completed (`2026-11-27T17:39:05Z`, `antigravity-agent` / `gemini-4-neon`):**
  - PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/437 (`OPEN`, `MERGEABLE`, `CLEAN`, awaiting
    human maintainer merge)
  - Branch: `I-1795798629-stage4-resolver-touch-set/P-1795798652-ANA-G4N/E-1795798908-ANA-G4N/_`
  - Worktree: `apps/holon-agentic-coder/flow-stage4-resolver-touch-set`
  - Checkpoint:
    `apps/holon-agentic-coder/flow-stage4-resolver-touch-set/.holon/flow/checkpoint-stage4-resolver-touch-set.json`
  - Review: 3/3 `APPROVED` at iteration 2 (1 full, 1 scoped); CI `16/16` passed on final head `a386121`.
  - Calibration: `plans/I-1795798629-stage4-resolver-touch-set/P-1795798652-ANA-G4N_calibration.md` included in PR diff
    (Predicted EV `56.64`, Actual EV `74.64`, ΔEV `+18.00`).
  - Changed code/tests: `apps/sandbox-executor/src/sandbox_executor/flow/review/resolver.py`,
    `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`,
    `apps/sandbox-executor/tests/flow/review/test_resolver_touch_set.py` (`flow/lazy_exports_review.py`,
    `flow/review/loop.py`, and `holon-config/hygiene/module_budgets.json` untouched).

## Resolution

Delivered via [PR #437](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/437) and merged into `main`
(`dc9a5cc1d4`):

- **Key Architectural Deliverables**: Propagated the effective plan Touch Set from
  `sandbox_executor/flow/review/resolver.py` into `sandbox_executor/entrypoint/review_loop.py` (`_build_resolver_prompt`
  and pre-commit guard) so Stage 4 resolvers know the allowed paths upfront and emit structured out-of-touch-set
  dispositions rather than committing out-of-scope edits.
- **Verification & Tests**: Added `apps/sandbox-executor/tests/flow/review/test_resolver_touch_set.py`; `16/16` CI
  checks `SUCCESS`.
- **Holon Flow Traversal & Readiness (`pr_readiness.py --record`)**: Head `a3861216`, Consensus `APPROVED` (`823e2659`),
  Stage 5 calibration `calibrate=success`
  (`plans/I-1795798629-stage4-resolver-touch-set/P-1795798652-ANA-G4N_calibration.md`),
  `gates: consensus=ok, calibration=ok, pipeline=ok`.
