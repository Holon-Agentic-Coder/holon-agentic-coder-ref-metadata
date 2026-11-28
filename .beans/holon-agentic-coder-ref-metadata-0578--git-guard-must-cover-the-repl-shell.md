---
# holon-agentic-coder-ref-metadata-0578
title: "Git guard and hooks must cover the REPL shell, not only the Bash tool"
status: todo
type: bug
priority: high
tags:
  - harness
  - hooks
  - git
created_at: 2026-11-26T23:51:36Z
updated_at: 2026-11-26T23:51:36Z
---

## Evidence

- `.claude/settings.json` registers `git_guard.py --hook` under `PreToolUse` with matcher `Bash` only. Subagents commit
  through the REPL `$` shell (bean 0577: the CF-0021 commit used plain `git commit -m` there), which the matcher never
  sees.
- Beans 0566 and 0577 mention this only as a side note; neither has it as a task, so it can close with the gap open.
- Ledger repeats: CF-0010, CF-0014, CF-0015 are all git-safety breaches by subagents.

## Change

- Extend the matcher to `REPL` and make `git_guard.py` parse the script text (`$\`...\``, `$("...")`) for `git
  stash`, `--no-verify`, `add -A`/`add .`, force-push and flow-branch rebase.
- Prepend `.agents/bin` to PATH inside the REPL shell environment so the wrapper catches what the text parse misses
  (variables, composed strings).
- Test: each forbidden form refused through a REPL-shaped payload; allowed forms pass.
- Register in the invariant registry next to the 0566 entry.

## Expected gain

Closes the only route the guard does not see; removes reliance on briefs (CF-0014, CF-0015). Cost: one hook entry, one
parser branch, tests.
