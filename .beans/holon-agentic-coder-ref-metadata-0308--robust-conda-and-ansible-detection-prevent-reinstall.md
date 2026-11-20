---
id: "0308"
title: "Robust Conda and Ansible detection preventing re-installation and base corruption"
status: completed
created_at: 2026-11-17T14:45:00+11:00
updated_at: 2026-11-17T15:32:00+11:00
tags:
  - dev-env
  - conda
  - ansible
  - bootstrap
  - bugfix
---

# 0308 - Robust Conda and Ansible detection preventing re-installation and base corruption

## Problem Statement

When running `make bootstrap` or `make converge` on a system with existing Conda (`/opt/homebrew/bin/conda`) and Ansible
(`~/.local/bin/ansible-playbook`):

1. `Makefile` and `ansible/roles/conda/tasks/main.yml` did not guarantee standard Homebrew/Linuxbrew paths in `PATH`,
   causing subshell command checks (`command -v conda`) to fail if not already exported.
2. `make bootstrap` ran
   `"$(CONDA)" install -y -c conda-forge --override-channels python=3.13 ansible-core ansible-lint pyyaml`, which
   attempted to downgrade or reinstall Python in the base environment (Miniforge shipped with Python 3.14). This caused
   Conda to redownload and reinstall Python from scratch and corrupted the base environment if interrupted.
3. `Makefile` hardcoded `PB := $(CONDA_DIR)/bin/ansible-playbook`, ignoring any existing `ansible-playbook` already on
   `PATH`.
4. If Conda was already installed, `bootstrap` did not clearly report that existing Conda is being reused.

## Scope of Changes

1. **`Makefile`**:
   - Prepend Homebrew and Linuxbrew standard paths
     (`/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/home/linuxbrew/.linuxbrew/bin:$(HOME)/.linuxbrew/bin`)
     to `PATH`.
   - Probe `CONDA` across `command -v conda` and known binary locations (`/opt/homebrew/bin/conda`,
     `/usr/local/bin/conda`, `/opt/homebrew/Caskroom/miniforge/base/condabin/conda`,
     `/opt/homebrew/Caskroom/miniforge/base/bin/conda`, `/home/linuxbrew/.linuxbrew/bin/conda`,
     `$(HOME)/.linuxbrew/bin/conda`, `$(HOME)/miniforge3/bin/conda`).
   - If `CONDA` is found, resolve `CONDA_DIR` dynamically via `$$CONDA info --base 2>/dev/null`.
   - Probe `PB`, `GALAXY`, `LINT` to reuse existing executables in `$(CONDA_DIR)/bin` or on `PATH`
     (`command -v ansible-playbook`).
   - In `bootstrap:`:
     - Skip Conda installation if `[ -x "$(CONDA)" ]` or `command -v conda` succeeds.
     - Skip Ansible installation if `[ -x "$(PB)" ]` succeeds.
     - If Ansible must be installed into Conda, do NOT pin `python=3.13` on the base environment; install
       `ansible-core ansible-lint pyyaml` cleanly.
2. **`ansible/roles/conda/tasks/main.yml`**:
   - Check candidate Conda binaries directly and resolve base prefix with `<discovered_bin> info --base`.
   - Never run `homebrew_cask` miniforge or micromamba when any Conda executable exists.
3. **Tests & Validation**:
   - Update tests in `tests/test_manifest.py`.
   - Ensure `uv run pytest`, `ruff`, `ansible-lint`, `prettier`, and `make check` all pass.

## Resolution

Merged in [PR #11](https://github.com/thomashan/dev-env/pull/11) (`ca3bec3`).

- Exported extended Homebrew/Linuxbrew PATH in `Makefile`.
- Dynamically discovers existing Conda (`info --base`) and existing Ansible on `PATH` (`~/.local/bin/ansible-playbook`),
  completely skipping package manager installations when already present.
- Removed `python=3.13` pin on Conda install, preserving whatever Python version exists in the host's base Conda
  environment without downgrade or corruption.
