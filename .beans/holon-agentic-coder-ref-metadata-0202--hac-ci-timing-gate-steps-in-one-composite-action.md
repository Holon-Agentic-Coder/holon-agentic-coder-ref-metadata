---
# holon-agentic-coder-ref-metadata-0202
title: "holon-agentic-coder: move the pasted CI timing-gate steps into one composite action"
status: todo
type: task
priority: low
tags:
  - ci
  - duplication
  - holon-agentic-coder
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T00:48:53Z
---

## Problem

Spawned by Bean 0177. PR #109 pasted the same `scripts/ci_timing_gate.py` invocation (start stamp, mode, thresholds,
JUnit path, record upload) into all 6 workflow files under `.github/workflows/` (7 files with the README). Any change to
the gate's flags now edits every workflow, so CI changes always conflict with each other. A local composite action
already exists (`.github/actions/docker-pull`) but no workflow `uses: ./...` it.

## Scope

1. `.github/actions/ci-timing-gate/action.yml` with inputs (`workflow`, `job`, thresholds, JUnit path); each workflow
   calls it in one step.
2. Remove or adopt the unused `docker-pull` action.
3. Behaviour of the gate unchanged; the existing `test_ci_timing_gate.py` and any workflow lint stay green.

## Touch set

`.github/workflows/*.yml`, `.github/actions/`, `.github/workflows/README.md`.

## Dependencies

After Bean 0184's holon-agentic-coder check (0184 notes the #109 gate may share the issues-permission defect). Needs a
token with the `workflow` scope (Bean 0175).

- 2026-10-30: the Bean 0184 check is satisfied. Bean 0184 is completed (holon-coherence PR #32, merged as `cefebe3`) and
  found the #109 gate unaffected: it reads the override label from the event payload, not the Issues API. The `workflow`
  token scope (Bean 0175) still applies.

## Notes

- Run through the Holon flow on holon-agentic-coder.
