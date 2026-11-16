---
# holon-agentic-coder-ref-metadata-0303
title: "Add host interactive wizard for dotfile merge and package variants"
status: todo
type: feature
priority: high
tags:
  - dev-env
  - dotfiles
  - stow
  - wizard
  - ansible
created_at: 2026-11-16T02:05:00Z
updated_at: 2026-11-16T02:22:00Z
---

## Summary

Add a pre-Ansible host interactive configuration wizard (`scripts/devenv_wizard.py` + `make configure`) and
multi-variant GNU Stow package support (`devenv_package_variants`) to `thomashan/dev-env`. Before `ansible-playbook`
converges, the wizard collects every decision requiring a human answer — OS/distro confirmation, Stow package enablement
and config distro/variant selection (e.g. Neovim `kickstart`, `lazyvim`, `minimal`), interactive dotfile
diff/merge/`.local` extraction, host feature flags (login shell, GUI casks, unmanaged competitor cleanup), and runtime
pin confirmation — and persists answers to `~/.config/dev-env/choices.yml`.

## Requirements & Acceptance Criteria

1. **Multi-Variant Stow Packages (`devenv_package_variants`)**:
   - Declare `devenv_package_variants` in `ansible/group_vars/all.yml` mapping configurable tools (starting with `nvim`,
     extensible to other tools) to a default variant and Stow package directories:
     - `nvim-kickstart` (`dotfiles/nvim-kickstart/.config/nvim/...` — full Kickstart config)
     - `nvim-minimal` (`dotfiles/nvim-minimal/.config/nvim/...` — lightweight built-in `vim.pack` config)
     - `nvim-lazyvim` (`dotfiles/nvim-lazyvim/.config/nvim/...` — LazyVim starter config)
   - In `ansible/roles/bootstrap/tasks/main.yml`, load `~/.config/dev-env/choices.yml` when present so human-selected
     variants, skips, and flags override defaults while CI/non-interactive runs fall back cleanly to `all.yml` defaults.
   - In `ansible/roles/dotfiles/tasks/main.yml` and `ansible/playbooks/unlink.yml`, unstow inactive variants
     (`stow --delete`) before running `stow --no-folding --restow` on the active packages, and honour
     `devenv_skip_links`.
2. **Host Interactive Pre-Ansible Wizard (`scripts/devenv_wizard.py` + `make configure`)**:
   - Implement `scripts/devenv_wizard.py` (no `.sh` files) collecting all human-required decisions before Ansible runs:
     - **OS / Distro & Package Backend Confirmation / Selection**: Detect host OS, arch, Linux `/etc/os-release` distro,
       and resolved package backend (`brew` / `apt`), display them, and require confirmation or override selection.
     - **Stow Package Enablement & Config Distro / Variant Selection**: Prompt via `fzf` (when available on TTY) or
       numbered `/dev/tty` selection for active Stow packages (`bash`, `conda`, `fish`, `nvim`, `tmux`, `zsh`) and
       multi-variant choices (`nvim`: `kickstart`, `lazyvim`, `minimal`).
     - **Interactive Dotfile Conflict Detection & Merge**: Scan target paths in `$HOME` for active Stow packages; when
       an existing non-symlink file differs from the repo's Stow file, prompt per file for `[d]` diff (`delta` /
       `diff -u`), `[m]` interactive merge (`nvim -d` / `$EDITOR -d`, then back up `$HOME/<file>`), `[l]` extract
       existing `$HOME` lines into `.local` override (`~/.bashrc.local`, `~/.bash_profile.local`, `~/.zshrc.local`,
       `~/.config/fish/conf.d/99-local.fish`), `[a]` adopt `$HOME` file into repo and back up `$HOME/<file>`, `[b]` back
       up `$HOME/<file>` and replace with repo version, or `[s]` skip (`devenv_skip_links`).
     - **Host Feature Flags & Runtime Pins**: Ask about `devenv_set_login_shell` (`chsh` to `fish`),
       `devenv_install_gui_casks` & `devenv_casks` selection (macOS), `devenv_remove_unmanaged` (only when conflicting
       unmanaged packages like `brew node`/`brew nvm` are detected), and confirm/override `devenv_python_version`,
       `devenv_conda_env_python`, and `devenv_node_default_version`.
     - **Persist Choices**: Write `~/.config/dev-env/choices.yml` (`0600` / `0644`).
   - Add `make configure` in `Makefile` and have `make install` automatically invoke the wizard on interactive TTYs
     (`[ -t 0 ]` and `CI != true`) when `~/.config/dev-env/choices.yml` does not exist yet.
3. **Documentation & Tests**:
   - Document `make configure`, OS/distro confirmation, `devenv_package_variants`, `~/.config/dev-env/choices.yml`,
     `.local` extraction, and interactive dotfile merging in `README.md`.
   - Add unit tests in `tests/test_wizard.py` and update `tests/test_manifest.py` & `tests/test_templating.py` covering
     distro detection, variant resolution, conflict detection, merge/`.local`/adopt/backup/skip flows, non-interactive
     fallback, and manifest invariants.

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/wizard.json`
- Prerequisite `holon-agentic-coder-ref-metadata-0302` (`PR #4`) is completed and merged (`c2eb50f`).

## Resolution

Planned via `intents/wizard.json`; ready for `holon flow`.
