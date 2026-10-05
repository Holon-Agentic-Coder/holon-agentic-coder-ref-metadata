---
# holon-agentic-coder-ref-metadata-0066
title: "`holon calibrate --no-commit` announces that it committed and created the calibrated branch"
status: completed
type: bug
priority: low
tags:
  - flow
  - calibration
  - cli
created_at: 2026-10-03T12:12:00Z
updated_at: 2026-10-05T09:50:00Z
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

Resolved via the 5-stage Holon flow (Batch B) in PR
[#63](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/63):

1. **Stage 1 (Intent)**:
   - Branch `I-1791151674-calibration-integrity-resilience-and-staleness-detection/_` logged in `intents.jsonl`.
2. **Stage 2 (Plan)**:
   - Branch `I-1791151674-.../P-1791151683-antigravity-agent-gemini-3.8-flash-medium/_`.
   - Artifact `plans/P-1791151683-antigravity-agent-gemini-3.8-flash-medium.md` logged in `plans.jsonl`.
3. **Stage 3 (Execute)**:
   - Branch `I-1791151674-.../E-1791151927-antigravity-agent-gemini-3.8-flash-medium/_`.
   - Core implementation:
     - In `run_calibrate`, when `skip_commit=True` (`--no-commit`), the console prints an accurate message stating that
       the report was written to the working tree and that no branch was created and nothing was committed.
     - The `Calibrated branch: ...` line is omitted when `skip_commit=True`.
     - `report.committed = not skip_commit`, ensuring that `--json` output explicitly includes `"committed": false`.
     - Added comprehensive unit tests in `TestNoCommitFlag` in `apps/sandbox-executor/tests/test_calibration.py`.
4. **Stage 4 (PR Review Loop)**:
   - PR [#63](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/63) opened.
   - Iteration 1 ensemble review flagged start-point resolution on branch checkout; resolved in commit `1171601`.
   - Iteration 2 ensemble review achieved unanimous approval (3/3 `APPROVED`, 0 Critical, 0 Important).
   - Consensus review posted to PR #63.
   - GitHub CI: 10/10 checks green.
5. **Stage 5 (Calibration)**:
   - Generated calibration report with predicted EV 85.95, actual EV 93.89 (ΔEV: +7.94).
   - Pushed to `/calibrated` branch.
6. **Merge Boundary**:
   - Preserved human-only PR merge constraint; halted with consensus approval and calibration complete. Ready for human
     merge at https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/63.
