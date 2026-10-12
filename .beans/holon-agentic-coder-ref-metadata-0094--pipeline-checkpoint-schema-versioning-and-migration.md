---
# holon-agentic-coder-ref-metadata-0094
title: "Pipeline checkpoint schema versioning and migration"
status: completed
type: task
priority: normal
tags:
  - reliability
  - flow
  - checkpoint
  - schema
created_at: 2026-10-14T13:40:00Z
updated_at: 2026-10-15T15:38:00Z
---

# Bean 0094: Pipeline Checkpoint Schema Versioning and Migration

- **Bean ID:** 0094
- **Title:** Pipeline Checkpoint Schema Versioning and Migration
- **Status:** completed
- **Priority:** medium
- **Category:** reliability
- **Components:** `apps/sandbox-executor/flow.py`, `FlowCheckpoint`, `FlowContext`
- **Created At:** 2026-10-14
- **Parent Audit Finding:** BUG-02

---

## 1. Context & Motivation

Holon flow pipelines persist execution state after each lifecycle stage (`intent`, `plan`, `execute`, `review`,
`calibrate`) into JSON checkpoint files under `.holon/flow/checkpoint-<slug>.json`. This mechanism allows workflows
interrupted by timeouts, manual halts (Bean 0034), or system crashes to be resumed safely via
`holon flow run --from-stage <stage> --checkpoint <path>`.

During the architecture audit (Finding BUG-02 in `docs/audit_report.md`), the checkpoint serialization schema was found
to lack an explicit version tag and formal migration handlers.

---

## 2. Problem Statement

1. In `apps/sandbox-executor/src/sandbox_executor/flow.py`, `FlowCheckpoint.to_dict()` and `from_dict()` serialize
   fields without a `schema_version` attribute.
2. As new flags and metadata fields are added to `FlowContext` (e.g. `token_reduce`, `mitm_web`,
   `max_review_iterations`), resuming from legacy checkpoints created by older holon versions requires ad-hoc fallback
   logic and risks runtime exceptions if unexpected types are encountered.

---

## 3. Proposed Remediation

1. **Explicit Schema Versioning:** Add `schema_version: int = 1` to `FlowCheckpoint` and `FlowContext` JSON payloads.
2. **Migration Registry:** Implement a structured migration dispatch table mapping `(from_version, to_version)` to
   migration transforms.
3. **Backward Compatibility:** When deserializing a checkpoint with missing `schema_version` (legacy v0 format), apply
   default transformations cleanly to upgrade it to current version invariants.
4. **Validation Tests:** Add unit tests validating migration pathways from legacy schemas (v0, v1) to the latest schema
   version.

---

## 4. Acceptance Criteria

- [x] Checkpoint files serialized by `save_checkpoint()` include `"schema_version": 1`.
- [x] Loading legacy checkpoints without `schema_version` correctly sets defaults without raising `KeyError` or
      `AttributeError`.
- [x] Attempting to load an unsupported future schema version raises a clear, actionable `ValueError` prompting the user
      to upgrade their CLI.

---

## 5. Verification Commands

```bash
# Run flow checkpoint unit and migration tests
uv run pytest apps/sandbox-executor/tests/test_flow.py -k "checkpoint"

# Verify linting and formatting
uv run ruff check .
npx prettier --check .beans/holon-agentic-coder-ref-metadata-0094--pipeline-checkpoint-schema-versioning-and-migration.md
```

---

## 6. Resolution

- Added `schema_version = 1` to `FlowCheckpoint` and `FlowContext` serialization in
  `apps/sandbox-executor/src/sandbox_executor/flow.py`.
- Implemented migration dispatch table mapping `(from_version, to_version)` to migration transform functions.
- Implemented backward compatibility for legacy v0 checkpoints (missing or null schema_version) and forward validation
  rejecting unsupported future versions with clear `ValueError`.
- Added comprehensive unit tests in `test_flow.py`.
- Validated via Holon flow lifecycle stages 1-5; PR #77 achieved 3/3 unanimous ensemble consensus approval, 10/10 green
  CI checks, and pre-merge calibration ($\Delta EV$ +4.30); merged to `main` at commit
  `29aa1c14d060c4b90657803f046c964c6beb54e3`.
