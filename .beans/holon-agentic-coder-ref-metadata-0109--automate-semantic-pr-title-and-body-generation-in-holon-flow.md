---
# holon-agentic-coder-ref-metadata-0109
title: "Automate semantic PR title and structured description generation in Holon flow"
status: completed
type: task
priority: normal
tags:
  - holon-flow
  - pr-creation
  - metadata
  - automation
created_at: 2026-10-17T04:15:00Z
updated_at: 2026-10-17T14:00:00Z
---

Automate the generation of conventional semantic Pull Request titles and structured markdown summaries during autonomous
PR creation in the Holon flow.

## Context

- During PR #52 review (Finding PO-01), the PR was created with a placeholder title `docs: wip` and an empty body,
  requiring an extra iteration step in the review loop to correct PR metadata.
- When `holon flow` raises a Pull Request via `gh pr create` after Stage 3 (Execute), it has full access to the intent
  payload (`I-...`), plan milestones (`P-...`), and execution commit diff (`E-...`).
- Standardising automated generation of rich semantic titles (`feat(...)`, `fix(...)`, `docs(...)`) and structured
  markdown descriptions provides immediate context for human maintainers, automated CI gates, and reviewer ensemble
  passes.

## Tasks

- [x] Implement a PR description builder in `sandbox_executor/flow.py` (or CLI PR creator helper) that compiles:
  - Intent objective and user motivation.
  - Plan overview and acceptance criteria.
  - Execution commit summary and affected components.
  - Verification commands and automated test results.
- [x] Derive a conventional commit title from the intent slug and primary change category.
- [x] Pass the generated title and body file to `gh pr create --title ... --body-file ...`.
- [x] Add unit and mock tests validating PR metadata generation.
- [x] Document the automated PR description convention in `.agents/workflows.md`.

## Resolution

Implemented via 5-stage Holon flow on `holon-agentic-coder` in PR
[#82](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/82).

- Added `generate_semantic_pr_metadata` in `sandbox_executor/flow.py` mapping categories to conventional commit prefixes
  (`feat`, `fix`, `docs`, `chore`, etc.) and generating structured markdown sections: Summary, Key Changes, Referenced
  Beans, and Plan & Validation Metadata.
- Added `create_or_update_pr` helper to automate PR creation or update via GitHub CLI with extracted PR numbers.
- Added hermetic unit tests in `apps/sandbox-executor/tests/test_flow.py` covering prefix mapping, scope sanitization,
  and structured section formatting.
- 3-agent ensemble consensus approved (0 Critical, 0 Important, 0 Nit). Calibration executed and included in PR.
