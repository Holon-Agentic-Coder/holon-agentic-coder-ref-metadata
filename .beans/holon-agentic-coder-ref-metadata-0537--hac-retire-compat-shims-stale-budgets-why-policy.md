---
# holon-agentic-coder-ref-metadata-0537
title: "Retire legacy re-export shims, stale budget overrides, conftest allowlist, and allow # WHY comments"
status: todo
type: task
priority: normal
tags:
  - holon-agentic-coder
  - hygiene
  - clean-code
  - testing
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

Over 834 lines of compatibility re-export shims expose `_`-private internals, 9 stale module-budget overrides and an
empty `token_reduction/` directory clutter the tree, `tests/conftest.py` carries a brittle hardcoded test-name allowlist
amid heavy white-box patching, and zero-comment enforcement in `tests/test_self_doc_modules.py` strips crucial "why"
explanations from subtle safety/platform invariants.

## Evidence

- 834 lines of compatibility shims exposing `_`-private symbols: `cli/__init__.py` (350L), `ledger/__init__.py` (167L),
  and `flow/lazy_exports*.py` (317L).
- 9 stale overrides in `holon-config/hygiene/module_budgets.json` (e.g. `flow/__init__.py` at 38L vs 522L cap) and
  orphaned empty `token_reduction/` directory.
- `tests/conftest.py:369-393`: hardcoded `_FEATURE_WORKTREE_CWD_TESTS` allowlist; 4 global autouse stubs
  (`lines 408-442`), 2,677 `monkeypatch`/`mock.patch` sites, and 84 private `_` imports across tests.
- `tests/test_self_doc_modules.py` (with stale `BASELINE_LINE_CEILINGS` at `line 190`) bans all inline comments, erasing
  critical rationale for non-obvious invariants (`local_llm.py:54-55` `0o777`, `git.py:71-72` `TypeError` retry,
  `ledger/lock.py:21` errno `45`, `git_flow.py:34-69` `.git` sentinels).

## Proposed Change

1. Update internal/test imports to reference canonical modules, delete the 834L compatibility shims and empty
   `token_reduction/` directory, and remove the 9 stale `module_budgets.json` overrides (coordinating with Bean `0489`).
2. Replace `_FEATURE_WORKTREE_CWD_TESTS` in `tests/conftest.py` with an explicit `@pytest.mark.allow_worktree_cwd`
   marker and shift new tests from `_`-private monkeypatching to adapter/contract seams.
3. Extend `tests/test_self_doc_modules.py` to explicitly permit `# WHY:` invariant comments on non-obvious
   platform/security constraints, refresh `BASELINE_LINE_CEILINGS`, and restore concise `# WHY:` annotations to the
   subtle invariants above.

## Acceptance Criteria

- Compatibility re-export shims and orphaned `token_reduction/` directory are removed; zero stale `module_budgets.json`
  caps remain above current+margin.
- `tests/conftest.py` contains no hardcoded test-function name allowlist.
- `test_self_doc_modules.py` permits `# WHY:` comments while continuing to reject redundant narrating comments.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Related existing beans: Bean `0379` (`__init__.py` logic), Bean `0405` (test cleanup), Bean `0489` (module budget
  step-down), Bean `0153` (self-doc).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
