---
# holon-agentic-coder-ref-metadata-0370
title: "Fix node/zsh/fish/brew converge bugs and add real e2e Ubuntu converge tests"
status: completed
type: bug
priority: high
tags:
  - target:dev-env
  - wsl
  - linux
  - zsh
  - nvm
  - testing
  - ci
  - docker
created_at: 2026-11-23T06:10:00Z
updated_at: 2026-11-23T07:33:55Z
pr: https://github.com/thomashan/dev-env/pull/40
---

## Problem

1. **Zsh `node` assertion failure on WSL after PR #39**:
   - `ansible/roles/node/tasks/main.yml` runs `bash -lc`, `zsh -lc`, and `fish -lc` without `env -i`, inheriting the
     parent interactive Fish session's `PATH` (where `nvm.fish` prepended
     `~/.local/share/nvm/versions/node/v26.13.1/bin`).
   - Unlike Bash (`~/.bash_profile` $\rightarrow$ `~/.bashrc`) and Fish (`00-devenv.fish`), `dev-env` does not stow a
     `~/.zprofile`, and non-interactive login Zsh (`zsh -lc`) never reads `~/.zshrc`. So `zsh -lc` kept Fish's inherited
     `~/.local/share/nvm/versions/node/v26.13.1/bin` first on `PATH`.
   - The `node` role assertions rejected `'.local/share/nvm/versions/node/v' ~ devenv_node_version ~ '/bin/node'`, even
     though it is NVM's canonical installed path (and what interactive `nvm use` / `nvm.sh` also prepends).
2. **Dishonest test & role blindspots**:
   - `tests/test_shell_hooks.py:_link_repo_dotfiles()` writes a synthetic `~/.zprofile` shim in `tmp_path` that does not
     exist in `dotfiles/zsh/` or on real machines.
   - `ansible/roles/fish/tasks/main.yml` (`Collect linked fish files`) omits `follow: true` in `ansible.builtin.find`,
     skipping stowed symlinks (`config.fish`, `00-devenv.fish`) during `fish -n` verification.
   - `community.general.homebrew*` tasks pass the `brew` binary path (`devenv_brew_bin`) instead of its parent directory
     (`devenv_brew_bin | dirname`) to `path:`.
3. **No end-to-end Ubuntu converge test in CI or local Docker**:
   - CI only runs unit tests, lint, and `--check` on `--tags dotfiles,nvim-sync`, never running an actual Linux/WSL
     `make converge` across `packages`, `dotfiles`, `conda`, `node`, `neovim`, and `fish`, so real playbook failures
     keep surfacing on WSL first.

## Action

Through the 5-stage Holon flow on `thomashan/dev-env`:

1. Add tracked `dotfiles/zsh/.zprofile` (non-interactive `~/.zshrc` sourcing + `~/.zprofile.local` without
   double-sourcing interactive `zsh -lic`) and declare it in `devenv_links` (`ansible/group_vars/all.yml`).
2. Harden `ansible/roles/node/tasks/main.yml` with `which bash`/`zsh`/`fish` probes, isolated `env -i` +
   `expand_argument_vars: false` login-shell checks, `not ansible_check_mode` guards, and assertions accepting
   `current/bin/node`, `.local/bin/node`, and canonical `versions/node/v{{ devenv_node_version }}/bin/node`.
3. Add `follow: true` to `Collect linked fish files` in `ansible/roles/fish/tasks/main.yml`.
4. Pass `devenv_brew_bin | dirname` (with `omit` fallback) to `path:` on `community.general.homebrew*` tasks across
   `homebrew`, `packages`, `conda`, and `neovim` roles.
5. Remove the fake `.zprofile` shim from `tests/test_shell_hooks.py`, add `.zprofile` single-source Zsh tests, update
   `tests/test_toolchain.py`, and add real hermetic `ansible-playbook` + Stow integration tests in
   `tests/test_converge_integration.py` (keeping `tests/test_manifest.py <= 1,000` lines).
6. Install `stow` in `.github/workflows/test-unit.yml`, add real end-to-end Ubuntu WSL-simulated converge CI workflow
   `.github/workflows/test-converge.yml` (documented in `.github/workflows/README.md`), and add local Docker Ubuntu
   converge harness (`tests/docker/ubuntu.Dockerfile`, `.dockerignore`, `make test-ubuntu` in `Makefile`) with zero
   `.sh` files and zero `apt-get`.

## Notes

- Target repository: `thomashan/dev-env` (`/Users/thomashan/git/dev-env/main`, at `eeb2032d`).
- Intent file: `todo/intent-0370-dev-env-e2e-converge.json`.
- Dedicated worktree: `/Users/thomashan/git/dev-env/flow-dev-env-e2e-converge-testing`.

## Progress

- 2026-11-23: Bean created (`0370`), intent authored
  ([`todo/intent-0370-dev-env-e2e-converge.json`](../todo/intent-0370-dev-env-e2e-converge.json)), flow worktree created
  at `/Users/thomashan/git/dev-env/flow-dev-env-e2e-converge-testing`, and 5-stage Holon flow launched in background
  subagent `35f3a8a6-eb68-4d1b-9680-00e8259801fc` (`bean 0370 - holon flow dev-env-e2e-converge-testing`,
  `antigravity-agent` / `gemini-4-argon`).
- 2026-11-23: All 5 Holon flow stages completed cleanly on
  [thomashan/dev-env#40](https://github.com/thomashan/dev-env/pull/40) (consensus APPROVED; Stage 5 calibration report
  `plans/I-1795414247-dev-env-e2e-converge-testing/P-1795414265-ANA-G4A_calibration.md` included in PR diff; 7/7 CI
  checks passed including `Ubuntu Converge E2E` in 5m25s; `MERGEABLE` / `CLEAN`). Keeping `status: in-progress` until
  human maintainer merge.

## Resolution

Delivered via [PR #40](https://github.com/thomashan/dev-env/pull/40) and merged into `main` (`22ca3862`):

- **Key Architectural Deliverables**:
  - Added tracked `dotfiles/zsh/.zprofile` (non-interactive `~/.zshrc` sourcing + `~/.zprofile.local` without
    double-sourcing interactive `zsh -lic`) and registered it in `devenv_links` (`ansible/group_vars/all.yml`).
  - Hardened `ansible/roles/node/tasks/main.yml` with `which bash`/`zsh`/`fish` availability probes, isolated `env -i` +
    `expand_argument_vars: false` login-shell checks, `not ansible_check_mode` guards, and assertions accepting
    `current/bin/node`, `.local/bin/node`, and canonical `versions/node/v{{ devenv_node_version }}/bin/node`.
  - Added `follow: true` to `Collect linked fish files` in `ansible/roles/fish/tasks/main.yml`, and passed
    `devenv_brew_bin | dirname` (with `omit` fallback) to `path:` across `homebrew`, `packages`, `conda`, and `neovim`
    roles.
  - Removed the fake `.zprofile` shim from `tests/test_shell_hooks.py`, added `.zprofile` single-source Zsh tests,
    updated `tests/test_toolchain.py`, and added hermetic `ansible-playbook` / Stow / Node / Fish integration tests in
    `tests/test_converge_integration.py`.
  - Added `stow` to `.github/workflows/test-unit.yml`, real end-to-end Ubuntu/WSL converge CI in
    `.github/workflows/test-converge.yml` (documented in `.github/workflows/README.md`), and local Docker Ubuntu
    converge harness (`tests/docker/ubuntu.Dockerfile`, `.dockerignore`, `make test-ubuntu`).
- **Verification & Tests**: All 7/7 GitHub Actions CI checks passed on clean PR #40 (`Ubuntu Converge E2E` in 5m25s,
  `test-unit` on macOS/Ubuntu, `Code Hygiene & Lint`, `Make Check`, `Network Upstream Asset Tests`). Locally on synced
  `main` (`22ca3862`), `uv run --extra test ruff check .` passed and `uv run --extra test pytest -q -m "not network"`
  reported `193 passed, 1 failed` (`4 deselected`), where the sole failure
  (`tests/test_manifest.py::test_readme_manifest_coverage`) came from the pre-existing unstaged local
  `dotfiles/nvim-kickstart/.config/nvim/nvim-pack-lock.json` diff (adding `diffview.nvim`, `fzf-lua`, `mini.completion`)
  on `/Users/thomashan/git/dev-env/main`.
- **Holon Flow Traversal**: All 5 stages (Intent $\rightarrow$ Plan $\rightarrow$ Execute $\rightarrow$ Review Loop
  $\rightarrow$ Calibration) completed cleanly on `antigravity-agent` / `gemini-4-argon` with calibration report
  included in PR diff (EV predicted `97.60` / actual `99.09`, delta `+1.49`).
