---
# holon-agentic-coder-ref-metadata-0374
title: "Sidecar wire logs and cache land in the target worktree's todo/ and get committed to the execution branch"
status: todo
type: bug
priority: high
tags:
  - flow
  - sidecar
  - stage-3
  - isolation
  - holon-agentic-coder
created_at: 2026-11-23T07:05:00Z
updated_at: 2026-11-23T07:05:00Z
---

## Problem

Bean 0191's child 3 execution branch (`…/E-1795415159-CLA-CO5.5/_` at `b676a12b`) tracks 47 scratch files under `todo/`
(`todo/cache/llm_cache.db`, `todo/mitm_wire_logs/*`). `origin/main` has none. A PR from that branch would carry proxy
wire logs (full request/response bodies) and an LLM cache database into the target repository.

Confirmed cause (2026-11-23), two defects:

1. **Default sidecar paths sit under the git root's `todo/`.** `launcher/sidecar_plan.py:57` (and the cache branch below
   it) defaults the wire-log and cache directories to `<git root>/todo/mitm_wire_logs` and `<git root>/todo/cache` when
   `WIRE_LOG_DIR` / `CACHE_DIR` are unset, using `proxy_paths._find_git_root()` from the current directory. When the
   flow is launched from inside the flow worktree (as the bean 0191 resume was), the git root is the target worktree, so
   the files are written into it. Every other flow that day was launched from the harness root, whose `todo/` is
   git-ignored, and has no such files. The target repository's `.gitignore` does not cover `todo/`, and target code
   naming `todo/` breaks the rule that target repositories never reference harness paths.
2. **Stage 3 commits stage untracked files indiscriminately.** The interrupted-run commit (`4278bd02`, "partial work")
   and the host's completion commit (`b676a12b`) both added the 47 files; the executor's own cleanup commit (`8c65f5e1`,
   "untrack todo/ cache and wire logs") was undone by the later completion commit.

## Goal

- Sidecar wire logs and cache never default to a path inside a repository worktree: default to a per-user state
  directory outside any worktree (for example under `~/.holon/`), still overridable by `WIRE_LOG_DIR` / `CACHE_DIR`. No
  target code names `todo/`.
- Stage 3 partial-work and completion commits never add files outside the executor's change: untracked files that are
  not part of the execution (proxy logs, caches, databases) are not staged; a guard fails the commit (or skips the path)
  for wire-log/cache directories and for files matching the secret/large-binary rules.
- A test launches the sidecar plan with the current directory inside a temp git worktree and asserts nothing is created
  inside it; a test for the completion commit asserts an untracked scratch directory is not committed.

## Related

Bean 0191 (blocked by this on child 3; recovery decision pending with the maintainer). Until this lands, always launch
`run_holon_flow.py` from the harness root, never from inside a flow worktree.
