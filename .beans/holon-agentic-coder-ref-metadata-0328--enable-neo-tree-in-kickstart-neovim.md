---
id: "0328"
title: "Enable neo-tree file explorer in kickstart Neovim configuration"
status: todo
created_at: 2026-11-18T14:08:00+11:00
updated_at: 2026-11-18T14:08:00+11:00
tags:
  - dev-env
  - neovim
  - dotfiles
  - plugins
  - feature
---

# 0328 - Enable neo-tree file explorer in kickstart Neovim configuration

## Problem Statement

In the `nvim-kickstart` dotfiles configuration, the `neo-tree` file explorer plugin is installed in
`lua/kickstart/plugins/neo-tree.lua` with keymapping `\` (`<Cmd>Neotree reveal<CR>`), but it is commented out by default
in `init.lua`:

```lua
-- require 'kickstart.plugins.neo-tree'
```

When users press `\` inside Neovim, nothing happens because the module is never required, leaving users without a
built-in file tree browser out of the box.

## Scope of Changes

1. **Enable Neo-Tree in `init.lua`**:
   - In `dotfiles/nvim-kickstart/.config/nvim/init.lua`, uncomment:
     ```lua
     require 'kickstart.plugins.neo-tree'
     ```
2. **Lockfile & Plugin Sync**:
   - Update `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json` to lock `neo-tree.nvim` and its dependencies
     (`nui.nvim`, `plenary.nvim`).
   - Ensure `make nvim-sync` (or `nvim --headless`) can resolve and sync plugins cleanly.
3. **Tests & Verification**:
   - Run unit tests (`uv run --extra test pytest -m "not network"`).
   - Run linter and formatting checks (`uv run ruff check .`, `npx prettier --check "**/*.md"`).
