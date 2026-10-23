---
# holon-agentic-coder-ref-metadata-0135
title: "check_pr_mergeability reports CONFLICTING/DIRTY for a branch ref that does not exist"
status: todo
type: bug
priority: medium
tags:
  - holon-flow
  - review-loop
  - git
  - diagnostics
created_at: 2026-10-22T02:40:00Z
updated_at: 2026-10-22T02:40:00Z
---

## Problem

`check_pr_mergeability()` in `apps/sandbox-executor/src/sandbox_executor/flow.py` classifies **any** non-zero exit of
`git merge-tree --write-tree` as a real merge conflict, including the case where the branch ref does not exist yet:

```text
$ git merge-tree --write-tree nonexistent-branch-ref origin/main ; echo $?
1
```

Git exits `1` for "conflicts" **and** for an unusable revision, and the code path (`flow.py:919-947`) never verifies
that the rev lookup itself succeeded — the `rev-parse --verify` probes above it only decide whether to _substitute_
`HEAD`/`origin/<branch>`, they never fail the check when both lookups miss. The result is reported upstream as
`is_dirty: True`, which the review loop turns into `FIND-DIRTY-00N` and halts consensus with:

```text
[CRITICAL: CI SIGNAL SUPPRESSED] Pull Request has merge conflicts against main
(mergeStateStatus=DIRTY, mergeable=CONFLICTING). GitHub Actions suppresses test workflows on refs/pull/<PR>/merge.
```

Observed 2026-10-22 running `holon flow <intent.json> --dry-run` in a fresh worktree cut from `origin/main` where no
`I-.../P-.../E-...` branch existed on disk or on `origin`, and `git merge-tree HEAD origin/main` was clean. The only
open pull request on the repository at that moment was an unrelated one, so the verdict was fabricated from a missing
ref.

Two harms: a false "merge conflict" that no `git` command reproduces, and a suppression narrative that sends the
operator to GitHub Actions instead of to the actual cause (an unresolved branch name).

## Scope

- In `check_pr_mergeability()`, resolve the branch ref and the target ref to object ids first
  (`git rev-parse --verify <ref>^{commit}`) and return an explicit `mergeable: "UNKNOWN"`,
  `merge_state_status: "MISSING_REF"` (with `is_dirty: False` and the offending ref in the diagnostics) when either
  lookup fails, instead of inferring a conflict.
- Only map the specific `git merge-tree --write-tree` exit code `1` **after** a successful pair of resolutions to
  `CONFLICTING`/`DIRTY`, and capture stderr into the diagnostics for the unexpected-exit case.
- Surface the distinction in the review-loop message: a missing ref must read as "cannot evaluate mergeability for ref
  X", never as "CI signal suppressed".
- Tests: a repository with a valid `origin/main` and a nonexistent branch must yield `MISSING_REF`, not `DIRTY`; a real
  conflicting branch must still yield `CONFLICTING`; the review loop must not emit `FIND-DIRTY` for a missing ref.

## Acceptance criteria

- No code path in the mergeability check can report `DIRTY`/`CONFLICTING` without a successful two-ref resolution.
- Regression tests cover the missing-ref, conflicting, and clean cases and pass under `uv run pytest`.

## Source

Observed 2026-10-22 while validating `holon flow --dry-run` for Bean 0132; the run also produced an empty-diff pull
request (tracked separately in Bean 0134).
