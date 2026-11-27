---
# holon-agentic-coder-ref-metadata-0614
title: "Coherence: add Promote Ledger workflow and drain pending ledger fragments"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - ci
  - ledger
created_at: 2026-11-27T05:26:26Z
updated_at: 2026-11-27T05:26:26Z
---

## Notes

- **Problem**: `holon-coherence` (`origin/main@c26a0c1`) writes append-only flow fragments under
  `holon-knowledge/ledger/pending/` (3 unpromoted fragments already present) but has no
  `.github/workflows/promote-ledger.yml` workflow to promote pending fragments into canonical ledgers (unlike
  `holon-agentic-coder`, where Bean `0611` tracks bot-token/debounce fixes for an existing workflow).
- **Proposed Change**: Port the debounced `promote-ledger.yml` workflow (avoiding the silent green no-op and per-push
  cancel storm tracked in Bean `0611`), ensure `holon-coherence` promotes pending fragments cleanly, and drain the 3
  existing pending fragments into canonical ledgers.
- **Acceptance Criteria**: `holon-coherence` has an automated ledger-promotion workflow (or explicit non-silent backlog
  alert when bot token is absent) and `holon-knowledge/ledger/pending/` is drained cleanly.
- **Reference**: Source: 2026-11-27 ecosystem architecture audit (`docs/ecosystem-audit-report-2026-11.md`); coordinate
  with Bean `0611`.

## Resolution
