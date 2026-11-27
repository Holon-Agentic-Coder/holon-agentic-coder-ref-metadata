---
# holon-agentic-coder-ref-metadata-0597
title: "Flow PR body still shows Agent and Model as N/A after PR #367"
status: todo
type: bug
priority: normal
tags:
  - flow
  - github
  - pr-metadata
  - holon-agentic-coder
created_at: 2026-11-27T00:58:24Z
updated_at: 2026-11-27T01:07:06Z
---

## Cause

PR #367 (bean 0560) merged with `Agent: N/A` and `Model: N/A` still in the body of the PR
(`gh pr view 367 --json body`). `FlowContext` defaults `agent` and `model` to non-empty values, so the runner that
`_semantic_pr_text` now passes is not empty. The fix therefore does not reach the path that wrote the merged body. Only
`flow/review/loop.py:260` calls `_semantic_pr_text`; confirm which code path creates or edits the PR body before
changing anything.

## Fix

- Make every flow PR body write (creation and review-loop edits) render the runner that planned the flow.
- Keep the plan-payload precedence and render `N/A` only for a value genuinely absent everywhere.

## Acceptance

- A new flow PR shows the real agent and model (e.g. `claude-agent` / `claude-opus-5-5`) in "Plan & Validation Metadata"
  on the PR as it appears on GitHub.
- A test drives the PR body write path with a plan record loaded from a real plan file (not an inline dict) and asserts
  the agent and model lines.
- `N/A` appears only when the value is genuinely unknown.
- No docstrings or comments except `# why:`.
