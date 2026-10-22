---
# holon-agentic-coder-ref-metadata-0132
title: "Record stage 4/5 review action entries (ACT-REV/ACT-POST) in executions.jsonl"
status: in-progress
type: bug
priority: medium
tags:
  - holon-flow
  - ledger
  - provenance
  - review-loop
  - calibration
  - holon-coherence
  - holon-agentic-coder
created_at: 2026-10-22T09:45:00Z
updated_at: 2026-10-22T09:35:00Z
---

## Problem

`AGENTS.md` rule 14 states that discrete micro-actions — including review-loop actions `ACT-REV`, `ACT-FIND`, `ACT-POST`
— and lifecycle summaries must be interleaved chronologically inside `holon-knowledge/ledger/executions.jsonl` under
`LedgerLock`.

In practice **no such records are ever written**. Verified on `holon-coherence` at PR #26 head `22f0f10`:

```text
grep -c "ACT-REV\|ACT-POST\|ACT-FIND" holon-knowledge/ledger/executions.jsonl  ->  0
```

Zero matches across the entire ledger history: every previously merged execution carries only stage-3 `action`/`summary`
entries for its `E-...` id. Stage 4 (PR review loop) and stage 5 (calibration) therefore leave no action-level
provenance in the append-only ledger, even though the ledger is declared the system of record.

This was raised as NIT-6b while reviewing PR #26 and rejected there as **out of scope for that PR**: it predates PR #26,
is systemic across the whole repository history, and cannot be fixed inside a feature PR because hand-backfilling an
audited target-repo ledger from the host worktree would itself violate the sole-change-path rule.

## Scope

- Determine whether the flow engine (`holon review` / the PR review-loop integration point) is meant to emit `ACT-REV` /
  `ACT-FIND` / `ACT-POST` entries, and whether calibration is meant to emit an action entry for stage 5.
- If intended but unwritten: fix the writer so those entries are appended under `LedgerLock` at the correct stages in
  both target repositories.
- If not intended: correct `AGENTS.md` rule 14 and the flow docs so the documented invariant matches the implemented
  3-ledger behaviour, rather than leaving a permanently-violated rule in place.
- Do **not** backfill historical entries; the ledger is append-only and retroactive records would falsify provenance.

## Acceptance criteria

- Either a new execution's ledger diff demonstrably contains the stage-4/stage-5 action entries, or the documented
  invariant no longer claims them.
- Target-repository changes land through the 5-stage Holon flow only.
- Docs and code agree on what `executions.jsonl` records.

## Source

- Raised as NIT-6b by ensemble reviewer 3 (blind pass) during `pr-review-loop` iteration 4 on
  <https://github.com/Holon-Agentic-Coder/holon-coherence/pull/26>, adjudicated `rejected: out of scope` and deferred
  here. Ruling recorded in `.subagent/holon-coherence_pr26_coordination.json` (`rejected_suggestions`,
  `adjudicated_findings`).
- The loop adjudication deferred **both** iteration-4 nits to this bean, but NIT-6a (wall-clock `time.time()` deadline
  in `wait_for_proxy_ready()`) is an unrelated finding and is tracked separately in **Bean 0133**. This bean covers
  NIT-6b only.
- Evidence still holds on `holon-coherence` `origin/main` (`29b7e50`, after PR #26 merged): counting
  `ACT-REV|ACT-POST|ACT-FIND` in `holon-knowledge/ledger/executions.jsonl` returns `0` matches, while the same query on
  `holon-agentic-coder` `origin/main` returns `159` matches. The gap is per-repository, so the fix must be verified in
  both target repositories rather than assumed fixed upstream.

## Progress (2026-10-22) -- blocked at Stage 2

Work is in `apps/holon-agentic-coder/flow-0132-stage-4-5-ledger-actions` (branch `flow/0132-stage-4-5-ledger-actions`,
cut from `origin/main` at `3bef6f7`, own virtualenv from `uv sync --group dev`). Intent file:
`todo/intent-0132-stage-4-5-ledger-actions.json`.

- **Stage 1 (Intent): done.** `holon intent` created and pushed `I-1792635019-flow-stage-4-5-ledger-action-entries/_`
  together with its `intents.jsonl` entry.
- **Stage 2 (Plan): blocked, no usable agent runner.** Every runner on this host failed:
  - `antigravity-agent` (default): `RESOURCE_EXHAUSTED (code 429) individual quota reached`, resets roughly 47h after
    the attempt.
  - `claude-agent`: host CLI reports `Not logged in`.
  - `codex-agent`: `refresh token was already used ... please log out and sign in again` (401).
  - `opencode-agent`: `This API key has expired`.
  - `pi-agent` on the host-local vMLX gateway (`HOLON_LOCAL_LLM=1`, `HOLON_HOST_LOCAL_HOSTS=localhost:8081`, model
    `vmlx/JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M`): the planner container ran 17 minutes and then failed with
    `Response was truncated: the model reached its output token limit`. The `vmlx` entry in `~/.pi/agent/models.json`
    declares `contextWindow` but no `maxTokens`, and a short control prompt on the same model succeeds, so the cap bites
    at planner-length outputs.
- **Related findings logged while attempting this bean:** Bean 0134 (`holon flow` dispatches no role agent and opened
  the now-closed empty PR #89), Bean 0135 (fabricated `CONFLICTING`/`DIRTY` verdict from a missing ref), Bean 0136 (live
  GitHub token printed in CLI command echoes).
- **GitHub side is verified working as of 2026-10-22 09:30 UTC**, so only the coding-agent credential gates a retry: the
  maintainer rotated the `gh` token (Bean 0136), `gh api user` and the repository API round-trip succeed, and PR #89 is
  confirmed `CLOSED`. `holon` needs no reconfiguration because `find_github_token()` (`cli.py:125-138`) falls back to
  `gh auth token` at call time rather than caching a value.
- **To resume** once a runner works: in the worktree above run
  `holon plan "I-1792635019-flow-stage-4-5-ledger-action-entries/_" --agent <runner> --model <model> --repo-dir .`, then
  `holon execute`, `holon review-loop <execution_branch> --auto-pr`, and `holon calibrate` as the pre-merge stage.
