---
# holon-agentic-coder-ref-metadata-0032
title: Standardize development and Docker prerequisite checks across repositories
status: completed
type: task
priority: normal
created_at: 2026-09-25T04:41:00Z
updated_at: 2026-09-25T12:42:00Z
---

Standardize development and Docker prerequisite checks (including GNU Make, Docker CLI/Buildx/daemon, uv, and npx) and
automated setup across `holon-agentic-coder` following and extending the reference implementation in `holon-coherence`.

## Context & Gap Analysis

1. **Docker Prerequisites**: In `holon-coherence` (`apps/holon-coherence/main/Makefile`), prerequisite validation is
   comprehensive:
   - **Docker CLI**: Verifies `docker --version`.
   - **Docker Buildx**: Verifies `docker buildx version` with automatic plugin installation if missing.
   - **Docker Daemon**: Checks `docker info` to verify the daemon is running, with automatic start probes (e.g.,
     launching Docker Desktop on macOS or `systemctl start docker` on Linux).
   - **Remediation**: Dedicated `install-docker`, `install-homebrew`, and `check-docker` targets guide or automate
     resolution.

   In `holon-agentic-coder` (`apps/holon-agentic-coder/Makefile`):
   - `check-prerequisites` currently only performs a basic `command -v docker` check as an advisory warning.
   - It does **not** check whether `docker buildx` is installed, even though `apps/sandbox-executor/build_all_images.sh`
     relies on `docker buildx bake`.
   - It does **not** check whether the Docker daemon is actually running (`docker info`). If Docker is stopped,
     container image builds (`make build-images` / `make test-integration`) fail mid-execution rather than failing fast.
   - It lacks automated remediation targets (`install-docker`, `check-docker`).

2. **Make & Toolchain Bootstrapping**:
   - `Makefile` requires GNU Make (GNU Make >= 3.81 on macOS; GNU Make 4+ on Linux).
   - Non-GNU make (e.g., BSD bmake) fails on GNU-specific directives (`.DEFAULT_GOAL`, `ifeq`, `$(shell ...)`).
   - Make is the standardized entry point for developer workflows; prerequisite validation (`make check-prerequisites`
     and `make check-docker`) is implemented directly in `Makefile`.
   - Note: Git presence is not checked because the repository is already cloned via Git.

## Acceptance Criteria

1. Align `apps/holon-agentic-coder/Makefile` with `holon-coherence`:
   - Check GNU Make version (`MAKE_VERSION >= 3.81`).
   - Check uv (`uv --version`).
   - Check npx (`npx --version`).
   - Check Docker CLI (`docker --version`).
   - Check Docker Buildx (`docker buildx version`).
   - Check Docker daemon running status (`docker info`).
   - Provide clear remediation steps or automated setup commands when tools are missing or daemon is stopped.
2. Implement prerequisite checks directly inside `Makefile` (`check-prerequisites`, `prerequisites`, `check-docker`),
   without requiring separate scripts.
3. Verify `make check-prerequisites` and `make check-docker` cleanly report all tools and running states.
4. Ensure CI environments without nested virtualization or Docker daemons (e.g. macOS runners) handle Docker checks
   gracefully with `AUTO_INSTALL=false` or advisory warning mode.

## Assignment

Assignee: `antigravity`

## Resolution

- Implemented pure Makefile targets `check-prerequisites` (alias `prerequisites`), `check-docker`, `install-docker`, and
  `install-homebrew` in `holon-agentic-coder` following and extending `holon-coherence`.
- Omitted redundant Git check per human instruction (Git is already present to clone the repo).
- Avoided separate shell scripts, housing all prerequisite detection and installation workflows directly in `Makefile`.
- Protected `check-docker` with short-circuiting on missing CLI, hardened dry-run detection (`make -n`) via
  `$(filter-out --%,$(MAKEFLAGS))`, and supported multi-distro Linux package managers (`apt-get`, `dnf`, `pacman`).
- Enforced test isolation in `apps/sandbox-executor/tests/test_token_reduction.py` by mocking socket `connect_ex` across
  custom port tests.
- Reviewed and unanimously approved via the 3-Agent Ensemble Consensus Reviewer; merged to `main` in
  [PR #55](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/55).
