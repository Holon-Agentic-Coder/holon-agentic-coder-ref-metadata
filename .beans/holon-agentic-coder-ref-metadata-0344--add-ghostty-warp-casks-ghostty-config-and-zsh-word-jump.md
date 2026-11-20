---
# holon-agentic-coder-ref-metadata-0344
title: "Install Ghostty and Warp on macOS and Linux, add Stow-managed Ghostty config, and Zsh word-jump bindings"
status: in-progress
type: feature
priority: normal
tags:
  - dev-env
  - macos
  - linux
  - ghostty
  - warp
  - zsh
  - tmux
created_at: 2026-11-20T23:17:00+11:00
updated_at: 2026-11-20T23:23:00+11:00
---

## Problem

1. Ghostty and Warp are installed manually outside `dev-env`, even though `dev-env` already manages GUI tools via
   `devenv_install_gui_casks` and `ansible/vars/os_Darwin.yml` (`devenv_casks`), and should install both terminals on
   macOS and Linux (Ubuntu/Debian `apt`, amd64 and arm64).
2. Ghostty's macOS default keybinds map `alt+arrow_left=esc:b` and `alt+arrow_right=esc:f`, which intercepts
   `Option+Left` / `Option+Right` before tmux sees `M-Left` / `M-Right` — breaking horizontal `prefix Option+Arrow` pane
   resizing in Ghostty while Warp passes standard CSI `\e[1;3D` / `\e[1;3C`.
3. Unlike Fish and Bash (Readline), Zsh does not bind CSI `\e[1;3D` / `\e[1;3C` (`Alt+Left` / `Alt+Right`) or `\e[1;5D`
   / `\e[1;5C` (`Ctrl+Left` / `Ctrl+Right`) to `backward-word` / `forward-word` by default, so word-jumping fails in Zsh
   under Warp, unbundled Ghostty, Linux terminals, and tmux.

## Action

Through the Holon flow on `dev-env`:

- **macOS**: add `ghostty` and `warp` to `devenv_casks` in `ansible/vars/os_Darwin.yml` (gated by
  `devenv_install_gui_casks`).
- **Linux (Ubuntu/Debian, amd64 & arm64)**: keep `devenv_casks: []` in `ansible/vars/os_Linux.yml` and add
  `devenv_linux_gui_apps: [ghostty, warp]` (default `[]` in `ansible/group_vars/all.yml`), installed in
  `ansible/roles/packages/tasks/main.yml` when `devenv_pkg_backend == 'apt'` and `devenv_install_gui_casks | bool`:
  - **Warp (`warp-terminal`)**: configure the official Warp APT keyring (`/etc/apt/keyrings/warpdotdev.gpg` from
    `https://releases.warp.dev/linux/keys/warp.asc`) and source list
    (`deb [arch=<amd64|arm64> signed-by=/etc/apt/keyrings/warpdotdev.gpg] https://releases.warp.dev/linux/deb stable main`),
    then install `warp-terminal` via `apt` if not already installed.
  - **Ghostty (`ghostty`)**: if `ghostty` is missing, install via native `apt` when available (`apt-cache show ghostty`,
    Ubuntu 26.04+), else via `snap install ghostty --classic` when `snap` is present, else on Ubuntu via
    `ppa:mkasberg/ghostty-ubuntu` + `apt`.
- **Wizard & README**: prompt for `devenv_install_gui_casks` on both `brew` and `apt` backends in
  `scripts/devenv_wizard.py` and document Ghostty & Warp on macOS and Linux in `README.md`.
- **Ghostty Stow package**: add `dotfiles/ghostty/.config/ghostty/config.ghostty` (registered in `devenv_stow_packages`
  and `devenv_links` in `ansible/group_vars/all.yml`) containing `keybind = alt+arrow_left=unbind` and
  `keybind = alt+arrow_right=unbind`.
- **Zsh word-jump parity**: add interactive-guarded (`[[ -o interactive ]]`) `bindkey` entries in `dotfiles/zsh/.zshrc`
  for `^[[1;3D`/`^[[1;3C` (`Alt+Left/Right`) and `^[[1;5D`/`^[[1;5C` (`Ctrl+Left/Right`) to
  `backward-word`/`forward-word`, preserving existing `^[b`/`^[f`.
- **Tests**: add hermetic pytest coverage for macOS casks, Linux GUI apps config and Ansible tasks, Ghostty Stow
  manifest/config, wizard prompt on both `brew` and `apt`, and Zsh word-jump bindings.
