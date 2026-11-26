---
# holon-agentic-coder-ref-metadata-0455
title: "post-pr-merge rebuilds holon-coherence on hac merges, collides on burst merges, and skips triage"
status: todo
type: bug
priority: high
tags:
  - harness
  - post-merge
  - install-holon
  - prioritise-beans
  - reliability
created_at: 2026-11-25T05:41:00Z
updated_at: 2026-11-25T06:05:00Z
---

# `post-pr-merge` rebuilds `holon-coherence` on `hac` merges, collides on burst merges, and skips triage

## Summary

Three operational defects in `.agents/skills/post_pr_merge/SKILL.md` and
`.agents/skills/install_holon/scripts/install_holon.py` compound whenever target PRs merge in bursts:

1. `post_pr_merge/SKILL.md:84` invokes `python3 .agents/skills/install_holon/scripts/install_holon.py` **without
   `--holon-only`** for `holon-agentic-coder` merges (`install_holon.py:250-278`), unconditionally syncing and
   rebuilding `holon-coherence:latest` + reinstalling `holon-coherence` even when `holon-coherence` (`#55`) has not
   changed. (`install_holon.py:229` also sets `default=True` on `--all` inside a mutually-exclusive argument group.)
2. Concurrent `#<N> - post-merge` subagents spawned during rapid bursts run overlapping builds (rebuilding the same
   images per commit instead of once for latest `main`), contend on `.git/index.lock` / non-fast-forward harness pushes,
   and repeatedly skip Step 5 (`prioritise_beans.py`).
3. Skipping Step 5 left the `139 KB` `.beans/bean-triage-prioritisation.md` matrix stale across an entire `3+` hour
   merge wave.

## Evidence (`2026-11-25T04:59Z–05:39Z` burst merges)

- `7` `holon-agentic-coder` PRs merged in `39 min` (`#295` `04:59:58Z`, `#296` `05:01:49Z`, `#297` `05:09:36Z`, `#298`
  `05:12:10Z`, `#299` `05:20:56Z`, `#300` `05:31:18Z`, `#301` `05:38:33Z`), while `holon-coherence` stayed unchanged at
  `#55` (`2026-11-24T12:44:47Z`).
- Harness commit history shows `6aaf358` (`05:06:16Z`), `5a5dd84` (`05:10:35Z`), `ae07885` (`05:18:35Z`), and `261a130`
  (`05:25:16Z`) updated beans without refreshing `.beans/bean-triage-prioritisation.md`, whose `mtime` remained
  **`2026-11-25T02:29:34Z`** (`3.1+ h` stale across `7+` merges).
- Meanwhile concurrent `post-merge` and audit runs needed explicit `.git/index.lock` waits, `--no-ff` push/rebase
  handling, and selective `git commit --only` instructions to avoid sweeping up peer working-tree changes.

## Proposed Change

1. Update `.agents/skills/post_pr_merge/SKILL.md:84` to pass `--holon-only` for `holon-agentic-coder` merges
   (`install_coherence.py` already handles `holon-coherence` merges separately), and clean up `--all` default handling
   in `.agents/skills/install_holon/scripts/install_holon.py:228-231` (or pass `--no-sync` since Step 1 already synced
   `apps/<repo>/main`).
2. Serialize or coalesce `install_holon` and Step 5 `prioritise_beans.py` across overlapping `post-pr-merge` invocations
   (e.g., flock/marker on latest `origin/main` SHA so burst merges build images and regenerate
   `.beans/bean-triage-prioritisation.md` once cleanly after catching up rather than N times or skipping Step 5
   indefinitely).
3. Standardize `post_pr_merge/SKILL.md` Step 6 commits to explicit `git commit --only <touched-files>` instead of
   `git add .beans/` when concurrent sessions share the harness worktree.

## Expected gain

Cuts unneeded `holon-coherence` Docker builds and CLI reinstalls from every `hac` merge, prevents burst build/git lock
contention, and keeps `.beans/bean-triage-prioritisation.md` accurate after burst merges.

## Cost

Small harness-only change in `.agents/skills/post_pr_merge/SKILL.md` and
`.agents/skills/install_holon/scripts/install_holon.py`.

## Notes

- Harness-only change.
- Related: Bean `0402` (running flows isolated from post-merge image rebuilds), Bean `0388` (stale inline triage
  narrative in `prioritise_beans.py`).
- Audit source: `2026-11-25T05:41Z` fifth-merge self-improvement audit (`#295–#299`).

## Audit evidence, 2026-11-25T06:05Z (self-improvement audit, fifth merge #300–#304)

- Following burst merges `#300–#304` (`05:31:18Z..05:46:57Z`, `5` merges in `15.65 min`), `git log` shows
  `.beans/bean-triage-prioritisation.md` has still not been updated since commit `0f0525f` (`2026-11-25T02:30:25Z`,
  `3.5+ h` stale across `12` merges `#293–#304`), and `flow-no-unneeded-full-review` (`0407`) remains an active worktree
  without completing triage/backfill parity.
