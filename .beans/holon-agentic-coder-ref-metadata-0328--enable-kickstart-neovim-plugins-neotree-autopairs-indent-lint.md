---
id: "0328"
title: "Enable neo-tree, autopairs, indent_line, and lint plugins in kickstart Neovim configuration"
status: todo
created_at: 2026-11-18T14:08:00+11:00
updated_at: 2026-11-18T14:10:00+11:00
tags:
  - dev-env
  - neovim
  - dotfiles
  - plugins
  - feature
---

# 0328 - Enable neo-tree, autopairs, indent_line, and lint plugins in kickstart Neovim configuration

## Problem Statement

In the `nvim-kickstart` dotfiles configuration, essential editing and navigation plugins are defined under
`lua/kickstart/plugins/` but left commented out by default in `init.lua`:

```lua
-- require 'kickstart.plugins.debug'
-- require 'kickstart.plugins.indent_line'
-- require 'kickstart.plugins.lint'
-- require 'kickstart.plugins.autopairs'
-- require 'kickstart.plugins.neo-tree'
```

Without these enabled:

1. Pressing `\` does nothing because `neo-tree` is never loaded.
2. Parentheses, brackets, and quotes do not auto-close (`nvim-autopairs`).
3. Indentation guide scopes on blank and nested lines are absent (`indent-blankline.nvim`).
4. Filetype linting on write and buffer events is disabled (`nvim-lint`).

## Scope of Changes

1. **Enable Plugins in `init.lua`**:
   - In `dotfiles/nvim-kickstart/.config/nvim/init.lua`, uncomment the following 4 plugin requirements:
     ```lua
     require 'kickstart.plugins.indent_line'
     require 'kickstart.plugins.lint'
     require 'kickstart.plugins.autopairs'
     require 'kickstart.plugins.neo-tree'
     ```
   - Keep `debug` commented out for now as an optional heavyweight debugging setup.

2. **Lockfile & Plugin Synchronization**:
   - Update `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json` to lock revisions for:
     - `nvim-neo-tree/neo-tree.nvim`
     - `MunifTanjim/nui.nvim`
     - `windwp/nvim-autopairs`
     - `lukas-reineke/indent-blankline.nvim`
     - `mfussenegger/nvim-lint`
   - Verify headless startup and plugin synchronization (`make nvim-sync` / `nvim --headless`).

3. **Tests & Verification**:
   - Update any templating or dotfiles manifest tests in `tests/test_templating.py` and `tests/test_manifest.py`.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.
