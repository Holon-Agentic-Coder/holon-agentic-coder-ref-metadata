---
# holon-agentic-coder-ref-metadata-0216
title: "Holon flow references and drives beads work items (claim on intent, close on merge)"
status: todo
type: feature
priority: normal
tags:
  - issue-tracking
  - beads
  - holon-flow
  - holon-agentic-coder
blocked_by:
  - "0214"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-10-30T00:00:00Z
---

## Problem

Once beads is target-native (Bean 0214), flow provenance should reference beads ids instead of harness bean ids: intent
JSON and `intents.jsonl` rows carry a target-native `hac-xxxx` work-item id (this also honours the standing rule that
harness bean ids never land in the target ledgers).

## Scope

- Intent schema: optional `work_item` field holding a beads id; validated when present.
- `holon intent` claims the referenced issue (`bd update <id> --claim`); the post-merge/calibration boundary closes it
  with the PR URL as close reason.
- Boundary with the 3-ledger invariant (rule 14): ledger rows cite the beads id but never mirror beads state; beads
  never duplicates ledger rows. No fourth ledger.
- Docs: flow usage docs explain the linkage and the narrow issue-data exception.

## Notes

- Runs through the **Holon flow**. Touch set includes `sandbox_executor/flow.py` and `cli.py` — per Bean 0151, never run
  concurrently with other flows touching those files; sequence after Bean 0214.
- Related: Bean 0156 (design), Bean 0183 (role containers need `bd` + push access to `refs/dolt/data` or
  `dolt.local-only` with host-side sync).
