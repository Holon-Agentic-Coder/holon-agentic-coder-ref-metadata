---
# holon-agentic-coder-ref-metadata-0464
title: "Install xterm-ghostty terminfo on Ubuntu WSL (Windows) and Linux hosts"
status: completed
type: feature
priority: normal
tags:
  - dev-env
  - windows
  - wsl
  - ubuntu
  - linux
  - ghostty
  - tmux
  - terminfo
parent: holon-agentic-coder-ref-metadata-0435
created_at: 2026-11-25T22:35:00Z
updated_at: 2026-11-26T00:09:00Z
---

# Install `xterm-ghostty` terminfo on Ubuntu WSL (Windows) and Linux hosts

## Problem

When connecting over SSH from macOS running Ghostty (`TERM=xterm-ghostty`) into an **Ubuntu WSL** instance on a Windows
machine (rather than native Windows PowerShell/Win32), SSH forwards `TERM=xterm-ghostty` into the Ubuntu WSL session.
`dev-env` converges inside Ubuntu WSL (`devenv_system == 'Linux'`, `devenv_pkg_backend == 'apt'`,
`devenv_is_wsl == true`) and deliberately skips installing Ghostty on WSL (per `dev-env-ansible-wsl-skip` in
`ansible/roles/packages/tasks/main.yml`, `not (devenv_is_wsl | default(false) | bool)`), as well as on headless Linux
hosts where `devenv_install_gui_casks` is false. Consequently, the Ubuntu WSL terminfo database does not contain an
`xterm-ghostty` entry.

Starting `tmux` (or other ncurses/TUI tools) inside the remote Ubuntu WSL instance then fails immediately before loading
`~/.tmux.conf`:

```text
missing or unsuitable terminal: xterm-ghostty
```

## Proposed Change

Through the Holon flow on `dev-env` (`git@github.com:thomashan/dev-env.git`):

1. **Vendor the `xterm-ghostty` terminfo source**:
   - Add the canonical plain-text `xterm-ghostty` terminfo definition (generated via `infocmp -x xterm-ghostty`) to the
     repository at `ansible/roles/dotfiles/files/xterm-ghostty.terminfo`, outside the GNU Stow `$HOME` link tree so Stow
     does not symlink raw terminfo text into `$HOME`.
2. **Compile `xterm-ghostty` into user terminfo via the `dotfiles` role**:
   - Keep all provisioning inside the Linux/Ubuntu WSL `dotfiles` role (`ansible/roles/dotfiles/tasks/main.yml`), with
     no native Windows changes (`winget.exe` or Windows Registry) required, so both `make converge` and `make dotfiles`
     apply it on Ubuntu WSL and headless Linux regardless of `devenv_is_wsl` or `devenv_install_gui_casks`.
   - Ensure `tic` / `infocmp` is available (`ncurses-bin` is standard on Ubuntu WSL and built into macOS; declare or
     verify `ncurses-bin` cleanly on Debian/Ubuntu if absent).
   - Add idempotent Ansible tasks in `ansible/roles/dotfiles/tasks/main.yml`:
     - Probe `infocmp xterm-ghostty` (`changed_when: false`, `failed_when: false`, `check_mode: false`).
     - When absent, compile the vendored source into `"{{ devenv_home }}/.terminfo"` via
       `tic -x -o "{{ devenv_home }}/.terminfo" <source_path>` (without requiring root privileges), respecting
       `ansible_check_mode`.
     - Assert `infocmp xterm-ghostty` succeeds post-compile (when not in `ansible_check_mode`).
3. **Optional client-side Ghostty SSH fallback**:
   - Evaluate adding `shell-integration-features = ssh-terminfo,ssh-env` to
     `dotfiles/ghostty/.config/ghostty/config.ghostty` as a complementary fallback for ad-hoc SSH hosts that have not
     run `dev-env`, while keeping host-side `~/.terminfo` compilation in `dev-env` as the primary guarantee for Ubuntu
     WSL and Linux machines.
4. **Tests & Documentation**:
   - Add hermetic pytest tests verifying:
     - the vendored `xterm-ghostty` terminfo file compiles cleanly with `tic -x -o <tmp_dir>` and
       `TERMINFO=<tmp_dir> infocmp xterm-ghostty` succeeds,
     - an isolated `tmux` check with `TERM=xterm-ghostty` and `TERMINFO=<tmp_dir>` starts cleanly without
       `missing or unsuitable terminal`,
     - the Ansible tasks in `ansible/roles/dotfiles/tasks/main.yml` are not gated out when `devenv_is_wsl: true` or
       `devenv_install_gui_casks: false`, handle check mode cleanly, and pass `ansible-lint`.
   - Extend Ubuntu E2E verification in `tests/test_converge_integration.py` to confirm `infocmp xterm-ghostty` succeeds
     after converge on Ubuntu.
   - Document `xterm-ghostty` terminfo provisioning for macOS Ghostty $\rightarrow$ Ubuntu WSL and Linux SSH sessions in
     `README.md`.

## Acceptance Criteria

- Running `make converge` or `make dotfiles` inside Ubuntu WSL (`devenv_is_wsl: true`, `apt` backend) installs
  `xterm-ghostty` into `~/.terminfo` idempotently without requiring Ghostty GUI installation or native Windows changes.
- `infocmp xterm-ghostty` exits `0` in the converged Ubuntu WSL instance (and Linux hosts).
- Starting `tmux` over SSH from macOS Ghostty (`TERM=xterm-ghostty`) into the Ubuntu WSL instance starts `tmux` and
  loads `~/.tmux.conf` cleanly with no `missing or unsuitable terminal: xterm-ghostty` error.
- `uv run --extra test pytest -m "not network"`, `uv run --extra test ansible-lint ansible/site.yml`,
  `npx prettier --check`, and Ubuntu E2E verification in `tests/test_converge_integration.py` pass.

## Notes

- Target repository: `dev-env` (`git@github.com:thomashan/dev-env.git`), delivered via `holon flow`.
- Active Holon flow slug: `ubuntu-wsl-ghostty-terminfo` (`antigravity-agent` / `gemini-4-neon`).
- Related beans: Bean `0344` (Ghostty installation and Stow config), Bean `0435` (`dev-env` improvements and
  cross-platform fixes epic).

## Resolution

Successfully delivered via Pull Request [#43](https://github.com/thomashan/dev-env/pull/43) (merged
`2026-11-26T00:03:54Z`, commit `77a7910da0b192cb78a423ac18339c3c6193f9ac`). Key deliverables:

- Vendored `ansible/roles/dotfiles/files/xterm-ghostty.terminfo` source definition.
- Idempotent Ansible compilation task in `ansible/roles/dotfiles/tasks/main.yml` targeting `~/.terminfo` via `tic -x`.
- Hermetic tests in `tests/test_ghostty_terminfo.py` and Ubuntu E2E checks in `tests/test_converge_integration.py`.
- Documentation updates in `README.md`. Verification: 7/7 CI checks green, 3/3 consensus approval, and Stage 5
  calibration EV (`96.05` predicted / `98.81` actual / `+2.76` delta).
