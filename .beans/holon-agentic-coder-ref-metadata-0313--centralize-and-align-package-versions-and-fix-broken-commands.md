---
id: "0313"
title: "Centralize and align package versions and fix breaking commands (make lint, check-mode, neovim assert)"
status: completed
created_at: 2026-11-17T16:08:00+11:00
updated_at: 2026-11-17T18:17:00+11:00
tags:
  - dev-env
  - versions
  - makefile
  - lint
  - check-mode
  - ansible
---

# 0313 - Centralize and align package versions and fix breaking commands

## Problem Statement

1. **Version Drift across Consumers**:
   - Node.js: `dotfiles/fish/.../00-devenv.fish` and `devenv_wizard.py` specify `26.13.1`, but
     `.github/workflows/test-hygiene.yml` was still hardcoded to `20`.
   - Python: `3.13` is duplicated across `Makefile` (`PYTHON_PIN`), `pyproject.toml`, `ansible/group_vars/all.yml`,
     GitHub workflows, and `devenv_wizard.py`.
   - Ansible Core & Lint: `Makefile` installs `ansible-core` via Conda without a version pin (pulling 2.22.0), while
     `pyproject.toml` had `>=2.19` (resolving 2.21.5 in uv). When `make lint` runs, `ansible_compat` crashes with
     `Ansible CLI (2.21.5) and python module (2.22.0) versions do not match`.
   - Neovim: Minimum version `0.12` is checked in Neovim health check and Ansible tasks.
2. **Broken Commands**:
   - `make lint`: Fails due to Ansible CLI/module version mismatch and missing `uv` integration. In CI,
     `uv run --extra test ansible-lint` passes cleanly against `.ansible-lint`.
   - `make converge`: Fails at `TASK [neovim : Assert Neovim is new enough for vim.pack and nvim-pack-lock.json]` with
     `object of type 'str' has no attribute 'regex_replace'` because `.regex_replace` is used as a string method instead
     of filter syntax or Ansible's built-in `is version('0.12', '>=')`.
   - `make check-mode` & `make doctor`: Fail on fresh machines at `TASK [node : Install the fisher function]` because
     directory creation was simulated in `--check` mode and didn't exist on disk for `get_url`.

## Scope of Changes

1. **Common Version Configuration**:
   - Introduce a centralized `versions.json` at the root of `dev-env` defining authoritative versions for:
     - `python`: `"3.13"`
     - `node`: `"26.13.1"`
     - `ansible_core`: `"2.22"`
     - `neovim_min`: `"0.12"`
   - Wire `Makefile`, `ansible/group_vars/all.yml`, `dotfiles/fish/.../00-devenv.fish`, `scripts/devenv_wizard.py`, and
     GitHub workflows to align with these versions.
2. **Fix `ansible/roles/neovim/tasks/main.yml`**:
   - Replace invalid `.regex_replace()` method call with Ansible standard version comparison:
     ```yaml
     - devenv_nvim_version.stdout_lines[0] is match('NVIM v')
     - devenv_nvim_version.stdout_lines[0] | regex_replace('^NVIM v', '') is version('0.12', '>=')
     ```
3. **Fix `make lint` in `Makefile`**:
   - Update `lint:` target to prefer `uv run --extra test ansible-lint` when `uv` is available, mirroring `make test`,
     and prepend `$(dir $(LINT))` to `PATH` when falling back to conda.
4. **Fix `ansible/roles/node/tasks/main.yml`**:
   - Add `check_mode: false` to `Ensure the fisher path exists` so dry-run check-mode does not fail downstream download.
5. **Tests & Validation**:
   - Add unit tests in `tests/test_manifest.py` verifying version alignment across all consumers and verifying
     `make lint` and assertion syntax.

## Resolution

- Introduced centralized `versions.json` manifest for python, node, ansible_core, and neovim_min.
- Aligned `devenv_wizard.py`, `Makefile`, and `test-hygiene.yml` with `versions.json`.
- Fixed `make lint` to prefer `uv run --extra test ansible-lint` with Conda PATH fallback.
- Fixed Neovim version assertion to use standard Ansible `is version('0.12', '>=')`.
- Added `check_mode: false` to fisher directory creation task.
- Added comprehensive unit tests in `tests/test_manifest.py` ensuring version alignment and command invariants.
- Merged via PR #16 (commit `9fae41e`).
