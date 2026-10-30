---
# holon-agentic-coder-ref-metadata-0162
title: "Stage 5 calibration commits a report that fails the hygiene Prettier check"
status: todo
type: bug
priority: high
tags:
  - calibration
  - ci
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-26T07:28:28Z
updated_at: 2026-10-30T00:01:17Z
---

## Problem

Found on 2026-10-26 on PR #97 (Bean 0159). Stage 5 logged "Prettier converged in 1 pass(es) for 1 file(s)", then
committed `plans/P-1792992691-claude-agent-claude-opus-5-5_calibration.md` (`a3c2d3f`/`a66ad46`). That file fails the CI
`hygiene` job: `prettier --check` with the repository configuration reports lines 56-58. `hygiene` passed on the
execution head `ca22157` and fails from the calibration commits on. So every flow PR turns CI red right after
calibration, and the review loop then reads a failure the change did not cause.

## Scope

- Find which Prettier config or version Stage 5 formats with (container versus repository `.prettierrc`, or formatting
  before the final write), and format with exactly what `hygiene` checks.
- Run the hygiene check on the calibration commit before it is pushed, and fail Stage 5 rather than push a red head.
- Test with a fixture report that needs re-wrapping.

## Notes

- Run through the Holon flow on holon-agentic-coder.

## Recurrence (2026-10-28)

Recurred on PR #99 (Bean 0168): `holon calibrate` reported "Prettier converged" yet the committed
`plans/P-1793104256-claude-agent-claude-opus-5-5_calibration.md` failed `uv run task lint-docs`. Fixed by a follow-up
commit (`6e9df1d`) formatting the report with the repository's `.prettierrc.json` (3 lines changed).

## Recurrence (2026-10-29)

Every calibrated holon-agentic-coder flow PR from #99 to #111 needed the same follow-up commit,
`docs: format the calibration report with the repository Prettier configuration`, after its `chore(calibration)` commit
(calibration then format commit, from `gh pr view --json commits`): #99 `8d1d913`/`6e9df1d`, #100 `728cff2`/`40333d9`,
#101 `0a69e9c`/`58ad02a`, #102 `45266d6`/`45debd1`, #104 `c3afba2`/`9bc1ed5`, #105 `8fd40d4`/`e41bcd0`, #106
`86e6031`/`553fe43`, #107 `c7cd0e2`/`e306256`, #109 `147ea4f`/`cd2ab9b`, #110 `9117677`/`79da203`, #111
`b5a286c`/`81b691f`. PR #103 was hand-authored (no flow, no calibration) and PR #108 was never calibrated.
