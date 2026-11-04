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
updated_at: 2026-11-04T04:30:00Z
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
   continues from it; the empty-diff and pre-flight gates fail closed when provoked.
2. **Full teardown, unconditionally** (on success AND on failure, e.g. a pytest fixture finaliser or trap): remove the
   test worktree, delete the local branches, delete every remote branch the run created (the whole `I-…` tree), and
   close any pull request the run opened — leaving the repository exactly as before the test. The teardown must
   enumerate what it deleted so a reviewer can audit it, and must refuse to touch anything outside the test run's own
   intent prefix.
3. Invocation: a dedicated task (for example `uv run task test-e2e`), explicitly NOT part of the default
   `uv run task test` suite or the CI pipelines — it spends real model tokens and pushes real branches. Operators run it
   before releases or after flow-engine changes.
4. Open design points for the plan stage: which runner/model the disposable intent uses (cheapest viable tier); and
   whether Stage 4/5 run fully or the test stops after proving stage transitions (cost versus coverage).

## Credential dependency (deferred decision)

The keychain-only credential design (see the keychain bean) assumes an operator machine. An e2e environment without an
OS keychain cannot authenticate the claude runner — the maintainer has deferred solving that to THIS bean: when the e2e
test is built, decide the credential route for keychain-less environments here (and only here), rather than adding
fallbacks to the production credential path.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Related: 0150 (hermetic tests — the e2e is the deliberate opposite: real pushes, hence the teardown contract), 0224
  and 0225 (credential discovery this test must drive), 0182 (the harness wait helper usable for CI gating inside the
  test), AGENTS.md zero-synthetic-data rule (this is a functional test, not a benchmark; it measures nothing).
