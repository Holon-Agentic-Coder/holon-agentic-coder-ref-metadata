---
# holon-agentic-coder-ref-metadata-0041
title: "Document comprehensive Holon Flow lifecycle instructions for agents and operators"
status: todo
type: task
priority: normal
tags:
  - documentation
  - holon-flow
  - instructions
created_at: 2026-09-26T09:22:00Z
updated_at: 2026-09-26T15:20:00Z
---

Create comprehensive reference and procedural documentation explaining the Holon Flow lifecycle for AI coding agents and
human operators.

## Context

While `.agents/rules.md` mandates using the `./holon` CLI wrapper for tasks in `holon-agentic-coder`, there is no
central instruction file that explains the Holon Flow from first principles: what it is, how the fractal branch
hierarchy works, how ledgers record state, how the review and calibration phases integrate, and how to execute it either
step-by-step or via the unified `holon flow` command.

## Acceptance Criteria

1. Create `.agents/holon_flow.md` detailing:
   - **What is the Holon Flow**: The foundational concepts of fractal intent evolution, entropy reduction, expected
     value (EV) optimization, and git-as-universal-state-machine.
   - **The 5+1 Lifecycle Phases**:
     1. _Intent Creation_ (`I-{timestamp}-{slug}/_` branch, schema validation, `intents.jsonl`).
     2. _Plan Generation_ (`I-.../P-{timestamp}-{agent}-{model}/_` branch, planner agent, predicted metrics,
        `plans.jsonl`).
     3. _Plan Execution_ (`I-.../P-.../E-{timestamp}-{action}/_` branch, containerized sandbox executor, code edits,
        test suites, `executions.jsonl`).
     4. _PR Reviewer Loop_ (3-agent ensemble consensus review, automated resolver iterations, stopping at unanimous
        approval).
     5. _Calibration_ (`.../calibrated` branch, `plans/P-..._calibration.md`, actual vs predicted metric delta
        analysis).
     6. _Human Merge Boundary_ (Strictly human-operated merge of root intents to canonical `main`).
   - **Branch Hierarchy & Naming Conventions**: Timestamp-based IDs, directory-level `/_` leaf suffixes, and nested git
     tree structures.
   - **System of Record**: The role of `holon-knowledge/ledger/` append-only ledgers and `holon-config/` rulesets.
   - **Execution Playbook**:
     - Unified automated execution: `holon flow <intent.json> [flags]`.
     - Step-by-step manual execution: `holon intent`, `holon plan`, `holon execute`, `pr-review-loop`,
       `holon calibrate`.
   - **Harness vs Sandbox Boundaries**: Clarifying when development happens in per-agent worktrees (control plane
     metadata and coherence repo) versus containerized Holon Flow sandboxes (`apps/holon-agentic-coder/`).
2. Add quick navigation links to `.agents/holon_flow.md` in `AGENTS.md` and `.agents/workflows.md`.
3. Format all markdown documents using `npx prettier --write "**/*.md"`.

## Notes

- Target files:
  - `.agents/holon_flow.md` (new)
  - `AGENTS.md`
  - `.agents/workflows.md`

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `.agents/holon_flow.md` does not exist.
`AGENTS.md` carries the 5-stage table, but the first-principles reference document (fractal branches, ledger semantics,
harness vs sandbox boundaries, execution playbook) is still unwritten.
