---
# holon-agentic-coder-ref-metadata-0453
title: "Consolidate 19+ duplicated test_*_self_doc.py AST and allowlist scanners into one parameterized check"
status: completed
type: task
priority: normal
tags:
  - tests
  - code-quality
  - hygiene
  - self-doc
  - holon-agentic-coder
created_at: 2026-11-25T05:41:00Z
updated_at: 2026-11-26T11:37:00Z
---

# Consolidate `19+` duplicated `test_*_self_doc.py` AST and allowlist scanners into one parameterized check

## Summary

Per-module self-documenting refactors under Bean `0153` each add a standalone `tests/test_*_self_doc.py` file (`79–154`
lines) that copy-pastes identical AST docstring collectors, `tokenize.generate_tokens` scanners, comment-allowlist
matchers, and 10+ parameterized `test_comment_allowlist_rules` test cases instead of reusing one shared helper and
parameterized test registry.

## Evidence

- **Cadence merges `#295–#299` and `#300` (`holon-agentic-coder`):**
  - `PR #295` (`099025f8`) added `apps/sandbox-executor/tests/test_local_llm_self_doc.py` (`88` lines).
  - `PR #297` (`0bd580ea`) added `apps/sandbox-executor/tests/test_claude_auth_self_doc.py` (`91` lines).
  - `PR #298` (`5e08904f`) added `apps/sandbox-executor/tests/test_touch_set_self_doc.py` (`147` lines).
  - `PR #300` (`efafa316`) added `apps/sandbox-executor/tests/test_decomposition_rule_self_doc.py` (`143` lines).
- **Scale across `main` and open `0153` PRs (`2026-11-25T05:35Z`):**
  - `main` now carries **`19` `test_*_self_doc.py` files (`2,199` lines total)**; **`19/19`** define their own custom
    AST/tokenize/allowlist helper functions (`_collect_docstrings`, `_is_allowlisted_comment`, etc.).
  - `7` open `0153` PR worktrees (`#301–#307`) carry another `7` standalone files (`932` lines), bringing the pattern to
    **`26` files (`3,131` lines)** if left fragmented.
  - Duplicates logic against project code-quality rules and grows the unit test suite (`Bean 0405`) on every module
    slice.

## Proposed Change

1. Once open `0153` PRs (`#301–#307`) land or drain (avoiding overlap conflicts), extract one shared `self_doc`
   AST/tokenize/allowlist checker + unit tests covering allowlist edge cases once.
2. Replace the `19+` standalone `test_*_self_doc.py` copies with a single parameterized test module over the governed
   module/package list (or unify into Bean `0153` Goal 4's global `task lint` self-doc gate).

## Expected gain

Deletes `~2,000–3,000` lines of duplicated test code and `~200+` redundant allowlist test invocations without losing
AST/comment enforcement on any module.

## Cost

Small refactor flow (`apps/sandbox-executor/tests/`) run after the active `0153` queue drains (`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`); wait until `#301–#307` merge/close so touch sets stay
  disjoint.
- Related: Bean `0153` (self-documenting code & Goal 4 global check), Bean `0405` (clean up unnecessary unit tests).
- Audit source: `2026-11-25T05:41Z` fifth-merge self-improvement audit (`#295–#299`).

## Progress

- 2026-11-26: flow `consolidate-self-doc-tests` launched (claude-agent, claude-opus-5-5); log
  `todo/flow-consolidate-self-doc-tests.log`.

## Resolution

Delivered via [PR #336](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/336) and merged into `main`
(`6d68e5dc`):

- **Key Architectural Deliverables**: the 26 standalone `test_*_self_doc.py` files are replaced by one shared helper
  `apps/sandbox-executor/tests/self_doc_scanner.py` (AST docstring collector, tokenize comment scanner, allowlist
  matcher) and one data-driven test module `test_self_doc_modules.py` over the governed module list. No production code
  changed.
- **Verification & Tests**: test-only change (+431 / -3,138 lines across the 26 removed files and the two new ones,
  excluding flow ledger and plan files). Merged after CI and review.
- **Holon Flow Traversal**: flow `consolidate-self-doc-tests` (claude-agent, claude-opus-5-5) reached merge with its
  plan and calibration artifacts in the merged diff. Install step skipped (test-only change).
