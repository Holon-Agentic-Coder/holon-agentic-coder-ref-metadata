---
# holon-agentic-coder-ref-metadata-1lh8
title: Align CI/CD workflows across all projects with agentic-knowledge-base convention
status: completed
type: task
priority: normal
created_at: 2026-09-24T12:22:00Z
updated_at: 2026-09-25T02:27:00Z
---

Adopt and standardize the CI/CD workflow architecture and conventions from
[agentic-knowledge-base/.github](https://github.com/thomashan/agentic-knowledge-base/tree/main/.github) across **all
managed projects** in the Holon ecosystem:

1. `apps/holon-agentic-coder` (Primary Fractal Intent Evolution Engine)
2. `apps/holon-coherence` (Optimization Gateway & Wire Telemetry)
3. `holon-agentic-coder-ref-metadata` (Control Plane, Task Tracking & Agent Harness)

## Reference Specification

The standard CI/CD convention established in `thomashan/agentic-knowledge-base` consists of:

1. **Modular Workflow Architecture (`.github/workflows/`)**:
   - `test-hygiene.yml`: Fast static verification gate running on push/PR:
     - Dependency sync and lockfile currency check (`uv lock --check` and `git diff --exit-code uv.lock`).
     - Static linting and style validation (`ruff check .`, `ruff format --check .`).
     - Markdown formatting verification (`prettier --check "**/*.md"`).
     - Structural/circular dependency and code hygiene analysis.
   - `test-unit.yml`: Fast multi-OS matrix tests (`ubuntu-latest`, `macos-latest`):
     - Dependency caching (`actions/cache` / uv package caches).
     - Pure unit tests excluding Docker/container dependencies (`pytest -m "not integration"`).
   - `test-integration.yml`: Integration test suite running on `ubuntu-latest`:
     - Containerized dependencies and service tests (`pytest -m "integration"`).
     - Image pre-pulling and container lifecycle management.
   - `make.yml`: Multi-OS target verification (`ubuntu-latest`, `macos-latest`):
     - Validates `make help`, default `make`, and environment / prerequisite checks.
   - `README.md`: Comprehensive documentation inside `.github/workflows/` detailing each workflow's purpose, triggers,
     matrix strategy, runner architecture, and caching mechanisms.
2. **Platform Constraints Documentation (`.github/macos-docker.md`)**:
   - Explains macOS runner constraints in GitHub Actions regarding Docker daemon unavailability and the architectural
     rationale for restricting containerized integration tests to Linux runners.
3. **Reusable Composite Actions (`.github/actions/`)**:
   - Custom composite actions (such as `docker-pull`) standardizing robust image pulls, retries, and token
     authorization.

## Per-Project Status & Implementation Scope

### 1. `apps/holon-agentic-coder`

- **Current State**: Uses legacy monolithic/ad-hoc workflows (`ci.yml`, `integration-tests.yml`, `build-images.yml`,
  `lint-docs.yml`). Lacks multi-OS matrix testing, workflow documentation, and modular separation.
- **Required Implementation**:
  - Restructure into modular workflows: `test-hygiene.yml`, `test-unit.yml` (multi-OS matrix), `test-integration.yml`
    (Ubuntu container runner), and `make.yml`.
  - Add `.github/workflows/README.md` and `.github/macos-docker.md`.
  - Add composite actions under `.github/actions/` (e.g. `docker-pull`) for Docker image pre-fetching.
  - Align Makefile targets with prerequisite checks.

### 2. `apps/holon-coherence`

- **Current State**: Previously implemented modular workflows under bean `0021` (`make.yml`, `test-hygiene.yml`,
  `test-unit.yml`, `test-integration.yml`, `docker-build.yml`, and `macos-docker.md`).
- **Required Implementation**:
  - Audit against the latest `agentic-knowledge-base/.github` pattern.
  - Ensure `.github/workflows/README.md` reflects current jobs and caching strategies.
  - Implement `.github/actions/docker-pull` if integration or docker-build tests pull container images.
  - Ensure action versions, runner matrix, and step parity are consistent.

### 3. `holon-agentic-coder-ref-metadata`

- **Current State**: Only has `.github/workflows/markdown-lint.yml`.
- **Required Implementation**:
  - Introduce modular workflows conforming to the convention:
    - `test-hygiene.yml`: Run Markdown linting, Prettier checks, link/anchor validation
      (`scripts/validate_agent_links.py`), and Beans schema validation.
    - `test-unit.yml` / validation tests if harness unit tests are present.
  - Add `.github/workflows/README.md` documenting metadata repo CI checks.

## Tasks & Acceptance Criteria

- [x] **`apps/holon-agentic-coder`**:
  - [x] Add `.github/workflows/README.md` and `.github/macos-docker.md`.
  - [x] Implement `test-hygiene.yml` (lockfile check, ruff, prettier).
  - [x] Implement `test-unit.yml` (`ubuntu-latest`, `macos-latest` matrix with caching).
  - [x] Implement `test-integration.yml` (`ubuntu-latest` with container setup).
  - [x] Add composite actions under `.github/actions/` where applicable (`docker-pull`).
  - [x] Verify Makefile and build targets (`make help`, `make check-prerequisites`).
- [x] **`apps/holon-coherence`**:
  - [x] Audit existing modular workflows and ensure complete feature parity with `agentic-knowledge-base/.github`.
  - [x] Verify `test-hygiene.yml`, `test-unit.yml`, and `test-integration.yml` follow exact conventions.
  - [x] Add `.github/actions/docker-pull` composite action and update README.md.
- [x] **`holon-agentic-coder-ref-metadata`**:
  - [x] Reorganize `.github/workflows/` with `test-hygiene.yml` and `README.md`.
  - [x] Ensure formatting and agent link validation run reliably in CI.
- [x] **Ecosystem Verification**:
  - [x] Validate workflow syntax and run local verification across all 3 repositories.
  - [x] Verify that branch protection rules and CI status checks cleanly map to the updated workflow names.

## Resolution Summary

Successfully standardized the CI/CD architecture and conventions across all three repositories in the Holon ecosystem:

1. **`holon-agentic-coder-ref-metadata`**: Transitioned legacy `markdown-lint.yml` to modular `test-hygiene.yml` and
   added `.github/workflows/README.md`. Committed to `main` (commit `fbef552`).
2. **`apps/holon-agentic-coder`**: Created dedicated feature worktree
   `apps/holon-agentic-coder/feat-ci-cd-standardisation` off `origin/main`. Replaced legacy monolithic workflows with
   modular `test-hygiene.yml`, multi-OS `test-unit.yml`, Linux `test-integration.yml`, and multi-OS `make.yml`.
   Introduced root `Makefile`, `.github/macos-docker.md`, `.github/workflows/README.md`, and
   `.github/actions/docker-pull/action.yml`. Committed as a single squashed commit (`7080056`).
3. **`apps/holon-coherence`**: Created dedicated feature worktree `apps/holon-coherence/feat-ci-cd-standardisation` off
   `origin/main`. Added `.github/actions/docker-pull/action.yml`, updated `.github/workflows/README.md`, and validated
   full parity. Committed as a single squashed commit (`40f4f17`).
4. **Git Safety Invariants Preserved**: Neither remote `origin` was pushed to, and feature branches remain isolated in
   their respective worktrees ready for PR creation or review loops.

## Notes & Worktrees

- Reference:
  [thomashan/agentic-knowledge-base/.github](https://github.com/thomashan/agentic-knowledge-base/tree/main/.github).
- Prior Art: Bean `holon-agentic-coder-ref-metadata-0021`.
- Targets:
  - `apps/holon-agentic-coder`: Dedicated worktree off `origin/main` (`feat/ci-cd-standardisation`).
  - `apps/holon-coherence`: Dedicated worktree off `origin/main` (`feat/ci-cd-standardisation`).
  - `holon-agentic-coder-ref-metadata`: Active checked-out branch (`main`).
