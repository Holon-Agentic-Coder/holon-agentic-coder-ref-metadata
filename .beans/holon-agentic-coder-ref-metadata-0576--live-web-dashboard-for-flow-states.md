---
# holon-agentic-coder-ref-metadata-0576
title: "Live web dashboard that pushes every bean and flow state, replacing on-demand progress tables"
status: todo
type: feature
priority: high
tags:
  - harness
  - dashboard
  - bean-progress
  - observability
created_at: 2026-11-26T23:29:34Z
updated_at: 2026-11-26T23:29:34Z
---

## Instruction (maintainer, 2026-11-27 local)

"Instead of having to show the bean progress we should have a web dashboard which pushes all the states to the
dashboard. Make a bean for this."

## Problem

Progress is only visible when someone asks and an agent runs the bean_progress skill (about 10 s per run, a full table
pasted into the chat each time). Between asks, nobody sees a flow halt, park, open a PR, get approved, become ready to
merge or merge.

## Goal

A local web dashboard that always shows the current state of every in-flight bean and flow, updated by push, so the
maintainer opens one page instead of asking.

## Design

- **One state model.** Reuse the bean_progress collector (`--json`: rows with stage, in-stage time, live, PR & CI,
  merge_state, total, notes) as the single source; the table and the dashboard render the same data, so they never
  disagree.
- **Push, not ask.**
  - Event producers write state changes as they happen: the flow wrapper (`run_holon_flow.py`: stage start/end,
    checkpoint, halt, park, resume, PR opened), post_pr_merge (merged, closed bean), and the review loop (iteration,
    verdicts).
  - A small local server (localhost only) merges these events with a periodic collector refresh (GitHub CI/merge state,
    process liveness) and pushes updates to the browser over Server-Sent Events (or WebSocket).
  - The page updates in place; no manual refresh.
- **Views.**
  - The bean_progress table with the same columns (Bean #, Target, Title, Agent, Model, Stage, In Stage, Live, PR & CI,
    Merge, Total) and the 🟢/🟡/🔴 dots.
  - The parked chain (who waits on which PR or file).
  - Slot usage against the cap (8).
  - Recent events (halts, approvals, merges) with timestamps.
  - Per-flow detail: checkpoint, log tail, PR link, review findings.
- **Alerts.** Ready-to-merge, halt and calibration-done events are highlighted. ntfy stays as it is (calibration only);
  the dashboard does not replace it.
- **Safety.**
  - Binds to 127.0.0.1 only.
  - Read-only: no buttons that merge, resume or stop anything.
  - No secrets in the page (the gh token stays server-side).
  - Started by a harness script and optionally by the SessionStart hook, idempotently.

## Constraints

- Harness-only (no target-repository change). Self-explaining code invariant: no docstrings, no comments except
  `# why:`.
- Every timestamp comes from the clock, in UTC; the dashboard shows UTC and local time.
- Tests via `uv run pytest`: collector-to-JSON contract, event ingestion and ordering, SSE stream (a fake client
  receives an update after an event), stale-state detection (a dead runner turns 🔴 within one refresh).
- Register its checks in `.agents/invariants.yml` where it enforces an invariant (e.g. slot cap).

## Acceptance

- Opening the dashboard shows the same rows as `bean_progress.py` at that moment.
- A stage change, halt, PR open or merge appears on the page within 10 s without a reload.
- The bean_progress skill points the maintainer to the dashboard URL; the chat table stays available as a fallback.
- Related: bean_progress skill, Bean 0412 / 0496 (per-step timing), Bean 0562 (invariant checks).
