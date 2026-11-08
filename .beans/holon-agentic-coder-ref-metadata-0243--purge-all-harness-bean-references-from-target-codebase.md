---
# holon-agentic-coder-ref-metadata-0243
title: "Purge all harness bean references and BEAN SAFETY HALT strings from holon-agentic-coder code and docs"
status: completed
type: task
priority: high
tags:
  - hygiene
  - isolation
  - rule-12
  - holon-agentic-coder
created_at: 2026-11-06T09:00:00Z
updated_at: 2026-11-08T11:01:15Z
---

## Problem

Under `AGENTS.md` Rule 12 (Target Repository Isolation & Zero Harness Path Leaks), target repositories
(`holon-agentic-coder` and `holon-coherence`) are independent, standalone software systems. They must never know about,
reference, or leak harness-specific tracking metadata or conventions (`.beans/`, `todo/`, `.agents/`).

Currently, numerous occurrences of the word `bean`, specific bean IDs (`Bean 0034`, `Bean 0019`, `Bean 0052`, etc.), and
runtime strings such as:

```text
[BEAN 0034 SAFETY HALT] Review Loop reached consensus approval.
[BEAN 0034 SAFETY HALT] Pipeline safely halted for human review (autonomous merge prohibited).
```

remain present across:

1. Runtime logs and CLI print messages (`cli/commands/flow.py`, `entrypoint/review_loop.py`, `flow.py`).
2. Module, class, and function docstrings across `sandbox_executor/`.
3. Test names, assertions, and test fixtures across `apps/sandbox-executor/tests/`.
4. Documentation files (`apps/sandbox-executor/README.md`, `docs/hermetic_testing.md`).

These references violate target isolation, leak external harness task IDs into production logs and code, and confuse
downstream consumers and agents.

## Goal

1. **Replace Runtime Output Strings**:
   - Change `[BEAN 0034 SAFETY HALT]` to `[SAFETY HALT]` or `[HUMAN MERGE SAFETY HALT]` across `cli/commands/flow.py`,
     `entrypoint/review_loop.py`, `flow.py`, and all test assertions.
2. **Remove Bean Mentions in Code and Docstrings**:
   - Audit all occurrences of `bean` / `Bean <id>` in `apps/sandbox-executor/src/` and replace or remove them with
     clean, target-native architectural descriptions (e.g. replace `(Bean 0124)` with nothing or
     `(centralised git operations)`).
3. **Clean Test Suites & Docs**:
   - Update test names, docstrings, and comments in `apps/sandbox-executor/tests/` and markdown files under
     `apps/sandbox-executor/` to use descriptive technical names instead of harness bean identifiers.
4. **Verification**:
   - Run `uv run task lint`, `uv run task lint-docs`, and `uv run task test` to ensure no tests break and all linters
     pass.

## Resolution

Holon flow completed all 5 stages (claude-agent / claude-fable-5; Stage 4 resumed from checkpoint after the driving
subagent was stopped mid-review). PR #141 raised, 3/3 ensemble consensus approved on iteration 1 (zero findings) and
posted once via the HTTP 422 `--comment` fallback, Stage 5 calibration included in the PR diff
(`plans/P-1794132519-claude-agent-claude-fable-5_calibration.md`, EV 46.33 predicted vs 53.17 actual, ΔEV +6.84). All CI
checks pass; PR is MERGEABLE/CLEAN and awaiting human merge:
https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/141
