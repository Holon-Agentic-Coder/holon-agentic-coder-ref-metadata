---
# holon-agentic-coder-ref-metadata-0459
title: "Maintainer rules kept only in one session's private memory never reach the other session"
status: completed
type: bug
priority: high
tags:
  - harness
  - instructions
  - coordination
  - antigravity
created_at: 2026-11-25T05:45:00Z
updated_at: 2026-11-25T06:05:00Z
---

## Problem

The Claude Code session keeps 34 maintainer rules in its private auto-memory (`~/.claude/projects/<workspace>/memory/`).
The Antigravity session never reads that directory. Several of those rules have no counterpart in `AGENTS.md` or
`.agents/`, so the Antigravity session cannot follow them, and it did not.

## Evidence (self-improvement audit, 2026-11-25T05:45Z)

- **"Intent scope lists files"** (memory: never put whole directories in intent scope; a globbed touch set blocks every
  flow). It is in no `.agents/` file, `AGENTS.md` or the `holon_flow` skill. The Antigravity intent for Bean 0407
  (`todo/intent-0407-no-unneeded-full-review.json`, 18 entries) lists `apps/sandbox-executor/tests/`. Stage 3 refused it
  at 02:41:40Z on 7 in-flight PRs and flows, and it is still refused at 05:41Z (about 180 min). Bean 0446 fixes the
  engine side; the rule itself is missing from the harness.
- **"Log a bean for every bug"**: no `.agents/` file says it.
- **"No human halt before merge"**: appears only in a script string of `prioritise_beans.py`.
- Bean 0411 already records that model ladders are written out in eight places; this is the same problem across
  sessions: a rule that lives in one place the other session cannot see.

## Proposed change

1. Go through the 34 memory files. Move each one that states a rule for the workspace (not a personal preference of one
   runtime) into its canonical `.agents/` file, following Bean 0411's one-canonical-place layout. In memory, keep only a
   pointer.
2. Put the intent-authoring rules in one place in `.agents/holon-flow.md`, linked from the `holon_flow` skill: scope
   lists files and never directories, no harness paths or bean ids in intent text, and slugs of at most 32 characters.
3. `run_holon_flow.py` refuses an intent whose `scope` entry is a directory, or ends in `/`, before Stage 1, so any
   session gets the same check.

## Expected gain

The Antigravity session follows the same rules. On Bean 0407 alone that saves about 180 min of refused Stage 3 and a
relaunch. Each new rule is written once, in a place both sessions read.

## Cost

Small, harness only. Step 3 is a few lines in `.agents/skills/holon_flow/scripts/run_holon_flow.py`.

## Notes

- Related: Bean 0411 (contradicting instructions), Bean 0446 (SPLIT parent admission), Bean 0423 (two sessions).

## Resolution

Reviewed all 33 memory files. Added to the shared instructions (each attributed to the maintainer with its memory date):

- `.agents/holon-flow.md` ("Intent Authoring and Running Rules"): scope lists files; no harness paths or bean ids in
  intent text; 32-character slugs; never stop a running flow; no human halt before merge; diagnose failures at once;
  rerun on end conflict.
- `.agents/coordination.md` (section 7): harness ops via skill subagents, escalated conflicts, subagent naming, main
  thread delegates.
- `.agents/pr-merging.md`: post-merge via the post-pr-merge skill in a lowest-tier subagent.
- `.agents/workflows.md`: log a bean for every bug; beans live in the main checkout's `.beans/`.
- `.agents/engineering-rules.md` (rule 16): module budgets force a split.
- `.agents/skills/holon_flow/scripts/run_holon_flow.py`: refuses an intent whose scope has a directory entry (test in
  `tests/test_flow_scope_files.py`).

Not added: "resolve a conflict the moment it is found", "only success postings wait for the pipeline", "fail early" and
the ledger merge-order rule have no memory text, so they could not be checked. Note `.agents/engineering-rules.md` rule
14 says to interleave ledger rows chronologically, which conflicts with the stated "keep main's order, append only"
rule; needs the maintainer's wording. Bean 0411 still owns the cross-runner switching contradiction (holon-flow.md,
instructions.md, workflows.md say switch automatically; the skill and the memory say ask first). The AGENTS.md
Antigravity default already reads `gemini-4-neon` in the working tree.

- Progress (2026-11-25): added "Flow principles (maintainer, 2026-11-24)" to `.agents/holon-flow.md`; rewrote the ledger
  conflict rule (main's order kept, only the branch's rows appended) in engineering-rules, workflows, instructions and
  the holon_flow, resolve_conflict and pr_review_loop skills; aligned runner switching with the skill (see Bean 0411).
  Open: resolve_known.py and a prompt string in run_holon_flow.py still interleave; noted on Bean 0436.
