---
# holon-agentic-coder-ref-metadata-0007
title: Create comprehensive PR review prompt with dynamic role activation
status: completed
type: task
created_at: 2026-07-18T00:00:00Z
updated_at: 2026-07-18T00:00:00Z
---

Write a comprehensive prompt template/system prompt for executing a PR review. The prompt should define a comprehensive
set of engineering and architect roles, and instruct the model to dynamically activate the relevant roles depending on
the contents/changes in the PR.

## Notes

- Include roles like Principal Engineer, Solution Architect, Data Engineer, Security Architect, Frontend Engineer,
  DevOps/SRE, QA, etc.
- The prompt should dynamically determine which roles should be activated based exclusively on the files that have
  changed in the diff.

## Assignment

Assignee: `antigravity`

## Resolution

Created a comprehensive, multi-role PR review prompt containing 17 technical and cross-functional roles across 5
distinct categories. The prompt is committed at
[.agents/prompts/pr_review_prompt.md](.agents/prompts/pr_review_prompt.md), with temporary copies stored as artifacts
and inside the `todo/` scratchpad.
