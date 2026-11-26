---
# holon-agentic-coder-ref-metadata-0435
title: "dev-env improvements and cross-platform fixes"
status: in-progress
type: epic
priority: high
tags:
  - dev-env
  - macos
  - windows
  - wsl
  - tmux
created_at: 2026-11-24T23:12:00Z
updated_at: 2026-11-26T05:53:00Z
---

Generic ongoing umbrella bean for improvements, bug fixes, and cross-platform parity updates to the `dev-env` repository
(`git@github.com:thomashan/dev-env.git`, canonical worktree `/Users/thomashan/git/dev-env/main`) across macOS and
Windows/WSL.

## Tracked Changes

| Item | Summary                                                                                            | Intent File                                         | PR / Status                                                                                                                                                                  |
| ---- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Restore `Shift+Enter` newline forwarding in `tmux` for Claude Code + PTY regression test           | `todo/intent-0435-tmux-shift-enter-extkeys.json`    | [PR #41](https://github.com/thomashan/dev-env/pull/41) (merged `2026-11-25T04:03:06Z`, commit `605559f`)                                                                     |
| 2    | Enable `tmux` `focus-events` (`set -g focus-events on`) for Neovim `autoread`/`FocusGained` + test | `todo/intent-0435-tmux-focus-events-on.json`        | [PR #42](https://github.com/thomashan/dev-env/pull/42) (merged `2026-11-26T03:46:21Z`, commit `649168b`, EV `94.83` predicted / `96.62` actual / `+1.79` delta)              |
| 3    | Install `xterm-ghostty` terminfo on Ubuntu WSL and Linux hosts                                     | `todo/intent-0464-ubuntu-wsl-ghostty-terminfo.json` | [PR #43](https://github.com/thomashan/dev-env/pull/43) (merged `2026-11-26T00:03:54Z`, commit `77a7910`, Bean `0464`)                                                        |
| 4    | Fix Warp `Shift+Enter` (`0x0a`) swallowed by `tmux` `C-j` binding + split-pane PTY test            | `todo/intent-0470-warp-shift-enter-tmux-cj.json`    | [PR #45](https://github.com/thomashan/dev-env/pull/45) (merged `2026-11-26T05:49:19Z`, commit `6a50860`, Bean `0470`, EV `96.46` predicted / `99.30` actual / `+2.84` delta) |

## Item 1: `Shift+Enter` Multiline Newline Regression & Automated PTY Test (macOS & Windows/WSL)

- **Reported symptom**: Pressing `Shift+Enter` on macOS and Windows submits instead of inserting a new line in the
  Claude Code agent.
- **Confirmed regression (`2026-11-18`, PR #27)**: Before PR #27 (`I-1794983648-tmux-home-conf`, `92a78b8`), the user's
  pre-existing `~/.tmux.conf` (archived in `~/.local/share/dev-env/backup/20261118184638/Users__thomashan__.tmux.conf`)
  explicitly configured:
  - `set -g extended-keys on`
  - `set -g extended-keys-format csi-u` When Stow began managing `~/.tmux.conf` with `dotfiles/tmux/.tmux.conf`, those
    extended-key settings were dropped.
- **Verified fix (live `tmux 3.8` PTY probe)**:
  - `set -s extended-keys always` (forwards modified keys such as `Shift+Enter` even when an inner TUI such as Claude
    Code inside `tmux` does not emit the xterm `modifyOtherKeys` activation handshake, while keeping plain `Enter` as
    `\r` and preserving bracketed multi-line paste).
  - `set -sq extended-keys-format csi-u` (selects CSI-u `\x1b[13;2u` on `tmux >= 3.5` while `-q` suppresses unknown
    option errors on Ubuntu 24.04 / WSL `tmux 3.4`, which cleanly falls back to `\x1b[27;2;13~`).
  - `set -as terminal-features 'xterm*:extkeys'` (advertises `extkeys` for `xterm-256color`, `xterm-ghostty`, etc.).
- **Automated regression coverage**: Static checks on `dotfiles/tmux/.tmux.conf` and
  `dotfiles/ghostty/.config/ghostty/config.ghostty` plus live isolated-socket `tmux` PTY tests across
  `TERM=xterm-256color` and `TERM=xterm-ghostty`, with `tmux` installed in `.github/workflows/test-unit.yml` on both
  `ubuntu-latest` and `macos-latest`.

## Item 2: Enable `tmux` `focus-events` (`set -g focus-events on`)

- **Reported issue**: Neovim `:checkhealth` warns: `tmux focus-events off` —
  `add 'set -g focus-events on' to ~/.tmux.conf and reattach for autoread / FocusGained`.
- **Confirmed regression (`2026-11-18`, PR #27)**: Pre-PR-#27 backup
  `~/.local/share/dev-env/backup/20261118184638/Users__thomashan__.tmux.conf` configured
  `set -g focus-events on # 'autoread' and FocusGained`, which was dropped alongside `extended-keys` when Stow replaced
  `~/.tmux.conf` with `dotfiles/tmux/.tmux.conf`.
- **Planned fix & regression test (queued behind Item 1)**:
  - Add `set -g focus-events on` to `dotfiles/tmux/.tmux.conf`.
  - Add a static config check plus a live `tmux show-options -g focus-events` regression check in `dev-env` tests.
  - Queued until Item 1 (`tmux-shift-enter-extkeys`) merges so two concurrent flows do not conflict on
    `dotfiles/tmux/.tmux.conf`.

## Notes

- Target repository: `/Users/thomashan/git/dev-env/main` (all target changes executed via `holon flow` in isolated
  sibling worktrees).

## Resolution

Ongoing umbrella bean (`Item 1` merged in `dev-env#41` / `605559f`; `Item 2` merged in `dev-env#42` / `649168b`, EV
`94.83` predicted / `96.62` actual / `+1.79` delta; `Item 3` merged in `dev-env#43` / `77a7910`; `Item 4` merged in
`dev-env#45` / `6a50860`, Bean `0470`, EV `96.46` predicted / `99.30` actual / `+2.84` delta). Status remains
`in-progress` as the ongoing umbrella epic for `dev-env` improvements.
