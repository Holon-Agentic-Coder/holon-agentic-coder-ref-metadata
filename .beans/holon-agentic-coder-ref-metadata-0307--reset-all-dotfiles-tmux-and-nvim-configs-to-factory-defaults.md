---
# holon-agentic-coder-ref-metadata-0307
title: "Reset all dotfiles, tmux, and nvim configs to factory defaults"
status: completed
type: task
priority: high
tags:
  - dev-env
  - dotfiles
  - neovim
  - tmux
  - conda
created_at: 2026-11-17T03:11:00Z
updated_at: 2026-11-17T03:37:01Z
---

## Summary

Reset all tracked dotfiles and tool configurations in `thomashan/dev-env` (`tmux`, `nvim-kickstart`, `nvim-lazyvim`,
`nvim-minimal`, `conda`, `fish`, `bash`, `zsh`) to clean upstream factory defaults, stripping custom personal bindings,
paths, and opinionated overrides while keeping only the minimal structural wiring required by the Stow/Ansible runtime
bootstrap.

## Requirements & Acceptance Criteria

1. **`tmux` (`dotfiles/tmux/.config/tmux/tmux.conf`)**:
   - Replace custom options and keybindings (`default-terminal`, `history-limit`, `escape-time`, `mouse`, `base-index`,
     `|`/`-` splits, `h`/`j`/`k`/`l` pane bindings, `status-position top`, etc.) with a comment-only factory-default
     `~/.config/tmux/tmux.conf`.
2. **Neovim Kickstart (`dotfiles/nvim-kickstart/`)**:
   - Delete custom plugin files `lua/custom/plugins/diffview.lua` and `lua/custom/plugins/render-markdown.lua`, and
     remove their entries from `devenv_links` in `ansible/group_vars/all.yml`.
   - Comment out `-- require 'kickstart.plugins.neo-tree'` and `-- require 'custom.plugins'` in `init.lua` to match
     upstream `nvim-lua/kickstart.nvim` factory defaults.
   - Prune the 7 non-default entries (`diffview.nvim`, `render-markdown.nvim`, `neo-tree.nvim`, `nui.nvim`, `fzf-lua`,
     `mini.completion`, `quicker.nvim`) from `nvim-pack-lock.json`, leaving only the 19 upstream `kickstart.nvim`
     plugins, and update `README.md` (`### 5. Neovim Plugins`) accordingly.
3. **Neovim LazyVim (`dotfiles/nvim-lazyvim/`)**:
   - Update `lua/plugins/example.lua` to match upstream `LazyVim/starter` (`if true then return {} end` guard at top).
   - Add `lua/config/autocmds.lua` stub matching upstream `LazyVim/starter` and register it in
     `ansible/roles/bootstrap/tasks/main.yml` under the `lazyvim` variant links.
4. **Neovim Minimal (`dotfiles/nvim-minimal/.config/nvim/init.lua`)**:
   - Replace custom options, keymaps, and autocmds with a comment-only factory-default `init.lua`.
5. **Conda (`dotfiles/conda/.condarc`)**:
   - Reset `.condarc` to Miniforge factory defaults (`channels:\n  - conda-forge\n`), removing custom overrides
     (`channel_priority`, `auto_activate_base`, `changeps1`, `always_yes`, `notify_outdated_conda`).
6. **Shells (`dotfiles/fish/`, `dotfiles/bash/`, `dotfiles/zsh/`)**:
   - Remove host-specific paths (`$HOME/.docker/bin`, `$HOME/.lmstudio/bin`,
     `$HOME/.antigravity-ide/antigravity-ide/bin`) from `fish/config.fish`, `bash/.bashrc`, and `zsh/.zshrc`.
   - Remove custom `fish_greeting`, `EDITOR`, `VISUAL`, `PAGER`, and `GIT_PAGER` overrides from
     `fish/conf.d/00-devenv.fish` (keeping `devenv_node_default_version`, `devenv_os`/`devenv_arch`, and
     `nvm_data`/`nvm_default_version`).
   - Remove custom SDKMAN initialization blocks from `bash/.bashrc` and `zsh/.zshrc` while preserving standard `XDG_*`,
     `nvm`/`~/.local/bin`, `brew shellenv`, `conda` hook, and `.local` override hooks.
7. **Tests & Verification (`tests/test_manifest.py`, `tests/test_templating.py`)**:
   - Add manifest assertions verifying no personal paths (`.lmstudio`, `.antigravity-ide`), factory-default `tmux.conf`
     and `nvim-minimal/init.lua`, no active `custom/plugins/*.lua` beyond `init.lua` in `nvim-kickstart`, and upstream
     `if true then return {} end` guard in `nvim-lazyvim/lua/plugins/example.lua`.
   - Verify with `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/factory-defaults.json`

## Resolution

Delivered via [PR #10](https://github.com/thomashan/dev-env/pull/10) and merged into `main` (`04ce4f4` /
`04ce4f405e417f8f937ca0c96a799af728d3e68e`):

- **Key Architectural Deliverables**:
  - Reset `dotfiles/tmux/.config/tmux/tmux.conf` and `dotfiles/nvim-minimal/.config/nvim/init.lua` to comment-only
    upstream factory defaults.
  - Reset `dotfiles/nvim-kickstart/` to upstream `kickstart.nvim` defaults (removed custom `diffview.lua` and
    `render-markdown.lua`, commented out `neo-tree` and `custom.plugins` in `init.lua`, pruned `nvim-pack-lock.json` to
    the 19 core plugins, updated `devenv_links` in `ansible/group_vars/all.yml`, and updated `README.md`).
  - Updated `dotfiles/nvim-lazyvim/` (`if true then return {} end` guard in `lua/plugins/example.lua`, added
    `lua/config/autocmds.lua` stub and registered it in `ansible/roles/bootstrap/tasks/main.yml`).
  - Reset `dotfiles/conda/.condarc` to Miniforge factory defaults (`channels: [conda-forge]`) and stripped personal host
    paths, SDKMAN blocks, and shell/editor overrides from `dotfiles/fish/`, `dotfiles/bash/`, and `dotfiles/zsh/`.
- **Verification & Tests**: Updated `tests/test_manifest.py` and `tests/test_templating.py`; verified with
  `pytest -m "not network"` (`85 passed, 4 deselected`), `ruff check .`, `ansible-lint ansible/site.yml`,
  `npx prettier --check "**/*.md"`, `make check`, and all 6 GitHub Actions CI checks (`hygiene`, `make-matrix` on
  macOS/Ubuntu, `test-unit` on macOS/Ubuntu, `test-network`).
- **Holon Flow Traversal**: Completed all 5 stages (`I-1794885128-factory-defaults/_` ->
  `P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium` ->
  `E-1794885445-63c07d72-antigravity-agent-gemini-3.8-flash-medium` -> 3/3 ensemble review approval -> calibration
  `30e5ad7` with Predicted EV `86.00`, Actual EV `87.58`, $\Delta\text{EV} = +1.58$).
