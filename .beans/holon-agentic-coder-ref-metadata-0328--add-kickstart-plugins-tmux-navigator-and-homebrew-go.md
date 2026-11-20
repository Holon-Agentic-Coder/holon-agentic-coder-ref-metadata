---
id: "0328"
title: "Add core development enhancements: Neovim plugins, seamless tmux navigation, and Homebrew Go toolchain"
status: completed
created_at: 2026-11-18T14:08:00+11:00
updated_at: 2026-11-18T15:42:00+11:00
tags:
  - dev-env
  - neovim
  - tmux
  - golang
  - homebrew
  - dotfiles
  - plugins
  - feature
---

# 0328 - Add core development enhancements: Neovim plugins, seamless tmux navigation, and Homebrew Go toolchain

## Problem Statement

Several key productivity and language development capabilities are missing or commented out in `dev-env`:

1. **Kickstart Neovim Plugins Disabled**: Essential editing and navigation plugins under `lua/kickstart/plugins/` are
   commented out by default in `dotfiles/nvim-kickstart/.config/nvim/init.lua`:
   - `neo-tree` (file explorer sidebar, bound to `\`)
   - `autopairs` (auto-closing quotes, brackets, and parentheses via `nvim-autopairs`)
   - `indent_line` (indentation guides and scope indicators via `indent-blankline.nvim`)
   - `lint` (asynchronous filetype linting on save via `nvim-lint`)

2. **No Seamless Tmux-Neovim Navigation**: Currently, navigating between Neovim splits uses `<C-h,j,k,l>` internally,
   but cannot cross split boundaries into tmux panes. In tmux, moving panes requires the prefix key `<C-b> <arrow>`,
   breaking seamless directional navigation between editor splits and terminal panes.

3. **Go Language Toolchain Missing**: The Go development toolchain is not currently installed or configured. Go is
   available as an official formula via Homebrew (`go`) for both macOS and Linux, providing native `GOTOOLCHAIN` support
   (Go 1.21+) for automatic project version switching without external wrapper complexity.

## Scope of Changes

1. **Enable Plugins in `init.lua`**:
   - In `dotfiles/nvim-kickstart/.config/nvim/init.lua`, uncomment:
     ```lua
     require 'kickstart.plugins.indent_line'
     require 'kickstart.plugins.lint'
     require 'kickstart.plugins.autopairs'
     require 'kickstart.plugins.neo-tree'
     ```
   - Keep `debug` commented out for now as an optional heavyweight debugging setup.

2. **Add Seamless Tmux-Neovim Navigation (`vim-tmux-navigator`)**:
   - **In Neovim** (`dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/tmux_navigator.lua`):
     - Add `christoomey/vim-tmux-navigator` via `vim.pack.add`:
       ```lua
       vim.pack.add { 'https://github.com/christoomey/vim-tmux-navigator' }
       vim.keymap.set('n', '<C-h>', '<cmd>TmuxNavigateLeft<cr>', { desc = 'Navigate window/pane left' })
       vim.keymap.set('n', '<C-j>', '<cmd>TmuxNavigateDown<cr>', { desc = 'Navigate window/pane down' })
       vim.keymap.set('n', '<C-k>', '<cmd>TmuxNavigateUp<cr>', { desc = 'Navigate window/pane up' })
       vim.keymap.set('n', '<C-l>', '<cmd>TmuxNavigateRight<cr>', { desc = 'Navigate window/pane right' })
       ```
     - Require `kickstart.plugins.tmux_navigator` in `init.lua`.
   - **In Tmux** (`dotfiles/tmux/.config/tmux/tmux.conf`):
     - Add smart pane switching bindings for `C-h`, `C-j`, `C-k`, `C-l` that detect whether the active pane is running
       Neovim:
       ```tmux
       is_vim="ps -o state= -o comm= -t '#{pane_tty}' | grep -iqE '^[^TXZ ]+ +(\\S+\\/)?g?(view|l?n?vim?x?|fzf)(diff)?$'"
       bind-key -n 'C-h' if-shell "$is_vim" 'send-keys C-h'  'select-pane -L'
       bind-key -n 'C-j' if-shell "$is_vim" 'send-keys C-j'  'select-pane -D'
       bind-key -n 'C-k' if-shell "$is_vim" 'send-keys C-k'  'select-pane -U'
       bind-key -n 'C-l' if-shell "$is_vim" 'send-keys C-l'  'select-pane -R'

       bind-key -T copy-mode-vi 'C-h' select-pane -L
       bind-key -T copy-mode-vi 'C-j' select-pane -D
       bind-key -T copy-mode-vi 'C-k' select-pane -U
       bind-key -T copy-mode-vi 'C-l' select-pane -R
       ```

3. **Install Go via Homebrew on macOS and Linux**:
   - Add `go` to logical core packages in `ansible/group_vars/all.yml` (`devenv_packages_core`) and `pkg_brew.yml` /
     `pkg_apt.yml`.
   - On Linux (`os_Linux.yml`), ensure `go` is skipped in `apt` via `devenv_pkg_skip: [neovim, go]` and installed via
     Homebrew (`community.general.homebrew: name: go`) using `devenv_brew_bin`.
   - Ensure `$HOME/go/bin` is exported in `PATH` across Bash, Zsh, and Fish shell startup files so user-installed Go
     binaries are immediately executable.

4. **Lockfile & Plugin Synchronization**:
   - Update `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json` to lock revisions for:
     - `nvim-neo-tree/neo-tree.nvim`
     - `MunifTanjim/nui.nvim`
     - `windwp/nvim-autopairs`
     - `lukas-reineke/indent-blankline.nvim`
     - `mfussenegger/nvim-lint`
     - `christoomey/vim-tmux-navigator`
   - Verify headless startup and plugin synchronization (`make nvim-sync` / `nvim --headless`).

5. **Tests & Verification**:
   - Update tests in `tests/test_templating.py` and `tests/test_manifest.py`.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Resolution

- Implemented via Holon flow `dev-enhancements` (Bean 0328).
- Pull Request #26: [https://github.com/thomashan/dev-env/pull/26](https://github.com/thomashan/dev-env/pull/26) merged
  to `main` (`4f1fa9f`).
- Enabled Kickstart plugins (`indent_line`, `lint`, `autopairs`, `neo-tree`), added `vim-tmux-navigator` in Neovim with
  matching `tmux.conf` smart pane-switching bindings, added Homebrew `go` installation and `$HOME/go/bin` `PATH` export
  across shells, and synchronized `nvim-pack-lock.json`.
- Main branch fast-forwarded to `4f1fa9f`, `delete_branch_on_merge` enabled on `thomashan/dev-env`, and all stale
  local/remote branches and flow worktree pruned.
