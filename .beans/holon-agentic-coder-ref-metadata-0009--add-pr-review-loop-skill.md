---
# holon-agentic-coder-ref-metadata-0009
title: Add autonomous pr-review-loop skill using fresh subagents
status: completed
type: feature
created_at: 2026-07-26T00:00:00Z
updated_at: 2026-07-26T00:00:00Z
---

Create a new agent skill `pr-review-loop` that orchestrates an autonomous PR review and resolution loop. The skill
spawns fresh subagents for each review pass (`pr-reviewer`) and resolution pass (`pr-review-resolver`), pushing resolved
commits back to the remote feature branch until the PR is approved or the max iteration cap (default 10) is reached.

## Notes

- Design decisions aligned with user via /grill-me session.

## Assignment

Assignee: `antigravity`

## Resolution

Created `.agents/skills/pr_review_loop/SKILL.md` detailing parameter parsing, fresh subagent orchestration for reviewer
and resolver passes, exit conditions (PR approval or max iteration cap), and remote branch synchronization.
