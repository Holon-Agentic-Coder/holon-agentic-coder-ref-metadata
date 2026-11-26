---
# holon-agentic-coder-ref-metadata-0577
title: "Hooks validate the working tree, not the staged commit; a staged-bad row landed (CF-0021)"
status: todo
type: bug
priority: high
tags:
  - harness
  - hooks
  - invariants
  - ci
created_at: 2026-11-26T23:31:46Z
updated_at: 2026-11-26T23:31:46Z
---

## Problem

Commit 1d1617d added failure-ledger row CF-0021 with category `post-merge`, which `check_failure_ledger.py` rejected at
that time, yet the commit landed with no `--no-verify`.

## Confirmed path (investigation, 2026-11-26T23:31:46Z)

Not a hook-install or Claude Code matcher gap. `.git/hooks/pre-commit` was installed and executable (10:19 local, ten
minutes before the commit), `core.hooksPath` is unset, and the subagent committed through the REPL `$` shell with plain
`git commit -m`. Its first attempt at 23:28:36Z was refused by the hook (exit 1, bean 0572 timestamp in the future), so
the hook fired through that route.

1. The subagent staged the ledger containing `"category":"post-merge"` (index version).
2. While it waited 60 s to retry, the coordinator edited the working-tree ledger to `conflict-handling` to get a green
   validator run, leaving the staged blob unchanged.
3. The retry at 23:29:45Z ran the hook; `check_failure_ledger.py` (and `check_beans.py`) read the working-tree file, saw
   a valid category and passed; git committed the staged blob with the invalid category.
4. The coordinator then restored `post-merge` in the working tree and added it to the validator (f224461).

Reproduced in a scratch clone at 1d1617d^: with the bad row staged the commit is refused (HEAD unchanged); after
changing only the working-tree copy to a valid category, `git commit` succeeds and
`HEAD:.agents/ledger/coordinator-failures.jsonl` still holds the `post-merge` row.

The hook also runs the validator from the working tree, so an uncommitted validator edit changes what is accepted.

## Fix

- `check_failure_ledger.py`, `check_beans.py` and every other pre-commit validator read the staged blob
  (`git show :<path>`, or `git diff --cached`), never the working-tree file, when run as a hook; keep the working-tree
  mode for manual runs.
- Run the validators from `HEAD`'s committed scripts (or fail if a validator script is itself modified and unstaged) so
  a working-tree validator edit cannot widen what is accepted.
- Add a pre-commit check that fails when a validated path has unstaged changes differing from the index (staged and
  working copies must match).
- CI (`test-hygiene.yml`) already runs `check_beans.py` and `check_failure_ledger.py`, but only on PRs and pushes to
  `main` and only against the final tree, so a bad row committed and fixed later is never seen. Add a per-commit CI step
  that replays the validators over each commit in the PR range (`git show <sha>:<path>`), so a bypass (staged mismatch,
  `--no-verify`, a hook not installed, a tool that skips PreToolUse hooks) fails the PR. The client hook is a
  convenience; CI is the gate.
- Tests: a regression test staging a bad ledger row, then fixing only the working tree, expecting the hook to fail.
- Register the check in the invariant registry (bean 0573).

## Notes

- Related: beans 0561, 0571 (timestamp and format checks), 0573, 0575 (hook installer), 0566 (git guard).
- Side finding: the Claude Code PreToolUse matcher is `Bash` only; commits issued through the REPL `$` shell are not
  seen by `git_guard.py --hook`, so `--no-verify` and `HOLON_GIT_GUARD_BYPASS` there are caught only if the matcher is
  extended to REPL (and the guard parses the script text). Not used in this incident, but the same gap; covered by the
  CI gate above.
