---
# holon-agentic-coder-ref-metadata-0066
title: "`holon calibrate --no-commit` announces that it committed and created the calibrated branch"
status: todo
type: bug
priority: low
tags:
  - flow
  - calibration
  - cli
created_at: 2026-10-03T12:12:00Z
updated_at: 2026-10-03T12:12:00Z
---

`run_calibrate()` gates the branch reset and the commit behind `if not skip_commit:`, but prints its success messages
**unconditionally**. With `--no-commit` it therefore announces two things it did not do.

## Reproduction (2026-10-03, `holon-agentic-coder` @ `496d7b6`)

```console
$ ./holon calibrate I-…/P-1790564277-…/E-1790564813-…/_ --repo-dir . --no-commit
Calibration report generated and committed at plans/P-1790564277-…_calibration.md
Calibrated branch: I-…/P-1790564277-…/E-1790564813-…/calibrated
Predicted EV: 69.98 | Actual EV: 73.39 (ΔEV: +3.41)
```

Neither statement was true: `git status` showed the report as an uncommitted modification, `HEAD` stayed at `496d7b6`,
and no branch was created or reset — which is precisely what `--no-commit` is for.

## Why it matters

This is not cosmetic. `calibrate` mutates branch state (`git checkout -B …/calibrated <execution_branch>`, which resets
that branch), and `--no-commit` is the flag an operator reaches for exactly when they want the numbers **without** the
mutation. A log line saying "committed" and naming a calibrated branch is what a later agent or human reads as evidence
that the branch exists and holds the record. The wrong belief is durable: it survives into PR bodies, bean summaries and
handoffs, and it is the opposite of the invariant this harness has been building — that the ledgers and the working
tree, not an agent's or a tool's word, are the system of record.

## Acceptance criteria

1. Under `--no-commit`, the message states that the report was written to the working tree and that **no branch was
   created and nothing was committed**.
2. The `Calibrated branch: …` line is printed only when that branch was actually created or reset.
3. `--json` output carries a field (e.g. `committed: false`) so a scripted caller can tell, rather than parsing prose.

## Notes

- Target repository: `holon-agentic-coder` — change must go through the flow ([AGENTS.md](../AGENTS.md), "Sole Change
  Path").
- File: `apps/sandbox-executor/src/sandbox_executor/calibration.py`, the two `print()` calls at the end of
  `run_calibrate()`.
- Small, well-scoped, and a good candidate to batch with Bean 0065, which lives in the same function.
- Related: bean 0054, bean 0060, bean 0065, PR #61.

## Resolution

Open.
