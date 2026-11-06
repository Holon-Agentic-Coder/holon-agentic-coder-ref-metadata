---
name: install-holon
description:
  Builds the container images and installs or updates the latest versions of holon and holon-coherence CLI tools via uv
  tool install. Activate this skill whenever the user asks to install, update, rebuild, or upgrade holon and
  holon-coherence or their Docker images.
---

# Install Holon Ecosystem Skill (`install-holon`)

This skill provides an automated, reproducible workflow for building all role and orchestrator Docker images using
Docker Buildx Bake and installing or updating the host-side `holon` and `holon-coherence` CLI tools via
`uv tool install`.

---

## 📐 Architecture & Operational Principles

1. **Dual Component Ecosystem**:
   - **`holon-agentic-coder`**: Sandboxed fractal intent evolution engine. Packages 8 Docker images (`holon/base`,
     `holon/agent-claude`, `holon/agent-codex`, `holon/agent-gemini`, `holon/agent-opencode`, `holon/agent-pi`,
     `holon/agent-antigravity`, `holon/orchestrator`) built via `apps/sandbox-executor/build_all_images.sh`
     (`docker-bake.hcl`). Its CLI entry point is defined in `apps/sandbox-executor/pyproject.toml`
     (`holon = "sandbox_executor.cli:main"`).
   - **`holon-coherence`**: Network optimization proxy and telemetry gateway. Packages the `holon-coherence` Docker
     image built via `build_image.sh` (`docker-bake.hcl`) and its CLI defined in `pyproject.toml`
     (`holon-coherence = "holon_coherence.cli:main"`).

2. **Hermetic Host Tool Installation (`uv tool install`)**:
   - The CLI binaries must be isolated from system Python and virtualenvs.
   - Installed using `uv tool install --force --reinstall --editable <path>`, ensuring binaries in `~/.local/bin/` link
     directly to worktree sources for instant feedback without re-packaging.

3. **Multi-Architecture & Cached Bake**:
   - All Docker images use Docker Buildx Bake targets to exploit layer caching and cache mounts for fast incremental
     rebuilds.

4. **Post-Merge Trigger (Bean 0182)**: When a reinstall is a recorded post-merge step for a PR that changed `holon` or
   `holon-coherence`, wait for the merge with `uv run python .agents/scripts/wait_for.py merged <owner/repo> <N>` (exit
   0 merged, 1 closed, 2 timeout) or act on the watcher's `pr_merged` event (see
   [`.agents/watcher/README.md`](../../watcher/README.md)). Never type a polling loop by hand.

---

## 🚀 Execution Phases

### Phase 1: Prerequisite Validation

Verify the local environment satisfies all execution requirements:

1. `uv` is installed and reports its version (`uv --version`).
2. Docker CLI is installed (`docker --version`).
3. Docker daemon is running and responsive (`docker info`).
4. Docker Buildx plugin is installed (`docker buildx version`).

### Phase 2: Upstream Git Synchronization (Optional)

Unless `--no-sync` is specified, fetch the latest references and fast-forward trunk:

```bash
git -C apps/holon-agentic-coder/main fetch origin
git -C apps/holon-agentic-coder/main pull --ff-only origin main

git -C apps/holon-coherence/main fetch origin
git -C apps/holon-coherence/main pull --ff-only origin main
```

### Phase 3: Docker Image Builds via Docker Buildx Bake

Rebuild all container images with latest source and dependencies:

```bash
# 1. Build all holon-agentic-coder images (base, agents, orchestrator)
make -C apps/holon-agentic-coder/main build-images
# Or: ./apps/holon-agentic-coder/main/apps/sandbox-executor/build_all_images.sh

# 2. Build holon-coherence proxy image
make -C apps/holon-coherence/main build-image
# Or: ./apps/holon-coherence/main/build_image.sh
```

### Phase 4: CLI Tool Installation via `uv tool install`

Install or update the CLI executables in `~/.local/bin/`:

```bash
# 1. Install holon CLI
uv tool install --force --reinstall --editable apps/holon-agentic-coder/main/apps/sandbox-executor

# 2. Install holon-coherence CLI
uv tool install --force --reinstall --editable apps/holon-coherence/main
```

### Phase 5: Verification & Health Checks

1. Verify registered tools:
   ```bash
   uv tool list
   ```
2. Verify binary paths and version/help output:
   ```bash
   which holon && holon --version
   which holon-coherence && holon-coherence -h
   ```
3. Inspect local Docker images:
   ```bash
   docker image inspect holon/orchestrator:latest holon/agent-antigravity:latest holon-coherence:latest
   ```

---

## 🛠️ Automated Orchestrator Script

A consolidated Python orchestrator is available at [install_holon.py](scripts/install_holon.py):

```bash
# Run full build and installation for both repositories
python3 .agents/skills/install_holon/scripts/install_holon.py

# Dry-run to preview actions
python3 .agents/skills/install_holon/scripts/install_holon.py --dry-run

# Skip Docker builds (reinstall CLIs only)
python3 .agents/skills/install_holon/scripts/install_holon.py --skip-images

# Skip CLI install (rebuild Docker images only)
python3 .agents/skills/install_holon/scripts/install_holon.py --skip-tools

# Target only holon-agentic-coder
python3 .agents/skills/install_holon/scripts/install_holon.py --holon-only

# Target only holon-coherence
python3 .agents/skills/install_holon/scripts/install_holon.py --coherence-only
```
