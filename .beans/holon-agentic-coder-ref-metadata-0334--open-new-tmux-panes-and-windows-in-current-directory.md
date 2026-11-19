---
id: "0334"
title: "Open new tmux panes and windows in the current pane's working directory"
status: in-progress
created_at: 2026-11-20T09:56:00+11:00
updated_at: 2026-11-20T09:56:00+11:00
tags:
  - dev-env
  - tmux
  - dotfiles
  - ux
  - feature
---

# 0334 - Open new tmux panes and windows in the current pane's working directory

## Problem Statement

When creating a new tmux split pane (`"` or `%`) or opening a new window (`c`), tmux defaults to opening the shell in
`$HOME` rather than the working directory of the current pane. Users working inside a repository or project directory
lose their working directory every time they split a pane or open a window.

## Scope of Changes

1. **Preserve Current Pane Working Directory (`dotfiles/tmux/.tmux.conf`)**:
   - Bind `"`, `%`, and `c` with `-c "#{pane_current_path}"`:
     ```tmux
     # Open new panes and windows in the current pane's working directory
     bind-key '"' split-window -v -c "#{pane_current_path}"
     bind-key % split-window -h -c "#{pane_current_path}"
     bind-key c new-window -c "#{pane_current_path}"
     ```

2. **Tests & Verification (`tests/test_toolchain.py`)**:
   - Add a unit test in `tests/test_toolchain.py` (keeping `tests/test_manifest.py` under 1,000 lines) verifying that
     `dotfiles/tmux/.tmux.conf` binds `"`, `%`, and `c` with `-c "#{pane_current_path}"`.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.
