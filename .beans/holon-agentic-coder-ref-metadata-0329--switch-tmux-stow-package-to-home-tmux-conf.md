---
id: "0329"
title: "Switch tmux Stow package from ~/.config/tmux/tmux.conf to ~/.tmux.conf"
status: completed
created_at: 2026-11-18T16:56:00+11:00
updated_at: 2026-11-18T18:54:00+11:00
tags:
  - dev-env
  - tmux
  - dotfiles
  - stow
  - bugfix
---

# 0329 - Switch tmux Stow package from ~/.config/tmux/tmux.conf to ~/.tmux.conf

## Problem Statement

Currently `dotfiles/tmux/` stores its configuration at `dotfiles/tmux/.config/tmux/tmux.conf`, which GNU Stow links to
`~/.config/tmux/tmux.conf`. This causes three practical issues:

1. **Silent Shadowing**: `tmux` checks `~/.tmux.conf` before `~/.config/tmux/tmux.conf`. Any pre-existing `~/.tmux.conf`
   on a machine completely shadows and overrides the stowed `~/.config/tmux/tmux.conf`.
2. **Wizard & Backup Blind Spot**: Because `devenv_links` in `ansible/group_vars/all.yml` only lists
   `{{ devenv_home }}/.config/tmux/tmux.conf`, neither the interactive wizard nor the `dotfiles` Ansible role detects,
   diffs/merges, or backs up a pre-existing `~/.tmux.conf`.
3. **Reload Friction**: Standard reload commands such as `<prefix> :source ~/.tmux.conf` either load a stale unlinked
   file or fail with `no such file or directory` on hosts where only `~/.config/tmux/tmux.conf` was stowed.

## Scope of Changes

1. **Relocate the Stow Package File**:
   - Move `dotfiles/tmux/.config/tmux/tmux.conf` to `dotfiles/tmux/.tmux.conf` and update its header comment
     accordingly.

2. **Update Link Manifest (`ansible/group_vars/all.yml`)**:
   - Update `devenv_links` from `dotfiles/tmux/.config/tmux/tmux.conf` -> `{{ devenv_home }}/.config/tmux/tmux.conf` to
     `dotfiles/tmux/.tmux.conf` -> `{{ devenv_home }}/.tmux.conf`.

3. **Clean Up Legacy Symlink (`ansible/roles/dotfiles/tasks/main.yml`, `ansible/playbooks/unlink.yml`)**:
   - Ensure any legacy symlink at `{{ devenv_home }}/.config/tmux/tmux.conf` pointing into the repository is removed
     during convergence/unlink so existing installations do not retain a broken symlink after
     `dotfiles/tmux/.config/tmux/tmux.conf` moves.

4. **Documentation (`README.md`)**:
   - Update references from `~/.config/tmux/tmux.conf` to `~/.tmux.conf`.

5. **Tests & Verification (`tests/test_manifest.py`)**:
   - Update `test_tmux_config_uses_the_xdg_path` (rename/invert to verify `~/.tmux.conf` is stowed instead of the XDG
     path) and update `test_tmux_conf_smart_pane_switching` to read `dotfiles/tmux/.tmux.conf`.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Resolution

- Implemented via Holon flow `tmux-home-conf` (Bean 0329).
- Pull Request #27: [https://github.com/thomashan/dev-env/pull/27](https://github.com/thomashan/dev-env/pull/27) merged
  to `main` (`12e4831`).
- Relocated `dotfiles/tmux/.config/tmux/tmux.conf` to `dotfiles/tmux/.tmux.conf`, updated `devenv_links`, added legacy
  XDG symlink cleanup in `ansible/roles/dotfiles/tasks/main.yml` and `ansible/playbooks/unlink.yml`, and updated
  `README.md` and `tests/test_manifest.py`.
- Main branch fast-forwarded and flow worktree/branches pruned.
