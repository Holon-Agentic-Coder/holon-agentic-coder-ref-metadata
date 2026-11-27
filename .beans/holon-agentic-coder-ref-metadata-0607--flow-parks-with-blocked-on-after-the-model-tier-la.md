---
# holon-agentic-coder-ref-metadata-0607
title: "Flow parks with blocked_on after the model tier ladder is exhausted on a test failure"
status: in-progress
type: feature
priority: high
tags:
  - holon-flow
  - tests
created_at: 2026-11-27T04:42:54Z
updated_at: 2026-11-27T17:11:29Z
---

## Evidence

Bean 0549 was closed on 2026-11-27 (resolution after PR #380 at `b5d9bfce`) with one design item deferred: parking with
`blocked_on` after the model tier ladder is exhausted. Its coverage file (`todo/intent-coverage-0549.json`) claimed a
separate intent for it, but no such intent exists in `todo/`. The acceptance check in 0549 records the gap:
`test_exhausted_ladder_stops_with_the_trail` covers the stop, but no `blocked_on` field or blocker link exists in the
diff or the repo. Blockers 0497 (`blocked_on` field on review results) and 0523 (resume a parked flow when its blocker
lands) are still `todo`.

Related: 0549 (closed, deferred item), 0497 (blocker field), 0523 (auto-resume), 0559 (resolver-halt runbook until 0549
lands), 0572 (parked on PR #360 overlap).

## Proposed change

- After the model tier ladder (claude fable, opus, sonnet, haiku) is exhausted on an environment, pre-existing or
  unresolved test failure, the flow parks instead of halting. The park record names the blocking bean or PR
  (`blocked_on`), the evidence, and the full ledger trail of attempts (classification, each tier, signatures).
- The park uses the `blocked` status already written by `test_failure_loop` (`blocked_evidence`), extended with
  `blocked_on` (bean id or PR number). Blocker identity comes from the classifier's evidence or an explicit mapping, not
  free text.
- Automatic resume when the blocker lands is delegated to 0523; this bean supplies the field and the record it reads.
  Until 0523 lands, the park is resumed by hand from its checkpoint.
- Repeated-signature handling is unchanged, with one missing test: a failure signature seen once creates no KB failure
  mode entry (`wisdom.promote_repeated_failure_signatures` needs two or more runs). This is the test from PR #380 that
  was not written.

## Acceptance

- After the tier ladder is exhausted on an environment, pre-existing or unresolved test failure, the flow parks with
  `blocked_on` naming the blocking bean or PR, and the ledger rows for every attempt.
- The parked record is readable by 0523's watcher (fields and checkpoint path documented in the record schema).
- Tests with a fake runner: (a) exhaustion on an environment failure parks with `blocked_on`; (b) exhaustion on an
  unresolved failure with no blocker parks with `blocked_on: none` and evidence rather than halting; (c) an introduced
  failure that is fixed does not park; (d) a failure signature seen once creates no KB failure mode entry.
- `uv run pytest` green; `check_beans.py` passes.

## Assumptions with validation

- A1: the ladder-exhaustion point is already a single code path in `test_failure_loop` / `test_failure_classify`.
  Validate by reading those modules before the intent is written; if it is spread across stages, scope the intent per
  stage.
- A2: `blocked_on` can be derived from the classifier evidence for at least the environment case (the 2026-11-26
  identity-env case). Validate with the fake runner in test (a); if no blocker can be named, the park records
  `blocked_on: none` and the 0523 watcher treats it as manual.
- A3: 0497 and 0523 are not required to land first for the record to be written; only the automatic resume depends on
  them. Validate by checking the intent's scope does not touch the resume watcher.
- A4: the intent scope lists files, not directories (per the intent-scope rule). Validate with the intent-check step
  before launch and record any companion files on this bean.

## Notes

Created as a follow-up to 0549's deferred item. Not started; no intent written yet.

- parked 2026-11-27: blocked by flow-review-posting-transient-retry (bean 0424) on
  `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports_review.py`; resume from checkpoint when 0424 merges.
- 2026-11-27: Holon flow completed all 5 stages (`antigravity-agent` / `gemini-4-neon`). PR:
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/433
  (`I-1795797310-exhausted-ladder-blocked-on/P-1795797341-ANA-G4N/E-1795797570-ANA-G4N/_`), 3/3 consensus APPROVED,
  calibration included (`plans/I-1795797310-exhausted-ladder-blocked-on/P-1795797341-ANA-G4N_calibration.md`, predicted
  EV: 62.82, actual EV: 80.33, delta: +17.51), 16/16 CI checks green, `MERGEABLE` / `CLEAN`. Checkpoint:
  `apps/holon-agentic-coder/flow-exhausted-ladder-blocked-on/.holon/flow/checkpoint-exhausted-ladder-blocked-on.json`.
  Awaiting human maintainer merge.

## Resolution
