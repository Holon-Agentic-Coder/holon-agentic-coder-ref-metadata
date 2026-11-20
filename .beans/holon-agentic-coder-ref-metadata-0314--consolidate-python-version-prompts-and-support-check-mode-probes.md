---
id: "0314"
title: "Consolidate Python version prompts to single prompt and support check-mode probes"
status: completed
created_at: 2026-11-17T18:18:00+11:00
updated_at: 2026-11-17T20:38:00+11:00
tags:
  - dev-env
  - wizard
  - python
  - check-mode
  - enhancement
---

# 0314 - Consolidate Python version prompts to single prompt and support check-mode probes

## Problem Statement

1. **Redundant Python Prompts in Wizard**: The interactive wizard (`scripts/devenv_wizard.py`) prompts users twice
   back-to-back for Python:
   ```text
   Python runtime version [3.13]:
   Conda dev environment Python version [3.13]:
   ```
   Both default to `3.13`, and the repository ruleset strictly pins `==3.13.*`. Asking for both creates redundant
   friction and invites version drift between the base environment and the Conda dev environment.
2. **Check-Mode Command Skipping**: In `ansible/roles/node/tasks/main.yml`,
   `TASK [node : Verify which node a login shell resolves]` is an `ansible.builtin.command` task. By default in Ansible,
   commands are skipped in `--check` mode (`make check-mode`, `make doctor`), leaving `devenv_node_which.stdout` empty
   (`""`). The subsequent assertion: `TASK [node : Assert nvm-managed node wins on PATH]` then fails because
   `'.local/share/nvm/current/bin/node' in ""` evaluates to false. Read-only verification commands
   (`changed_when: false`) must declare `check_mode: false`.

## Scope of Changes

1. **`scripts/devenv_wizard.py`**:
   - Consolidate the two Python prompts into a single prompt:
     `py_version = prompt_user("Python version", default=py_version, interactive=True)`
   - Set both `devenv_python_version` and `devenv_conda_env_python` to `py_version` in the persisted choices dictionary.
2. **`ansible/group_vars/all.yml`**:
   - Update `devenv_conda_env_python: "{{ devenv_python_version }}"` so the Conda dev environment Python version
     defaults directly to the authoritative Python pin.
3. **`ansible/roles/node/tasks/main.yml`**:
   - Add `check_mode: false` to `Verify which node a login shell resolves`.
4. **`ansible/roles/neovim/tasks/main.yml`**:
   - Add `check_mode: false` to `Read the installed Neovim version`.
5. **Tests & Validation**:
   - Update `tests/test_wizard.py` and `tests/test_manifest.py` for the unified Python prompt and check-mode support.
   - Verify `make test`, `make lint`, `make check-mode`, and `make check`.

## Resolution

Delivered via [PR #17](https://github.com/thomashan/dev-env/pull/17) and merged into `main` (`0fcc9d3`):

- **Consolidated Python Prompts**: Unified the wizard prompts in `scripts/devenv_wizard.py` to a single
  `Python version [3.13]:` prompt, persisting both `devenv_python_version` and `devenv_conda_env_python` synchronously.
- **Dynamic Group Defaults**: Configured `devenv_conda_env_python: "{{ devenv_python_version }}"` in
  `ansible/group_vars/all.yml` to prevent version drift between base Conda and environment runtime.
- **Check-Mode Probing**: Added `check_mode: false` to read-only shell probing tasks in `node` and `neovim` roles so
  that `make check-mode` and `make doctor` correctly execute assertions without failing on empty dry-run stdout.
- **Verification**: Added 4 unit tests in `tests/test_wizard.py` (all 105 tests passing, `ansible-lint`, `ruff`, and
  `make check` green).
- **Holon Flow Traversal**: All 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed
  successfully under subagent `eb6e0333-f3ad-446b-a2cc-1580a5ea998f`.
