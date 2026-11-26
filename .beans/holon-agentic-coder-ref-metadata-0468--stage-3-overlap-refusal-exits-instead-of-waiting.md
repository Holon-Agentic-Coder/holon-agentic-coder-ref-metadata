---
# holon-agentic-coder-ref-metadata-0468
title: "run_holon_flow.py exits on a Stage 3 overlap refusal instead of waiting it out"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - holon-agentic-coder
created_at: 2026-11-25T23:05:00Z
updated_at: 2026-11-25T23:05:00Z
---

## Problem

Flow `macos-unit-only-when-relevant` (Bean 0400, claude-agent / claude-opus-5-5) finished Stage 2 and was refused at
Stage 3 admission:
`Stage 3 refused: the touch set overlaps local flow on branch I-1795584436-ledger-fragments-and-promotion/P-1795584464-CLA-CO5.5/_ ... on .github/workflows/README.md; finish or merge that flow first, or rerun with --allow-overlap.`
The wrapper then logged `Holon flow exited with non-zero code 1.` and exited 1. The Stage 3 overlap wait
(`wait_for_overlapping_prs` / the local-flow re-check in `run_holon_flow.py`) never ran: the process ended within
seconds of the refusal, with no `Waiting for overlapping pull request` or re-check line.

## Expected

Per SKILL.md, "Stage 3 overlap refusals are waited out": the wrapper polls the overlapping flow (or pull request) and
resumes from the checkpoint, without `--allow-overlap` and without stopping.

## Evidence

- Log `todo/flow-macos-unit-only-when-relevant.log` held only the final `Holon flow exited` line (see Bean 0385), so the
  refusal text was not visible there.
- Checkpoint `.holon/flow/checkpoint-macos-unit-only-when-relevant.json` in
  `apps/holon-agentic-coder/flow-macos-unit-only-when-relevant` records `admission.state: blocked` with the local-flow
  blocker above.
- The overlapping flow `intent-0371-ledger-fragments-and-promotion` was still running and had no pull request yet, so
  the local-flow branch (sleep, then re-run admission) was the one that should have run.

## Notes

- Not confirmed which condition failed (the `or rerun with --allow-overlap` text match on the captured output, or the
  `is_overlap_refusal` check); the captured output needs to be printed before the branch decides.
- Related: Bean 0395 (work during an overlap wait), Bean 0385 (flow log empty until the run ends), Bean 0422
  (allow-overlap sticky across resumes).
- The overlap itself is real: the intent scope names `.github/workflows/README.md`, which the ledger-fragments flow also
  touches. The flow was run with the same touch set, so no `--allow-overlap` was used.

## Update, 2026-11-26

The same macos-unit-only-when-relevant run later resumed from its checkpoint on its own and completed Stage 3 to Stage 5
(PR #315), after PR #310 merged. So the overlap wait does resume in at least this case. The first exit (2026-11-25
23:03Z) is still unexplained; the flow log holds only the final line (Bean 0385). Keep this open for investigation of
why the wrapper exited at the first refusal.
