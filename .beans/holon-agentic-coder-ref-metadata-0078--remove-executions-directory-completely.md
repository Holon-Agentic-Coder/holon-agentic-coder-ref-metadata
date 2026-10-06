---
# holon-agentic-coder-ref-metadata-0078
title: "Remove the executions directory and deprecate execution markdown files"
status: completed
type: task
priority: normal
tags:
  - cleanup
  - execution
  - ledger
  - refactor
  - holon-flow
created_at: 2026-10-09T08:53:00Z
updated_at: 2026-10-09T13:35:00Z
---

## Summary

The repository root currently contains an `executions/` directory housing individual execution Markdown files
(`executions/E-*.md`). These files were originally created as a human-readable counterpart to `plans/P-*.md`, but in
practice they provide almost zero unique value:

- They duplicate data already tracked in `holon-knowledge/ledger/executions.jsonl` (and the upcoming action ledger in
  Bean 0077).
- They are typically thin 15-line boilerplate records (`Status: Success`, `Plan executed successfully`).
- They clutter the repository root instead of keeping dynamic operational artifacts encapsulated within
  `holon-knowledge/`.

This task completely removes the `executions/` directory, updates all flow code (`executor.py`, `flow.py`,
`calibration.py`), adjusts the test suites, updates documentation across repositories, and cleans up historical
execution markdown files from the tree.

---

## Detailed Inventory of Changes

### 1. Source Code in `holon-agentic-coder`

#### A. `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py`

- **Remove markdown file generation**:
  - Delete `exec_file_rel = f"executions/{exec_id}.md"` and the file-writing block that creates `executions/E-*.md`
    (lines 1245–1268).
  - Stop adding `exec_file_rel` to prettier formatting targets (lines 1307–1312).
  - Stop staging `exec_file_rel` in `git add` targets (lines 1319–1325).
- **Ledger record adjustment**:
  - Deprecate or remove `"execution_file": exec_file_rel` from `exec_entry` in `executions.jsonl` (or set to
    `None`/omit).

#### B. `apps/sandbox-executor/src/sandbox_executor/flow.py`

- **Remove execution markdown scaffolding**:
  - Remove `exec_md_rel = f"executions/{exec_id}.md"` (line 579) and disk write logic (lines 634–635).
  - Remove `"execution_file"` from `exec_entry` (line 649).
  - Remove `exec_md_rel` from `run_git(["add", ...])` (line 691).

#### C. `apps/sandbox-executor/src/sandbox_executor/calibration.py`

- **Remove markdown inspection fallback**:
  - Remove `read_git_file(target_ref, f"executions/{execution_id}.md")` and disk fallback check (lines 737–760).
    Calibration should derive `p_success` and `exit_code` solely from `holon-knowledge/ledger/executions.jsonl`.
- **Remove markdown reference links**:
  - Update line 909 where the calibration report writes
    `- **Execution Reference:** [executions/{execution_id}.md](...)`. Replace with execution ID and branch metadata
    referencing the ledger.

---

### 2. Test Suite Updates in `holon-agentic-coder`

- **`tests/test_executor.py`**:
  - Update assertions checking for `executions/E-*.md` in `call_files` or staged git trees (e.g. lines 501, 2530).
  - Ensure assertions expect only `holon-knowledge/ledger/executions.jsonl` and code files to be committed.
- **`tests/test_flow.py`**:
  - Remove assertions checking for `executions/E-*.md` (e.g. line 411).
- **`tests/test_calibration.py`**:
  - Update tests that mock or assert execution markdown file presence/contents to verify direct ledger resolution.

---

### 3. File Deletions & Git Cleanup

- **Delete directory and files**:
  - Remove `apps/holon-agentic-coder/executions/` and all contained `E-*.md` files.
  - Delete any stray references in `.gitignore` or clean-up lists.

---

### 4. Documentation Updates

- **`AGENTS.md` (in `holon-agentic-coder-ref-metadata`)**:
  - Update the "Sole Change Path: The Holon Flow" table row for Stage 3 (Execute) from:
    `I-.../P-.../E-{ts}-{agent}-{model}/_ + executions/*.md + executions.jsonl` to:
    `I-.../P-.../E-{ts}-{agent}-{model}/_ + holon-knowledge/ledger/executions.jsonl`.
- **`docs/executor/execution_architecture_specification.md`**:
  - Update Mermaid sequence diagram (line 64) and specification text (line 118) to remove references to
    `executions/E-*.md`.
- **`docs/ledger_schema.md`**:
  - Clarify that execution details are captured in `executions.jsonl` without auxiliary `executions/*.md` files.

---

## Verification & Acceptance Criteria

1. Running `./holon execute` or `executor.py` no longer creates or stages `executions/` or `executions/E-*.md`.
2. All execution metadata continues to be recorded faithfully in `holon-knowledge/ledger/executions.jsonl`.
3. `holon calibrate` completes successfully using only `executions.jsonl` without warning or error regarding missing
   markdown files.
4. All unit and flow tests in `sandbox-executor` pass (`uv run task test` or `uv run pytest`).
5. Prettier validation succeeds across all modified documentation and python files.

---

## Resolution

- **`holon-agentic-coder` (PR [#68](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/68))**:
  - Traversed the complete 5-stage Holon flow: Intent (`I-1791547482-drop-executions-and-fix-ledger-rev2/_`) -> Plan ->
    Execute -> PR Review Loop (3-agent ensemble consensus approval) -> Calibration.
  - Removed `executions/` directory and deprecated execution markdown generation in `executor.py` and `flow.py`.
  - Refactored `calibration.py` to read execution outcomes directly from `holon-knowledge/ledger/executions.jsonl`.
  - Removed all historical `executions/E-*.md` files.
- **`holon-coherence` (PR [#12](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/12))**:
  - Removed `executions/` directory and all standalone `E-*.md` files from git tracking.
  - Updated plan calibration markdown links to point to ledger execution entries.
- **Harness Documentation (`holon-agentic-coder-ref-metadata`)**:
  - Updated `AGENTS.md` Stage 3 row to point to `holon-knowledge/ledger/executions.jsonl`.
