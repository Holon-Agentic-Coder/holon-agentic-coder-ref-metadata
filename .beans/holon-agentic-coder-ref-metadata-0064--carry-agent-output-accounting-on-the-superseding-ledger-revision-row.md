---
# holon-agentic-coder-ref-metadata-0064
title: "Carry the agent-output accounting on the superseding ledger_revision: 2 row"
status: todo
type: bug
priority: low
tags:
  - sandbox-executor
  - ledger
  - observability
  - flow
created_at: 2026-09-30T18:55:00Z
updated_at: 2026-09-30T18:55:00Z
---

The git-recovery-failure path in `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` writes **two**
`executions.jsonl` rows for one execution. The first (`ledger_revision: 1`, ~line 1235) carries the agent-output
accounting introduced by PR #61; the second (`ledger_revision: 2`, ~line 1326) supersedes it and declares itself, in its
own comment, **"authoritative for readers"** — but it carries **no** `agent_output_truncated` and **no**
`agent_output_bytes` key.

```console
$ grep -n 'agent_output_bytes\|agent_output_truncated\|ledger_revision' \
      apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py
1235:                "agent_output_truncated": agent_output_truncated,
1236:                "agent_output_bytes": agent_output_bytes,
1237:                "ledger_revision": 1,
1338:                            "ledger_revision": 2,      # no agent_output_* fields
```

Because the ledger is append-only and readers are told to prefer the highest revision, a reader of a recovery-failed
execution sees a row with **no byte accounting at all** — the keys are absent, not `false`/`0` — so it cannot tell
whether the record kept bounded diagnostics or nothing. The diagnostics themselves are **not** lost: the
`## Agent Output` block is still in the execution file and the fields are still in the `rev-1` row. This is an
accounting asymmetry, not data loss, which is why it is `priority: low`.

## Origin

`ledger_revision: 2` was introduced by **PR #60 (`9e66c88`)**, not by PR #61; PR #61 added the fields to the `rev-1` row
only. Found by ensemble reviewer 2 during PR #61 iteration 13 and deliberately **not** actioned in that PR: adding keys
to a row shape that PR #60 already merged onto `main` is a contract change that deserves its own intent rather than a
last-mile edit at a review gate (`F-IT13-R2-1` in `.subagent/holon-agentic-coder_pr61_coordination.json`).

## Acceptance criteria

1. The `rev-2` row carries `agent_output_truncated` and `agent_output_bytes` with the same values the `rev-1` row
   reported for the same execution (both variables are already in scope at that point).
2. A regression test drives the git-recovery-failure path, reads `executions.jsonl`, and asserts that the
   **highest-revision** row — not just the first — states the byte accounting.
3. Decide and document the reader contract for a superseding row: either "a superseding row must repeat every field it
   intends readers to rely on", or "readers must merge rows by `execution_id`". Pick one and say so where the
   `ledger_revision` comment lives, so the next field added to `rev-1` does not reproduce this gap.
4. `holon-knowledge/ledger/executions.jsonl` stays append-only: no historical row is rewritten.
