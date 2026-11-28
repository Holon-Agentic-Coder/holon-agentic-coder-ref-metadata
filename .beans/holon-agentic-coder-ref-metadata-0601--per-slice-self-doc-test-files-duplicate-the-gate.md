---
# holon-agentic-coder-ref-metadata-0601
title: "Each 0153 slice adds its own copy of the comment scanner as a test file instead of using the one gate"
status: completed
type: task
priority: high
tags:
  - holon-flow
  - self-explaining-code
  - tests
  - duplication
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T23:48:13Z
---

## Evidence

- PR #401 adds `apps/sandbox-executor/tests/test_self_doc_src_27.py` (93 lines): its own `_forbidden_comments`,
  `_WHY_COMMENT_RE`, `_FMT_DIRECTIVE_RE`, a slice module tuple and parametrised "has no docstrings / has no forbidden
  comments" tests. Slice `self-doc-src-24` and `src-28` add the same shape. Nine `self_doc` test files already sit in
  the tests directory and about 25 slices were launched, so the copies will grow to 25 or more.
- The same rule is already enforced by `scripts/check_self_explaining.py` (beans 0558, 0153). A per-slice test pins one
  file list and one regex that the gate also owns: duplicated mechanism, and a slice list that rots as modules move.
- The slice tests assert absence of docstrings and comments only (string and token checks). Nothing in the slice shows
  behaviour is unchanged beyond the existing full suite; the bean text claims "behaviour unchanged (full suite green)".

## Goal

1. Replace the per-slice files by the one gate run over the whole tree (or one shared parametrised test fed by the
   gate's file list); delete the `test_self_doc_*` copies once the gate covers their modules.
2. Add to the slice intent a behaviour-preservation check that is not a string compare: compare the AST of each touched
   module before and after with docstrings, comments and the renamed identifiers normalised (or run the module's own
   tests by name and report their count), and put the result in the PR body.
3. Slice intents stop requesting a new test file for the invariant.

## Expected gain and cost

Gain: fewer tests to maintain, 90 lines less per slice PR, review of a slice reads only the code change; behaviour claim
becomes checked. Cost: one shared test and an AST-normalising helper; touches the 0153 intent template.

## Notes

- Source: self-improvement audit 2026-11-27 (fifth merge, #371 to #402).
- Related: 0153, 0558.

## Acceptance

- The per-slice scanner test copies (`tests/test_self_doc_src_*.py`, `test_self_doc_tests_*.py` and similar) are deleted
  and replaced by the single self-explaining gate (`scripts/check_self_explaining.py`) covering all code.
- An AST-normalised before/after check proves a self-doc change is behaviour-preserving: the AST of each changed module,
  with docstrings and comments stripped, is identical before and after.
- That check runs in CI for PRs labelled or titled as self-doc changes, or for any PR whose diff only removes docstrings
  or comments.
- Tests for the check: a real removal of docstrings and comments passes; a sneaked code change fails.
- No reduction in what the gate enforces; the self-explaining code invariant holds.

## Assumptions

- `ast.dump` comparison is stable across the Python version used in CI. Validation: run the check on the CI interpreter
  and assert identical output for an unchanged module; pin the comparison to `ast.dump` without attributes.
- Deleting the copies loses no coverage because the gate scans the same files. Validation: before deletion, diff the
  gate's scanned file list against the union of the module tuples in the copies; every module must be in the gate's
  list.
- Stripping docstrings leaves a comparable AST. Validation: the normaliser removes only a leading string expression in a
  module, class or function body (substituting `pass` when the body would be empty); a test covers that case.
- A PR can be identified as a self-doc change from its label, its title or a diff that only removes docstrings and
  comments. Validation: the CI test covers each trigger on a sample diff.

## Progress

- `self-doc-ast-behavior-gate` ([PR #425](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/425),
  `da13a83c`) merged into `main`, delivering the AST behaviour-preservation CI gate
  (`scripts/check_self_doc_behavior.py` and `.github/workflows/test-self-doc-behavior.yml`; Stage 5 calibrated:
  Predicted EV 59.33 / Actual EV 73.55 / ΔEV +14.22). Bean stays `in-progress` while deleting per-slice
  `test_self_doc_*` copies remains as slice 2.
- Audit update (`2026-11-27T15:46Z`, `1f3331637`):
  [PR #426](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/426) (`0153` `self-doc-tests-49`) cleaned 12
  test modules while still adding another `89`-line per-slice file
  (`apps/sandbox-executor/tests/test_self_doc_tests_49.py`), bringing `apps/sandbox-executor/tests/test_self_doc*.py` to
  **31 files** awaiting slice-2 deletion.

## Resolution

Delivered via [PR #428](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/428) and merged into `main`
(`8c3e13e396`):

- **Key Architectural Deliverables**: Deleted 30 redundant per-slice `apps/sandbox-executor/tests/test_self_doc_*.py`
  scanner copies and consolidated gate-coverage verification into
  `apps/sandbox-executor/tests/test_self_doc_gate_coverage.py` alongside `scripts/check_self_explaining.py` and the AST
  behaviour-preservation CI gate (`PR #425`).
- **Verification & Tests**: `apps/sandbox-executor/tests/test_self_doc_gate_coverage.py` verified; `16/16` CI checks
  `SUCCESS`.
- **Holon Flow Traversal & Readiness (`pr_readiness.py --record`)**: Head `1fc9b3ad`, Consensus `APPROVED` (`d8c4ad6d`),
  Stage 5 calibration `calibrate=success`
  (`plans/I-1795794454-prune-self-doc-test-copies/P-1795794477-ANA-G4N_calibration.md`),
  `gates: consensus=ok, calibration=ok, pipeline=ok`.
