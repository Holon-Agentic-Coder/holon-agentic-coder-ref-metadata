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
updated_at: 2026-11-27T11:55:26Z
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
