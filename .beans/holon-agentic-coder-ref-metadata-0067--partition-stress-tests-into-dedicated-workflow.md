---
id: "0067"
title: Partition workspace survival stress suite into dedicated workflow
status: completed
created_at: 2026-10-05T07:40:00Z
updated_at: 2026-10-05T07:55:00Z
labels:
  - ci
  - testing
  - holon-agentic-coder
  - workflows
---

# Partition workspace survival stress suite into dedicated workflow

## Context

The workspace survival stress suite (`apps/sandbox-executor/tests/test_workspace_survival_stress.py`) simulates live
container workspace conditions by cloning the target repository into `~/.holon-sandbox/workspace` and re-running the
test suite from within that clone. This test was previously nested within `.github/workflows/test-unit.yml` under the
`workspace-survival` job, which caused unit test workflow runs to take 5–8 minutes and mixed quick feedback with
long-running stress validation.

Furthermore, operators and developers need to measure the runtime of the stress suite explicitly in its own dedicated
workflow without blocking fast unit testing.

## Implementation

1. **Dedicated Workflow**:
   - Created `.github/workflows/test-stress.yml` with workflow name `Test - Stress` and job `Workspace survival`.
   - Instrumented test execution with `time uv run pytest -v -l --tb=short -m stress --junitxml=stress-report.xml` to
     measure and output explicit duration in GitHub Actions.
   - Retained the XML assertion step ensuring the stress test suite executed and was not silently skipped.

2. **Cleaned Unit Test Workflow**:
   - Removed `workspace-survival` from `.github/workflows/test-unit.yml`.
   - `Test - Unit` now runs exclusively fast unit tests on `macos-latest` and `ubuntu-latest`, completing in seconds.

3. **Neutral Pytest Configuration**:
   - Configured `[tool.pytest.ini_options]` in `pyproject.toml` with `addopts = ["--strict-markers"]` so that test
     targets can be executed explicitly without unexpected default marker deselections.

4. **Documentation**:
   - Updated `.github/workflows/README.md`, `apps/sandbox-executor/docs/hermetic_testing.md`, and
     `test_workspace_survival_stress.py` docstrings.

## Resolution

Resolved via commits on PR #63 (`c95abcc`, `948df36`):

- Pushed workflow separation and explicit timing to `holon-agentic-coder`.
- Calibrated with `holon calibrate` (Actual EV: 93.61, ΔEV: +7.66).
