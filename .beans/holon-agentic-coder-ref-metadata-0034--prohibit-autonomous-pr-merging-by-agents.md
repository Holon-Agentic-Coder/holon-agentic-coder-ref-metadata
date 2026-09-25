---
# holon-agentic-coder-ref-metadata-0034
title: "Prohibit autonomous PR merging by agents"
status: completed
type: task
priority: high
tags:
  - instructions
  - pr-review
  - security
created_at: 2026-09-26T01:25:00Z
updated_at: 2026-09-26T03:00:00Z
---

Update agent instructions, rules, workflows, and PR review skills across the repository to strictly prohibit autonomous
Pull Request merging by AI agents. Merging must exclusively be performed by a human maintainer.

## Notes

- User requested explicit control over when PRs get merged after noticing PR #55 was merged autonomously.
- Prohibits commands such as `gh pr merge` (with `--squash`, `--rebase`, `--merge`, `--auto`, etc.), `gh api` calls to
  merge endpoints, and enabling repository auto-merge settings (`allow_auto_merge`).
- After consensus review passes, agents must stop and hand off to the human maintainer with instructions on manual
  merging.

## Resolution

Updated all instruction and skill files to enforce the human-only PR merge constraint:

- `AGENTS.md`: Updated Incoming Agent Checklist step 7 and added a dedicated `## 🔒 PR Merging — Human-Only` constraint
  section.
- `.agents/workflows.md`: Updated step 5 (Pull Requests & Pushing) with an explicit CAUTION block detailing forbidden
  merge commands and hand-off protocol.
- `.agents/rules.md`: Added Invariant 11 ("Human-Only Pull Request Merging Invariant") to permanent engineering
  learnings and invariants.
- `.agents/skills/pr_review_loop/SKILL.md`: Added Principle 7 (Human-Only PR Merging Boundary) and updated Case 1 to
  stop and notify the human for manual merging without calling `gh pr merge`.
- `.agents/skills/pr_reviewer/SKILL.md`: Added CAUTION block to Step 4 prohibiting PR merging upon completing review
  submission.
- `.agents/skills/pr_review_resolver/SKILL.md`: Added CAUTION block to Step 5 prohibiting PR merging.
- `.agents/prompts/pr_review_prompt.md`: Clarified overall approval verdict to emphasize that merging is performed by
  the human maintainer.
