---
# holon-agentic-coder-ref-metadata-0580
title: "Brief builder: resolve slug, PR state and time from live state, embed the standing preamble"
status: todo
type: task
priority: high
tags:
  - harness
  - coordination
  - subagents
created_at: 2026-11-26T23:51:36Z
updated_at: 2026-11-26T23:51:36Z
---

## Evidence (coordinator failure ledger, repeated categories)

- `brief` is the most repeated category: CF-0012, 0013, 0014, 0015, 0018, 0019 (6 of 22). `verification` x4 (CF-0008,
  0011, 0017, 0022), `readiness-check` x3, `bookkeeping` x3.
- CF-0019: post-merge brief carried a slug from memory (`main-push-tree-gate`; real head `main-push-superseded-skip`).
  CF-0007: figures copied from a previous brief. CF-0018: wrapper run inline despite the skills rule. This audit's own
  brief had to be told timestamps and git safety again; bean 0556 put the preamble in text but each brief still re-types
  it.

## Change

- `.agents/scripts/make_brief.py <kind> <pr-number>` for post-merge, resume, audit and review briefs: reads
  `gh pr view --json headRefName,state,mergedAt`, derives slug and worktree, checks the PR is not queued or merged
  before a resume brief (CF-0021), embeds the git-safety and clock preamble verbatim, and prints the clock-read time.
- Coordinator uses it instead of free text; the skill names it.
- Test: a merged PR yields a post-merge brief with the head-branch slug and refuses a resume brief.

## Expected gain

Removes the largest recurring failure category by construction. Cost: one script, tests, skill text.
