---
# holon-agentic-coder-ref-metadata-0460
title: "Stage 4 resolver runs full 7,800+ pytest suite twice and even on Markdown/bookkeeping-only fixes"
status: todo
type: feature
priority: high
tags:
  - flow
  - stage-4
  - resolver
  - performance
  - holon-agentic-coder
created_at: 2026-11-25T06:05:00Z
updated_at: 2026-11-25T06:05:00Z
---

# Stage 4 resolver runs full 7,800+ pytest suite twice and even on Markdown/bookkeeping-only fixes

## Problem

In `apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`, the Stage 4
resolver incurs unnecessary full test runs on two paths:

1. **Unconditional full test run on non-code diffs:** `_verify_before_push` (`review_loop.py:295-324`, line `315`)
   always invokes `uv run task test` even when the resolver only edited Markdown/bookkeeping files (such as formatting a
   plan file with Prettier, updating `executions/` or `plans/`, or fixing a docstring/YAML nit covered by
   `lint`/`run_markdown_gate`).
2. **Duplicate execution of the full suite on code fixes:** `_build_resolver_prompt` (`review_loop.py:389, 397`)
   instructs the resolver agent to run `uv run task lint` and `uv run task test` locally before marking findings
   `applied`, after which `_verify_before_push` (`review_loop.py:306-315`) immediately re-runs `uv run task lint`,
   `run_markdown_gate`, and the entire `uv run task test` suite again before committing and pushing.

## Evidence (2026-11-25T06:05Z audit, #300-#304 & #309)

- **`PR #309` (`0438`, `calibration-merge-adapted-file`):** After `3/3` reviewers `APPROVED (0/0/0)` at `05:40:16Z`,
  Stage 4 blocked solely on unformatted Markdown
  (`plans/I-1795584436-calibration-merge-adapted-file/P-1795584464-CLA-CO5.5.md`, `Test - Hygiene` run `45554742211`
  failed at `05:37:27Z`). Dispatching the resolver (`05:40:17Z`) to format one `.md` file (`89eae143`) took
  **`6.58 min`** before committing ledger rows at `05:47:06Z`
  (`checkpoint-calibration-merge-adapted-file.json:878-888`), triggering `26eca98f` / `4ded0b14` (`9.95 min` CI) and a
  `10.15 min` full Iter 2 re-review (`05:47:26Z..05:57:35Z`).
- **`PR #308` (`workspace-survival-job-parallel`):** Iter 3 doc-only fix (`ebb688d6`, `05:16:12Z`) likewise ran a
  multi-minute resolver pass, and Iter 4 resolver (`05:25:12Z..06:02Z+`, container `d7a5f5ec82a1`) stayed live `37+ min`
  inside `claude-opus-5-5` + pytest verification loops (related: Bean `0430`).

## Proposed Change

1. **Diff-scoped pre-push gate in `_verify_before_push` (`review_loop.py:295-324`):** Inspect
   `git diff --name-only <base>..HEAD` plus working-tree changes; when every file modified by the resolver is
   documentation/Markdown/bookkeeping (`*.md`, `plans/`, `executions/`, `holon-knowledge/`), run `run_markdown_gate`
   (Prettier) and `uv run task lint-docs` (or fast doc/hygiene checks) and skip `uv run task test`.
2. **Avoid redundant back-to-back full test runs:** Either delegate final test verification exclusively to
   `_verify_before_push` with targeted pytest guidance for the agent prompt (or reuse a clean verified-head marker
   written when the resolver ran `uv run task test` without subsequent edits), so the full `uv run task test` suite runs
   at most once per resolver turn on Python/workflow edits and zero times on doc-only edits.
3. Add unit tests covering `_verify_before_push` doc-only skipping vs Python/workflow full verification.

## Expected Gain

- Saves **`~3–6 min`** wall time on every doc/Markdown-only Stage 4 resolver pass (like `#309`'s `6.58 min` formatting
  pass) and **`~2–3 min`** on every code resolver pass that currently runs `uv run task test` twice.
- Combines cleanly with Bean `0407` (skip unneeded full re-review when only hygiene/bookkeeping changed).

## Cost

Small: scoped diff check in `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py` + unit tests via
`holon flow` (`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0407` (skip full re-review when nothing reviewable changed), Bean `0430` (resolver turn budget &
  test-loop watchdog), Bean `0442` (Stage 2/5 Prettier timeouts causing `#309` hygiene failure).
