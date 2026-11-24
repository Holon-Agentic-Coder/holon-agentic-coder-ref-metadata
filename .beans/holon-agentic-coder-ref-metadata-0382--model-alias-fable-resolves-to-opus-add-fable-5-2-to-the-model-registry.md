---
# holon-agentic-coder-ref-metadata-0382
title: "The model alias 'fable' resolves to claude-opus-5-5; add claude-fable-5-2 to the model registry"
status: completed
type: bug
priority: high
tags:
  - models
  - runner
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-24T05:47:29Z
pr: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/267
---

## Problem

`apps/sandbox-executor/src/sandbox_executor/agent_defaults.py` lists `"fable"` as an alias of the `claude-opus-5-5`
capability (`aliases=["opus", "claude-opus", "fable"]`). `--model fable` therefore runs Opus silently, although the
maintainer's flow model is Fable 5.2 (2026-11-23). There is no `claude-fable-5-2` entry; the full id only works because
unknown ids are passed to the claude CLI verbatim.

## Goal

- A `claude-fable-5-2` capability entry with aliases `fable` and `claude-fable`; `fable` no longer aliases Opus.
- `holon doctor` and the resolved-model log line show the canonical id a flag or alias resolved to.
- A test asserts every alias resolves to a model of the same family as its name.
- Related: Bean 0270 (discover runner models dynamically) would remove the hand-kept list; this bean is the small fix.

## Progress

- 2026-11-23: Active in `apps/holon-agentic-coder/flow-fable-model-registry-entry` (intent
  `todo/intent-0382-fable-model-registry-entry.json`, `antigravity-agent` / `gemini-4-argon`).
- 2026-11-23: Stopped the parallel Claude Code runner for `flow-fable-model-registry-entry` and took over Bean 0382 in
  Antigravity background subagent `709edd6a-27ac-4941-93ae-90a64a02b7e4` (`antigravity-agent` / `gemini-4-argon`),
  resuming cleanly from the Stage 1 checkpoint (`I-1795444112-fable-model-registry-entry/_`).
- 2026-11-23: All 5 stages completed on [PR #267](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/267)
  (head `94f9dff6`, `MERGEABLE`, `CLEAN`, `11/11` CI checks passed, Stage 4 consensus APPROVED, Stage 5 calibration
  report included in PR diff); awaiting human merge (`status: in-progress`).

## Resolution

- Delivered via [PR #267](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/267) and merged into `main` (`9f57492d`).
- Key deliverables: added `claude-fable-5-2` capability entry with aliases `fable` / `claude-fable` (removing `fable` from Opus), displayed canonical resolved model IDs in `holon doctor` and log lines, and added alias-family regression tests (`test_model_alias_families.py`).
- Verification & Holon Flow traversal: 3/3 consensus approval, 11/11 CI checks green on calibrated head `ec6bc115`, Stage 5 calibration included (`plans/I-1795444112-fable-model-registry-entry/P-1795444541-ANA-G4A_calibration.md`).
