---
# holon-agentic-coder-ref-metadata-0003
title: Develop validation script for agent links and rules
status: completed
type: task
created_at: 2026-07-18T00:00:00Z
updated_at: 2026-07-18T00:00:00Z
---

Write a script (e.g. Node.js or Python) that runs checks on AGENTS.md, README.md, and all files under the .agents/
folder to verify that referenced relative file links actually exist in the workspace and are not broken.

## Assignment

Assignee: `antigravity`

## Resolution

Created .agents/scripts/validate-links.js Node.js script. Configured it to run as part of the local git pre-commit hook
and added a step in the GitHub Action (.github/workflows/markdown-lint.yml) to run it in CI. Tested it locally and
confirmed it passes successfully with zero errors.
