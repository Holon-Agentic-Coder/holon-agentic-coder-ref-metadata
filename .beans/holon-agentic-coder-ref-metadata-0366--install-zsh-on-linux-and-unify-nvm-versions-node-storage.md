---
# holon-agentic-coder-ref-metadata-0366
title: "Install zsh on Linux/WSL and unify NVM storage strictly under versions/node"
status: in-progress
type: bug
priority: high
tags:
  - target:dev-env
  - wsl
  - linux
  - zsh
  - nvm
  - fish
created_at: 2026-11-23T05:26:00Z
updated_at: 2026-11-23T05:26:00Z
---

## Problem

1. **Missing `zsh` on Linux/WSL**: `zsh` is omitted from `devenv_packages_core` (`ansible/group_vars/all.yml`) and
   `ansible/vars/pkg_apt.yml`. macOS ships `/bin/zsh` out of the box, whereas Ubuntu/WSL ships only `bash`, so `dev-env`
   stows `~/.zshrc` without installing `zsh` on Linux/WSL.
2. **NVM bi-directional symlink trap & recursive `versions` loop**:
   - `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` uses `find "$XDG_DATA_HOME/nvm" -maxdepth 1 -name "v*"`, which
     matches the `versions` directory itself and creates a recursive symlink
     `~/.local/share/nvm/versions/node/versions -> ~/.local/share/nvm/versions`.
   - Mirroring `~/.local/share/nvm/v*` <-> `~/.local/share/nvm/versions/node/v*` with symlinks breaks
     `nvm uninstall <ver>` in Bash/Fish: uninstalling only removes the symlink under `versions/node/`, leaving the real
     directory under `~/.local/share/nvm/vX.Y.Z` so `nvm ls` still lists the version while `nvm uninstall` fails with
     `N/A version is not installed...` (and starting Fish recreates the deleted symlink).
   - `ansible/roles/node/tasks/main.yml` still points `creates:` and the `current` symlink `src:` at the legacy flat
     `~/.local/share/nvm/v{{ devenv_node_version }}` path instead of the unified
     `~/.local/share/nvm/versions/node/v{{ devenv_node_version }}` directory shared by both `nvm.fish` (`nvm_data`) and
     `nvm-sh`.

## Action

Through the 5-stage Holon flow on `dev-env`:

1. **`ansible/group_vars/all.yml`, `ansible/vars/pkg_apt.yml`, `ansible/vars/os_Darwin.yml`**:
   - Add `zsh` to `devenv_packages_core` (next to `fish`) in `ansible/group_vars/all.yml`.
   - Add `zsh: zsh` to `devenv_pkg_aliases` (next to `fish: fish`) in `ansible/vars/pkg_apt.yml`.
   - Add `- zsh` to `devenv_pkg_skip` (next to `- unzip`) in `ansible/vars/os_Darwin.yml` since macOS ships `/bin/zsh`
     (leaving Linux/WSL to install `zsh`, and verifying `README.md` mentions `zsh` for `test_readme_manifest_coverage`).
2. **`ansible/roles/node/tasks/main.yml`**:
   - Ensure `{{ devenv_home }}/.local/share/nvm/versions/node` directory exists (`state: directory`, `mode: "0755"`).
   - Update `Install the pinned node through nvm` `creates:` to
     `{{ devenv_home }}/.local/share/nvm/versions/node/v{{ devenv_node_version }}/bin/node`.
   - Update `Point current at the pinned version` `src:` to
     `{{ devenv_home }}/.local/share/nvm/versions/node/v{{ devenv_node_version }}`.
3. **`dotfiles/fish/.config/fish/conf.d/00-devenv.fish`**:
   - Keep `set -g nvm_data $XDG_DATA_HOME/nvm/versions/node` and `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`.
   - Replace the bi-directional `-name "v*"` symlink loops with idempotent one-way migration & cleanup:
     - Ensure `$nvm_data` exists (`test -d "$nvm_data" || mkdir -p "$nvm_data"`).
     - Remove `$nvm_data/versions` if `test -L "$nvm_data/versions"` (`command rm -f "$nvm_data/versions"`).
     - Scan only `(command find "$XDG_DATA_HOME/nvm" -maxdepth 1 -name "v[0-9]*" 2>/dev/null)`: remove legacy
       back-symlinks (`test -L "$legacy_ver"`), and move any real legacy directory into `$nvm_data/$vname` (replacing an
       existing symlink at `$nvm_data/$vname` if present, never overwriting a real directory).
     - Repair a dangling `$XDG_DATA_HOME/nvm/current` symlink to `$nvm_data/v$devenv_node_default_version` when present.
     - Never create back-symlinks into `$XDG_DATA_HOME/nvm/v*`.
4. **`tests/test_manifest.py`** (strictly `<= 1,000` lines, currently 990):
   - Update `test_fish_nvm_path_resolution_in_conf_d()` to assert `v[0-9]*` (not `-name "v*"`), assert no
     back-symlinking into `$XDG_DATA_HOME/nvm/$vname`, and retain `set -g nvm_data $XDG_DATA_HOME/nvm/versions/node` and
     `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"`.
5. **`tests/test_toolchain.py`**:
   - Assert `zsh` is in `devenv_packages_core`, mapped to `zsh` in `pkg_apt.yml`, and skipped in `os_Darwin.yml`
     `devenv_pkg_skip` (not skipped in `os_Linux.yml`).
   - Assert `ansible/roles/node/tasks/main.yml` points `creates` and `current` symlink `src` at
     `{{ devenv_home }}/.local/share/nvm/versions/node/v{{ devenv_node_version }}`.
6. **`tests/test_shell_hooks.py`**:
   - Add `test_fish_nvm_migration_and_no_versions_symlink_loop` running real Fish (`fish -lc 'true'`) against a hermetic
     fake HOME seeded with legacy flat `v24.18.0` + symlink `versions/node/v24.18.0`, bogus `versions/node/versions`
     symlink, dangling `v22.0.0`, real `versions/node/v26.13.1`, and dangling `current`, verifying cleanup, one-way
     migration, no `v26.13.1` back-symlink, and `current` repair.
7. Keep zero `.sh` files outside `dotfiles/examples/`.

## Acceptance Criteria

- Stage 2 plan declares an explicit `## Touch Set` section listing all created/modified repo-relative paths.
- `zsh` is declared in `devenv_packages_core`, aliased in `ansible/vars/pkg_apt.yml`, and skipped in
  `ansible/vars/os_Darwin.yml`.
- `ansible/roles/node/tasks/main.yml` ensures `~/.local/share/nvm/versions/node` and points `creates` and `current` at
  `versions/node/v{{ devenv_node_version }}`.
- `dotfiles/fish/.config/fish/conf.d/00-devenv.fish` cleans up `versions/node/versions`, migrates legacy `v[0-9]*`
  directories one-way into `versions/node/`, repairs a dangling `current` symlink, and never creates back-symlinks into
  `~/.local/share/nvm/v*`.
- `tests/test_manifest.py` stays `<= 1,000` lines, `tests/test_toolchain.py` checks `zsh` packaging + unified node role
  paths, and `tests/test_shell_hooks.py` tests the Fish migration and loop cleanup in a real Fish subprocess.
- `make check-syntax`, `uv run --extra test ruff format --check .`, `uv run --extra test ruff check .`,
  `uv run --extra test ansible-lint`, `npx --yes prettier@3 --check "**/*.md"`, and
  `uv run --extra test pytest -m "not network"` all pass cleanly with zero deprecation warnings.

## Notes

- Target repository: `thomashan/dev-env` (`/Users/thomashan/git/dev-env/main`, at `68ddec98`).
- Any `dev-env` Holon flow intent JSON MUST instruct the Stage 2 planner to include a `## Touch Set` section listing all
  modified/created repo-relative paths.

## Progress

- 2026-11-23: Wrote `todo/intent-0366-dev-env-zsh-and-nvm-storage.json` and launched Holon flow
  `dev-env-zsh-and-nvm-storage` off `/Users/thomashan/git/dev-env/main` (`68ddec98`) with `antigravity-agent` /
  `gemini-4-argon`.

## Resolution
