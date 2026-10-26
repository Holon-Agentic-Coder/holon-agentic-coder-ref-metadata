---
# holon-agentic-coder-ref-metadata-0133
title: "Use a monotonic clock for the proxy readiness poll deadline"
status: completed
type: bug
priority: low
tags:
  - coherence
  - proxy
  - readiness
  - time
  - robustness
created_at: 2026-10-22T00:30:00Z
updated_at: 2026-10-26T02:33:21Z
---

## Problem

`wait_for_proxy_ready()` in `holon-coherence` bounds its readiness poll with a wall-clock deadline, while sibling
polling loops in the same module already use a monotonic clock. On `origin/main` (`29b7e50`) of `holon-coherence`:

```text
src/holon_coherence/commands/start.py:154    deadline = time.time() + timeout
src/holon_coherence/commands/start.py:159    while time.time() < deadline:
src/holon_coherence/commands/start.py:396    deadline = time.monotonic() + 10.0
src/holon_coherence/commands/start.py:397    while in_use(port) and time.monotonic() < deadline:
```

`time.time()` is subject to NTP slew, manual clock changes, and suspend/resume jumps. A backwards step during sandbox
startup stretches the readiness wait past its configured timeout (a stalled `holon-coherence start`); a forwards step
short-circuits the poll and reports the proxy as not ready while it is still booting, which is the exact cold-start
failure mode Bean 0130 was raised to remove. The timeout contract should be measured against a clock that only moves
forwards.

## Scope

- Convert the `wait_for_proxy_ready()` deadline computation and loop bound to `time.monotonic()` so the timeout is a
  duration, not a wall-clock instant.
- Audit the remaining `time.time()` timeout/deadline usages in `holon-coherence` and convert any that measure an elapsed
  duration (leave genuine epoch timestamps — log lines, wire records, telemetry timestamps — alone).
- Add a regression test that drives the poll with an injectable/fake clock and asserts that a wall-clock step (backwards
  and forwards) cannot extend or short-circuit the poll, consistent with the fake-clock test style already introduced in
  Bean 0130.

## Acceptance criteria

- No duration-bounded loop in `holon-coherence` measures elapsed time with `time.time()`.
- `uv run pytest` passes in the `holon-coherence` worktree, including the new clock-step regression test.
- Change lands through the 5-stage Holon flow only.

## Source

Raised as **NIT-6a** by ensemble reviewer 2 (blind pass) during `pr-review-loop` iteration 4 on
<https://github.com/Holon-Agentic-Coder/holon-coherence/pull/26> and rejected there as not diff-grounded (pre-existing
unchanged context at merge-base `d8e34d9`). The loop adjudication recorded it as "deferred to bean 0132", but Bean 0132
covers only NIT-6b (the `executions.jsonl` stage-4/5 action-record gap), so the clock finding had no tracking bean. This
bean closes that bookkeeping gap; the ruling recorded in `.subagent/holon-coherence_pr26_coordination.json`
(`rejected_suggestions`, `adjudicated_findings`) is the primary source.

## Execution status (2026-10-22)

Not started, blocked by the same unusable agent runners recorded in Bean 0132. The change is prepared: it is bundled
with Bean 0129 in `todo/intent-0129-0133-coherence-mitmweb-monotonic.json`, to be run in
`apps/holon-coherence/flow-0129-0133-coherence-mitmweb-monotonic-clock`. Target lines on `origin/main` (`29b7e50`) are
confirmed still present at `src/holon_coherence/commands/start.py:154` and `:159`.

## Resolution

- **Pull Request**:
  [Holon-Agentic-Coder/holon-coherence#27](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/27)
- **5-Stage Provenance**:
  - Intent: `I-1792762893-coherence-mitmweb-inspection-and-monotonic-readiness/_`
  - Plan: `P-1792766452-claude-agent-claude-opus-5-5`
  - Execution: `E-1792767369-claude-agent-claude-opus-5-5`
  - Review: 3-agent ensemble consensus `APPROVED` (3/3) at `de60a6d` after 5 iterations.
  - Calibration: report `aec5f7d` plus Bean 0146 annotation `ed2cf2f` (Predicted EV 5.84 from the wrong row; Overall
    6.48 | Actual EV 5.18).
- **CI Status**: passing. Merged by the maintainer on 2026-10-24 as `acbe924`.
- **Outcome**: Beans 0129 and 0133 were delivered together. A plain mitmweb inspector exposes live requests and
  responses, and the proxy readiness deadline now uses a monotonic clock.
