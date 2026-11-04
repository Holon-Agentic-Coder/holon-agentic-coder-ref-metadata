---
# holon-agentic-coder-ref-metadata-0226
title: "End-to-end test for the holon flow commands, with full teardown of worktrees and local/remote branches"
status: todo
type: feature
priority: normal
tags:
  - testing
  - e2e
  - holon-flow
  - holon-agentic-coder
created_at: 2026-11-04T04:30:00Z
updated_at: 2026-11-04T05:30:00Z
---

## Problem

The flow's commands are only ever exercised for real by operators running real beans. Defects therefore surface in
production runs (recent examples: the empty-diff quota signature, the plan stall budget, the pre-flight credential hint,
the pi-agent session-dir mount). There is no end-to-end test that drives the actual `holon flow` command across all five
stages and proves the machinery works before a release — and no automated cleanup, so every failed experiment leaves
worktrees and orphan `I-…/P-…/E-…` branches behind for manual cleanup passes.

## Scope

1. An end-to-end test that invokes the REAL commands (`holon flow <intent.json>`, plus `--from-stage` / `--checkpoint`
   resume paths) against a disposable, trivially small intent, asserting per stage: the intent, plan and execution
   branches exist with the expected shapes; the three ledgers only ever append; the checkpoint is written and a resume
   continues from it; the empty-diff and pre-flight gates fail closed when provoked. **The run must never open a pull
   request** (maintainer, 2026-11-04 — otherwise every e2e run proliferates PRs): the test invokes the flow in a mode
   that stops before PR creation (`--skip-review --skip-calibrate`, or the no-auto-PR path), and asserts afterwards that
   zero pull requests reference the run's branches — a PR appearing is itself a test failure (the teardown then closes
   it and the test still fails). Stage 4/5 therefore run only to the extent possible without a PR; their PR-dependent
   behaviour stays covered by the existing unit and integration tests.
2. **Full teardown, unconditionally** (on success AND on failure, e.g. a pytest fixture finaliser or trap): remove the
   test worktree, delete the local branches, and delete every remote branch the run created (the whole `I-…` tree) —
   leaving the repository exactly as before the test. The teardown must enumerate what it deleted so a reviewer can
   audit it, and must refuse to touch anything outside the test run's own intent prefix.
3. Invocation: a dedicated task (for example `uv run task test-e2e`), explicitly NOT part of the default
   `uv run task test` suite or the CI pipelines — it spends real model tokens and pushes real branches. Operators run it
   before releases or after flow-engine changes.
4. The disposable intent runs on the local model (see Credentials below), so no cloud tier choice is needed.

## Credentials: the e2e runs on a LOCAL model (maintainer, 2026-11-04)

The e2e needs no cloud LLM credential at all: it drives the flow on a host-local model through the existing
`local_llm.py` envelope (`HOLON_LOCAL_BASE_URL` / `HOLON_LOCAL_PROVIDER` / `HOLON_LOCAL_MODELS`, with the
`HOLON_HOST_LOCAL_HOSTS` allow-list) pointing at an OpenAI-compatible endpoint such as Ollama, LM Studio or mlx. That
dissolves the keychain problem for the e2e entirely — the keychain-only production credential path stays untouched.

- The disposable intent must be trivial enough for a small local model (for example: append one line to one file); the
  e2e proves the FLOW MACHINERY — stages, branches, ledgers, checkpoints, gates, teardown — never model quality.
- The only secret the run still needs is a git push credential, and in GitHub Actions that is the workflow's own
  ephemeral `GITHUB_TOKEN` — nothing stored.
- Where it runs: the operator's machine, or a self-hosted runner with the local model installed. GitHub-hosted runners
  are too weak to serve a capable local model; the task stays out of the hosted CI pipelines either way.
- **Model choice (maintainer, 2026-11-04): as small as possible — sub-1B, ideally the ~300M class.** Candidates,
  smallest first: Gemma 3 270M, SmolLM2-360M-Instruct, Qwen3-0.6B / Qwen2.5-Coder-0.5B. The constraint to respect: the
  planner must emit structured markdown the stage parsers accept and the executor must follow the coding-agent CLI's
  instructions, so the build includes a one-off calibration step — run the happy path on each candidate from smallest up
  and document the smallest model that passes as the reference setup (expected floor around 0.5-0.6B; if the 270M class
  passes, use it). The chosen model id, runtime (for example Ollama with a q4 quantisation) and a timeout envelope sized
  for local inference are recorded in the task's docs; a model failing the e2e's happy path is a selection outcome, not
  a flow defect.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Related: 0150 (hermetic tests — the e2e is the deliberate opposite: real pushes, hence the teardown contract), 0224
  and 0225 (credential discovery this test must drive), 0182 (the harness wait helper usable for CI gating inside the
  test), AGENTS.md zero-synthetic-data rule (this is a functional test, not a benchmark; it measures nothing).
