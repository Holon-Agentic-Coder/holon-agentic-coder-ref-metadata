---
# holon-agentic-coder-ref-metadata-0346
title: "Merge repository devenv_stow_packages with stale choices.yml and add upgrade regression tests"
status: in-progress
type: bug
priority: high
tags:
  - dev-env
  - ansible
  - dotfiles
  - stow
  - tests
created_at: 2026-11-20T23:52:00+11:00
updated_at: 2026-11-20T23:52:00+11:00
---

## Problem

Running `make install` in `dev-env` after PR #31 added the new `ghostty` GNU Stow package failed at
`dotfiles : Assert the link manifest is fully satisfied`:

- `ansible/roles/bootstrap/tasks/main.yml` loads `~/.config/dev-env/choices.yml` via `include_vars`, which overwrites
  `devenv_stow_packages` with the stale list saved on an earlier run (`[bash, conda, fish, nvim-kickstart, tmux, zsh]` —
  missing `ghostty`).
- Meanwhile `devenv_links` is not stored in `choices.yml` and comes fresh from `ansible/group_vars/all.yml` (which
  includes `dotfiles/ghostty/.config/ghostty/config.ghostty`).
- As a result, `stow` never runs for newly added repository Stow packages on existing machines, and the post-stow
  symlink assertion fails.
- CI and existing unit tests missed this because CI runs with no pre-existing `choices.yml` and only runs
  `make check-mode` (which skips the post-stow symlink assertion), and no test simulated upgrading with a stale
  `choices.yml`.

## Action

Through the Holon flow on `dev-env`:

- In `ansible/roles/bootstrap/tasks/main.yml`, snapshot the repository's declared `devenv_stow_packages` (e.g.
  `devenv_repo_stow_packages`) before `include_vars` loads `~/.config/dev-env/choices.yml`, and union it with the loaded
  `devenv_stow_packages` when resolving active Stow packages (still subtracting `devenv_inactive_packages` for
  non-selected Neovim variants and preserving `devenv_skip_links` omission in the `dotfiles` role).
- Add regression tests in `tests/` that run in `uv run --extra test pytest`:
  1. A real `ansible-playbook` test (using a temporary `HOME` pre-populated with a stale `~/.config/dev-env/choices.yml`
     whose `devenv_stow_packages` omits newly added repo packages such as `ghostty` — and testing both default and
     `nvim: minimal` variants plus `devenv_skip_links`) proving `bootstrap` resolves every package required by
     `devenv_links` and, whenever `stow` is installed on `PATH`, proving a real non-check-mode `--tags dotfiles`
     converge succeeds and creates every expected symlink (including `ghostty`).
  2. A verbatim Jinja `templar` test in `tests/test_templating.py` exercising the exact `Resolve active stow packages`
     expression against a stale `choices.yml` package list.
