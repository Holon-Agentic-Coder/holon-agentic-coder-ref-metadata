---
# holon-agentic-coder-ref-metadata-0185
title: "holon-agentic-coder: adopt ruff complexity rules (C901, PLR0911-PLR0915) with an inline noqa baseline"
status: todo
type: task
priority: high
tags:
  - code-quality
  - lint
  - complexity
  - holon-agentic-coder
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T01:41:00Z
---

## Problem

Spawned by Bean 0177 (research findings). On `origin/main` `993b686` nothing limits function complexity: the ruff
`select` is `E W F I UP B C4 SIM RUF`. Measured with `uvx ruff check --isolated --no-cache` over
`apps/sandbox-executor/src`:

- C901 (CC > 10): **56** functions. Worst: `entrypoint/executor.main` CC 178, `flow.run_review_loop` 131, `cli.main`
  114, `mitm_addon.extract_sse_token_counts` 85.
- PLR0912 too many branches: 47; PLR0915 too many statements: 37; PLR0913 too many arguments: 35; PLR0911 too many
  returns: 13.
- radon: 672 functions, 13 graded F and 8 graded E; 35 functions over 100 lines.

Without a gate every refactor in Beans 0187-0201 can regress while it lands.

## Scope

1. Add `C901` (`lint.mccabe.max-complexity = 10`) and `PLR0911`, `PLR0912`, `PLR0913`, `PLR0915` (ruff defaults: 6
   returns, 12 branches, 5 arguments, 50 statements) to the ruff config. No new dependency.
2. Baseline every current offender with an **inline** `# noqa: <codes>` on its `def` line (`ruff check --add-noqa`), not
   with `per-file-ignores`, so each later refactor deletes the `noqa` in its own file and `pyproject.toml` never becomes
   a file every flow edits.
3. Add a pytest that counts baseline `noqa` markers for these codes and fails if the count rises (ratchet down only),
   with the current count recorded in the test.
4. Document the thresholds in `docs/architecture.md` in one short section.

## Touch set

`pyproject.toml`, the `def` lines of the 56+ offenders across `apps/sandbox-executor/src` (one-line edits), one new test
file, `docs/architecture.md`.

## Dependencies

No bean blockers. Must land before 0187, 0188, 0195 and 0198, which move or edit the baselined lines.

- 2026-10-30: PR #113 (`docs/architecture.md`) has merged as `760ee87` (2026-10-30T01:27:16Z); sequenced after
  holon-agentic-coder flow PR #112 (edits `flow.py` and `calibration.py`, which carry baselined offenders) merges.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Do not run concurrently with any flow touching `flow.py`, `cli.py` or `entrypoint/executor.py` (one-line edits there
  still conflict).
- Tests are pytest only (`uv run pytest`). The target must not mention harness paths or bean ids.
