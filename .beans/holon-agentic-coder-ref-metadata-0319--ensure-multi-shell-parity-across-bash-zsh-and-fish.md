---
id: "0319"
title: "Ensure first-class multi-shell parity across Bash, Zsh, and Fish for all managed tools"
status: todo
created_at: 2026-11-17T23:08:00+11:00
updated_at: 2026-11-17T23:08:00+11:00
tags:
  - dev-env
  - multi-shell
  - bash
  - zsh
  - fish
  - nvm
  - node
  - conda
  - architecture
---

# 0319 - Ensure first-class multi-shell parity across Bash, Zsh, and Fish for all managed tools

## Problem Statement

`dev-env` historically evolved with a Fish-first mindset, delegating Node version management strictly to `nvm.fish` (via
Fisher) and testing path resolution solely using `fish -lc "which node; node -v"`.

Consequently:

1. **Bash & Zsh Were Unwired**: When repository dotfiles were reset to pure OS defaults, Bash and Zsh were left without
   NVM on `PATH`. In Bash and Zsh, `which node` fell back to legacy host symlinks (such as `~/.local/bin/node` pointing
   to Hermes Node v22.23.2).
2. **Missing Multi-Shell Tests**: Verification in Ansible roles (`node`, `conda`, `neovim`) and `tests/test_manifest.py`
   tested only Fish, leaving Bash and Zsh unverified and susceptible to broken paths and version drift.
3. **Core Architectural Principle**: All tools installed and managed by `dev-env` (Node, Python/Conda, Homebrew, Neovim)
   must be first-class citizens and operate with complete parity across all three supported shells: **Bash**, **Zsh**,
   and **Fish**.

## Architectural Requirements & Scope of Changes

1. **Node & NVM Multi-Shell Integration**:
   - **Bash & Zsh**: Install and wire official `nvm-sh/nvm` (respecting XDG Base Directory standards
     `$XDG_DATA_HOME/nvm` or `$HOME/.nvm`) so Bash and Zsh users can use `nvm` commands natively.
   - **Fish**: Retain `nvm.fish` via Fisher for native Fish event-driven version switching.
   - **Universal Binary Linkage**: Symlink `~/.local/bin/node`, `~/.local/bin/npm`, and `~/.local/bin/npx` directly to
     `~/.local/share/nvm/current/bin/*`. Because `~/.local/bin` is in standard `$PATH` across all OS default shells, all
     subshells, non-interactive scripts, and cron jobs immediately resolve the authoritative pinned Node version.
2. **Conda & Python Parity**:
   - Ensure Conda hooks (`conda shell.bash hook`, `conda shell.zsh hook`, `conda shell.fish hook`) and binary paths are
     consistently available and functional across Bash, Zsh, and Fish.
3. **Multi-Shell Automated Verification**:
   - In `ansible/roles/node/tasks/main.yml`, verify and assert Node resolution across all three shells:
     - `bash -lc "which node; node -v"`
     - `zsh -lc "which node; node -v"`
     - `fish -lc "which node; node -v"`
   - Assert that all three shells resolve to the pinned Node version (`v26.13.1`).
   - In `tests/test_manifest.py`, add tests asserting that all managed tools declare and verify multi-shell parity.
