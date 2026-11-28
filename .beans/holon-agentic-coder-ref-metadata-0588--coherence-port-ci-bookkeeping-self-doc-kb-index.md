---
# holon-agentic-coder-ref-metadata-0588
title: "Port ci_bookkeeping_gate, self-explaining check, budget-label actor check, and remove KB index.json"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - ci
  - hygiene
  - invariants
created_at: 2026-11-27T00:33:33Z
updated_at: 2026-11-28T00:03:59Z
---

## Problem

`holon-agentic-coder` now enforces `scripts/ci_bookkeeping_gate.py` (PR `#346`), AST-based
`scripts/check_self_explaining.py` (PR `#357`), maintainer-actor verification on `module-budget-change` labels in
`scripts/check_module_budgets.py` (PR `#366`), and derived KB indexing with no committed `index.json`. `holon-coherence`
(`HEAD 18084f3`) still lacks these CI/hygiene guardrails and continues committing legacy
`holon-knowledge/kb/*/index.json` conflict magnets.

## Evidence

- `apps/holon-coherence/main/scripts/` contains only `check_ci_runtime_budget.py`, `check_module_budgets.py`,
  `ci_timing_gate.py`, `module_budget_base.py`, and `pre_commit_check.py` (no `ci_bookkeeping_gate.py`, no
  `check_self_explaining.py`, and no actor check on `module-budget-change`).
- `apps/holon-coherence/main/holon-knowledge/kb/failure_modes/index.json` and `patterns/index.json` remain tracked on
  `main` (unlike `holon-agentic-coder`, which uses derived indexing).
- Note: 3-ledger store/append-only checks and harness-reference checks for both repos are already tracked in Beans
  `0563` and `0564`.

## Proposed Change

1. Port `ci_bookkeeping_gate.py`, `check_self_explaining.py` (covering code + PR/ledger invariant rules cleanly), and
   `module-budget-change` maintainer-actor verification into `holon-coherence/scripts/` and `.github/workflows/`.
2. Remove the tracked legacy `holon-knowledge/kb/{failure_modes,patterns}/index.json` files (and ignore derived
   `index.json` if needed) so concurrent KB additions never collide.

## Acceptance Criteria

- `holon-coherence` CI enforces bookkeeping gating, self-explaining checks, and authorised budget-label checks on every
  PR.
- `holon-knowledge/kb/*/index.json` files are no longer tracked in `holon-coherence`.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Related shared-invariant beans: Bean `0563` (3 append-only ledgers check), Bean `0564` (no harness refs in targets),
  Bean `0558` (self-explaining gate), Bean `0570` (budget-change authorisation).
- Source: 2026-11-27 architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- Audit refresh (`2026-11-27`, `ce39bf34d`): `no-harness-references` (`#58`, Bean `0564`) landed; remaining work is
  `ci_bookkeeping_gate.py`, `check_self_explaining.py`, `module-budget-change` maintainer-actor verification, and
  removing tracked `holon-knowledge/kb/{failure_modes,patterns}/index.json`.
- Progress (`2026-11-27`): [PR #68](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/68)
  (`coherence-remove-kb-index-json`, merge commit `dbf76cd6`) merged into `main`, removing
  `holon-knowledge/kb/{failure_modes,patterns}/index.json` and adding `tests/test_no_kb_index_files.py`. Bean remains
  `in-progress` for `ci_bookkeeping_gate.py`, `check_self_explaining.py`, and `module-budget-change` maintainer-actor
  verification.
- Audit evidence (`2026-11-27`, `4a02926b`): Across `holon-coherence` PRs `#76`–`#82`, **`14` of `24` CI-tested heads
  (`58.3%`, `132` of `222` total check-runs)** were pure `chore(review)` / `chore(calibration)` bookkeeping commits that
  re-ran the full `9–10` job CI pipeline (`unit`, `integration`, `docker-build`, `make`, `hygiene`) on unchanged code
  for lack of `ci_bookkeeping_gate.py`.
- Audit evidence (`2026-11-27T15:46Z`, `4d2cfcf8`): Across `holon-coherence` PRs `#83`, `#67`, `#84`, `#85`, **`17` of
  `23` CI-tested heads (`73.9%`, `155` of `222` total check-runs = `69.8%`)** ran full CI on `chore(review)`,
  `chore(calibration)`, and `sync: merge target` commits (`unit (macos-latest)` taking `2.5–4.1 min` per bookkeeping
  head).
- parked 2026-11-27 (`coherence-bookkeeping-gate`): Stage 3 re-planned into `tests/test_scripts_self_doc.py` (enforcing
  `SCRIPTS_SELF_DOC_FILES` on `4d2cfcf8`) and parked at Stage 3 admission on open PR `#86` (`coherence-prune-self-doc`,
  which deletes `tests/test_scripts_self_doc.py`) (`CF-0066`); resume or re-cut cleanly once PR `#86` merges.
- **Audit evidence (`2026-11-28T00:01Z`, `bcad21c86e`):** Across `holon-coherence` PRs `#86..#88, #90..#94`, **`16/24`
  CI-tested heads (`66.7%`, `160/240` check-runs)** still ran full CI on `chore(review)` and `chore(calibration)`
  commits (taking up to `15.55 min` on `COH #88`'s `chore(calibration)`). `PR #86` (`6976c7b`) has now merged,
  unblocking `coherence-bookkeeping-gate` for resume/re-cut.
