---
# holon-agentic-coder-ref-metadata-0118
title: "Implement explicit native holon review-loop CLI step after execute stage"
status: completed
type: task
priority: high
tags:
  - holon-flow
  - cli
  - pr-review-loop
  - review
  - architecture
  - holon-agentic-coder
created_at: 2026-10-17T07:05:00Z
updated_at: 2026-10-18T09:40:00Z
---

## Summary

Promote the Pull Request review loop from an external agent harness skill (`pr-review-loop`) into an explicit, native
containerised `holon review-loop` (`holon review`, `holon pr-review-loop`) CLI command and first-class sandboxed role
agent (**`Holon Review Loop Agent`**) within `holon-agentic-coder`, following the exact same containerised role pattern
as `intent-creator` (`Holon Intent Agent`), `planner` (`Holon Planner Agent`), and `executor` (`Holon Executor Agent`).

## Context & Problem Statement

Currently, Stages 1–3 of the Holon flow run inside containerised role agents dispatched via `cli.py` ->
`run_docker_container(role, ...)` -> `entrypoint/role_dispatcher.sh` -> `sandbox_executor.entrypoint.<role>`:

| #   | Stage              | Container Role (`HOLON_ROLE`) | Entrypoint Module                             | Git Author Identity                                                       |
| --- | ------------------ | ----------------------------- | --------------------------------------------- | ------------------------------------------------------------------------- |
| 1   | Intent             | `intent-creator`              | `sandbox_executor.entrypoint.intent_creator`  | `Holon Intent Agent <intent-agent@holon-agentic-coder.com>`               |
| 2   | Plan               | `planner`                     | `sandbox_executor.entrypoint.planner`         | `Holon Planner Agent <planner-agent@holon-agentic-coder.com>`             |
| 3   | Execute            | `executor`                    | `sandbox_executor.entrypoint.executor`        | `Holon Executor Agent <executor-agent@holon-agentic-coder.com>`           |
| 4   | **PR Review Loop** | **`review-loop`**             | **`sandbox_executor.entrypoint.review_loop`** | **`Holon Review Loop Agent <review-loop-agent@holon-agentic-coder.com>`** |
| 5   | Calibration        | Host/Container calibration    | `sandbox_executor.calibration`                | `Holon Calibration Agent <calibrate-agent@holon-agentic-coder.com>`       |

### Why Stage 4 Must Follow the First-Class Containerised Role Pattern:

1. **Isolated Workspace Checkout**: Like `planner.py` and `executor.py`, `review_loop.py` must clone the target
   `execution_branch` (`I-.../P-.../E-.../_`) from `HOLON_REPO_URL` into `/home/holon/.holon-sandbox/workspace` inside
   the container rather than mutating a host worktree.
2. **Real Agent-Driven Review & Resolution**: Inside the container, `review_loop.py` must invoke
   `get_runner(agent_name)` to execute the multi-pass review ensemble and, when findings or verification failures are
   detected, invoke the configured coding agent (`get_runner(agent_name)`) to apply code fixes in the checked-out
   workspace, run tests and linters, and commit + push new commits to the execution branch.
3. **Audited Provenance Identity**: Every review-loop fix commit and ledger update on the execution branch must be
   authored by **`Holon Review Loop Agent <review-loop-agent@holon-agentic-coder.com>`** with RFC 2822 git trailers
   (`Action-Origin: pr_review`, `Review-Iteration`, `Review-Finding-Ids`, `Review-Severity`) and recorded in
   `holon-knowledge/ledger/executions.jsonl`.

## Tasks & Scope

- [x] Dispatch `HOLON_ROLE=review-loop` in `apps/sandbox-executor/entrypoint/role_dispatcher.sh` to
      `python3 -m sandbox_executor.entrypoint.review_loop "$@"`.
- [x] Implement `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`:
  - Clone `execution_branch` into `get_workspace_dir()`, fetch `origin/main`, and proactively check/resolve conflicts.
  - Configure `git config --local user.name "Holon Review Loop Agent"` and
    `git config --local user.email "review-loop-agent@holon-agentic-coder.com"`.
  - Raise or update the GitHub PR via `generate_semantic_pr_metadata` and `create_or_update_pr`.
  - Iteratively run verification + agent-driven review passes (`get_runner(agent_name)`) and agent-driven resolution
    passes (`get_runner(agent_name)`), committing fixes and `executions.jsonl` updates as
    `Holon Review Loop Agent <review-loop-agent@holon-agentic-coder.com>` and pushing to `origin <execution_branch>`.
  - Dual-post consensus review to GitHub (`post_pr_review_consensus`) and halt for human merge (Bean 0034).
- [x] Update `cli.py` so `holon review` / `holon review-loop` / `holon pr-review-loop` accepts `--agent`, `--model`,
      `--mitm-web` and dispatches `run_docker_container("review-loop", image_name, container_args, ...)` (with `--local`
      / `HOLON_IN_SANDBOX=1` / `--dry-run` support for in-process execution).
- [x] Add unit tests in `apps/sandbox-executor/tests/test_review_loop.py`, `test_cli.py`, and `test_flow.py`.
- [x] Route implementation through the 5-stage Holon flow.

## Resolution Summary

Implemented containerised `Holon Review Loop Agent` (`sandbox_executor.entrypoint.review_loop`) with dispatch from
`role_dispatcher.sh` (strictly matching `review-loop)`), `cli.py`, and `flow.py`. Configures git identity
`Holon Review Loop Agent <review-loop-agent@holon-agentic-coder.com>`, performs isolated workspace checkout, runs
multi-pass ensemble reviews and agent fixes, logs granular actions in `executions.jsonl`, and halts at consensus
approval under Bean 0034. Completely removed the `fail_fast` CLI argument and function parameter from `flow.py`, and
placed `holon-config/prompts/review_loop.template.md` alongside `planner.template.md` and `executor.template.md` fully
aligned with the `pr-review-loop` skill. Delivered in PR #84.
