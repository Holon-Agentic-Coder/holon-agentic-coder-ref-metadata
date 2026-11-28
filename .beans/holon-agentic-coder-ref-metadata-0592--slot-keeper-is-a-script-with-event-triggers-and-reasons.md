---
# holon-agentic-coder-ref-metadata-0592
title: "Slot keeper: a script with event triggers and a recorded reason for every unlaunched queue item"
status: in-progress
type: bug
priority: high
tags:
  - harness
  - holon-flow
  - scheduling
  - slots
created_at: 2026-11-27T00:57:23Z
updated_at: 2026-11-27T05:19:35Z
---

## Evidence

- `todo/slot-keeper.log`: entries at 00:42:22Z (live=8) and 00:53:37Z (live=4). The standing rule is a pass every 60 s;
  the gap is 11 min. Between 00:39:32Z and 00:53:37Z the queue held six ready intents (0400, 0532, 0570, 0558 x3) and
  live was 4 at the end, so four slots idled with work queued. The maintainer had to ask why.
- The `launched=` field repeats `0574,0583,0436,resume0567` on every line since 00:31:49Z: it carries over earlier
  launches instead of reporting this pass, so the log cannot show what a pass did.
- No line says why a queued item was not launched (overlap with an open PR, with a sibling intent, cap, quota). Three
  0558 intents and 0570 share files, so overlap is the likely reason, but this is not recorded, so it is not measured.
- Live fell from 8 to 4 when several flows reached calibration together; calibrated flows exit, so the drop is sudden
  and nothing triggers on it.
- Category `overlap-scheduling` recurs: CF-0023, CF-0024, CF-0026, CF-0027 (high priority). CF-0024 rule (poll every 60
  s) was not met; CF-0027 rule (re-count before each launch) is the only part visible in the log.

## Goal

Slots are refilled within 60 s of freeing, and every pass states what it did and why each queued item stayed queued.

## Design

- The keeper is a script (`.agents/scripts/`), not a model turn: a pass costs no tokens and cannot stall on a long turn.
  A model is called only to draft or repair an intent that failed its checks.
- Pass: count live runners (ps), re-count before each launch, evaluate each queue item in order, launch while live <
  cap.
- Log one line per pass: `ts live cap launched=[this pass only] held=[item:reason]` with reasons
  `overlap:<file>:<holder>`, `blocked_by:<bean>`, `cap`, `quota`, `check:<failure>`.
- Triggers besides the 60 s timer: a flow log reaching Stage 5 or "calibrated", a PR merge, a park. A flow in Stage 5 no
  longer counts against the cap for launching purposes (it uses no coding-agent turns); decide with the maintainer.
- Heartbeat: if no pass is logged for 120 s the watcher raises a notice and restarts the keeper.
- Queue items held for overlap are retried when the holder merges; the queue order is recomputed so that a
  non-overlapping item is never held behind an overlapping one.

## Acceptance

- [x] Keeper runs as a script; a pass with a held item logs the reason; `launched` lists only this pass.
- [x] Test: live 4, cap 8, six queued with two disjoint sets: launches enough to reach 8 or until all remaining overlap,
      and logs reason for each held item.
- [x] Test: no pass for 120 s triggers the heartbeat notice.
- [x] Event trigger: a flow reaching calibration triggers a pass within 10 s.
- [x] Code has no docstrings and no comments except `# why:`; run with `uv run pytest`.

## Notes

- Extends beans 0545 and 0576; CF-0024 and CF-0027. Idle time per slot is still not measured; the log's live count per
  pass becomes the measurement.
- **Audit evidence (2026-11-27T04:43Z–05:18Z, high-priority repeat of CF-0027 & CF-0024):** `todo/slot-keeper.log` shows
  `live=10` again at `04:43:15Z` and `04:47:09Z` (exceeding the 8-flow cap), and stopped logging completely after
  `04:47:09Z` (25+ min gap against the 60 s rule and 120 s heartbeat). Also launched `self-doc-tests-45..51` on
  `claude-agent` instead of `AGENTS.md` default `antigravity-agent` / `gemini-4-neon`.

## Progress

2026-11-27T04:37:17Z: `.agents/scripts/slot_keeper.py` (tests: `tests/test_slot_keeper.py`, docs and launchd example:
`.agents/slot-keeper.md`). One pass per invocation, `--loop-seconds` adds the 60 s timer and a trigger within 5 s of a
flow state-file change, `--check-heartbeat` raises the 120 s notice. Remaining: install the launchd job and switch the
coordinator to the queue file (maintainer step); PR-merge and park triggers beyond the state-file change; the Stage 5
cap exemption is undecided; keeper restart relies on launchd `KeepAlive`.
