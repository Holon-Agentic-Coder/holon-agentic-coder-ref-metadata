---
id: "0330"
title: "Auto-install markdownlint via mason-tool-installer on Neovim startup and guard lint.try_lint"
status: in-progress
created_at: 2026-11-18T18:54:00+11:00
updated_at: 2026-11-18T18:54:00+11:00
tags:
  - dev-env
  - neovim
  - dotfiles
  - mason
  - lint
  - bugfix
---

# 0330 - Auto-install markdownlint via mason-tool-installer on Neovim startup and guard lint.try_lint

## Problem Statement

Opening a Markdown file in `nvim-kickstart` (for example from `neo-tree`) triggers `nvim-lint` on `BufEnter` and fails
with:

```text
Vim(append):Error running markdownlint: ENOENT: no such file or directory
```

This happens because `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua` configures
`markdown = { 'markdownlint' }` and invokes `lint.try_lint()`, while `markdownlint` is missing from `ensure_installed`
in `mason-tool-installer.nvim` (`dotfiles/nvim-kickstart/.config/nvim/init.lua`). Furthermore, `lint.try_lint()` does
not pass `{ ignore_errors = true }`, so opening a Markdown buffer during the brief window before Mason finishes
downloading `markdownlint` on first startup still throws `ENOENT`.

## Scope of Changes

1. **Auto-install `markdownlint` on Neovim Startup (`dotfiles/nvim-kickstart/.config/nvim/init.lua`)**:
   - Add `'markdownlint'` to `ensure_installed` for `mason-tool-installer.nvim` so Mason automatically installs
     `markdownlint` on `VimEnter` whenever it is missing.

2. **Guard `nvim-lint` Against Missing Linter Binaries
   (`dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua`)**:
   - Update `lint.try_lint()` to `lint.try_lint(nil, { ignore_errors = true })` so missing linter executables never
     raise `ENOENT` on `BufEnter`, `BufWritePost`, or `InsertLeave` (including during initial background installation).

3. **Tests & Verification (`tests/test_manifest.py`)**:
   - Add unit test assertions verifying `'markdownlint'` is present in `ensure_installed` in
     `dotfiles/nvim-kickstart/.config/nvim/init.lua` and `ignore_errors = true` is passed to `lint.try_lint` in
     `dotfiles/nvim-kickstart/.config/nvim/lua/kickstart/plugins/lint.lua`.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.
