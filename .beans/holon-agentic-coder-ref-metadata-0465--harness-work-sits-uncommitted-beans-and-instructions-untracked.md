---
# holon-agentic-coder-ref-metadata-0465
title: "Harness beans, skills and the audit instruction sit uncommitted in the working tree"
status: todo
type: bug
priority: high
tags:
  - harness
  - git
  - hygiene
created_at: 2026-11-25T22:49:00Z
updated_at: 2026-11-25T22:49:00Z
---

## Problem

The harness branch carries 86 uncommitted paths: 49 modified tracked files (49 files, +1829/-315 lines, including 17
under `.agents/`, skills and their tests) and 37 untracked paths. Of those, 30 are untracked beans (for example 0389
to 0420) and `.agents/self-improvement-audit.md`, the file `AGENTS.md` names as the audit's rule, is itself untracked
(`git ls-files` returns nothing), as is `.agents/scripts/beans_to_issues.py`. A fresh clone or a second worktree does
not see them; one `git clean` or checkout loses them. Peer sessions also trip on the unstaged files (Bean 0440, the
pre-commit Prettier check).

## Evidence (self-improvement audit, 2026-11-25T22:49Z)

- `git status --short`: 49 `M`, 37 `??`; `git ls-files --others --exclude-standard .beans | wc -l` gives 30.
- Last commit touching `.beans/`: 2026-11-25T17:59:50+11:00; the beans written since by the audits and by sessions were
  never committed.
- Related: Bean 0459 (rules kept only in one session's memory) is the same failure on another channel.

## Proposed change

- Commit each bean on creation: have the bean-writing step (and the audit) stage and commit only its own new files,
  never with other paths.
- Session start reports the count of uncommitted harness paths and commits or names them before new work.
- Ask the maintainer to decide on the 49 modified files now; do not commit them from an audit.

## Expected gain and cost

No lost beans or rules, and a harness a second session can actually read. Cost: one small commit per bean and one check
at session start.

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- Still present at `2026-11-26T03:50Z`: `30+` untracked beans (`0389`–`0474`), untracked
  `.agents/self-improvement-audit.md` and `.agents/scripts/beans_to_issues.py`, `48+` modified harness files, and a
  stray zero-byte untracked root file `=2026-11-24T08:00:00Z`.
