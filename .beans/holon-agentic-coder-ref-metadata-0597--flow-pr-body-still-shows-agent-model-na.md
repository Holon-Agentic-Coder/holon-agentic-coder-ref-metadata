---
# holon-agentic-coder-ref-metadata-0597
title: "Flow PR body still shows Agent and Model as N/A after PR #367"
status: completed
type: bug
priority: normal
tags:
  - flow
  - github
  - pr-metadata
  - holon-agentic-coder
created_at: 2026-11-27T00:58:24Z
updated_at: 2026-11-27T05:15:52Z
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

## Resolution

Delivered via [PR #377](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/377) and merged into `main`
(`c51be37b`, `2026-11-27T05:08:05Z`):

- **Key Architectural Deliverables**: Updated `apps/sandbox-executor/src/sandbox_executor/flow/github/pr_metadata.py`
  (`_PLACEHOLDER_VALUES`, `_is_real_value`, `_first_present`) so placeholders (`N/A`, `n/a`, `na`, `none`, `null`,
  `unknown`, `-`) never shadow a real value in a lower-precedence source (plan payload -> runner -> intent -> `N/A`),
  and extracted `_planning_runner` in `apps/sandbox-executor/src/sandbox_executor/flow/review/ensemble.py` so every PR
  body create and review-loop edit passes the planning runner. Verified on GitHub: PR `#377` (and subsequent PRs `#378`,
  `#379`, `#381`, `#386`, `#387`, `#388`, `#391`) render `Agent: claude-agent` and `Model: claude-opus-5-5`.
- **Verification & Tests**: Added `apps/sandbox-executor/tests/test_pr_body_real_agent_model.py` driving `plan_metrics`
  / `plan_stage_payload` from a real plan file on disk across both create and edit paths (`uv run task test` 9552
  passed, 7 skipped; `uv run task lint` passed in `E-1795742362-CLA-CO5.5`).
- **Post-Merge Cleanup**: Worktree `flow-pr-body-real-agent-model` and its flow/remote branches pruned at
  `2026-11-27T05:14:20Z`.
