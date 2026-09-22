---
# holon-agentic-coder-ref-metadata-0021
title: Add Makefile with prerequisite checks to holon-coherence
status: completed
type: task
created_at: 2026-09-15T00:00:00Z
updated_at: 2026-09-22T00:00:00Z
---

Add a Makefile to holon-coherence with prerequisite checks (Docker CLI, buildx, daemon running status, and Conda)
inspired by agentic-knowledge-base, along with core build-image, test, lint, clean, and help targets.

## Notes

- Prerequisites checked: Docker (CLI, buildx, daemon) and Conda (which manages python/uv). Git omitted as repo is
  already checked out.
- Check reports status with clear installation commands for missing tools, without auto-installing.
- Includes build-image target wrapping build_image.sh / docker-bake.hcl.
- Merged: holon-coherence PR #3 (2026-09-17), squash commit caa0bf0 on origin/main.
- Post-merge audit 2026-09-22: worktree holon-coherence/feat-add-makefile-prerequisites and local branch already
  removed; remote ref gone. Verified make check-prerequisites and make build-image targets present on origin/main.

## Assignment

Assignee: `antigravity`

## Resolution

Created Makefile and config/config.mk in holon-coherence worktree feat-add-makefile-prerequisites. Implemented
check-prerequisites (verifying Docker CLI, Docker buildx, Docker daemon running status, and Conda), build-image, test,
test-docker, lint, fix-ruff, clean, and help targets. Integrated taskipy in pyproject.toml ([tool.taskipy.tasks]) to
drive test, lint, and clean tasks. Created environment.yml specifying Conda environment with uv and python. Added unit
tests in tests/test_makefile.py and tests/test_conda_environment.py (all 16 tests passing). Adopted modular CI workflows
from agentic-knowledge-base: make.yml (testing make help/make across ubuntu/macos), test-hygiene.yml (pulling out
lockfile validation, taskipy lint, and taskipy clean into an isolated build), test-unit.yml (unit test execution across
ubuntu/macos), and test-integration.yml (Docker integration tests on ubuntu). Squashed all changes on
feat/add-makefile-prerequisites into a single commit. Landed on origin/main as squash commit caa0bf0 via holon-coherence
PR #3 (merged 2026-09-17).
