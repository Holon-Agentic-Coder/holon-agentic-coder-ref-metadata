---
# holon-agentic-coder-ref-metadata-0220
title: "Remove GitHub-specific PR wording; standardize on Review Loop and Change Diff"
status: todo
type: task
priority: normal
tags:
  - cli
  - flow
  - review-loop
  - terminology
  - holon-agentic-coder
created_at: 2026-10-30T09:05:09Z
updated_at: 2026-10-30T09:05:09Z
---

## Problem

Throughout `holon flow`, the CLI help text, role prompts, logs, and internal modules, Stage 4 is frequently described as
the "PR review loop" and references "PR", "PR diff", "PR description", and "PR merging":

- In `holon flow --help`:
  ```text
  --skip-review         Skip Stage 4 (PR review loop) and proceed to calibration.
  ```
- In `flow.py`, `cli.py`, `review_report.py`, and `review_ensemble.py`:
  - "Stage 4 (PR Review Loop)"
  - "PR review consensus"
  - "PR description" / "PR body" / "PR title"
  - "Human-Only PR Merging"

"PR" (Pull Request) is GitHub-specific wording (GitLab uses Merge Request, Gerrit uses Change, plain Git uses branches
and patches). Holon Flow is Git-native, branch-based (`I-.../_`, `P-.../_`, `E-.../_`, `/calibrated`), and
provider-agnostic. Tying core flow and CLI concepts to "PR" leaks external platform terminology into the domain
language.

## Scope & Implementation Plan

1. **CLI Help Text & Flags**:
   - Update `cli.py` and `flow.py` argparse descriptions:
     - Change `--skip-review` help: From: `Skip Stage 4 (PR review loop) and proceed to calibration.` To:
       `Skip Stage 4 (review loop) and proceed to calibration.`
     - Review all other CLI flag help strings in `holon flow` and `holon review` to replace "PR" with "review" or
       "change branch / target branch" where applicable.

2. **Flow Engine & Domain Terminology**:
   - In `apps/sandbox-executor/src/sandbox_executor/flow.py`:
     - Standardize stage names and logging:
       - `Stage 4: Review Loop` (not `Stage 4: PR Review Loop`).
       - `Review consensus` (not `PR review consensus`).
       - `Human-Only Merging Boundary` (not `Human-Only PR Merging`).
   - In `apps/sandbox-executor/src/sandbox_executor/review_report.py`:
     - Update module docstrings and headings from "The Stage 4 PR review consensus report" to "The Stage 4 review
       consensus report".
   - In `apps/sandbox-executor/src/sandbox_executor/review_ensemble.py` & `review_target.py`:
     - Keep GitHub adapter functionality (resolving a numerical PR identifier via `gh` when interacting with GitHub
       remotes), but decouple the core interface:
       - Rename prompt field labels and templates from `PR description:` / `PR diff:` to `Change description:` /
         `Review diff:`.
       - Decouple review target resolution docstrings so that a target is described as a branch, change ref, or optional
         remote PR reference.

3. **Role Prompts & Scaffolding**:
   - In `apps/sandbox-executor/src/sandbox_executor/scaffold.py` and `holon-config/prompts/review_loop.template.md`:
     - Update prompt instructions: evaluate the change diff against the plan and intent (replacing "Evaluate the Pull
       Request diff").
     - Replace `{pr_title}` / `{pr_description}` placeholders with `{change_title}` / `{change_description}` (keeping
       backward-compatible fallbacks if needed).

4. **Test Suite Alignment**:
   - Update tests in `test_cli.py`, `test_flow.py`, `test_review_ensemble.py`, and `test_review_target.py` that assert
     on CLI help output or log messages containing "PR review loop" to expect "review loop".

## Acceptance Criteria

1. `holon flow --help` displays `Skip Stage 4 (review loop) and proceed to calibration.` with no mention of "PR review
   loop".
2. Flow execution logs and console summaries display `Stage 4: Review Loop` and `review consensus` without referring to
   "PR review loop".
3. Prompt templates and scaffolded reviewer prompts describe changes as change diffs and change descriptions rather than
   PR diffs.
4. GitHub CLI interactions (e.g. `gh pr view`, `gh pr review`) remain functional as the remote transport adapter, but
   the core engine vocabulary is platform-agnostic.
5. All test suites pass cleanly under `uv run pytest`.
