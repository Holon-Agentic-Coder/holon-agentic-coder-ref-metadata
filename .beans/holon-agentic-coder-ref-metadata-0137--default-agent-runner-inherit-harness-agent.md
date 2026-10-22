---
# holon-agentic-coder-ref-metadata-0137
title: "Default agent runner must be inherited from the harness agent, not hard-coded to antigravity-agent"
status: todo
type: task
priority: high
tags:
  - cli
  - holon-flow
  - agent-runner
  - dx
  - provenance
created_at: 2026-10-22T07:20:00Z
updated_at: 2026-10-22T07:20:00Z
---

## Problem

The runner is a compile-time constant, so a flow silently uses a runner the operator may not even be able to
authenticate, no matter who is driving the harness.

- `cli.py`: `--agent` defaults to `antigravity-agent` at `:1159` (plan), `:1189` (execute), `:1391` (review-loop), and
  the flow branch `:1777` (`agent=args.agent or "antigravity-agent"`).
- `flow.py`: same literal in `FlowContext.agent` (`:232`), checkpoint default (`:305`), context default (`:164`),
  consensus attribution (`:1360`), and review records (`:2735`).
- There is **no** override surface: grepping for a default-runner env var finds only `HOLON_AGENT_KEY` (an SSH key) and
  `PI_CODING_AGENT_DIR` (a filesystem path, not an identity).

Consequences observed on 2026-10-22: the default runner was at individual quota (`RESOURCE_EXHAUSTED 429`) and the run
failed at Stage 2 after having already created the intent branch and pushed it; the operator learned the quota state
only from the planner's stderr. Every audited ledger row also carries `agent` / `model`, so the provenance record names
a runner that was never chosen deliberately.

## Scope

- Resolve the runner by precedence, first match wins, and log the decision plus its reason:
  1. explicit `--agent`,
  2. `HOLON_AGENT` (new, also honoured by `holon flow`),
  3. **the harness agent currently driving the session** — detect from the runtime environment (`PI_CODING_AGENT` for
     pi, which this harness already exports; the equivalent markers for `claude`, `codex`, `opencode`, and `agy`),
  4. `antigravity-agent` as the last-resort fallback, logged as a fallback.
- Map the detected identity onto `AGENT_IMAGE_MAPPING` (`cli.py:88`) and fail early if it has no image.
- Add a pre-flight readiness probe (`holon doctor`, or a `--preflight` check run before Stage 1) that exercises the
  selected runner with a one-token prompt inside its container and reports the concrete blocker — quota exhausted, not
  logged in, expired key, missing mount — **before** any intent branch is created or pushed. Today the first signal is a
  planner failure minutes into the run.
- Keep the resolved runner in the ledger rows exactly as it is recorded now, so provenance names the runner that
  actually authored the change.
- Tests: precedence order (flag beats env beats harness detection beats fallback), unmapped-runner failure, and a mocked
  quota-exhausted probe that aborts before Stage 1 with an actionable message.

## Acceptance criteria

- Running the flow from inside a pi-driven harness defaults to `pi-agent` (and equivalently for other harnesses) with no
  flags, and the log line states why that runner was chosen.
- `--agent` and `HOLON_AGENT` still win over detection.
- An unusable runner is reported before any branch or ledger write happens.
- `uv run pytest` passes in `apps/sandbox-executor`.

## Relates to

Bean 0132 (blocked on exactly this, among other runners), Bean 0139 (budgets so a dead runner fails fast), and
AGENTS.md's AGY-centric subagent guidance, which should be softened to "the runner that is driving the harness".
