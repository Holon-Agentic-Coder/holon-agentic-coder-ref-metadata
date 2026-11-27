---
# holon-agentic-coder-ref-metadata-0560
title: "PR body 'Plan & Validation Metadata' shows Agent and Model as N/A"
status: in-progress
type: bug
priority: normal
tags:
  - flow
  - github
  - pr-metadata
  - holon-agentic-coder
created_at: 2026-11-26T23:04:48Z
updated_at: 2026-11-27T00:58:24Z
---

## Instruction (maintainer, 2026-11-27)

"In the summary the agent and model is empty … make a bean to fix this." Example from PR #344:

```text
Plan & Validation Metadata
Plan ID: P-1795696276-CLA-CO5.5
Expected Value (EV): 39.27
Agent: N/A
Model: N/A
```

## Cause (from origin/main)

`apps/sandbox-executor/src/sandbox_executor/flow/github/pr_metadata.py` `_plan_metadata_lines` (around line 108) reads
`plan_meta.get("agent") or intent_data.get("agent", "N/A")` and the same for `model`. The plan metadata handed in
carries `plan_id` and `ev` but not the agent or model, and intents do not carry them, so both fall back to `N/A` —
although the flow knows them (the plan id even encodes them: `CLA-CO5.5` = claude-agent / claude-opus-5-5, and the plan
file's "created by claude-agent (claude-opus-5-5)" commit).

Callers:

```text
origin/main:apps/sandbox-executor/src/sandbox_executor/flow/github/pr_metadata.py:127:def generate_semantic_pr_metadata(
origin/main:apps/sandbox-executor/src/sandbox_executor/flow/review/ensemble.py:40:        return generate_semantic_pr_metadata(context.intent_data, plan_metadata=plan_meta)
```

## Fix

- Pass the planning runner's agent and model (the ones recorded for the plan) into the plan metadata at every caller of
  `generate_semantic_pr_metadata`; prefer the recorded plan/execution values over the intent.
- Never render `N/A` when the flow knows the runner; if the PR is later driven by a different runner (review/resolver on
  a fallback model), list the planning agent/model (and optionally the executing one) explicitly.
- Self-explaining code invariant: no docstrings, no comments except `# why:`.

## Acceptance

- A new flow PR shows the real agent and model (e.g. `claude-agent` / `claude-opus-5-5`) in "Plan & Validation
  Metadata".
- Unit test covering the PR body with plan metadata from a real plan record; test that `N/A` appears only when the value
  is genuinely unknown.

## Flow status (2026-11-27)

Flow ran to the merge boundary: PR #367 approved 3/3 (review iteration 1), calibrated, CI green, MERGEABLE/CLEAN,
awaiting human merge. The first execute push was refused by the remote with no reason; the kept commits were republished
from refs/holon/recovery and Stage 3 was rerun from the checkpoint. The orphan branch
I-1795738057-pr-metadata-real-agent-model/P-1795738135-CLA-CO5.5/E-1795738289-CLA-CO5.5/_ stays on origin and should be
deleted in post-merge cleanup.

## Post-merge acceptance check (2026-11-27)

PR #367 merged into `main` as `6e6cec045e968f8008a5aeeadc858486049c3f5d`. Against the merged diff:

- Not delivered: the merged PR body still reads `Agent: N/A` and `Model: N/A`, so the first acceptance item is unmet.
  Follow-up in bean 0597.
- Partly delivered: unit tests cover the runner fallback and the N/A cases, but the plan record used in
  `test_pr_metadata.py` and `test_ensemble.py` is an inline dict, not a real plan record, so the second item is unmet.
- Code adds no docstrings and no comments (0 added lines of `"""` or `#`), so nothing for bean 0153.

Bean stays `in-progress` until bean 0597 delivers the real PR body and a plan-record fixture.
