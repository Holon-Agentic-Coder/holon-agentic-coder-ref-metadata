---
name: install-coherence
description:
  Builds the holon-coherence container image via Docker Buildx Bake and installs or updates the latest version of the
  holon-coherence CLI tool via uv tool install. Activate this skill whenever the user asks to install, update, rebuild,
  or upgrade holon-coherence or its Docker image.
---

# Install Holon-Coherence Skill (`install-coherence`)

This skill provides an automated workflow for building the `holon-coherence` container image using Docker Buildx Bake
and installing or updating the host-side `holon-coherence` CLI tool via `uv tool install`.

---

## Architecture & Operational Principles

1. **Holon-Coherence Overview**:
   - `holon-coherence` is the network optimization proxy and telemetry gateway for the Holon ecosystem.
   - It packages a Docker image built via `build_image.sh` (`docker-bake.hcl`).
   - Its host CLI entrypoint is defined in `pyproject.toml` (`holon-coherence = "holon_coherence.cli:main"`).

2. **Hermetic Host Tool Installation (`uv tool install`)**:
   - The CLI binary must be installed via `uv tool install --force --reinstall --editable apps/holon-coherence/main`.
   - `--editable` ensures executables placed in `~/.local/bin/` reflect live repository changes without manual
     re-packaging.

---

## Execution Phases

### Phase 1: Prerequisite Validation

Verify the local environment satisfies all execution requirements:

1. `uv` is installed and reports its version (`uv --version`).
2. Docker CLI is installed (`docker --version`).
3. Docker daemon is running and responsive (`docker info`).
4. Docker Buildx plugin is installed (`docker buildx version`).

### Phase 2: Upstream Git Synchronization (Optional)

Unless `--no-sync` is specified, fetch the latest references and fast-forward trunk:

```bash
git -C apps/holon-coherence/main fetch origin
git -C apps/holon-coherence/main pull --ff-only origin main
```

### Phase 3: Docker Image Build via Docker Buildx Bake

Rebuild the `holon-coherence` Docker image with latest source and dependencies:

```bash
make -C apps/holon-coherence/main build-image
# Or: ./apps/holon-coherence/main/build_image.sh
```

### Phase 4: CLI Tool Installation via `uv tool install`

Install or update the `holon-coherence` executable in `~/.local/bin/`:

```bash
uv tool install --force --reinstall --editable apps/holon-coherence/main
```

### Phase 5: Verification & Health Checks

1. Verify registered tools:
   ```bash
   uv tool list
   ```
2. Verify binary path and help output:
   ```bash
   which holon-coherence && holon-coherence -h
   ```
3. Inspect local Docker image:
   ```bash
   docker image inspect holon-coherence:latest
   ```

---

## Automated Orchestrator Script

A dedicated Python orchestrator is available at [install_coherence.py](scripts/install_coherence.py):

```bash
# Run full build and installation for holon-coherence
python3 .agents/skills/install_coherence/scripts/install_coherence.py

# Dry-run to preview actions
python3 .agents/skills/install_coherence/scripts/install_coherence.py --dry-run

# Skip Docker build (reinstall CLI only)
python3 .agents/skills/install_coherence/scripts/install_coherence.py --skip-image

# Skip CLI install (rebuild Docker image only)
python3 .agents/skills/install_coherence/scripts/install_coherence.py --skip-tool
```
