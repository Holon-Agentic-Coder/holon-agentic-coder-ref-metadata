---
# holon-agentic-coder-ref-metadata-1lh8
title: Align CI/CD workflows across all projects with agentic-knowledge-base convention
status: todo
type: task
priority: normal
created_at: 2026-09-24T12:22:00Z
updated_at: 2026-09-24T12:23:45Z
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

- [ ] **`apps/holon-agentic-coder`**:
  - [ ] Add `.github/workflows/README.md` and `.github/macos-docker.md`.
  - [ ] Implement `test-hygiene.yml` (lockfile check, ruff, prettier).
  - [ ] Implement `test-unit.yml` (`ubuntu-latest`, `macos-latest` matrix with caching).
  - [ ] Implement `test-integration.yml` (`ubuntu-latest` with container setup).
  - [ ] Add composite actions under `.github/actions/` where applicable.
  - [ ] Verify Makefile and build targets.
- [ ] **`apps/holon-coherence`**:
  - [ ] Audit existing modular workflows and ensure complete feature parity with `agentic-knowledge-base/.github`.
  - [ ] Verify `test-hygiene.yml`, `test-unit.yml`, and `test-integration.yml` follow exact conventions.
- [ ] **`holon-agentic-coder-ref-metadata`**:
  - [ ] Reorganize `.github/workflows/` with `test-hygiene.yml` and `README.md`.
  - [ ] Ensure formatting and agent link validation run reliably in CI.
- [ ] **Ecosystem Verification**:
  - [ ] Validate workflow syntax and run local verification across all 3 repositories.
  - [ ] Verify that branch protection rules and CI status checks cleanly map to the updated workflow names.

## Notes & Worktrees

- Reference:
  [thomashan/agentic-knowledge-base/.github](https://github.com/thomashan/agentic-knowledge-base/tree/main/.github).
- Prior Art: Bean `holon-agentic-coder-ref-metadata-0021`.
- Targets:
  - `apps/holon-agentic-coder`: Dedicated worktree off `origin/main`.
  - `apps/holon-coherence`: Dedicated worktree off `origin/main`.
  - `holon-agentic-coder-ref-metadata`: Active checked-out branch.
