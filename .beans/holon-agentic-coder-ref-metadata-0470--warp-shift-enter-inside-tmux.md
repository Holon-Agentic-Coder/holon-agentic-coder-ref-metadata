---
# holon-agentic-coder-ref-metadata-0470
title: "Fix Warp Shift+Enter swallowed by tmux C-j binding"
status: completed
type: bug
priority: normal
tags:
  - dev-env
  - macos
  - warp
  - tmux
  - wsl
parent: holon-agentic-coder-ref-metadata-0435
created_at: 2026-11-25T23:19:00Z
updated_at: 2026-11-26T05:53:00Z
---

# Fix Warp `Shift+Enter` swallowed by `tmux` `C-j` binding

## Problem

Empirically verified on macOS Warp $\rightarrow$ SSH $\rightarrow$ Ubuntu WSL `tmux 3.8` (with `extended-keys always`,
`extended-keys-format csi-u`, and `terminal-features 'xterm*:extkeys'`):

1. Outside `tmux` with Kitty keyboard protocol (`\e[>1u`), Warp sends CSI-u `\x1b[13;2u` (`1b 5b 31 33 3b 32 75`) on
   `Shift+Enter`.
2. Outside `tmux` with `modifyOtherKeys=2` (`\e[>4;2m`, which is what `tmux 3.8` sends to the outer terminal), Warp
   sends `0x0a` (`\n`, ASCII Line Feed) on `Shift+Enter`, while `Alt+Enter` sends `\x1b\r` (`1b 0d`).
3. Because `0x0a` is identical to `Ctrl-J` (`C-j`), `dotfiles/tmux/.tmux.conf` intercepts it via
   `bind-key -n C-j if-shell "$is_vim" 'send-keys C-j' 'select-pane -D'` (`vim-tmux-navigator`), swallowing
   `Shift+Enter` completely (0 bytes reach the pane).
4. Ghostty is **not** affected: macOS Ghostty works natively with `Shift+Enter` inside `tmux 3.8` once `xterm-ghostty`
   terminfo is present (Bean `0464`).

## Investigation Findings (Warp Key Mapping)

- Warp does **not** support custom keybindings that send arbitrary raw text or escape sequences (such as `\x1b\r` or
  `\x1b[13;2u`) via `~/.warp/keybindings.yaml` or `~/.warp/settings.toml`. Warp's keybinding file only maps keys to
  built-in internal Warp UI actions.
- Therefore, unlike Ghostty, a `dev-env` Stow dotfile for Warp cannot remap `Shift+Enter` to `\x1b\r` inside Warp
  itself.

## Approved Design

1. **`dotfiles/tmux/.tmux.conf`**:
   - Define `is_vim_or_agent` matching `vim`/`nvim`/`view`/`diff` and coding-agent TUIs (`claude`, `codex`, `agy`,
     `antigravity`, `opencode`, `pi`, `node`).
   - Update `bind-key -n C-j` to:
     ```tmux
     bind-key -n C-j if-shell -F '#{pane_at_bottom}' 'send-keys C-j' "if-shell \"$is_vim_or_agent\" 'send-keys C-j' 'select-pane -D'"
     ```
     so single/bottom panes forward `0x0a` (`C-j`, Warp's `Shift+Enter` under `modifyOtherKeys=2`) with zero subprocess
     overhead, top split panes running Neovim or coding-agent TUIs also forward `0x0a`, and top split panes running
     plain shells retain `select-pane -D`.
2. **`tests/test_manifest.py`**:
   - Update the `bind-key -n C-j` assertion for the new `is_vim_or_agent` + `#{pane_at_bottom}` directive while
     preserving `is_vim` checks for `C-h`/`C-k`/`C-l` and `copy-mode-vi C-j`.
3. **`tests/test_tmux_shift_enter.py`**:
   - Expand with a universal Warp + Ghostty real-`tmux` PTY matrix covering `Shift+Enter` (Ghostty `\x1b[13;2u` /
     `\x1b[27;2;13~` and Warp `\x0a` / `\x1b[13;2u`), `Alt+Enter` (`\x1b\r` and `\x1b[13;3u`), and plain `Enter` (`\r`).
   - Add a vertical split-pane PTY test proving `C-j` switches down from a plain top shell pane while forwarding `\x0a`
     when the top pane runs a coding-agent process (e.g. `claude`).

## Notes

- Target repository: `dev-env` (`git@github.com:thomashan/dev-env.git`), delivered via `holon flow`.
- Active Holon flow slug: `warp-shift-enter-tmux-cj` (`antigravity-agent` / `gemini-4-neon`).
- Earlier Ghostty flow (`ghostty-shift-enter-esc-cr`) was stopped and cleaned up on 2026-11-26 after verifying Ghostty
  works natively and the `0x0a` / `C-j` behaviour was Warp-specific.
- Related beans: Bean `0344`, Bean `0435`, Bean `0464`.

## Resolution

Delivered via [PR #45](https://github.com/thomashan/dev-env/pull/45) and merged into `main` (`6a50860`,
`2026-11-26T05:49:19Z`):

- **Key Deliverables**:
  - `dotfiles/tmux/.tmux.conf`: added `is_vim_or_agent` matching Vim/Neovim and coding-agent TUIs and updated
    `bind-key -n C-j` to forward `C-j` (`0x0a`, Warp `Shift+Enter` under `modifyOtherKeys=2`) when `#{pane_at_bottom}`
    is set or the active pane runs Vim/an agent TUI, while preserving `select-pane -D` for plain top split panes.
  - `tests/test_manifest.py`: updated `bind-key -n C-j` manifest assertions for `#{pane_at_bottom}` and
    `is_vim_or_agent`, while keeping `is_vim` assertions intact for `C-h`/`C-k`/`C-l` and `copy-mode-vi C-j`.
  - `tests/test_tmux_shift_enter.py`: expanded the real-`tmux` PTY matrix covering Warp and Ghostty (`Shift+Enter`,
    `Alt+Enter`, plain `Enter`) plus vertical split-pane tests verifying `C-j` pane navigation vs forwarding `\x0a` to
    coding-agent processes.
- **Verification & Reviews**: 7/7 GitHub Actions CI checks green; 3/3 Stage 4 consensus review approval.
- **Holon Flow Traversal**: Completed all 5 stages (Intent $\rightarrow$ Plan $\rightarrow$ Execute $\rightarrow$ Review
  Loop $\rightarrow$ Calibration); Stage 5 calibration EV: `96.46` predicted / `99.30` actual / `+2.84` delta (`0.00`
  bug EV drag).
