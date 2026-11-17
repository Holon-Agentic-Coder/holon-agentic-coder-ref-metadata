---
id: "0324"
title:
  "Support Micromamba prefix on Linuxbrew, resolve Ansible galaxy collection path isolation, and allow make configure
  Python fallback"
status: in-progress
created_at: 2026-11-18T10:32:00+11:00
updated_at: 2026-11-18T10:32:00+11:00
tags:
  - dev-env
  - linuxbrew
  - micromamba
  - conda
  - ansible
  - makefile
  - bugfix
---

# 0324 - Support Micromamba prefix on Linuxbrew, resolve Ansible galaxy collection path isolation, and allow make configure Python fallback

## Problem Statement

During fresh bootstrap and installation testing on Linux (Ubuntu 26.04 x86_64 with Linuxbrew), three interconnected
defects were encountered:

1. **`make configure` Fails Prior to Bootstrap Due to Strict Conda Python Requirement**:
   - Running `make configure` on a freshly cloned repository fails with:
     ```text
     Error: Python 3 not found in /home/thomashan/miniforge3/bin/python3. Run 'make bootstrap' first.
     make: *** [Makefile:193: configure] Error 1
     ```
   - `scripts/devenv_wizard.py` uses standard library Python exclusively (with graceful `yaml` fallback). It does not
     require any third-party dependencies from Conda or Ansible.
   - Forcing `$(CONDA_DIR)/bin/python3` prevents users from configuring choices before bootstrapping or running
     `make configure; make install`.

2. **Ansible Galaxy Collection Path Mismatch (`community.general` Resolution Failure)**:
   - During `make bootstrap`, `ansible-galaxy collection install` runs:
     ```makefile
     ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install -r "$(SELF_DIR)/ansible/requirements.yml"
     ```
   - If `community.general` already exists in `~/.ansible/collections/` (e.g. from a system Ansible installation),
     `ansible-galaxy` reports:
     ```text
     Starting galaxy collection install process
     Nothing to do. All requested collections are already installed.
     ```
     and skips installing into `$(COLLECTIONS)` (`~/.local/share/dev-env/collections`).
   - However, `ansible.cfg` isolates collections to `collections_path = ~/.local/share/dev-env/collections`, and
     `converge` sets `ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS)`.
   - When `ansible-playbook` executes, it cannot find `community.general`, causing execution to abort:
     ```text
     [ERROR]: couldn't resolve module/action 'community.general.homebrew_tap'. This often indicates a misspelling, missing collection, or incorrect module path.
     Origin: /home/thomashan/git/dev-env/ansible/roles/homebrew/tasks/main.yml:66:3
     ```
   - `ansible-galaxy collection install` must explicitly pass `-p "$(COLLECTIONS)"` (or `--upgrade`) so dependencies are
     guaranteed to be present in `$(COLLECTIONS)`. Additionally, `ansible.cfg` should include `~/.ansible/collections`
     as a secondary fallback.

3. **Legacy Hardcoded `miniforge3` Path When Bootstrapping with Micromamba on Linuxbrew**:
   - On Linux with Linuxbrew, `make bootstrap` installs `micromamba` via Homebrew (`brew install micromamba`), but
     `CONDA_DIR` resolves to `~/miniforge3` due to legacy defaults from the standalone Miniforge shell installer.
   - Consequently, `micromamba create -y -p "$(CONDA_DIR)"` creates an environment at `~/miniforge3` instead of
     respecting standard Micromamba / XDG / Linuxbrew conventions (such as `$MAMBA_ROOT_PREFIX`, `~/.local/share/mamba`,
     or `~/micromamba`).
   - Furthermore, Linux users running `conda` in interactive shells expect `micromamba` to respond or an alias/wrapper
     `conda -> micromamba` to be provided when micromamba is the active Conda provider.

## Scope of Changes

1. **`make configure` System Python Fallback (`Makefile`)**:
   - In `Makefile`, update `configure` target to probe for `$(CONDA_DIR)/bin/python3`, then fall back to
     `command -v python3`, before displaying an error if no Python 3 interpreter exists.

2. **Fix Ansible Galaxy Collection Isolation (`Makefile`, `ansible.cfg`)**:
   - Update `Makefile` collection installation to explicitly pass the target directory via `-p "$(COLLECTIONS)"`:
     ```makefile
     ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install -p "$(COLLECTIONS)" -r "$(SELF_DIR)/ansible/requirements.yml"
     ```
   - In `ansible.cfg`, update `collections_path` to include `~/.ansible/collections` as a fallback:
     ```ini
     collections_path = ~/.local/share/dev-env/collections:~/.ansible/collections
     ```

3. **Align Linuxbrew Micromamba Prefix & Shell Alias (`Makefile`, `ansible/group_vars/all.yml`, dotfiles)**:
   - On Linux when `micromamba` is used, resolve `CONDA_DIR` cleanly to `$MAMBA_ROOT_PREFIX` or `~/.local/share/mamba`
     (or `~/micromamba` / Linuxbrew prefix).
   - Ensure `alias conda=micromamba` or a shell function wrapper is registered in Bash, Zsh, and Fish when `micromamba`
     is present and `conda` is absent.
   - Support discovery of the micromamba environment in shell conda hook probes across `dotfiles/bash/.bashrc`,
     `dotfiles/zsh/.zshrc`, and `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.

4. **Tests & Verification**:
   - Update `tests/test_manifest.py` to assert:
     - `Makefile` configure target has `python3` fallback.
     - `Makefile` galaxy collection install explicitly passes `-p "$(COLLECTIONS)"`.
     - `ansible.cfg` collections path search list includes fallback.
     - Shell configs provide `conda` alias or hook for `micromamba`.
   - Run `make test`, `make lint`, and `make check`.

5. **CI Cold-Start & Ansible Execution Coverage (`.github/workflows/make.yml`)**:
   - In `.github/workflows/make.yml`, on both `ubuntu-latest` and `macos-latest`:
     - Test `make configure` cold-start before `make bootstrap` to ensure configuration succeeds on bare machines.
     - Execute `make bootstrap` to verify the GNU Make -> Conda/Micromamba -> Ansible bootstrap chain actually works
       end-to-end on both OSes.
     - Execute Ansible playbook syntax & module check (`ansible-playbook ansible/site.yml --syntax-check` or
       `make check-syntax`) using the runtime `ANSIBLE_COLLECTIONS_PATH`, directly testing that all collections
       (including `community.general.homebrew_tap`) resolve without failure.
     - Execute `make check-mode` (or tag-scoped dry-run e.g. `--tags dotfiles,nvim-sync`) on both runners to exercise
       real playbook task execution without modifying runner system packages.
