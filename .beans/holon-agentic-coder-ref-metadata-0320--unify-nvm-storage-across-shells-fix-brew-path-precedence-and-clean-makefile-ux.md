---
id: "0320"
title: "Unify NVM storage across Fish and Bash/Zsh, prevent Homebrew path usurpation, and clean Makefile bootstrap UX"
status: todo
created_at: 2026-11-18T00:35:00+11:00
updated_at: 2026-11-18T00:35:00+11:00
tags:
  - dev-env
  - nvm
  - fish
  - bash
  - zsh
  - homebrew
  - makefile
  - bugfix
---

# 0320 - Unify NVM storage across Fish and Bash/Zsh, prevent Homebrew path usurpation, and clean Makefile bootstrap UX

## Problem Statement

Following the multi-shell parity work in Bean 0319, four usability and architectural issues were identified during live
shell testing:

1. **Fish `nvm.fish` vs Bash/Zsh `nvm-sh` Storage Disconnect**:
   - In Fish, `jorgebucaran/nvm.fish` installs Node versions to `$nvm_data/v<version>` (`~/.local/share/nvm/v26.13.1`).
   - In Bash and Zsh, official `nvm-sh/nvm` installs Node versions to `$NVM_DIR/versions/node/v<version>`
     (`~/.local/share/nvm/versions/node/v26.13.1`).
   - Consequently, Node versions installed in Fish are invisible to Bash/Zsh (`nvm use` fails with
     `N/A: version is not yet installed`), and versions installed in Bash/Zsh cannot be uninstalled or managed by Fish.
     They must share the identical version storage directory.

2. **Homebrew `brew shellenv` Usurping NVM on `$PATH`**:
   - `eval "$(/opt/homebrew/bin/brew shellenv)"` unconditionally prepends `/opt/homebrew/bin` to the front of `$PATH`.
   - In `.bashrc` and `.zshrc`, the check `case ":$PATH:" in *":$NVM_DIR/current/bin:"*) ;;` skipped re-prepending NVM
     if NVM was already present anywhere in `$PATH`.
   - When `brew shellenv` runs (e.g. from `.zprofile` or subshells), Homebrew's `/opt/homebrew/bin/node` permanently
     usurps precedence over NVM's Node.
   - In Fish, this was prevented via `fish_add_path -m` (moving NVM to the front); Bash and Zsh require an equivalent
     guarantee so NVM always wins over Homebrew.

3. **`nvm ls` Marking NVM-Managed Node as `-> system`**:
   - `nvm_ls_current()` in `nvm-sh` inspects `which node` and performs a non-dereferencing string prefix check against
     `$NVM_DIR`.
   - When `~/.local/bin` or `/opt/homebrew/bin` preceded NVM on `$PATH`, `which node` resolved to `~/.local/bin/node` or
     `/opt/homebrew/bin/node`. Because `~/.local/bin` is not a subdirectory of `$NVM_DIR`, NVM assumed it was an
     unmanaged external binary and displayed `-> system`.
   - Sourcing NVM and setting the default version must guarantee NVM's directory is at the front of `$PATH`.

4. **Misleading `make install` Message**:
   - The `Makefile`'s `bootstrap` target unconditionally prints: `Run 'make install' or 'make check-mode' next.`
   - When a user runs `make install`, it invokes `make bootstrap` internally, which prints this message right in the
     middle of execution before kicking off `make converge`. This misleads users into thinking `make install` halted or
     failed.

## Scope of Changes

1. **Unify NVM Version Storage (`dotfiles/fish/.config/fish/conf.d/00-devenv.fish`)**:
   - Set `set -g nvm_data $XDG_DATA_HOME/nvm/versions/node` in `00-devenv.fish` (and ensure backward-compatibility
     symlinks exist if needed) so that `nvm.fish` in Fish and `nvm-sh` in Bash/Zsh read and write the exact same version
     directory (`~/.local/share/nvm/versions/node/v*`).

2. **Prevent Homebrew `$PATH` Usurpation & Ensure NVM Precedence (`dotfiles/bash/.bashrc`, `dotfiles/zsh/.zshrc`)**:
   - Only evaluate `brew shellenv` if `/opt/homebrew/bin` (or `/home/linuxbrew/.linuxbrew/bin`) is not already on
     `$PATH`.
   - Ensure NVM's path is moved to the front of `$PATH` after Homebrew initialization, matching Fish's
     `fish_add_path -m` behavior.
   - Clean up custom redundant NVM checks to align with official canonical XDG NVM sourcing conventions:
     ```sh
     export NVM_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/nvm"
     [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
     [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
     ```

3. **Clean Up `Makefile` Bootstrap UX (`Makefile`)**:
   - In `Makefile`, only print `Run 'make install' or 'make check-mode' next.` when `bootstrap` is the explicit
     top-level target (e.g. `ifeq ($(MAKECMDGOALS),bootstrap)`), avoiding misleading output during `make install`.

4. **Tests & Invariants**:
   - Update `tests/test_manifest.py` to verify:
     - `00-devenv.fish` sets `nvm_data` to match the official NVM version storage layout.
     - `.bashrc` and `.zshrc` enforce NVM precedence over `/opt/homebrew/bin`.
     - `Makefile` does not output the next-step prompt during `make install`.
   - Run `make test`, `make lint`, and `make check`.
