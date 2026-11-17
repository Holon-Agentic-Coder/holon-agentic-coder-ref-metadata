---
id: "0318"
title: "Remove step letter prefixes from wizard prompts, default to fish and docker-desktop, and fix nvm path in fish"
status: in-progress
created_at: 2026-11-17T22:55:00+11:00
updated_at: 2026-11-17T22:57:00+11:00
tags:
  - dev-env
  - wizard
  - fish
  - docker-desktop
  - nvm
  - bugfix
---

# 0318 - Remove step letter prefixes from wizard prompts, default to fish and docker-desktop, and fix nvm path in fish

## Problem Statement

1. **Inconsistent Step Letter Prefixes**: Running `make configure` shows prompts jumping from `Step B` to `Step D` (when
   no dotfile conflicts exist), giving an appearance of skipped steps. Furthermore, other prompts lack step prefixes
   entirely.
2. **Feature Flag Defaults**: `devenv_set_login_shell` (fish) and `devenv_install_gui_casks` (docker-desktop) currently
   default to `false`. Users want these defaulted to `true` out of the box.
3. **Node NVM Path Assertion Failure in `make install`**: `TASK [node : Assert nvm-managed node wins on PATH]` fails
   during `make converge` because PR #18 stripped the NVM PATH prepend from `config.fish` to make it pure OS default,
   leaving Fish sessions resolving `/opt/homebrew/bin/node` instead of `~/.local/share/nvm/current/bin/node`. This was
   not caught in CI because unit test suites run in virtualenv without an end-to-end converge against a live host with
   Homebrew node installed.

## Scope of Changes

1. **Wizard Prompt Cleanup (`scripts/devenv_wizard.py`)**:
   - Remove `Step A: `, `Step B: `, and `Step D: ` prefixes from all interactive prompts.
   - Default `devenv_set_login_shell` and `devenv_install_gui_casks` fallbacks to `True`.
2. **Ansible Defaults (`ansible/group_vars/all.yml`)**:
   - Set `devenv_set_login_shell: true`.
   - Set `devenv_install_gui_casks: true`.
3. **Fish NVM Integration (`dotfiles/fish/.config/fish/conf.d/00-devenv.fish`)**:
   - Prepend `$XDG_DATA_HOME/nvm/current/bin` to PATH in `00-devenv.fish` so Fish login shells correctly resolve
     nvm-managed node over Homebrew node, while keeping `config.fish` pure OS default.
4. **Tests & Validation**:
   - Update `tests/test_wizard.py` and `tests/test_manifest.py`.
   - Run `make test`, `make lint`, and `make check`.
