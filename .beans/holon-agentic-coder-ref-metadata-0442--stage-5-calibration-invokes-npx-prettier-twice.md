---
# holon-agentic-coder-ref-metadata-0442
title: "Stage 5 calibration invokes npx prettier twice instead of local binary"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-5
  - calibration
  - prettier
  - performance
  - holon-agentic-coder
created_at: 2026-11-25T03:08:00Z
updated_at: 2026-11-25T04:02:00Z
---

## Problem

Stage 5 calibration work (`Starting Stage 5: Post-Execution Calibration` to `Stage 5 promoted ...`) jumped from
`0.2–0.4 min` (`12–24 s`) to `2.57–2.65 min` (`154–159 s`) on every flow because `format_calibration_report` in
`apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/calibration.py:66,1359-1409` invokes
`npx --yes prettier` twice (`--write`, then `--check`). On the host, `npx --yes prettier` takes `>30–70 s` per call even
when `prettier` is already cached in `~/.npm/_npx`, whereas calling the cached `prettier` binary directly takes
`0.064 s`.

## Evidence (2026-11-25T00:28Z–02:54Z fifth-merge audit)

- Across all `13` Stage 5 runs in the window (`12` checkpoints + `todo/flow-timing-gate-judges-test-time.log`),
  `stage5_calib_work` took a median of **`2.58 min`** (max `2.65 min` on `#278`), consuming **`0.58 h` (`~35 min`)** of
  wall-clock work.
- Read-only profiling against `apps/holon-agentic-coder/flow-agent-defaults-self-doc`:
  - `generate_calibration`: `8.87 s`
  - `enforce_report_self_check`: `0.04 s`
  - `promote_pending_candidates(dry_run=True)`: `0.45 s`
  - Total Python/git calibration work: **`9.36 s`**
  - `npx --yes prettier --check <report>`: **timed out at `20.01 s`** (`npx --yes prettier --version` also timed out
    after `>30 s`)
  - Direct cached binary `~/.npm/_npx/b388654678d519d9/node_modules/.bin/prettier --check <report>`: **`0.064 s`**
    (`64 ms`)
- Because `_converge_report` runs both `--write` and `--check` (`calibration.py:1402-1405`), `npx` startup/resolution
  accounts for **`~140 s` (`~91%`)** of Stage 5 calibration work on every single flow.

## Proposed change

1. Resolve a local/cached `prettier` binary first (e.g., repository `node_modules/.bin/prettier`,
   `shutil.which("prettier")`, or `npx --offline prettier` / cached `_npx` binary matching the repository's
   `.prettierrc.json` expectations) before falling back to `("npx", "--yes", "prettier")`, or skip `--check` when
   `--write` succeeded on the exact file and verify via `--write` + single fast binary call.
2. Add a hermetic unit test in `tests/test_calibration_format.py` (or existing calibration formatting tests) covering
   the direct binary preference and `npx` fallback.

## Expected gain

Cuts Stage 5 calibration work from `~2.58 min` (`155 s`) back to `~0.2 min` (`~10–12 s`), saving **`~2.3 min` per flow**
(`~30 min` across `13` flows in a 2.4-hour window).

## Cost

Small: single command-resolution helper in `calibration.py` + unit test, delivered via the Holon flow.

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0048` (dropped `@3.8.4` pin), Bean `0383` (Stage 5 timing & budget), Bean `0408` (local hygiene gate).

## Audit evidence, 2026-11-25T04:02Z (self-improvement audit, fifth merge)

- **`PR #308` (`workspace-survival-job-parallel`):** Stage 5 calibration work (`03:35:18Z–03:37:54Z`) took **`2.60 min`
  (`156 s`)** (`calibrate` total `12.69 min` vs `10 min` budget), and Stage 2 in
  `todo/flow-workspace-survival-job-parallel.log:45-46` also hit **two `30 s` `npx --yes prettier@3.8.4` timeouts**
  (`60 s` wasted in Stage 2).

## Audit evidence, 2026-11-25T05:07Z (self-improvement audit, fifth merge #290–#294)

- **`PR #308` Round 1 re-calibration (`04:10:12Z..04:12:52Z`)** spent **`2.50 min`** (`150 s`, incl. `10 s` re-point),
  and **`thomashan/dev-env#42` Stage 5 calibration (`04:29:23Z..04:31:59Z`)** spent **`2.60 min`** (`156 s`) on
  calibration work before `final_head_ci`.
