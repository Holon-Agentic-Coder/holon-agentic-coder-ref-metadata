---
# holon-agentic-coder-ref-metadata-0556
title: "Standing subagent brief preamble: no git stash, no --no-verify, no git add -A, no main-worktree measuring"
status: todo
type: task
priority: high
tags:
  - harness
  - subagents
  - coordinator-failures
created_at: 2026-11-27T00:30:00Z
updated_at: 2026-11-27T00:30:00Z
---

## Problem (repeat category, high priority)

The coordinator ledger shows the category `brief` four times in one day (CF-0012, CF-0013, CF-0014, CF-0015) and
`bookkeeping`/`verification` twice each (CF-0007/CF-0010, CF-0008/CF-0011). Each rule breach by a subagent traces to a
brief that did not state a rule that already exists somewhere:

- `git stash` by a resume subagent (CF-0014, PR #353 flow): forbidden in `.agents/skills/pr_review_loop/SKILL.md` and
  the main-worktree rule, but not in the generic brief.
- `git commit --no-verify` by a harness fix subagent (CF-0015, commit 27bdb6b on PR #62): the string `--no-verify`
  appears nowhere in `.agents/*.md` or the skills; the rule exists only in the session instructions.
- `git add -A` by concurrent post-merge subagents (CF-0010, commit 89a2e56): `.agents/workflows.md` line 311 forbids it,
  but the brief for the post-merge skill said to use it.
- Measuring in the main worktree (CF-0011), against the AGENTS.md hard rule.

## Proposal

1. Add one fixed "git safety" preamble to `.agents/subagents.md` that every brief includes verbatim: never `git stash`;
   never `--no-verify` (if a hook fails on a file you did not change, format only that file with prettier or stop and
   report); stage by explicit path, never `git add -A` or `git add .`; never check out, build or measure in a main
   worktree; uncommitted work you must set aside is saved as a patch file and, if the tree must be clean, a temporary
   WIP commit.
2. Fix the `post_pr_merge` skill so it stages an explicit file list (no `git add -A`), and add `--no-verify` to the
   forbidden list in `.agents/worktrees-and-git.md`.
3. Add a one-line check to the coordinator readiness list: the brief contains the preamble.

## Expected gain

Removes the four breaches seen today (no loss occurred, but each risked another session's work). Cost: one paragraph and
two skill edits.

## Resolution
