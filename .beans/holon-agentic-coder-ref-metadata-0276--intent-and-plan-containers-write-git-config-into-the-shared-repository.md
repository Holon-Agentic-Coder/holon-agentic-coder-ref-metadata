---
# holon-agentic-coder-ref-metadata-0276
title: "Intent and plan containers write git config into the shared repository; every flow fails at Stage 1"
status: in-progress
type: bug
priority: critical
tags:
  - flow
  - sandbox
  - worktree
  - holon-agentic-coder
created_at: 2026-11-12T01:00:00Z
updated_at: 2026-11-12T01:00:00Z
---

## Problem

After PR #165 (Bean 0274) the intent creator and planner run in the mounted host worktree, but they still set the commit
identity with `git config --local user.email ...` (`entrypoint/intent_creator.py:134-135`,
`entrypoint/planner.py:189-190` and `:553-554`). In a mounted worktree `--local` is the shared repository's own `config`
(the common git directory is shared with the host and its config is mounted read-only), so the write fails:

```
Running: git config --local user.email intent-agent@holon-agentic-coder.com
error: could not write config file .../apps/holon-agentic-coder/.git/config: Device or resource busy
Intent stage failed: intent-creator agent exited with code 4.
```

All three flows started on 2026-11-12 (intents for Beans 0271, 0222 and 0224) died in Stage 1 within 0.1 minute. The
executor already handles this (`entrypoint/executor.py`, scope `--global` when `workspace_mounted()`); #165 missed the
other two roles. Every flow is blocked until this lands.

## Action

**Exception to the sole-change-path rule:** `holon flow` cannot run Stage 1, so the fix is hand-authored on
`fix/0276-intent-plan-git-identity` (worktree `apps/holon-agentic-coder/fix-0276-intent-plan-git-identity`) at the
maintainer's standing bootstrap-harness fallback in `AGENTS.md`. It sets the commit identity with
`git -c user.email=... -c user.name=...` on the commit command (no config write anywhere), updates the tests that assert
the old calls, and adds a hermetic test that no role entrypoint runs `git config` against a mounted worktree. The
exception is named in the commit message. Pull request creation and merge stay with the maintainer.

## Follow-up

After it merges: rebuild the images (`install-holon --holon-only`), then restart the three flows (intents
`todo/intent-0271-mdcheck.json`, `todo/intent-0222-pimount.json`, `todo/intent-0224-creds.json`) and remove the leftover
worktrees `flow-mdcheck`, `flow-pimount` and `flow-creds`.

## Progress (2026-11-12)

Branch `fix/0276-intent-plan-git-identity` (commit `1ef9f3d`, off `origin/main` at `660c50b`) is pushed; no PR opened
(PR creation for hand-authored work stays with the maintainer). It changes `entrypoint/intent_creator.py` and
`entrypoint/planner.py` (identity via `git -c` on the commit command, no `git config` writes), updates the two tests
that matched the old command shape, and adds `tests/test_entrypoint_git_identity.py` (source guard plus a commit made
with the repository config read-only). Full suite 3548 passed, lint clean. Waiting for the maintainer to open and merge
the PR.

## Progress (2026-11-12, later)

PR #167 was opened and driven through the review loop: 5 iterations, 2 Nits applied in `7a53144`, 5 more in `1435e14`
and 2 rejected with reasons (brittle source-scan guard, public name of the identity constant); 3/3 consensus approval at
`1435e14`, CI green, posted as a comment review. A review was then submitted from the wrong account, so #167 was closed
and replaced by **PR #168** at the same head. Not calibrated: hand-authored, no `E-...` branch. Waiting for the
maintainer to merge #168; the follow-up above then applies.
