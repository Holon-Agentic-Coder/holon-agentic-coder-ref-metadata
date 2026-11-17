---
id: "0312"
title: "Ensure nvm-managed node precedes Homebrew in fish PATH"
status: completed
created_at: 2026-11-17T15:49:00+11:00
updated_at: 2026-11-17T16:06:00+11:00
tags:
  - dev-env
  - fish
  - node
  - path
  - bugfix
---

# 0312 - Ensure nvm-managed node precedes Homebrew in fish PATH

## Problem Statement

When running `make converge` or `make install` on macOS with Homebrew installed, Ansible task:
`TASK [node : Assert nvm-managed node wins on PATH]` fails with:

```text
Action failed: node did not resolve through nvm. Resolved:
/opt/homebrew/bin/node | v26.13.1
Likely cause: another PATH entry (brew node, ~/.local/bin/node from an
agent runtime) precedes $XDG_DATA_HOME/nvm/current/bin.
```

In `dotfiles/fish/.config/fish/config.fish`, `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` is currently invoked
before `brew shellenv | source`. However, `brew shellenv` runs:
`fish_add_path --global --move --path "/opt/homebrew/bin" "/opt/homebrew/sbin"`, which uses `--move` to move
`/opt/homebrew/bin` to the front of `$PATH`, overtaking the nvm-managed node path.

## Scope of Changes

1. **`dotfiles/fish/.config/fish/config.fish`**:
   - Reorder PATH configurations so Homebrew environment (`brew shellenv | source`) and system tool paths are sourced
     before `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`.
   - By prepending and moving `$XDG_DATA_HOME/nvm/current/bin` after Homebrew initializes, nvm-managed node is
     guaranteed to win on PATH in login and interactive shells.
2. **Tests & Validation**:
   - Run `uv run pytest -m "not network"` to ensure manifest and templating tests pass.
   - Verify `fish -l -c "which node"` resolves to `$HOME/.local/share/nvm/current/bin/node`.

## Resolution

- Reordered PATH initialization in `dotfiles/fish/.config/fish/config.fish` so Homebrew environment initializes prior to
  nvm path prepending.
- Updated `test_node_bin_is_first_on_path` in `tests/test_manifest.py` ensuring the relative order invariant is tested.
- Merged via PR #15 (commit `ea61908`).
