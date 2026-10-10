---
# holon-agentic-coder-ref-metadata-0077
title: "Append every action to execution ledger with searchable labels and categories"
status: todo
type: feature
priority: high
tags:
  - ledger
  - execution-ledger
  - observability
  - searchability
  - continuous-learning
created_at: 2026-10-09T08:15:00Z
updated_at: 2026-10-09T08:15:00Z
---

## Summary

Currently, `holon-knowledge/ledger/executions.jsonl` only records a single coarse-grained summary entry at the end of an
entire execution cycle (`status: success|failed`, `test_pass_rate`, `summary`). This coarse granularity makes individual
agent actions invisible: code edits, documentation changes, configuration mutations, shell commands, and intermediate
test runs are not logged individually. Furthermore, the existing records lack structured metadata (such as actionable
labels, categories, affected paths, command signatures, failure patterns, or root causes) required to search past
actions and avoid repeating past mistakes.

This feature refactors and expands the execution ledger so that:

1. **Every action appends to the execution ledger**: Rather than logging only once per execution cycle, every discrete
   action (code changes, doc updates, dependency changes, shell commands, test executions, git mutations) appends an
   event to the execution ledger.
2. **Action metadata, labels, and categories**: Every action record captures the specific action carried out, its
   category (e.g., `code_edit`, `doc_update`, `config_change`, `test_run`, `shell_command`), labels/tags, targeted
   files/symbols, rationale, and immediate outcome (`success`, `failure`, `reverted`).
3. **Searchable error and mistake indices**: Fields specifically designed for queryability and pattern matching (e.g.,
   `mistake_type`, `error_signature`, `correction_for`, `lessons_learned`, `tags`) to prevent recurrence of prior
   errors.
4. **Documentation updates**: Overhaul `docs/ledger_schema.md` and related documentation across repositories to
   formalize the action-level ledger schema, storage invariants, querying interfaces, and integration into the Holon
   flow.

## Problem Statement & Audited Deficiencies

1. **Coarse-Grained Logging**:
   - `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` writes to
     `holon-knowledge/ledger/executions.jsonl` exactly once upon completion of an execution run.
   - Intermediate failures, attempted fixes, and fine-grained code diffs are collapsed into a single `summary` string
     and raw markdown file.
2. **Lack of Searchable Facets for Mistake Prevention**:
   - The current schema (`execution_id`, `plan_branch`, `agent`, `model`, `status`, `summary`, `created_at`,
     `duration_seconds`) contains no fields to index or query past failures, error messages, anti-patterns, or affected
     components.
   - Future agents cannot query the ledger to ask: "What failed last time we modified this component, and why?"
3. **Documentation Drift**:
   - `docs/ledger_schema.md` defines an abstract event model (`events.jsonl`, envelope with `seq`, `ts`, `run_id`,
     `host`, `git`), but implementation drifted to a simplified `executions.jsonl`.
   - The schema docs need synchronization with the reality of containerized agent execution while expanding to support
     granular, action-level events.

## Key Requirements & Scope

### 1. Action-Level Execution Logging

- Intercept and log every discrete action during execution:
  - **Code modifications**: file path, diff/patch summary, affected AST symbols.
  - **Doc modifications**: updated documents, sections affected.
  - **Environment / Config changes**: dependencies, config files, permissions.
  - **Command executions & Tests**: command executed, exit code, failure output / trace.
  - **Git operations**: commits, branch operations, stashes.
- Maintain immutability and append-only guarantees in `holon-knowledge/ledger/executions.jsonl` (or aligned event
  ledger).

### 2. Standardized Action Schema & Searchable Fields

Each action entry must include structured, queryable fields:

- `event_type` / `action_type`: e.g. `action_executed`, `tool_call`, `verification_run`, `execution_completed`.
- `action`: Specific operation carried out (e.g. `edit_file`, `run_test`, `update_doc`, `execute_command`).
- `category`: Coarse classification (`code`, `doc`, `config`, `test`, `build`, `dependency`).
- `labels` / `tags`: Multi-dimensional tags (e.g. `["security", "mitmproxy", "networking", "pytest"]`).
- `target`: File path, command string, or component identifier.
- `outcome`: `success`, `failure`, `reverted`, `blocked`.
- `error_context`: Captured error signature, stack trace snippet, or exit code.
- `mistake_category` / `lesson`: Optional structured classification of what went wrong to prevent repeats.
- `execution_id` & `parent_action_id`: Traceability back to the overarching plan and execution run.

### 3. Querying & Search Interface

- Define and implement a CLI or utility interface (`holon ledger query` or fast search function) to search ledger
  records by label, category, target path, outcome, or error keyword.
- Allow agents (in planner and executor phases) to retrieve relevant past failures and successes before undertaking
  changes on a specific path or subsystem.

### 4. Documentation Overhaul

- Update `docs/ledger_schema.md` in `holon-agentic-coder` (and mirror relevant guidelines in `holon-coherence`).
- Document the schema specifications, field definitions, and query patterns.
- Update `.agents/rules.md` and `AGENTS.md` to reference the action-level ledger requirements.

## Confirmed Design Decisions

1. **Real-time Tool Interception**: Granular agent actions are captured and appended in real time directly within the
   agent runner harness (intercepting file writes/edits, bash command executions, document modifications, and test
   invocations as they occur, rather than post-hoc git diffing).
2. **Unified Storage in `executions.jsonl`**: Both discrete action events and final run summaries will be stored in
   `holon-knowledge/ledger/executions.jsonl`, distinguished by an `entry_type` field (`"action"` vs `"summary"`). This
   maintains backward compatibility for tools parsing run summaries while unlocking continuous event streams.
3. **CLI Query Interface (`holon ledger query`)**: A dedicated query CLI command with structured filtering
   (`--category`, `--labels`, `--target`, `--outcome=failure`) to allow agents (and human developers) to look up prior
   failures and lessons learned before taking action.

## Action Provenance: Origin & Review Criticality (added)

Beyond _what_ an action did, the ledger must record _why it happened_, so learning can distinguish an agent's first-pass
mistakes from defects found later by review.

1. **`action_origin`** (required on every `entry_type: "action"` row), one of:
   - `initial_implementation` -- the LLM's own first-pass work against the plan step.
   - `pr_review` -- an edit made in response to a PR review finding (resolver pass).
   - `ci_fix` -- an edit made to repair a failing CI check.
   - `calibration` / `operator` -- stage 5 output or an explicit human instruction.
2. **For `action_origin: pr_review`, also record**:
   - `review_severity`: `critical` | `important` | `nit` (matches the 🔴 / 🟡 / 🟢 levels the `pr-reviewer` emits).
   - `review_iteration` (loop iteration number) and `review_finding_ids` (stable ids the reviewer assigns).
   - `review_disposition`: `applied` | `rejected`, with `rejection_reason` when rejected (Nits are always dispositioned;
     see below).
   - `introduced_by_action_id`: the earlier action row whose output the finding criticised, when attributable (links a
     review defect back to the initial implementation step that caused it).
3. **Why it matters**: `holon ledger query` gains `--origin` and `--review-severity` filters, enabling queries such as
   "which components repeatedly need Critical review fixes after initial implementation" -- the highest-signal input for
   Beans 0052/0046 (consult-before-act).
4. **Capture mechanism**: the resolver commits carry trailers (`Action-Origin: pr_review`, `Review-Severity: <level>`,
   `Review-Iteration: <n>`, `Review-Finding-Ids: <ids>`); the harness ingests these trailers into ledger rows, so
   provenance does not rely on free-text parsing. Initial-implementation actions default to
   `action_origin: initial_implementation`.

### Coupled harness change: PR review loop actions Nits

The `pr-review-loop`, `pr-review-resolver` and `pr-reviewer` skills now require **every Nit to be actioned**: `applied`,
or `rejected` with a one-line reason; an open actionable Nit blocks approval. Rejected Nits are passed to the next
review pass as already adjudicated (no oscillation), and a Nit-only set that survives 3 unchanged iterations is closed
as `rejected: no-convergence`. This is what makes `review_severity: nit` rows exist in the ledger at all.
