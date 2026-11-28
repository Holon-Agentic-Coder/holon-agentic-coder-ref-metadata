---
# holon-agentic-coder-ref-metadata-0566
title: "Check: git safety rules enforced by tooling, not only by briefs"
status: in-progress
type: task
priority: critical
tags:
  - harness
  - git
  - invariants
  - subagents
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:32:34Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

Agents never use `git stash`, `--no-verify`, `git add -A`/`git add .`, force-push, or rebase a flow branch. Bean 0556
put this in the brief text only; CF-0014, CF-0015 and CF-0010 show briefs alone do not hold.

## Check

- A `git` wrapper placed first on PATH for every agent/subagent session (and for flow runners) that refuses these
  subcommands/flags with a clear message; bypass only by the maintainer.
- Server side: branch protection forbids force-push on flow branches (`I-*`, `P-*`, `E-*`) and on the harness branch.
- Post-run audit in the coordinator: after each subagent, `git stash list` must be unchanged and the reflog shows no
  forced update; a difference is recorded in the failure ledger automatically.
- Tests for the wrapper (each forbidden form refused, allowed forms pass).

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.

## Resolution

Done: `.agents/scripts/git_guard.py` as a project `PreToolUse` Bash hook (`.claude/settings.json`) and as the
`.agents/bin/git` PATH wrapper, with tests for every blocked and allowed form. Remaining: `run_holon_flow.py` must
prepend `.agents/bin` to the runner PATH; maintainer sets server-side branch protection (no force-push on flow
branches); coordinator post-run stash/reflog audit.

## Gap found (2026-11-26T23:32:34Z)

The PreToolUse hook matches only the `Bash` tool. Subagents mostly run git through the REPL tool's `$` shell, which the
hook does not see, so `--no-verify`, `git stash` or `HOLON_GIT_GUARD_BYPASS` there are unguarded. Extend the matcher to
the REPL tool (or guard at the git level for every process, e.g. the PATH wrapper for all sessions) and rely on the
per-commit CI replay from Bean 0577 as the backstop.
