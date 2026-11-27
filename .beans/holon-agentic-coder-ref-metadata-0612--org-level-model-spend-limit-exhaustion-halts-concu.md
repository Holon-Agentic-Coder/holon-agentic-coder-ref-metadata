---
# holon-agentic-coder-ref-metadata-0612
title: "Org-level model spend-limit exhaustion halts concurrent flows and retries dead provider"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - quotas
  - model-tiers
  - holon-agentic-coder
created_at: 2026-11-27T05:18:43Z
updated_at: 2026-11-27T21:18:45Z
---

## Notes

### Evidence (2026-11-27T04:43Z–05:18Z fifth-merge audit)

- Three concurrent flows hit the same org-level Claude failure within 83 seconds:
  - `self-doc-tests-51` (`04:48:57Z`):
    `Reviewer 3: claude-agent / claude-opus-5-5: FAILED (the reviewer exited with code 1 (other: You've hit your org's monthly spend limit ...))`
  - `self-doc-tests-48` (`04:49:18Z`): all 3 reviewers failed with the same `org's monthly spend limit` error.
  - `self-doc-tests-45` (`04:50:20Z`): `Reviewer 1` failed with the same `org's monthly spend limit` error.
- At `05:11:15Z` (22 min later), `self-doc-tests-51` resumed on `claude-agent` and ran preflight into the same
  `monthly spend limit` error again before switching to `antigravity-agent / gemini-4-neon`.
- In addition, `slot-keeper` had queued/launched `self-doc-tests-45..51` on `claude-agent / claude-opus-5-5` even though
  `AGENTS.md` sets `antigravity-agent / gemini-4-neon` as the default coding model.

### Proposed Change

- Record a shared host-level provider cooldown marker (e.g., under `~/.holon/` with reset/TTL timestamp) when preflight
  or a role fails with org spend-limit / quota exhaustion, so concurrent launches and checkpoint resumes skip the
  exhausted provider immediately instead of halting or re-probing it.
- Ensure `slot_keeper.py` and queued intents default to the configured coding runner/model (`antigravity-agent` /
  `gemini-4-neon` per `AGENTS.md`) unless explicitly overridden.

### Expected Gain & Cost

- Prevents cascading Stage 4 halts across all 8 concurrent slots and saves ~2–5 min of wasted preflight/reviewer
  container turns per halted flow.
- Cost: small shared cooldown file read/write in preflight/wrapper + `slot_keeper.py` default check.

## Acceptance Criteria

- [ ] A shared host-level provider cooldown marker (under `~/.holon/` with reset/TTL timestamp) is recorded when
      preflight fails with org spend-limit or quota exhaustion, so concurrent launches and checkpoint resumes fail fast
      without re-probing the exhausted provider while its cooldown is active.
- [ ] Hermetic unit tests in `tests/test_preflight.py`, `tests/test_preflight_outage.py`, and
      `tests/test_preflight_retries.py` verify cooldown marker write, expiry, and fast-fail behaviour under
      `uv run pytest` and `uv run task lint`.
- [ ] Ensure `slot_keeper.py` and queued intents default to the configured coding runner/model (`antigravity-agent` /
      `gemini-4-neon`) unless explicitly overridden.

## Flow

- **Slice 1 (`hac-provider-cooldown`):** Launched `todo/intent-0612-hac-provider-cooldown.json`
  (`todo/intent-coverage-0612.json`) covering `cli/preflight.py`, `preflight.py`, `preflight_outage.py`, new
  `preflight_cooldown.py`, and `tests/test_preflight*.py` for the target-repo cooldown marker. AC #3
  (`.agents/scripts/slot_keeper.py`) is harness-side and deferred (`todo/intent-coverage-0612.json`).

## Resolution
