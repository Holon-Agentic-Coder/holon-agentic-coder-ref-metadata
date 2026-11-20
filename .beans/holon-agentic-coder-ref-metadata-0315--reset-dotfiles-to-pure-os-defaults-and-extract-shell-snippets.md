---
id: "0315"
title: "Reset dotfiles to pure OS defaults and extract modular shell setup snippets"
status: completed
created_at: 2026-11-17T18:30:00+11:00
updated_at: 2026-11-17T20:47:26+11:00
tags:
  - dev-env
  - dotfiles
  - bash
  - zsh
  - fish
  - snippets
  - enhancement
---

# 0315 - Reset dotfiles to pure OS defaults and extract modular shell setup snippets

## Problem Statement

Currently, the tracked dotfiles in `dotfiles/` (`.bashrc`, `.zshrc`, `config.fish`) contain pre-injected toolchain hooks
for Homebrew (`brew shellenv`), Conda (`conda shell hook`), and NVM (`$XDG_DATA_HOME/nvm/current/bin`).

While intended to wire tools automatically, this overrides clean system behavior and prevents users from starting from a
clean OS baseline where they can selectively choose what to add to their `.bashrc`.

Furthermore, Ansible roles (`node`) and test invariants in `tests/test_manifest.py` tightly couple to the presence of
these strings inside `dotfiles/fish/.config/fish/config.fish` and `00-devenv.fish`, rather than referencing the single
source of truth in `versions.json`.

## Scope of Changes

1. **Reset Dotfiles to Pure OS Defaults**:
   - `dotfiles/bash/.bashrc` & `.bash_profile`: Reset to clean vanilla OS skeleton stubs. Remove embedded nvm, brew, and
     conda hooks.
   - `dotfiles/zsh/.zshrc`: Reset to clean vanilla OS skeleton stub. Remove embedded nvm, brew, and conda hooks.
   - `dotfiles/fish/.config/fish/config.fish`: Reset to a clean default skeleton without hardcoded brew, conda, or nvm
     path injections.
   - Ensure `dotfiles/tmux/.config/tmux/tmux.conf` and `dotfiles/conda/.condarc` remain clean upstream defaults.
2. **Extract Modular Shell Snippets (`dotfiles/examples/devenv-shell-snippets.sh`)**:
   - Create a clean reference snippet file with modular, well-commented blocks that users can selectively copy into
     their `.bashrc` or `.bashrc.local`:
     - NVM managed node PATH prepend (`$XDG_DATA_HOME/nvm/current/bin`)
     - Multi-OS Homebrew/Linuxbrew `brew shellenv` evaluation
     - Conda (miniforge) shell hook probe and activation
     - Local override hook loading (`.bashrc.local`, `.zshrc.local`)
3. **Decouple Node Role and Test Manifest**:
   - In `ansible/roles/node/tasks/main.yml`, load `devenv_node_default_version` from `versions.json` (or
     `group_vars/all.yml`) instead of parsing `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`.
   - In `tests/test_manifest.py`, update tests that previously required `config.fish` to contain `$HOME/miniforge3` and
     `brew shellenv`/`nvm` (`test_conda_path_parity_between_ansible_and_fish`, `test_node_bin_is_first_on_path`) to
     validate pure OS default invariants, and update node pin tests to reference `versions.json`.
   - Add test coverage verifying `dotfiles/examples/devenv-shell-snippets.sh` exists and contains valid syntax.
4. **Validation**:
   - Run full verification suite (`make test`, `make lint`, `make check`).

## Resolution

Delivered via [PR #18](https://github.com/thomashan/dev-env/pull/18) and merged into `main`
(`a3a21aa130ae34d953ecb546781c725a34f3d3f6`):

- **Pure OS Default Dotfiles**: Reset `dotfiles/bash/.bashrc`, `dotfiles/bash/.bash_profile` (retained clean OS
  skeleton), `dotfiles/zsh/.zshrc`, and `dotfiles/fish/.config/fish/config.fish` to pure vanilla OS defaults without
  pre-injected toolchain hooks.
- **Modular Shell Snippets**: Created `dotfiles/examples/devenv-shell-snippets.sh` providing opt-in modular snippets for
  Homebrew/Linuxbrew, Conda (miniforge), NVM, and local override loading (`.bashrc.local`, `.zshrc.local`).
- **Role & Test Decoupling**: Decoupled `ansible/roles/node/tasks/main.yml` and `tests/test_manifest.py` /
  `tests/test_templating.py` from fish dotfile parsing, referencing `versions.json` and validating pure OS default
  invariants plus snippet syntax.
- **Holon Flow Traversal**: Completed all 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration)
  successfully.
