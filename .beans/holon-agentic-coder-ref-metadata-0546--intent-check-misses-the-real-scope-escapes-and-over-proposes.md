---
# holon-agentic-coder-ref-metadata-0546
title: "holon intent-check misses the files plans actually escape into and over-proposes test files"
status: todo
type: bug
priority: high
tags:
  - flow
  - intent
  - touch-set
  - holon-agentic-coder
created_at: 2026-11-26T21:08:00Z
updated_at: 2026-11-27T15:55:01Z
---

## Problem

First trials of `holon intent-check` (PR #348, bean 0508) on 2026-11-26:

- On the intent of flow `single-runner-per-checkpoint` it made 30 proposals (mostly every test file that imports
  `turns.py`, plus co-change neighbours) but **did not** propose
  `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py` or `launcher/run_tracking.py` — the two files that
  flow's executor actually changed outside its touch set, which forced a re-plan and then parked it on `lazy_exports.py`
  for hours.
- On the first `conftest.py` split intent it proposed no companions at all.

So it is noisy where it does not matter and silent where it does. Today's escapes were dominated by registries and hub
files: `flow/lazy_exports.py` (any new module under `flow/`), `docs/architecture.md` / `docs/git_flow.md`, and
`conftest.py`.

## Proposed fix

- Add a rule: a new or moved module under a package with a hand-maintained export map (`flow/lazy_exports.py`) proposes
  that map (until Bean 0543 generates it).
- Rank proposals by evidence and cap the list; demote "every test that imports a listed module" to a single summary
  line.
- Replay the check over today's flows that escaped scope (beans 0492, 0502, 0508 evidence) and report precision/recall.
- Related: Bean 0508 (completed), 0502, 0543.

## Note (2026-11-27)

Scope drift on PR #357 (bean 0153, flow `self-explaining-code-gate`, merged `5a2868af`): the executor added three helper
modules outside the intent's scope, `scripts/self_explaining_comments.py`, `scripts/self_explaining_diff.py` and
`scripts/self_explaining_hash.py`. The intent named only the gate script, the pre-commit and hygiene wiring, the tests
and the prompt templates. Add this escape to the replay set (see the Proposed fix above).

## Audit evidence (2026-11-27T10:55Z fifth-merge audit)

- **`CF-0055` (`HAC #413`, bean `0611`, `promote-ledger-debounce-alert`, `08:44:21Z`):** `holon intent-check` did not
  propose `.github/workflows/README.md` when `.github/workflows/promote-ledger.yml` was in `intent.scope`. All `3/3`
  reviewers requested updating `.github/workflows/README.md` to match the new trigger/behavior, and the Stage 4 resolver
  halted on `touch_set_violation` (`ac8f76db3dda`). Add `.github/workflows/*.yml -> .github/workflows/README.md`
  companion rule to `intent-check`.

## Audit evidence (2026-11-27T11:52Z fifth-merge audit)

- **`CF-0058` (`HAC #420`, bean `0601`, `self-doc-ast-behavior-gate`, `11:41:15Z`):** Adding
  `.github/workflows/test-self-doc-behavior.yml` triggered on `pull_request` required registering the workflow in
  `apps/sandbox-executor/tests/test_ci_bookkeeping_wiring.py`. `intent_scope_check.py` missed this companion because it
  only scans Python imports and `git log` co-changes, causing a `15.0 min` Stage 4 `touch_set_violation` halt
  (`1906a1b8`). Add a rule proposing `apps/sandbox-executor/tests/test_ci_bookkeeping_wiring.py` whenever a new
  `.github/workflows/*.yml` file is in scope.
- **`CF-0059` (`HAC #421`, bean `0617`, `stage5-fail-closed-calibrate`, `11:45:56Z`):** Stage 3 re-plans and Stage 4
  resolver both escaped into `flow/lazy_exports.py` (which `0546` already flags as missing from `intent-check` for
  `flow/` modules) and `flow/stages/calibrate.py`.
- **`CF-0060` (`HAC #423`, bean `0607`, `exhausted-ladder-blocked-on`, `12:00:07Z`):** Adding/moving public helpers in
  `apps/sandbox-executor/src/sandbox_executor/flow/review/*` caused Stage 4 resolver (`755a54cdec86`) to export
  `parked_record_from_ci_status` in `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports_review.py`, halting
  with `touch_set_violation` after `15.0 min` Stage 4 + `13.9 min` Stages 1–3. Add a rule proposing
  `flow/lazy_exports_review.py` whenever `flow/review/*.py` is in scope (mirroring `flow/lazy_exports.py`).

## Audit evidence (2026-11-27T15:46Z fifth-merge audit)

- **`CF-0064` (`0424`, `review-posting-transient-retry`, `12:29:32Z`):** Stage 3 halted after 2 re-plans because
  `intent-0424` omitted `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports_review.py` (`REVIEW_LAZY_EXPORTS`)
  and `apps/sandbox-executor/tests/test_review_loop.py` (permanent failure fixture using `"HTTP 502"`). Inspecting
  `intent_scope_check.py:88-96` (`_source_proposals`) at `1f3331637` confirms it only proposes `__init__.py`
  (`reexporting_init`), never `flow/lazy_exports.py` or `flow/lazy_exports_review.py`.
- **`CF-0065` (`HAC #427`, `0607`, `exhausted-ladder-blocked-on`, `15:39:27Z`):** After expanding `intent-0607` for
  `lazy_exports_review.py` (`CF-0060`), `PR #427` halted in Stage 4 iteration 1 with `touch_set_violation` on
  `apps/sandbox-executor/tests/flow/test_local_test_finding.py` (`9.0 min` execute + `3.4 min` review).
  `test_local_test_finding.py` directly imports `local_test_finding` (so `intent_scope_graph.py` can detect it), yet
  `run_holon_flow.py` pre-flight did not fail closed when `holon intent-check` exited `1` on unresolved companion tests.
