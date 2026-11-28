---
# holon-agentic-coder-ref-metadata-0636
title: "HAC: drain 303 pending ledger fragments and configure HOLON_LEDGER_BOT_TOKEN"
status: todo
type: task
priority: high
tags:
  - holon-agentic-coder
  - ci
  - ledger
created_at: 2026-11-27T15:53:29Z
updated_at: 2026-11-28T00:03:58Z
---

## Notes

### Evidence (2026-11-27 fifth-merge audit, `holon-agentic-coder@1f3331637`)

- Bean `0611` closed via [PR #424](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/424) (`c03385aff`),
  which removed the `on.push` storm trigger from `.github/workflows/promote-ledger.yml` and added a `::warning::` step
  reporting the unpromoted fragment count when `HOLON_LEDGER_BOT_TOKEN` is unset.
- `HOLON_LEDGER_BOT_TOKEN` remains unconfigured on `Holon-Agentic-Coder/holon-agentic-coder`, so
  `holon-knowledge/ledger/pending/` grew `+12` fragments across `#415`, `#424`–`#426` to **303 `.jsonl` files** (**4,357
  rows** across `intents/`, `plans/`, `executions/` at `1f3331637`, up from 291 files at `2a83e4cc7`).
- **Audit update (`2026-11-28T00:01Z`, `27b4197e7`):** Pending fragments grew `+69` across `#428..#456` to **372
  `.jsonl` files** (**4,985 rows**: `124` files each under `intents/`, `plans/`, `executions/`) while
  `HOLON_LEDGER_BOT_TOKEN` remains unset.

### Proposed Change

1. Configure the `HOLON_LEDGER_BOT_TOKEN` repository secret on `Holon-Agentic-Coder/holon-agentic-coder` (maintainer
   action, mirroring Coherence Bean `0620`).
2. Dispatch `.github/workflows/promote-ledger.yml` (`workflow_dispatch` with `force=true` if needed) to promote and
   drain all `303` pending fragment files into canonical `holon-knowledge/ledger/{intents,plans,executions}.jsonl`.

### Expected Gain & Cost

- Drains 303 unpromoted fragment files (`4,357` rows) into canonical HAC ledgers and stops daily `::warning::` misses.
- Cost: repository secret configuration + one `workflow_dispatch` run.

## Acceptance Criteria

- [ ] `HOLON_LEDGER_BOT_TOKEN` is configured on `Holon-Agentic-Coder/holon-agentic-coder` and `promote-ledger.yml`
      succeeds without emitting the missing-token warning.
- [ ] `holon-knowledge/ledger/pending/` contains `0` unpromoted `.jsonl` files on `holon-agentic-coder/main`.

## Resolution
