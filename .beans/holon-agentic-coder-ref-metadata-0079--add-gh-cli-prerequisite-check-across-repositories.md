---
# holon-agentic-coder-ref-metadata-0079
title: "Add gh and openssl prerequisite checks and align per-repo toolchain requirements"
status: in-progress
type: task
priority: high
tags:
  - prerequisites
  - tooling
  - makefile
  - github-cli
  - conda
  - holon-flow
created_at: 2026-10-09T12:12:00Z
updated_at: 2026-10-09T12:35:00Z
---

## Summary

Align and standardize prerequisite validation and toolchain bootstrapping across `holon-agentic-coder` and
`holon-coherence` Makefiles:

1. Add `gh` (GitHub CLI) to `holon-agentic-coder` (required by Holon Flow Stage 5 calibration and review skills).
2. Confirm `holon-coherence` does **not** require `gh`.
3. Support flexible Conda environment selection in `holon-coherence`: tools (`uv`, `python`) can be installed into
   `holon`, `base`, or any user-specified conda environment, with interactive confirmation/prompting for the target
   environment name.
4. Add `openssl` validation to **both** repositories (required by `ca_generator.py` for Root CA TLS interception).
5. Add `npx` (Prettier) check to `holon-coherence` to match doc hygiene checks.

## Architecture & Gap Analysis

### 1. Does `holon-coherence` require `gh`?

**No.** `holon-coherence` is a background network proxy, caching, and telemetry engine (`mitmproxy`, SQLite cache,
semantic embeddings, web dashboard). Its source code, CLI commands, and test suites never invoke `gh`. Requiring `gh` in
`holon-coherence`'s `check-prerequisites` would impose an unnecessary external dependency on developers who only need to
run the proxy or local unit tests.

### 2. Does `holon-agentic-coder` require `gh`?

**Yes.** Specifically:

- **Stage 5 Calibration (`sandbox_executor/calibration.py`)**: Invokes
  `gh pr view <pr_num> --json headRefOid -q .headRefOid` to resolve the authoritative remote PR head commit SHA
  (preventing stale calibrations; Beans 0060 and 0065). If `gh` is missing, ref resolution degrades or fails.
- **Stage 4 Review Loop & Agent Harness**: The review, resolution, and branch cleanup skills (`pr-reviewer`,
  `pr-review-resolver`, `pr-review-loop`, `clean-branches`) rely heavily on `gh`.

### 3. Flexible Conda Environment Selection in `holon-coherence`

- In `holon-coherence`, `uv` and `python` are provisioned via Conda (`conda-forge`).
- However, users are **not required** to use a dedicated environment named `holon`. A user may choose to install `uv`
  into their existing `base` conda environment, or into an environment named `holon`, or into any custom environment
  name (e.g., `dev`, `proxy`).
- **Interactive User Confirmation**:
  - When running `make create-conda-env` (or setup targets) interactively, the Makefile should ask for user
    confirmation: prompt the user to confirm installing `uv` through Conda and allow them to press Enter for default
    `holon`, or type `base`, or type any custom environment name.
  - In non-interactive mode or CI, support `CONDA_ENV ?= holon` (or inherit from active `CONDA_DEFAULT_ENV`).
- **Prerequisite Validation**:
  - `check-prerequisites` checks:
    1. Is `conda` available?
    2. Is `uv` accessible in the active Conda environment (`$$CONDA_DEFAULT_ENV`), or does the target Conda environment
       (`$$CONDA_ENV`, default `holon` or `base`) exist with `uv` available?
    3. If neither is satisfied, provide actionable guidance to run `make create-conda-env` with interactive selection or
       `make create-conda-env CONDA_ENV=base`.

### 4. Missing OpenSSL Check in Both Repositories

- Both `holon-agentic-coder` (`apps/sandbox-executor/src/sandbox_executor/token_reduction/ca_generator.py`) and
  `holon-coherence` (`src/holon_coherence/ca_generator.py`) invoke `shutil.which("openssl")` and `openssl req -x509` /
  `openssl x509` to generate and evaluate the Root CA for TLS MITM proxy interception.
- If `openssl` is missing on `$PATH`, CA generation raises a `RuntimeError`. Neither Makefile checks `openssl` in
  `check-prerequisites`.

## Requirements & Acceptance Criteria

1. **`holon-agentic-coder` Makefile**:
   - Add `gh` CLI presence check (`command -v gh`) and version report (`gh --version | head -n 1`).
   - If missing, fail with platform-specific install instructions (`brew install gh`, `apt install gh`).
   - Add advisory warning if `gh auth status` indicates an unauthenticated session.
   - Add `openssl` presence and version check (`openssl version`), warning or failing if missing.
2. **`holon-coherence` Makefile**:
   - Do **not** require `gh` (keep proxy dependencies lean).
   - Check Conda CLI presence (`$(FIND_CONDA_BIN)`).
   - **Flexible Conda environment & `uv` check**:
     - Check if `uv` is installed and available in the current active conda environment (`$$CONDA_DEFAULT_ENV`) or
       target environment (`$$CONDA_ENV`).
     - Allow `CONDA_ENV` to be configured (defaulting to `holon` or `base` if active).
   - **Interactive prompt in `create-conda-env`**:
     - Prompt the user to confirm installation of `uv` and Python via Conda.
     - Allow user to accept `holon` (default), enter `base`, or type a custom environment name.
     - Handle `base` installation via `conda install -n base -c conda-forge uv python=3.13` or `conda env update`.
   - Add `openssl` check (`openssl version`) required for `ca_generator.py`.
   - Add `npx` (Prettier) check for doc hygiene.
3. **Tests & CI**:
   - Update `tests/test_makefile.py` in `holon-coherence` to test both default `holon` and custom/`base` `CONDA_ENV`
     values in dry-run and non-interactive modes.
   - Update Makefile tests in `holon-agentic-coder`.
   - Verify dry-run (`make -n`) and non-interactive CI executions pass cleanly.
