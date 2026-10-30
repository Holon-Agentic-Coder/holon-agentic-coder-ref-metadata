---
# holon-agentic-coder-ref-metadata-0221
title: "Standardise Review Loop Agent output with skill consensus template"
status: todo
type: task
priority: high
tags:
  - review-loop
  - prompts
  - consensus-report
  - holon-agentic-coder
created_at: 2026-10-30T09:55:00Z
updated_at: 2026-10-30T09:55:00Z
---

## Problem

The native containerised Review Loop Agent and report generator in `holon-agentic-coder` produce an output format that
diverges from the production consensus review template established by the harness `pr-review-loop` skill.

The `pr-review-loop` skill consistently posts clean, structured, and informative reviews:

```markdown
## ✅ Ensemble Consensus Review — APPROVED (3/3)

Three independent blind review passes evaluated this PR at head `920e4d9` and unanimously approve it with zero Critical,
zero Important, and zero open Nit findings. All CI checks are green and the PR is mergeable/clean against `main`.

**Verified:**

- Decomposed monolithic src/holon_coherence/mitm_addon.py (2,348 lines) into modular components under
  src/holon_coherence/proxy/ by concern: scrubbing.py, wire_log.py, timing.py, metrics.py, routing.py, dashboard.py,
  normalise/anthropic.py, translation/gemini_openai.py, and addon.py.
- Preserved backward compatibility: src/holon_coherence/mitm_addon.py re-exports all 21 public API symbols and addons =
  [MitmproxyAddon()], along with dynamic compatibility dispatch for legacy monkeypatch targets (in_container,
  resolve_gateway_address, ctx, log_telemetry, _proxy_own_ports).
- Added modular unit tests under tests/proxy/ for all newly extracted proxy submodules while keeping legacy test suites
  100% passing.
- Quality gates: uv run task lint clean, npx prettier --no-config --check clean, uv run task test 1,037 passed with zero
  failures.
- Complexity baseline ratchet ceiling and repository hygiene verified.
- Canonical 3-ledger provenance integrity strictly maintained.

Stage 5 calibration will be added to this PR before merge. Merging remains with the human maintainer.
```

In contrast, `sandbox_executor.review_report.build_pr_review_consensus_report()` in `holon-agentic-coder` produces a
mechanical report (`## Holon PR Review: <title> (iteration <n>)` with unformatted reviewer lists and checks sections),
and the older `holon-config/prompts/review_loop.template.md` contained an obsolete persona table schema.

## Analysis: Requirements to Produce the Review Loop Template

To enable the native Review Loop Agent and Stage 4 orchestrator to consistently produce this review template, four
architectural requirements must be satisfied:

### 1. Prompt Template Alignment (`holon-config/prompts/review_loop.template.md`)

- Define the standard schema for both `APPROVED` (unanimous 3/3, 0 Critical, 0 Important, 0 open Nits, green CI) and
  `CHANGES_REQUESTED` (findings table).
- Provide explicit instructions for synthesizing the `**Verified:**` section from:
  - Key architectural refactorings and module extractions identified in the PR diff.
  - Backward compatibility preservation (re-exports, dispatch compatibility, CLI flags).
  - Test suite coverage and execution pass counts (`uv run task test`).
  - Lint and formatting quality gates (`uv run task lint`, `prettier`).
  - Complexity baseline ratchet ceiling and repository hygiene.
  - Canonical 3-ledger provenance integrity (`intents.jsonl`, `plans.jsonl`, `executions.jsonl`).
- Include standard closing notice:
  `Stage 5 calibration will be added to this PR before merge. Merging remains with the human maintainer.`

### 2. Python Report Generator Alignment (`sandbox_executor/review_report.py`)

- Update `build_pr_review_consensus_report()`:
  - When approved: render `## ✅ Ensemble Consensus Review — APPROVED ({configured}/{configured})`, the evaluation
    summary paragraph (`Three independent blind review passes evaluated this PR at head {head}...`), the bulleted
    `**Verified:**` list, and the human merge notice.
  - When changes requested: render `## ❌ Ensemble Consensus Review — CHANGES REQUESTED (Iteration {iteration})`
    followed by the structured findings table (`ID`, `Severity`, `File:Line`, `Description`, `Recommendation`).
- Ensure all text passed into the template continues to be strictly sanitized and bounded via `_inline()`.

### 3. Synthesis & Transport Seam (`entrypoint/review_loop.py` & `flow.py`)

- Wire verified findings and evaluation highlights produced by the containerised reviewer ensemble through the result
  transport back into `build_pr_review_consensus_report()`.
- Ensure dual-posting (`post_pr_review_consensus()`) formats and submits this markdown body for official PR review and
  discussion comments.

### 4. Hermetic Test Verification

- Update `apps/sandbox-executor/tests/test_review_report.py` to assert the new headers, `**Verified:**` section, and
  closing boundary notice.
- Update `apps/sandbox-executor/tests/test_prompt_templates.py` to ensure placeholder hygiene.
- Update `apps/sandbox-executor/tests/test_review_loop.py` and `test_flow.py` to verify mock consensus report assertions
  pass cleanly.

## Scope

1. **Prompt Template**: Align `holon-config/prompts/review_loop.template.md` with the skill consensus schema.
2. **Report Generator**: Update `apps/sandbox-executor/src/sandbox_executor/review_report.py` to render the skill
   consensus format.
3. **Tests**: Update test suites across `test_review_report.py`, `test_prompt_templates.py`, and `test_flow.py`.
4. **Formatting & Hygiene**: Run Prettier and `uv run task lint` across changed files.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be executed via the 5-stage Holon flow (`holon flow <intent.json>`).
- Depends on Bean 0179 (PR #116) for container review routing; sequence after PR #116 merges to prevent merge conflicts
  on `flow.py` and `entrypoint/review_loop.py`.
- Target repository isolation (Rule 12): No references to harness paths (`.beans/`, `todo/`, `.agents/`) or bean IDs in
  target code or commits.
