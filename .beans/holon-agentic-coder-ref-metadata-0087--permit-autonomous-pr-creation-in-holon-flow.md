---
# holon-agentic-coder-ref-metadata-0087
title: "Permit autonomous Pull Request creation when executing the Holon flow"
status: completed
type: task
priority: normal
tags:
  - harness
  - rules
  - holon-flow
  - pr-lifecycle
created_at: 2026-10-12T08:35:00Z
updated_at: 2026-10-12T08:35:00Z
---

## Summary

Update workspace rules and agent operating guidelines across `AGENTS.md`, `.agents/workflows.md`, and `.agents/rules.md`
to permit autonomous Pull Request creation when executing the full Holon flow lifecycle.

Previously, rule 7 in `AGENTS.md` and rule 5 in `.agents/workflows.md` stated that Pull Request creation stayed with the
human maintainer unless explicitly instructed otherwise. Because the 5-stage Holon flow requires an active Pull Request
to execute Stage 4 (`pr-review-loop`), requiring manual PR creation interrupted the flow between Stage 3 (Execute) and
Stage 4.

Under this update:

- **Autonomous PR Creation in the Holon Flow**: When executing the Holon flow pipeline, the agent autonomously creates
  the Pull Request (`gh pr create`) upon completion of Stage 3 (Execute) so Stage 4 (`pr-review-loop`) can execute
  without manual interruption.
- **Non-Flow Work Unchanged**: Hand-authored worktree branches and standalone harness branches continue to require
  maintainer instruction before raising a PR.
- **Human-Only Merge Invariant Preserved**: The non-negotiable invariant that **PR merging is strictly human-only**
  remains fully enforced across all repositories and roles without exception.

## Changes

1. **`AGENTS.md`**:
   - In the Holon flow table, explicitly note autonomous PR creation as the transition between Stage 3 and Stage 4.
   - In Section 5 (Incoming Agent Checklist, item 7), grant autonomy for raising PRs when executing the Holon flow.
2. **`.agents/workflows.md`**:
   - In Step 5 (Pull Requests & Pushing), clarify that Holon flow execution autonomously opens the PR targeting the base
     branch for Stage 4 review.
3. **`.agents/rules.md`**:
   - Under Rule 11 (Human-Only PR Merging Invariant), add explicit guidance that autonomous PR creation is permitted
     during flow execution while merging remains strictly human-only.
