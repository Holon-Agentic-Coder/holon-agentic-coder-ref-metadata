---
# holon-agentic-coder-ref-metadata-0302
title: "Use GNU Stow for managing dotfiles in dev-env"
status: completed
type: task
priority: high
tags:
  - dev-env
  - dotfiles
  - stow
  - ansible
created_at: 2026-11-16T00:59:45Z
updated_at: 2026-11-16T02:22:00Z
---

## Summary

Convert `/Users/thomashan/git/dev-env` to a bare `.git` + worktree layout (`git/dev-env/.git`, `git/dev-env/main`,
`git/dev-env/<worktree>`), make GNU Stow an explicit prerequisite for dotfile management, move all dotfiles in
`thomashan/dev-env` into per-tool Stow packages (`dotfiles/<pkg>/...`) managed via `stow --no-folding` (including the
user's updated `~/.config/nvim/` config and `.bashrc` / `.bash_profile` / `.zshrc` with `.local` override hooks), and
explicitly document every prerequisite and package in `README.md` with manifest test verification.

## Requirements & Acceptance Criteria

1. **Bare `.git` + Worktrees Layout (Host Repo)**:
   - `/Users/thomashan/git/dev-env/.git` is the bare repository; `/Users/thomashan/git/dev-env/main` is the `main`
     worktree; all sibling worktrees (including `/Users/thomashan/git/dev-env/flow-stow`) live inside
     `/Users/thomashan/git/dev-env/`.
2. **Stow Prerequisite & Package Manifest**:
   - Add `stow` to `devenv_packages_core` in `ansible/group_vars/all.yml` and map `stow: stow` in
     `ansible/vars/pkg_brew.yml` and `ansible/vars/pkg_apt.yml`.
   - Probe `stow` in `Makefile`'s `make check` and require `stow` on `PATH` for `make dotfiles` and `make unlink`.
   - Assert `stow` is present at the start of `ansible/roles/dotfiles/tasks/main.yml` and
     `ansible/playbooks/unlink.yml`.
3. **Per-Tool Stow Package Layout (`dotfiles/<pkg>/...`)**:
   - Move all dotfiles into per-tool Stow packages (`bash`, `conda`, `fish`, `nvim`, `tmux`, `zsh`) with zero files
     directly under `dotfiles/`:
     - `dotfiles/bash/.bashrc`, `dotfiles/bash/.bash_profile` (with `.local` override hooks and multi-OS `Darwin)` /
       `Linux)` guards)
     - `dotfiles/conda/.condarc`
     - `dotfiles/fish/.config/fish/{config.fish,fish_plugins,conf.d/00-devenv.fish}`
     - `dotfiles/nvim/.config/nvim/` (`init.lua`, `nvim-pack-lock.json`, `.stylua.toml`, `lua/custom/plugins/*.lua`,
       `lua/kickstart/**/*.lua` copied from host `.cache/host-nvim/`)
     - `dotfiles/tmux/.config/tmux/tmux.conf`
     - `dotfiles/zsh/.zshrc` (with `.zshrc.local` override hook and multi-OS `Darwin)` / `Linux)` guards)
   - Declare `devenv_stow_packages: [bash, conda, fish, nvim, tmux, zsh]` in `ansible/group_vars/all.yml` and list all
     managed files in `devenv_links`.
4. **Ansible `dotfiles` Role & `unlink.yml`**:
   - Use `stow --no-folding --restow` in `ansible/roles/dotfiles/tasks/main.yml` after validating `devenv_links`,
     backing up unmanaged real files, and cleaning stale symlinks.
   - Update `ansible/playbooks/unlink.yml` to use `stow --delete`.
   - Ensure post-condition assertions handle GNU Stow's relative symlinks cleanly.
5. **Explicit Prerequisites & Packages Documentation (`README.md`)**:
   - Explicitly list all prerequisites and bootstrap tools (`GNU Make`, `git`, `curl`, `apt-get`, `uv`, `ansible-core`,
     `ansible-lint`, `community.general`, `stow`, `Homebrew`, optional `docker-desktop`), all 22 core CLI packages with
     `brew` & `apt` mappings, all runtimes & `uv` tools (`CPython 3.13`, `ruff`, `pre-commit`, `Miniforge3` + `dev` env,
     `Node.js 22.23.2`), all Fish & 26 locked Neovim plugins, unmanaged duplicates (`nvm`, `node`), and `.local`
     override hooks.
   - Add tests in `tests/test_manifest.py` verifying `README.md` names every logical package, `uv` tool, Fish plugin,
     and Neovim plugin.
6. **References, `.gitignore`, World Docs, and Tests**:
   - Update path references in `ansible/roles/{node,neovim,conda}/tasks/main.yml`,
     `dotfiles/fish/.config/fish/config.fish`, `.gitignore`, `holon-config/world/constraints.md`, and
     `holon-config/world/ruleset.md`.
   - Update `tests/test_manifest.py` and `tests/test_templating.py` for multi-OS shell guards, `gh '...'` Neovim plugin
     lockfile checks, `stow` prerequisite checks, `devenv_stow_packages` parity, and `devenv_links` coverage.
7. **Verification**:
   - `uv run --extra test pytest -m "not network"`
   - `uv run ruff check .`
   - `uv run --extra test ansible-lint ansible/site.yml`
   - `npx prettier --check "**/*.md"`
   - `make check`

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Flow Worktree: `/Users/thomashan/git/dev-env/flow-stow`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/stow.json`

## Resolution

Delivered via [PR #4](https://github.com/thomashan/dev-env/pull/4) and merged into `main` (`c2eb50f`):

- **Key Architectural Deliverables**:
  - Converted `/Users/thomashan/git/dev-env` to bare `.git` (`/Users/thomashan/git/dev-env/.git`) + worktree layout
    (`/Users/thomashan/git/dev-env/main` and sibling worktrees).
  - Enforced `stow` as a prerequisite across `devenv_packages_core` (`pkg_brew.yml` + `pkg_apt.yml`), `Makefile`
    (`check`, `dotfiles`, `unlink`), `ansible/roles/dotfiles/tasks/main.yml`, and `ansible/playbooks/unlink.yml`.
  - Migrated all dotfiles into 6 per-tool Stow packages (`bash`, `conda`, `fish`, `nvim`, `tmux`, `zsh`) managed via
    `stow --no-folding --restow` / `stow --delete`, including the full Kickstart `nvim` configuration (26 locked plugins
    in `nvim-pack-lock.json`) and multi-OS `.bashrc`, `.bash_profile`, and `.zshrc` configs with `.local` override
    hooks.
  - Explicitly documented all prerequisites, bootstrap tools, 22 core CLI packages, runtimes, Fish plugins, Neovim
    plugins, and `devenv_packages_remove` items in `README.md` with manifest test verification in
    `tests/test_manifest.py`.
- **Verification & Tests**:
  - 3/3 unanimous ensemble review approval (`APPROVED`, 0 open findings).
  - All 6 GitHub Actions CI checks passed (`Code Hygiene & Lint`, `Make Check (ubuntu-latest)`,
    `Make Check (macos-latest)`, `Network Upstream Asset Tests`, `Unit Tests (ubuntu-latest)`,
    `Unit Tests (macos-latest)`).
- **Holon Flow Traversal**:
  - **Intent**: `I-1794792028-stow/_`
  - **Plan**: `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Execution**:
    `I-1794792028-stow/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium/E-1794792504-cd8c00d3-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Calibration**: `plans/P-1794792046-6a25eec5-antigravity-agent-gemini-3.8-flash-medium_calibration.md` included in
    PR diff (Predicted EV `78.87`, Actual EV `-12.46`, Delta `-91.33`).
