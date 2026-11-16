---
# holon-agentic-coder-ref-metadata-0305
title: "Treat uv as a standard toolset package without special treatment"
status: completed
type: task
priority: high
tags:
  - dev-env
  - readme
  - conda
  - ansible
  - makefile
  - hygiene
created_at: 2026-11-16T05:16:00Z
updated_at: 2026-11-16T07:54:02Z
---

## Summary

Establish **`brew` (macOS) and `apt` (Linux)** as the system prerequisites in `thomashan/dev-env` (failing cleanly in
`make check` and `make bootstrap` if missing, while `make`, `curl`, and every other tool can be installed via
`brew`/`apt`), treat `uv` uniformly as a standard Conda-installed toolset member (`devenv_conda_tools` inside the
`conda` role), convert the `README.md` ASCII toolchain diagram into a Mermaid `flowchart TD` diagram, eliminate legacy
`~/.local/share/dev-env/bin` shim symlinks and `stow`/`git`/`curl` probes from `make check`, and fix the bare-repo clone
snippet in `README.md`.

## Requirements & Acceptance Criteria

1. **System Prerequisites (`brew` on macOS, `apt` on Linux)**:
   - Document and enforce `brew` (macOS) and `apt` (Debian/Ubuntu Linux) as the system prerequisites across `Makefile`,
     `README.md`, `holon-config/world/ruleset.md`, and `holon-config/world/constraints.md` (`make` and `curl` can be
     installed through `brew`/`apt`).
   - In `Makefile` `check:`, probe `GNU Make`, `OS`, `apt (Linux backend)`, `brew (macOS backend)`, `conda`,
     `ansible-core`, and `community.general`; fail with `err=$((err+1))` if `brew` (Darwin) or `apt` (Linux) is missing;
     remove `stow`, `git`, and `curl` checks (`stow`, `git`, `curl` are converged through Ansible's `packages` role).
   - In `Makefile` `bootstrap:`, fail immediately (`exit 1`) if `brew` (Darwin) or `apt` (Linux) is missing, install
     `curl` via `brew install curl` (Darwin) or `apt update && apt install -y curl` (Linux) if missing, and fetch
     Miniforge3 using `curl -fsSL` (never `wget`, `urllib.request`, or `apt-get`).
2. **Consolidate `uv` & Remove Special-Treatment Wording**:
   - Remove `(git, curl, and uv are NOT cold-start prerequisites; ...)`, the `> [!NOTE]` callout, `"for app dev"` /
     `"purely as an application development tool"`, `"Conda Application-Dev Tools"` heading, and stale `uv` comments
     from `README.md`, `holon-config/world/ruleset.md`, `holon-config/world/constraints.md`, `.ansible-lint`, and
     `ansible/group_vars/all.yml`.
   - Replace `devenv_uv_tools` with `devenv_conda_tools: [uv, ruff, pre-commit]` in `ansible/group_vars/all.yml`, fold
     `devenv_conda_tools` and optional `devenv_holon_source` installation into `ansible/roles/conda/tasks/main.yml`,
     delete `ansible/roles/uv/`, and remove `uv` from `ansible/site.yml`.
3. **Convert Toolchain Diagram to Mermaid & Remove Shims**:
   - Replace the ASCII box diagram under `## Tool Chain & Execution Order` in `README.md` with a `mermaid`
     (`flowchart TD`) diagram.
   - Update the `Stage-by-Stage Execution` table in `README.md` (`brew`/`apt` prerequisite, `make check`,
     `make bootstrap`) and fix the bare-repo clone snippet (`remote.origin.fetch`, `git fetch origin`,
     `git worktree add`).
   - Remove `BIN := $(DEVENV_HOME)/bin` and `ln -sfn` shims from `Makefile`; set `PB`, `GALAXY`, and `LINT` directly to
     `$(CONDA_DIR)/bin/...`; remove all `shims` and `~/.local/share/dev-env/bin/` references from `README.md`.
4. **Tests (`tests/test_manifest.py`) & Verification**:
   - Update `tests/test_manifest.py` to enforce the consolidated `conda` role (`devenv_conda_tools`), absence of
     `ansible/roles/uv`, direct `$(CONDA_DIR)/bin/...` executables without `BIN`/`ln -sfn` shims, updated `make check`
     (`GNU Make`, `OS`, `apt`, `brew`, `conda`, `ansible-core`, `community.general`; missing `apt`/`brew` fails; no
     `uv`, `stow`, `git`, or `curl` probes), `make bootstrap` (fails without `brew`/`apt`, installs `curl` via
     `brew`/`apt` if missing, downloads Miniforge3 via `curl -fsSL`, no `wget`/`urllib.request`/`apt-get`), and Mermaid
     diagram + clean `README.md` copy.
   - Verify with `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Flow Worktree: `/Users/thomashan/git/dev-env/flow-toolset`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/toolset.json`

## Resolution

Delivered via [PR #7](https://github.com/thomashan/dev-env/pull/7) and merged into `main` (`4a8fb18` /
`4a8fb1833dc355c1562916511b6d9c46091929ef`):

- **Key Architectural Deliverables**:
  - Established `brew` (macOS) and `apt` (Linux) as the system prerequisites in `Makefile`, `README.md`,
    `holon-config/world/ruleset.md`, and `holon-config/world/constraints.md` (`make check` and `make bootstrap` fail if
    `brew`/`apt` is missing; `curl` is installed via `brew`/`apt` in `make bootstrap` when absent; `stow`, `git`, and
    `curl` probes removed from `make check`).
  - Consolidated `uv`, `ruff`, and `pre-commit` into `devenv_conda_tools` in `ansible/group_vars/all.yml` and
    `ansible/roles/conda/tasks/main.yml`, removed `ansible/roles/uv/` and `- role: uv` from `ansible/site.yml`, and
    removed all special-treatment `uv` callouts.
  - Removed `~/.local/share/dev-env/bin` shim symlinks (`BIN` and `ln -sfn`) from `Makefile` (`PB`, `GALAXY`, `LINT`
    invoke `$(CONDA_DIR)/bin/ansible-*` directly) and `README.md`.
  - Converted the `README.md` ASCII toolchain diagram to a Mermaid `flowchart TD` diagram, updated the Stage-by-Stage
    Execution table, and fixed the bare-repo worktree clone snippet.
- **Verification & Tests**: Updated `tests/test_manifest.py`; verified with `pytest -m "not network"` (`84 passed`),
  `ruff check .`, `ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, `make check`, and all 6 GitHub
  Actions CI checks (`hygiene`, `make-matrix` on macOS/Ubuntu, `test-unit` on macOS/Ubuntu, `test-network`).
- **Holon Flow Traversal**: Completed all 5 stages (`I-1794808105-toolset/_` ->
  `P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium` ->
  `E-1794808371-23cac9c7-antigravity-agent-gemini-3.8-flash-medium` -> 3/3 ensemble review approval -> calibration
  `d539a5b` with Predicted EV `87.77`, Actual EV `90.32`, $\Delta\text{EV} = +2.55$).
