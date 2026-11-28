---
# holon-agentic-coder-ref-metadata-0625
title: "Stage 3 and 4 quota exit-3 halts idle 2h instead of stepping down model ladder"
status: todo
type: feature
priority: high
tags:
  - flow
  - quotas
  - model-tiers
  - holon-agentic-coder
created_at: 2026-11-27T10:55:04Z
updated_at: 2026-11-27T15:55:01Z
---

## Notes

### Evidence (2026-11-27T07:49Z–10:49Z fifth-merge audit)

- At `08:42–08:46Z`, `antigravity-agent / gemini-4-neon` hit `quota (resets 2026-11-27T10:30Z)` (`RESOURCE_EXHAUSTED`),
  cleanly halting **6 concurrent flows** with container exit code `3`:
  - Stage 4: `HAC #414` (`flow-hac-broad-except-ratchet`, `08:44:20Z`), `HAC #415` (`flow-hac-import-cycle-ratchet`,
    `08:45:53Z`). Both resumed cleanly after `10:30Z` (`110–112 min` idle) and passed `3/3 APPROVED` + Stage 5.
  - Stage 3: `0538` (`flow-hac-architecture-audit-kb-entries`, `08:43:20Z`), `0617`
    (`flow-stage5-fail-closed-calibrate`, `08:44:29Z`), `0621` (`flow-coherence-import-cycle-ratchet`, `08:42:23Z`),
    `0623` (`flow-coherence-ratchet-test-deadlock`, `08:42:21Z`). All four idled `~126 min` before resuming at `10:49Z`.
- While exit-code-3 failure containment worked cleanly with zero corrupted state, the engine made no attempt to step
  down the configured `antigravity-agent` fallback ladder (`gemini-4-neon` $\rightarrow$ `gemini-4-argon` $\rightarrow$
  `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash` per `AGENTS.md`), costing `110.8 min` median (`126.2 min` max)
  idle wall time across `6` slots.
- Related: Bean `0612` tracks a shared host-level cooldown marker for org-level spend limits so launches do not re-probe
  exhausted providers; Bean `0424` covers Stage 4 transient network/Docker retries. This bean owns automatic
  intra-ladder model step-down on Stage 3/4 quota `exit code 3`.

### Evidence (2026-11-27T15:46Z fifth-merge audit)

- At `12:45:16Z–12:45:46Z`, **3 concurrent Stage 3 flows** (`0599` `flow-replan-feedback-file-dispatch`, `0590`
  `flow-stage1-requires-assumptions`, `0619` `flow-stage4-main-baseline-guard`) failed Stage 3 `execute` with
  `exit code 3` (`3.8–9.4 min` execute turns) and sat idle for **`~181 min` (`3.0 hours`, `>9` flow-hours lost)** until
  restarted at `15:46:55Z–15:47:02Z` (coordinated with `0612`).

### Proposed Change

1. Detect quota/rate-limit `exit code 3` signatures (`RESOURCE_EXHAUSTED`, `Individual quota reached`, `resets ...`) in
   Stage 3 (`execute`) and Stage 4 (`review` / `resolver`) turns.
2. Automatically step down to the next available model on the configured runner ladder (`gemini-4-neon` $\rightarrow$
   `gemini-4-argon` $\rightarrow$ `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash`), persist the active cooldown in
   the host cooldown marker (`0612`), and record the fallback model in the execution/review ledger row.
3. Halt cleanly (preserving checkpoint) only when the entire configured ladder is exhausted.

### Expected Gain & Cost

- Eliminates `~110–126 min` quota-reset idle stalls per halted flow (`>11` flow-hours saved in one quota window) when
  lower ladder tiers still have capacity.
- Cost: small ladder-advance helper wired into Stage 3/4 turn failure handling + hermetic tests.

## Acceptance Criteria

- [ ] Stage 3 and Stage 4 turns exiting with code `3` and a quota-exhaustion message automatically retry on the next
      configured fallback model in the runner's ladder without halting the flow.
- [ ] Each fallback step records the exhausted model + reset hint and the replacement model in checkpoint/ledger logs.
- [ ] When all ladder tiers are exhausted, the flow halts cleanly at the checkpoint without corrupting branch state.
- [ ] Hermetic tests verify ladder step-down and full-ladder exhaustion; `uv run pytest` passes.

## Resolution
