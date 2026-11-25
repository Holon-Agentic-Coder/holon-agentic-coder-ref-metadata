---
# holon-agentic-coder-ref-metadata-0439
title: "Stage 4 resolver edits out-of-scope files and reacts to timing-gate CI failures"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - resolver
  - scope
  - holon-agentic-coder
created_at: 2026-11-25T00:28:00Z
updated_at: 2026-11-25T04:02:00Z
---

## Problem

Unlike Stage 3 (which checks edits against the plan's touch set), the Stage 4 review-loop resolver has no scope or
touch-set guard, and it is dispatched on `FIND-CI-*` findings triggered by `CI Timing Gate (compare with main)` variance
on bookkeeping-only commits. As a result, a scoped flow silently edits unrelated modules and weakens unrelated tests
across the repository.

## Evidence (2026-11-24)

- **PR #276 (`launcher-proxy-self-doc`):** scoped to 9 `launcher/` modules and `test_launcher_proxy_self_doc.py`.
  - Bookkeeping ledger commits `c1f20b9e` and `f5baea47` failed `unit (macos-latest)` at
    `CI Timing Gate (compare with main)`, producing `FIND-CI-002` and `FIND-CI-004`.
  - Stage 4 resolver commits `d937c11b`, `43c1119d`, and `00cc36cc` edited **8 files outside the plan's scope**:
    `apps/sandbox-executor/src/sandbox_executor/cli/__init__.py`, `config_env_report.py`, `scripts/pre_commit_check.py`,
    `tests/test_approval_fingerprint.py` (halving Hypothesis `max_examples` from `25` to `12`),
    `tests/test_calibration_diff_property.py`, `tests/test_turn_supervisor.py`, `tests/test_turns.py`, and
    `tests/test_url_credential_redaction.py`.
  - Merging those out-of-scope `cli/__init__.py` edits into `main` directly caused **PR #296
    (`split-cli-init-modules`)** to fail Stage 4 at `2026-11-24T23:47:23Z` with
    `Unresolvable merge conflicts detected in stage 'review': apps/sandbox-executor/src/sandbox_executor/cli/__init__.py`.
- **PR #292 (`config-env-self-doc`):** scoped to `config_env*.py`, yet Stage 4 resolver commit `66f45713`
  (`FIND-CI-004`, `R1-F1`, `R2-F1`, `R3-F1`) modified out-of-scope `redaction.py` and `test_redaction.py`.

## Proposed change

1. Enforce a touch-set / scope boundary on Stage 4 resolver commits (matching the plan's touch set plus scoped test
   files, or rejecting/reverting out-of-scope edits and marking the finding `unresolvable_out_of_scope` rather than
   silently mutating unrelated packages).
2. Do not convert `CI Timing Gate (compare with main)` failures—especially on bookkeeping-only heads—into actionable
   `FIND-CI-*` code-edit tasks for the resolver (coordinate with Bean `0419` / `0407`).
3. Add a hermetic test in `tests/flow/` asserting a Stage 4 resolver edit outside the allowed scope is caught before
   commit/push.

## Expected gain

Prevents cross-PR merge collisions (`PR #276` $\rightarrow$ `PR #296`), protects property-test budgets from silent
weakening, and eliminates wasted Stage 4 resolver turns (`9.4 min` median, `33.4 min` max) plus subsequent full
re-reviews (`26.6 min` median).

## Cost

Medium: Stage 4 resolver guard and `FIND-CI` filter in `sandbox_executor`, delivered via the Holon flow.

## Notes

- Related: Bean `0414` (Stage 3 touch-set enforcement), Bean `0419` (CI timing gate false failures), Bean `0407` (no
  full re-review when nothing reviewable changed), Bean `0392` (resolver repo-wide Prettier).
- Target repo change through the Holon flow (`holon-agentic-coder`).

## Audit evidence, 2026-11-25T04:02Z (self-improvement audit, fifth merge)

- **`PR #287` (`ledger-self-doc`, merged `03:21:48Z`):** `9f75f261` failed `unit (macos-latest)` at
  `CI Timing Gate (compare with main)` (`18:16Z–18:27Z`). Stage 4 resolver commit `ba6b525a` (`FIND-CI-001`) edited **7
  files outside `ledger/` scope**: `cli/__init__.py`, `config_env_report.py`, `redaction.py`,
  `tests/test_approval_fingerprint.py`, `tests/test_calibration_diff_property.py`,
  `tests/test_url_credential_redaction.py`, and `scripts/pre_commit_check.py`.
- **`PR #290` (`knowledge-self-doc`):** `9b4d2bd4` and `b15549be` failed `unit (macos-latest)` at
  `CI Timing Gate (compare with main)`. Stage 4 resolver commits `a06586a6` (`FIND-CI-002`) and `0b7f019c`
  (`FIND-CI-003`) edited **12 files outside `knowledge/` scope**: `cli/__init__.py`, `config_env_report.py`,
  `redaction.py`, `config_env.py`, `tests/flow/conftest.py`, `tests/test_approval_fingerprint.py`,
  `tests/test_calibration_diff_property.py`, `tests/test_credential_hermeticity.py`,
  `tests/test_executor_agent_output_redaction.py`, `tests/test_turn_supervisor.py`,
  `tests/test_url_credential_redaction.py`, and `scripts/pre_commit_check.py`.
- **Downstream collision in window:** When `#287` merged (`03:21:48Z`), `#290`'s `Merge origin/main` commit `a344ce2f`
  (`03:50:30Z`) hit **9 code/test merge conflicts** on those shared out-of-scope files (plus 3 ledgers), and both `#287`
  and `#290` appeared in Bean `0407`'s Stage 3 `blocked_by` list on `apps/sandbox-executor/tests/`.
