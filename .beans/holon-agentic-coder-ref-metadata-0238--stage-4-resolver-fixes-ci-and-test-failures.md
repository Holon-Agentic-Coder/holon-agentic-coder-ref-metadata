---
# holon-agentic-coder-ref-metadata-0238
title: "Stage 4 resolver fixes CI and test failures: synthesise FindingRow for FIND-CI when CI fails"
status: completed
type: bug
priority: high
tags:
  - flow
  - review-loop
  - resolver
  - stage-4
  - ci
  - holon-agentic-coder
created_at: 2026-11-06T04:05:00Z
updated_at: 2026-11-06T05:16:00Z
---

## Problem

In `sandbox_executor.flow.run_review_loop()`, when GitHub Actions CI checks fail (or local test suites fail) resulting
in `ci_finding = True` and a consensus verdict of `CHANGES_REQUESTED`:

1. **`iter_findings` Only Collects Reviewer Findings**: Line 4426 defines:
   ```python
   iter_findings = collect_review_data(reviewers).findings
   if not resolver_enabled or not iter_findings or is_dirty or resolved_target is None:
       context.log(
           f"[Review Loop] Halting review loop at iteration {iteration}: verdict "
           f"{ensemble_verdict} (no resolver pass applicable)."
       )
       break
   ```
   If all 3 reviewers unanimously approve the code diff (`critical 0, important 0, nit 0`),
   `collect_review_data(reviewers).findings` is an empty list (`[]`).
2. **Resolver Guard Trips on Empty `iter_findings`**: Because `iter_findings` contains 0 items, `not iter_findings`
   evaluates to `True`. The review loop immediately halts with `(no resolver pass applicable)` and marks Stage 4 as
   failed, rather than dispatching the resolver.
3. **`FIND-CI` Is Never Handed to the Resolver**: `FIND-CI-{iteration:03d}` is generated only as a raw string ID in
   `finding_ids` and written to the execution ledger as an `ACT-FIND` row. It is never synthesised into a
   `FindingRow(id, severity, path, line, summary, recommendation)`. Even if reviewers had reported other findings, the
   resolver would never see the CI failure in its input payload.

Consequently, any CI failure (such as a linter error, markdown formatting failure from `make lint-md`, or a failing unit
test on GitHub Actions) that is not caught by the LLM reviewers cannot be resolved by the resolver, causing autonomous
flows to halt prematurely.

## Decision

Synthesise a first-class `FindingRow` for `FIND-CI` and include it in `iter_findings` whenever CI checks fail:

1. **Synthesise `FindingRow` for CI and Test Failures**:
   - In `run_review_loop()`, when `ci_finding` is `True` (failing CI checks or failed local tests):
     - Extract failing check names, workflow names, or descriptions from `last_ci_status.get("checks", [])` (e.g.
       `Test - Hygiene / hygiene (ubuntu-latest)`).
     - Construct a synthetic `FindingRow`:
       - `id`: `f"FIND-CI-{iteration:03d}"`
       - `severity`: `"important"`
       - `path`: failing path if identifiable, or `"Makefile"` / repository root
       - `line`: None
       - `summary`: Concise description of failing CI check(s), e.g. `GitHub CI check 'Test - Hygiene' failed (lint-md)`
         or `Local test suite reported failures`
       - `recommendation`:
         `"Inspect and fix failing CI checks or linters (e.g. run 'make lint', 'make test', or 'uv run pytest'), commit fixes, and push to the execution branch."`
     - Append the synthetic `FindingRow` to `iter_findings`.
2. **Resolver Invocation and Linter Pre-Push Verification**:
   - When `iter_findings` contains the synthetic `FIND-CI` finding (even if all reviewers returned `APPROVED`),
     `not iter_findings` is `False`, allowing the resolver pass to be invoked.
   - The resolver role container receives the CI finding with exact failure details (check name, failed workflow), runs
     local diagnostics (`make lint`, `make test`, `uv run task lint`, `npx prettier --write`, etc.), commits the fix,
     and pushes.
   - Ensure the resolver's pre-commit / pre-push verification in `entrypoint/review_loop.py`
     (`_verify_resolver_changes()`) includes markdown formatting and hygiene checks (`make lint` / `make lint-md`) so
     hygiene issues are caught locally before pushing.
   - The next review iteration re-verifies that CI settles green.
3. **Hermetic Unit Tests**:
   - Add unit tests in `apps/sandbox-executor/tests/test_review_loop.py` verifying that when all reviewers return
     `APPROVED` but CI fails:
     - A synthetic `FindingRow` for `FIND-CI-{iteration:03d}` is created with failing check metadata.
     - `run_resolver_fn` is invoked with `FIND-CI-{iteration:03d}`.
     - The resolver's resolution (e.g. committing a fix) allows the subsequent iteration to pass.

## Scope

1. `apps/sandbox-executor/src/sandbox_executor/flow.py`: Synthesise `FindingRow` for `ci_finding` and include in
   `iter_findings` passed to the resolver.
2. `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`: Update resolver verification and prompts to
   handle CI failure findings and run full lint/hygiene checks.
3. `apps/sandbox-executor/tests/test_review_loop.py`: Hermetic tests for CI failure resolution when reviewers approve.

## Resolution

- Implemented in `holon-agentic-coder` via `holon flow` across Intent `I-1793939965-...`, Plan `P-1793939982-...`, and
  Execution `E-1793940300-...`.
- Synthesised first-class `FindingRow` for `FIND-CI-{iteration:03d}` with failing check details, workflow names, and
  actionable recommendations in `sandbox_executor.flow.run_review_loop()`.
- Appended `FIND-CI` to `iter_findings`, ensuring the resolver is dispatched on CI and test failures even when all code
  reviewers approve.
- Updated `entrypoint/review_loop.py` to ensure resolver prompt formatting and pre-push verification handle
  infrastructure findings cleanly.
- Added comprehensive hermetic unit tests in `apps/sandbox-executor/tests/test_review_loop.py`.
- Passed Stage 4 ensemble review, completed Stage 5 calibration ($\Delta\text{EV} = +11.52$, predicted `83.11`
  $\rightarrow$ actual `94.63`), and merged into `main` via PR
  [#129](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/129) (`ecec262`).
