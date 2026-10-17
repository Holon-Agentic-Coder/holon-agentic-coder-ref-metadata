---
# holon-agentic-coder-ref-metadata-0117
title: "Implement install-holon skill to build container images and install CLI tools via uv tool install"
status: completed
type: task
priority: normal
tags:
  - skills
  - installation
  - docker
  - uv
  - buildx
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-17T07:02:00Z
updated_at: 2026-10-17T07:05:00Z
---

## Summary

Implement a dedicated `install-holon` skill (`.agents/skills/install_holon/SKILL.md`) and companion orchestration script
(`.agents/skills/install_holon/scripts/install_holon.py`) to automate building container images via Docker Buildx Bake
and installing/updating the latest versions of the `holon` and `holon-coherence` CLIs via `uv tool install`.

## Context & Problem Statement

Developers and agents frequently need to sync, rebuild, and update the Holon runtime environment after code merges or
dependency upgrades (such as Bean 0112 and Bean 0114):

1. **Multi-Component Build Complexity**:
   - `holon-agentic-coder` requires building 8 role and orchestrator Docker images via Buildx Bake
     (`apps/sandbox-executor/build_all_images.sh` or `make build-images`).
   - `holon-coherence` requires building its proxy gateway container (`build_image.sh` or `make build-image`).
   - Both CLI tools (`holon` and `holon-coherence`) must be installed into the host environment (`~/.local/bin/`) via
     `uv tool install`.
2. **Manual & Error-Prone Upgrades**:
   - Manually navigating across multiple worktree directories, remembering `--editable` flags, running separate make
     targets, and checking PATH resolution creates friction and potential version drift.
3. **Agent Reproducibility**:
   - An autonomous agent needs a codified skill with standard instructions, flags (`--skip-images`, `--no-cache`,
     `--dry-run`), and automated health checks to verify that local images and host binaries are healthy and up to date.

## Tasks & Scope

- [x] Create `.agents/skills/install_holon/SKILL.md` detailing:
  - Architecture and operational principles.
  - Phase 1: Prerequisite validation (Docker daemon, Buildx, uv, PATH).
  - Phase 2: Upstream git repository synchronization (`git fetch origin`).
  - Phase 3: Docker image builds via Buildx Bake for both `holon-agentic-coder` and `holon-coherence`.
  - Phase 4: Host CLI installation via `uv tool install --force --reinstall --editable`.
  - Phase 5: Verification and post-installation health probing.
- [x] Implement `.agents/skills/install_holon/scripts/install_holon.py` supporting:
  - `--all`, `--holon-only`, `--coherence-only`.
  - `--skip-images`, `--skip-tools`, `--no-cache`, `--no-sync`, `--dry-run`.
- [x] Add `.agents/skills/install_holon/SKILL.md` to `.agents/scripts/validate-links.js`.
- [x] Format markdown with Prettier and verify all repository links.
- [x] Test the script execution and mark bean as `completed`.

## Resolution

- Implemented `.agents/skills/install_holon/SKILL.md` defining the 5-phase build and install lifecycle.
- Created and tested executable orchestrator script `.agents/skills/install_holon/scripts/install_holon.py` with support
  for `--all`, `--holon-only`, `--coherence-only`, `--skip-images`, `--skip-tools`, `--no-cache`, and `--dry-run`.
- Rebuilt all Docker container images and installed latest `holon` and `holon-coherence` CLIs in editable mode via
  `uv tool install`.
- Added link verification in `.agents/scripts/validate-links.js` with 100% passing checks.
