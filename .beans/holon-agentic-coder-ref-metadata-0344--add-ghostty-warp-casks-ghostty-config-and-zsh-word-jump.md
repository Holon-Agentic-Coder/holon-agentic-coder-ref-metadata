---
# holon-agentic-coder-ref-metadata-0344
title: "Add Ghostty and Warp macOS casks, Stow-managed Ghostty keybind fix, and Zsh word-jump bindings"
status: in-progress
type: feature
priority: normal
tags:
  - dev-env
  - macos
  - ghostty
  - warp
  - zsh
  - tmux
created_at: 2026-11-20T23:17:00+11:00
updated_at: 2026-11-20T23:17:00+11:00
---

## Problem

1. Ghostty and Warp are installed manually on macOS outside `dev-env`, even though `dev-env` already manages macOS GUI
   apps via `devenv_casks` in `ansible/vars/os_Darwin.yml` (gated by `devenv_install_gui_casks`).
2. Ghostty's macOS default keybinds map `alt+arrow_left=esc:b` and `alt+arrow_right=esc:f`, which intercepts
   `Option+Left` / `Option+Right` before tmux sees `M-Left` / `M-Right` — breaking horizontal `prefix Option+Arrow` pane
   resizing in Ghostty while Warp passes standard CSI `\e[1;3D` / `\e[1;3C`.
3. Unlike Fish and Bash (Readline), Zsh does not bind CSI `\e[1;3D` / `\e[1;3C` (`Alt+Left` / `Alt+Right`) or `\e[1;5D`
   / `\e[1;5C` (`Ctrl+Left` / `Ctrl+Right`) to `backward-word` / `forward-word` by default, so word-jumping fails in Zsh
   under Warp, unbundled Ghostty, Linux terminals, and tmux.

## Action

Through the Holon flow on `dev-env`:

- Add `ghostty` and `warp` to `devenv_casks` in `ansible/vars/os_Darwin.yml` (keep `ansible/vars/os_Linux.yml`
  `devenv_casks: []` headless/CLI-only), and update the GUI casks prompt in `scripts/devenv_wizard.py` and `README.md`.
- Add a GNU Stow package `dotfiles/ghostty/.config/ghostty/config.ghostty` (registered in `devenv_stow_packages` and
  `devenv_links` in `ansible/group_vars/all.yml`) containing `keybind = alt+arrow_left=unbind` and
  `keybind = alt+arrow_right=unbind` (verified with `ghostty +show-config`: Ghostty on macOS loads XDG
  `~/.config/ghostty/config.ghostty` before macOS `Application Support` overrides, and it is a harmless no-op on Linux).
- Add interactive-guarded Zsh word-jump bindings in `dotfiles/zsh/.zshrc` for `^[[1;3D`/`^[[1;3C` (`Alt+Left/Right`) and
  `^[[1;5D`/`^[[1;5C` (`Ctrl+Left/Right`) to `backward-word`/`forward-word`, preserving existing `^[b`/`^[f`.
- Add hermetic pytest tests covering the macOS casks list, Linux headless cask list, Ghostty Stow manifest/config, and
  Zsh word-jump bindings.
