---
# holon-agentic-coder-ref-metadata-0423
title: "Two agent sessions launch flows into one workspace with no shared registry, cap or log"
status: todo
type: bug
priority: high
tags:
  - harness
  - flow
  - concurrency
created_at: 2026-11-24T12:58:00Z
updated_at: 2026-11-25T05:45:00Z
---

## Problem

Two agent sessions drive flows in this workspace at the same time: this Claude Code session (wrappers started with
`python3 -u .agents/skills/holon_flow/scripts/run_holon_flow.py ... > todo/flow-<slug>.log`) and an Antigravity CLI
session (`agy`, PID 2573, wrappers started with `uv run python ... run_holon_flow.py` and no log file). Neither sees the
other's flows except through Stage 3 admission.

## Evidence (self-improvement audit, 2026-11-24T12:58Z)

- At 12:47Z six wrappers were alive: Beans 0403 and 0405 (Claude Code, `claude-fable-5-2`) and Beans 0265, 0399, 0376
  and 0153 (Antigravity, `gemini-4-neon`). The cap in `AGENTS.md` and `.agents/coordination.md` is 4. Four of the six
  had an engine running; 0265 and 0399 were waiting on admission. Each session kept to its own count.
- The four Antigravity flows write no `todo/flow-<slug>.log`; their steps can be read only from the checkpoints (stage
  start and end), so no step inside Stages 3 to 5 of PRs #273, #274 or coherence #53 to #55 can be timed.
- Cross-session overlap: the Antigravity flow for Bean 0376 (PR #273) was admitted over the Claude Code flow of Bean
  0405 through a sticky override (Bean 0422); then the Antigravity flow for Bean 0265 was launched at 12:23Z onto files
  the Claude Code flow of Bean 0405 (PR #275) was changing and has been refused since 12:29:50Z.
- Bean 0393 got two worktrees (`flow-preflight-ok-reply-slow-exit-and-retry`, failed in 3 ms at 11:38:06Z on a 38
  character slug, and `flow-intent-0393-preflight-retry`, which delivered PR #274); the first is left behind.
- Shared host: the Bean 0405 executor measured unit-suite times on a host running four to six flows and wrote "the
  difference is load from other tenants of the machine"; its three baseline runs spread 16.8 percent against a 15
  percent tolerance in its own plan. The OOM kill of Bean 0421 happened under the same load.

Two sessions are not what makes the ledger conflicts (any two merges do that, Bean 0371), but they are the cause of the
over-cap load and of the cross-session overlap above.

## Goal

- One workspace-wide registry of live flows that every launcher writes and reads: an exclusive-create claim file per
  flow under `.subagent/flows/` naming the session, PID, runtime, bean, slug, worktree and log path, removed on exit and
  taken over when its PID is dead.
- `run_holon_flow.py` refuses to start an engine when four engines are live in the registry (waiting wrappers do not
  count), whatever session launched them, and says which four.
- The wrapper writes `todo/flow-<slug>.log` itself whatever launched it (Bean 0412 Goal 1), so every runtime is timed.
- A flow whose acceptance is a timing measurement takes an exclusive host slot (no other engine in Stage 3 or 4 while it
  measures), or measures in CI.
- `AGENTS.md` says that only one session launches flows at a time, or how two share the registry.

## Notes

- Related: Bean 0390 (two runners on one checkpoint), Bean 0396 (flows survive the session), Bean 0421 (OOM under
  concurrent role containers), Bean 0422 (sticky override).
- Harness-only change (`.agents/skills/holon_flow/`, `AGENTS.md`, `.agents/coordination.md`).

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- Concurrency measured from the ledger rows and checkpoints, 00:28Z to 05:41Z: never more than 4 flows at a time across
  both sessions (3 Antigravity + 1 Claude Code at 00:28Z). The Antigravity session launched in waves of 3 (00:51Z,
  01:17Z to 01:20Z, 01:42Z to 01:43Z). No over-cap minute was seen, but each session still counts only its own flows.
- Cross-session blocking: the Claude Code flow for Bean 0371, launched at 05:27Z, was refused at 05:32:48Z on
  Antigravity PR #305 (`flow/git_refs.py`, a self-doc slice approved at 01:49Z and waiting for the merge). The
  Antigravity flow for Bean 0407 has been refused since 02:41:40Z, partly on Claude Code's #308 (Bean 0459 for the
  directory in its scope).
- Same-session blocking with an engine cause: #308 (Claude Code) waited 181.5 min (23:26:48Z to 02:28:17Z) because
  `gh pr diff 283` returned HTTP 406. Antigravity's #299 fixed this and merged at 05:20:56Z.
- No duplicate flow for one bean was found in the period. Bean 0407 has a single flow (Antigravity), and no Claude Code
  flow was started for it.
- Every merge shows `mergedBy: thomashan`, the account all sessions share, so the record cannot tell who merged into
  `main` (Bean 0458, step 5).
- Bean files and the audit log are shared too, and nothing claims an id. While this audit ran (05:41Z to 05:50Z), both
  sessions created 0452 and 0453, then both renamed to 0456 and 0457. One write to `.beans/self-improvement-audits.md`
  and one to Bean 0412 replaced the other session's text, which had to be written again. Bean ids need an
  exclusive-create claim, the same as flows, and edits to shared files should append rather than rewrite the whole file.
