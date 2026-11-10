---
# holon-agentic-coder-ref-metadata-0271
title: "Resolver pre-push verification includes the Markdown formatting check that CI runs"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - resolver
  - ci
  - holon-agentic-coder
created_at: 2026-11-10T05:00:00Z
updated_at: 2026-11-10T05:00:00Z
---

## Problem

The Stage 4 resolver verifies its fixes before it pushes with `uv run task lint` and `uv run task test`
(`_verify_before_push` in `entrypoint/review_loop.py`). CI's `Test - Hygiene` job runs `make lint`, which also runs
`lint-md`, a Prettier formatting check over every Markdown file. The resolver's lint does not include that check, so a
resolver that edits a Markdown file can push a fix that passes its own verification and fails CI.

Seen repeatedly:

- PR #148 (Bean 0258): the iteration 1 resolver left `Test - Hygiene` red; the CI-repair step fixed it at iteration 2.
- PR #153 (Bean 0266): the same, on `.github/workflows/README.md`, fixed at iteration 2.
- PR #159 (Bean 0262): `apps/sandbox-executor/README.md` has failed `Test - Hygiene` on every head from `dd5a1c4` to
  `e392cda`, across iterations 1 to 10 of the resumed review loop, while Unit, Integration and Stress went green. The
  resolver edits that README almost every round and never leaves it Prettier-clean.

Each occurrence costs at least one extra review iteration, and on PR #159 it has survived ten.

## Goal

1. **Same gate as CI**: `_verify_before_push` runs the Markdown formatting check CI runs (`make lint-md`, or the
   Prettier `--check` it wraps) after `uv run task lint`, limited to the Markdown files the resolver changed so it stays
   fast, and reports a failing file by name in the resolver result.
2. **Fix, don't just report**: when the only failure is Markdown formatting, the resolver runs Prettier `--write` on the
   changed Markdown files (using the target repository's configuration, never a repo-wide run that could reformat
   unrelated files), re-runs the check, and includes the formatting in the same fix commit.
3. **One definition of lint**: make the resolver's lint step and CI's hygiene job call the same task, so adding a check
   to one adds it to both. A test asserts that every check in the hygiene workflow's lint command is covered by the
   resolver's verification command.
4. **Tests**: hermetic tests with a fixture repository: a resolver change that leaves a Markdown file unformatted fails
   verification, is auto-formatted and then passes; a change that touches no Markdown skips the check; an unrelated
   unformatted file is left alone.
5. **Constraints**: `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no new dependencies.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow. The intent JSON
  must not mention bean IDs or harness paths.
- Touches `entrypoint/review_loop.py` and the lint task wiring, so run it when no other flow is editing the review loop.
- Related: Bean 0258 (the resolver's pre-push verification and its failure handling).
