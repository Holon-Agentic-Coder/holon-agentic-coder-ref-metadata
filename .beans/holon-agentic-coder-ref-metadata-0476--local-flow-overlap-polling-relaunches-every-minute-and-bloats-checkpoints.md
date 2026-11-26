---
# holon-agentic-coder-ref-metadata-0476
title: "Local-flow overlap polling relaunches holon flow every minute, logs false clear, and bloats checkpoint logs"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - harness
  - checkpoint
created_at: 2026-11-26T03:50:00Z
updated_at: 2026-11-26T03:50:00Z
---

# Local-flow overlap polling relaunches `holon flow` every minute, logs false clear, and bloats checkpoint logs

## Problem

When Stage 3 refuses admission due to a **local flow** that has not opened a pull request yet (`numbers == []`),
`.agents/skills/holon_flow/scripts/run_holon_flow.py:678-693` sleeps `60 s`, unconditionally logs
`INFO: Overlap cleared; resuming Stage 3 (admission is checked again).`, and spawns a full `holon flow --checkpoint`
subprocess.

This causes three compounding problems:

1. **False log signal & process churn:** While a multi-hour decomposed parent flow runs locally, the waiting wrapper
   re-launches `holon flow` (plus pre-flight, git fetch, and Stage 3 admission) every `60 s` — printing
   `Overlap cleared` hundreds of times when nothing cleared.
2. **Unbounded checkpoint log bloat:** Each failed `holon flow --checkpoint` run appends its refusal lines into
   `checkpoint["context"]["logs"]` and re-writes the checkpoint JSON without deduplication or cap, inflating the
   checkpoint file to hundreds of kilobytes.
3. **Late PR transition:** Even while the blocking flow opens sequential sub-intent PRs, the wrapper keeps hitting the
   60 s local-flow re-launch loop until the blocker finally opens its parent PR.

## Evidence (2026-11-26T03:50Z fifth-merge audit)

- **`macos-unit-only-when-relevant` (`0400`, `todo/flow-macos-unit-only-when-relevant.log`):**
  - Refused at `2026-11-25T23:02:33Z` on local flow `I-1795584436-ledger-fragments-and-promotion/...`
    (`.github/workflows/README.md`).
  - Re-launched `holon flow --checkpoint` **`200+` times** across **`274.7+ min`** (`23:02:33Z..03:37:15Z+`; `400`
    refusal lines already flushed by `03:01:05Z`, `median 0.083 min` / `5 s` per failed launch, `max 0.133 min` / `8 s`,
    totalling **`~16–20 min`** of pure process/git/checkpoint overhead), printing
    `INFO: Overlap cleared; resuming Stage 3` on every single minute.
  - `apps/holon-agentic-coder/flow-macos-unit-only-when-relevant/.holon/flow/checkpoint-macos-unit-only-when-relevant.json`
    bloated to **`298,110` bytes**, with `context["logs"]` containing **`1,752` lines (`274,923` bytes = `92.2%`** of
    the file).
- **`ledger-fragments-and-promotion` (`0371`):**
  - `checkpoint-ledger-fragments-and-promotion.json` similarly accumulated **`126,217` bytes** in `context["logs"]`
    (`79.1%` of `159,481` bytes) across resumes.

## Proposed Change

1. **Harness (`run_holon_flow.py`):**
   - When `numbers` is empty (local-flow blocker), never log `"Overlap cleared"`; log
     `"Re-checking local-flow Stage 3 admission..."` instead.
   - Check the blocking local worktree's checkpoint / branch state directly in Python (or back off the poll interval,
     e.g. `60 s -> 120 s -> 300 s`, and also watch `gh pr list` for the blocking slug) before spawning a full
     `holon flow --checkpoint` subprocess.
2. **Engine (`holon-agentic-coder` checkpoint writer via `holon flow`):**
   - Cap or deduplicate repeated identical Stage 3 overlap-refusal lines in `context["logs"]` (e.g., keep a bounded tail
     or collapse consecutive refusal entries) so checkpoint JSON files stay small across long overlap waits or retries.

## Expected Gain

Eliminates `200+` redundant `holon flow` process launches (`~16–20 min` CPU/git/IO churn over a 4.5 h wait), removes
misleading `"Overlap cleared"` log spam, and prevents `275 KB+` checkpoint JSON bloat.

## Cost

Small in harness (`.agents/skills/holon_flow/scripts/run_holon_flow.py` + `tests/`) and small in `holon-agentic-coder`
(checkpoint `context.logs` bounding via `holon flow`).

## Notes

- Related: Bean `0468` (wrapper previously exited on overlap), Bean `0385` (buffered log hid final `36+ min` of
  `flow-macos-unit-only-when-relevant.log`), Bean `0412` (log overlap wait as one wait, not refused runs).
