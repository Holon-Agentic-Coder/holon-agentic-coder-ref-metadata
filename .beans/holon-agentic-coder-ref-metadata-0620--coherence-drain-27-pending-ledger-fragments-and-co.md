---
# holon-agentic-coder-ref-metadata-0620
title: "Coherence: drain 27 pending ledger fragments and configure HOLON_LEDGER_BOT_TOKEN"
status: todo
type: task
priority: high
tags:
  - holon-coherence
  - ci
  - ledger
created_at: 2026-11-27T08:03:26Z
updated_at: 2026-11-28T00:03:58Z
---

## Notes

- **Problem**: Bean `0614` was closed after PR `#65` (`ce39bf34d`) added `.github/workflows/promote-ledger.yml`, yet
  `holon-knowledge/ledger/pending/` in `holon-coherence@ce39bf34d` still contains **27 unpromoted `.jsonl` fragments**
  (`9` flows across `intents/`, `plans/`, and `executions/`, up from `3` at `c26a0c1`), because `HOLON_LEDGER_BOT_TOKEN`
  is unconfigured on `Holon-Agentic-Coder/holon-coherence` so `promote-ledger.yml` emits `::warning::` and skips
  promotion.
- **Audit update (`2026-11-27T10:55Z`, `52019174f`):** Pending fragments grew `+21` to **48 `.jsonl` files** across
  `#68`, `#69`, `#71`–`#75` while `HOLON_LEDGER_BOT_TOKEN` remains unconfigured.
- **Audit update (`2026-11-27`, `4a02926b`):** Pending fragments grew another `+21` to **69 `.jsonl` files** (`23` flows
  across `intents/`, `plans/`, and `executions/`) across `#76`–`#82` while `HOLON_LEDGER_BOT_TOKEN` remains
  unconfigured.
- **Audit update (`2026-11-27T15:46Z`, `4d2cfcf8`):** Pending fragments grew another `+12` (`#83`, `#67`, `#84`, `#85`)
  to **81 `.jsonl` files** (`737` rows across `intents/`, `plans/`, and `executions/`) while `HOLON_LEDGER_BOT_TOKEN`
  remains unconfigured.
- **Audit update (`2026-11-28T00:01Z`, `bcad21c86e`):** Pending fragments grew another `+24` (`#86..#88, #90..#94`) to
  **105 `.jsonl` files** (**881 rows**: `35` files each under `intents/`, `plans/`, `executions/`) while
  `HOLON_LEDGER_BOT_TOKEN` remains unset (recent `promote-ledger.yml` runs on `bcad21c86` emit the warning and no-op).
- **Proposed Change**: Configure `HOLON_LEDGER_BOT_TOKEN` on `Holon-Agentic-Coder/holon-coherence` (or run
  `promote-ledger.yml` via `workflow_dispatch` once configured) and drain all 27 pending fragments into canonical
  `holon-knowledge/ledger/{intents,plans,executions}.jsonl`.
- **Expected Gain & Cost**: Keeps canonical Coherence ledgers current without manual fragment promotion; tiny secret +
  workflow dispatch cost.
- **Reference**: Source: 2026-11-27 architecture & code-quality refresh (`docs/ecosystem-audit-report-2026-11.md`);
  follows Bean `0614` and mirrors HAC Bean `0611`.

## Acceptance

- `HOLON_LEDGER_BOT_TOKEN` is configured (or promotion executed) and `holon-knowledge/ledger/pending/` contains `0`
  unpromoted `.jsonl` files on `holon-coherence/main`.

## Resolution
