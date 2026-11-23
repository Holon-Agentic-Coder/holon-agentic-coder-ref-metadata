---
# holon-agentic-coder-ref-metadata-0361
title: "Restore Fish Conda and Homebrew hooks and add clean-env multi-shell runtime regression tests"
status: completed
type: bug
priority: high
tags:
  - target:dev-env
  - fish
  - conda
  - homebrew
  - shell-parity
  - tests
created_at: 2026-11-22T23:48:00Z
updated_at: 2026-11-23T01:42:00Z
pr: https://github.com/thomashan/dev-env/pull/33
---

## Problem

1. `dev-env` PR #18 (`0a4771e`) deleted the Conda shell hook, `brew shellenv`, and NVM PATH prepend from
   `dotfiles/fish/.config/fish/config.fish`, turning `test_conda_path_parity_between_ansible_and_fish` and
   `test_node_bin_is_first_on_path` in `tests/test_manifest.py` into negative assertions forbidding them in
   `config.fish`.
2. PR #20 (_multi-shell parity_) restored Conda and Homebrew hooks in `dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`
   alongside what it assumed was already in `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, and its parity test
   (`test_multishell_conda_and_homebrew_parity`) checked only `.bashrc` and `.zshrc`.
3. PR #22 (_mamba-ansible_) added only `micromamba` discovery and hooking to `00-devenv.fish`, leaving macOS
   Miniforge/`conda` (and Homebrew `brew shellenv`) unhooked in Fish.
4. All existing shell tests in `tests/` are static substring greps; no test spawns a clean (`env -i`) login/interactive
   shell for Bash, Zsh, and Fish, `ansible/roles/conda/tasks/main.yml` only tests `{{ devenv_conda_bin }} --version` by
   absolute path, `ansible/roles/fish/tasks/main.yml` only runs `fish -n`, and CI (`make.yml`) only runs
   `make check-mode --tags dotfiles`.
5. Consequently, in a clean login Fish terminal on macOS, `which conda` passes only via Homebrew's
   `/opt/homebrew/bin/conda` symlink -> `/opt/homebrew/Caskroom/miniforge/base/condabin/conda`, while `CONDA_SHLVL` and
   `CONDA_DEFAULT_ENV` stay unset, `conda` is a raw binary instead of a shell function, and
   `/opt/homebrew/Caskroom/miniforge/base/bin` is never on `$PATH` (so `conda install pipx` succeeds yet `pipx` fails
   with `fish: Unknown command: pipx`).
6. Separately, in `.bashrc` and `.zshrc`, the Conda/Micromamba hook runs _after_ the `$NVM_DIR/current/bin` PATH
   prepend, which allows `conda activate base` to place `miniforge/base/bin` ahead of NVM-managed Node.

## Action

Through the 5-stage Holon flow on `thomashan/dev-env`:

1. **`dotfiles/fish/.config/fish/conf.d/00-devenv.fish`** (keeping `config.fish` pure so existing `config.fish` tests
   remain satisfied):
   - Add OS-guarded (`switch "$devenv_os"`) Homebrew/Linuxbrew evaluation (`brew shellenv | source`):
     - `case Darwin`: `/opt/homebrew/bin/brew` (if not already in `$PATH`) and `/usr/local/bin/brew`.
     - `case Linux`: `/home/linuxbrew/.linuxbrew/bin/brew`, `$HOME/.linuxbrew/bin/brew`, and
       `/home/linuxbrew/.linuxbrew/bin` / `/home/linuxbrew/.linuxbrew/sbin` fallback.
   - Add Conda root discovery probing `$MAMBA_ROOT_PREFIX`, `$HOME/.local/share/mamba`, `$HOME/micromamba`,
     `$HOME/miniforge3`, `$HOME/miniforge`, `$HOME/mambaforge`, `case Darwin`-guarded
     `/opt/homebrew/Caskroom/miniforge/base` and `/usr/local/Caskroom/miniforge/base`, `/opt/miniforge3`, `/opt/conda`,
     `$HOME/anaconda3`, and `$HOME/miniconda3`. On the first root where `test -x "$conda_root/bin/conda"`, evaluate
     `"$conda_root/bin/conda" shell.fish hook 2>/dev/null | source` (valid Fish syntax, never POSIX `eval "$(...)"`) and
     track `conda_hook_activated 1`.
   - Guard the `micromamba` fallback (`alias conda=micromamba` + `micromamba shell hook --shell fish | source`) on
     `test $conda_hook_activated -eq 0`.
   - Re-assert `fish_add_path -gpPm "$XDG_DATA_HOME/nvm/current/bin"` and `fish_add_path -gpPm "$HOME/.local/bin"`
     **after** both Homebrew and Conda/Micromamba hooks so NVM-managed Node always wins ahead of Homebrew and Conda.
2. **`dotfiles/bash/.bashrc` and `dotfiles/zsh/.zshrc`**:
   - Re-assert `$NVM_DIR/current/bin` and `$HOME/.local/bin` at the front of `$PATH` **after** the Conda/Micromamba hook
     block so `conda activate base` never puts `miniforge/base/bin` ahead of NVM-managed Node (while preserving
     non-interactive PATH setup and `test_multishell_nvm_and_node_parity`).
3. **`ansible/roles/conda/tasks/main.yml`**:
   - Add clean-environment
     (`env -i HOME="{{ devenv_home }}" USER="{{ ansible_facts['user_id'] | default(lookup('env', 'USER')) }}" PATH=...`)
     runtime verification probes and assertions across available shells (`fish`, `zsh`, `bash`) — guarded by
     `when: not ansible_check_mode` (and shell-present checks), with `changed_when: false`, `check_mode: false` on
     read-only probes — verifying `conda` is a shell function, `CONDA_DEFAULT_ENV` is non-empty, and
     `{{ devenv_conda_dir }}/bin` is on `$PATH`.
4. **`tests/test_shell_hooks.py`** (new module; keep `tests/test_manifest.py` <= 1,000 lines; generate fake scripts
   dynamically under `tmp_path` so zero `.sh` files are tracked in git):
   - **Static 3-shell parity checks**: assert `.bashrc`, `.zshrc`, and `00-devenv.fish` all evaluate OS-guarded Homebrew
     `brew shellenv`, probe Conda roots (with macOS Caskroom inside `case Darwin` / `Darwin)`), invoke the shell's Conda
     hook (`shell.bash hook`, `shell.zsh hook`, `shell.fish hook` piped to `source`), and re-assert NVM `current/bin`
     precedence _after_ both Homebrew and Conda hooks.
   - **Clean-env (`env -i`) runtime shell execution tests** in a hermetic `tmp_path` `$HOME` symlinking the repo's real
     dotfiles, with fake `$HOME/miniforge3/` (`bin/conda` implementing `shell.bash`/`shell.zsh`/`shell.fish` hooks,
     `condabin/conda`, `bin/pipx`, and a competing `bin/node`), fake `$HOME/.local/share/nvm/current/bin/node`, and a
     Homebrew-style symlink `<fakebrew>/bin/conda -> <tmp_home>/miniforge3/condabin/conda` on the initial minimal `PATH`
     (reproducing the exact masking bug):
     - Exercise `bash -lic`, `zsh -lic` (and `zsh -lc`), and `fish -lc` + `fish -ic` under minimal `env -i`.
     - Assert `CONDA_SHLVL == "1"`, `CONDA_DEFAULT_ENV == "base"`, `conda` is a shell function, `pipx` resolves inside
       `<tmp_home>/miniforge3/bin/pipx` and executes, and `node` resolves to
       `<tmp_home>/.local/share/nvm/current/bin/node`.
     - Run `fish -n` on `config.fish` and `00-devenv.fish`.
     - Verify clean-env `micromamba` fallback when no `bin/conda` exists.
     - Fail closed in CI (`os.environ.get("CI") == "true"` and `os.environ.get("HOLON_IN_SANDBOX") != "1"`) if `bash`,
       `zsh`, or `fish` is missing rather than skipping silently.
5. **`.github/workflows/test-unit.yml`**:
   - Install `fish` and `zsh` on `ubuntu-latest` (`sudo apt update && sudo apt install -y fish zsh`) and `fish` on
     `macos-latest` (`brew install fish`) prior to running pytest so CI exercises all three real shells on both OSes.
   - Add a static assertion in `tests/test_shell_hooks.py` verifying `.github/workflows/test-unit.yml` installs `fish`
     (and `zsh` on Ubuntu).

## Acceptance Criteria

- Stage 2 plan declares a `## Touch Set` section listing all created/modified repo-relative paths.
- `tests/test_manifest.py` remains <= 1,000 lines and zero `.sh` files are added outside `dotfiles/examples/`.
- Clean-env (`env -i`) runtime shell tests pass across real `bash`, `zsh`, and `fish` verifying `CONDA_SHLVL=1`,
  `CONDA_DEFAULT_ENV=base`, `conda` as a shell function, `pipx` on `$PATH`, and NVM `node` ahead of Conda `node`.
- `uv run --extra test pytest -m "not network"`, `uv run --extra test ruff check .`, `uv run --extra test ansible-lint`,
  `npx prettier --check "**/*.md"`, and `make check-syntax` pass cleanly.

## Progress

- 2026-11-23: Logged bean, wrote `todo/intent-0360-fish-conda-homebrew-hooks.json`, and launched Holon flow
  `fish-conda-homebrew-hooks` on `/Users/thomashan/git/dev-env/main` (`antigravity-agent` / `gemini-4-argon`).
- 2026-11-23: Flow `fish-conda-homebrew-hooks` (`antigravity-agent` / `gemini-4-argon`) completed all 5 stages and
  opened [PR #33](https://github.com/thomashan/dev-env/pull/33) (head `aa3b72e`): Stage 4 consensus APPROVED 3/3 (0
  critical, 0 important, 0 nit), Stage 5 calibration report included in PR diff (predicted EV 92.88, actual 94.53, delta
  +1.65; touch-set precision/recall 100%), all 6 post-calibration CI checks green (including `test-unit` installing and
  executing real `bash`/`zsh`/`fish` on `ubuntu-latest` and `macos-latest`), `MERGEABLE`/`CLEAN`, awaiting human
  maintainer merge. (Renumbered from 0360 to 0361 after concurrent commit `a8006b2` claimed 0360.)

## Resolution

Delivered via [PR #33](https://github.com/thomashan/dev-env/pull/33) and merged into `main` (`425ff6fe`):

- **Key Architectural Deliverables**: Restored OS-guarded Homebrew `brew shellenv` and Conda/Miniforge
  `conda shell.fish hook | source` (with guarded `micromamba` fallback) in
  `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, enforced NVM-over-Conda PATH ordering across Fish/Bash/Zsh, and
  added read-only clean-environment (`env -i`) shell verification probes in `ansible/roles/conda/tasks/main.yml`.
- **Verification & Tests**: Added `tests/test_shell_hooks.py` (3-shell static parity, hermetic `env -i`
  `bash`/`zsh`/`fish` runtime execution reproducing the Homebrew symlink masking scenario, `fish -n` syntax,
  `micromamba` fallback, and fail-closed CI shell checks) and updated `.github/workflows/test-unit.yml` to install
  `fish`/`zsh` on Ubuntu and `fish` on macOS (`6/6` CI checks green).
- **Holon Flow Traversal**: Completed all 5 stages (`I-1795391675-fish-conda-homebrew-hooks`, `P-1795391695-ANA-G4A`,
  `E-1795391884-ANA-G4A`), Stage 4 consensus APPROVED 3/3 (0 findings), Stage 5 calibrated (EV predicted `92.88`, actual
  `94.53`, delta `+1.65`; touch-set 100%).
