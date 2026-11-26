---
# holon-agentic-coder-ref-metadata-0493
title: "An approved PR shows CLEAN but breaks main's hygiene after a budget-tightening merge"
status: todo
type: bug
priority: high
tags:
  - flow
  - ci
  - module-budget
  - holon-agentic-coder
created_at: 2026-11-26T07:55:00Z
updated_at: 2026-11-26T07:55:00Z
---

## Problem

PR #317 (merged 2026-11-26 07:50Z) froze module line budgets on every package. Two PRs that were already approved,
calibrated and `MERGEABLE`/`CLEAN` with green CI would have turned `main`'s hygiene check red if merged: #320 grows
`sandbox_executor/preflight.py` to 552 lines (frozen at 548) and #321 makes `flow/github/ci_final_head.py` 328 lines
(frozen at 299). GitHub reported both as clean because there was no textual conflict, and their CI had run against the
old base. Nothing in the flow or the harness flagged them; the coordinator first called #321 ready without checking.

## Proposed fix

- After any merge that changes `holon-config/hygiene/module_budgets.json` (or any lint/hygiene configuration), every
  open flow PR is re-checked against the new `main`: run the budget check on the PR head merged with `main`, and re-run
  the flow from review for each PR that fails.
- The `post-pr-merge` skill lists open PRs that the merge makes stale and resyncs them.
- Long term: CI requires the PR branch to be up to date with `main` for hygiene, or runs a merge-queue style check.
