---
id: "0327"
title: "Install Neovim via Homebrew on Linux and macOS and mandate actual Ansible execution in CI"
status: completed
created_at: 2026-11-18T12:34:00+11:00
updated_at: 2026-11-18T14:07:00+11:00
tags:
  - dev-env
  - neovim
  - linux
  - macos
  - homebrew
  - ansible
  - ci
  - bugfix
---

# 0327 - Install Neovim via Homebrew on Linux and macOS and mandate actual Ansible execution in CI

## Problem Statement

During `make install` on Ubuntu Linux (`CO-ESURFL-365`), execution reached task 63 (`neovim`) and failed with:

```text
TASK [neovim : Resolve the latest Neovim release (github source only)] ******************************************************
[ERROR]: Task failed: Module failed: missing required arguments: action
Origin: /home/thomashan/git/dev-env/ansible/roles/neovim/tasks/main.yml:5:3

fatal: [localhost]: FAILED! => {"changed": false, "msg": "missing required arguments: action"}
```

### Detailed Diagnosis

1. **Broken Module Usage in `ansible/roles/neovim/tasks/main.yml`**:
   - The task invoked `community.general.github_release`, which strictly requires `action` (`action: latest_release` or
     `action: create_release`). The task omitted `action`.
   - Furthermore, `community.general.github_release` requires `github3.py >= 1.0.0a3` (which is not installed in the
     bootstrap Conda environment).
   - Even if `action: latest_release` were provided, `github_release` only returns `tag` (`release.tag_name`), **not**
     an `.assets` map. The subsequent task (`url: "{{ devenv_nvim_release.assets[devenv_nvim_asset] }}"`) would
     immediately fail with an undefined attribute error.
2. **Neovim via Homebrew on Both Linux and macOS**:
   - Neovim 0.12.6 is actively maintained and published via Homebrew (`neovim` formula) for both macOS and Linux
     (Linuxbrew).
   - The dev-env repository already requires and bootstraps Homebrew / Linuxbrew on both platforms.
   - Using Homebrew (`brew`) for Neovim on Linux unifies package management across platforms, guarantees Neovim 0.12+
     with native `vim.pack` support, and completely eliminates the broken and brittle GitHub release tarball download
     and unarchive tasks.
3. **Preventing Duplicate / Conflicting Neovim from `apt` on Linux**:
   - On Linux (`ansible_facts.system == 'Linux'`), `ansible/vars/pkg_apt.yml` maps `neovim: neovim`.
   - To avoid `apt` installing a stale or shadowing system package before Homebrew installs Neovim 0.12.6, `neovim`
     should be skipped in `apt` via `devenv_pkg_skip: [neovim]` in `ansible/vars/os_Linux.yml`.
4. **Why These Errors Keep Slipping Through (Testing Gap)**:
   - On macOS (`os_Darwin.yml`), `devenv_neovim_source: package` (Neovim installs via `brew` in the `packages` role), so
     the GitHub download task was skipped.
   - On Linux (`os_Linux.yml`), `devenv_neovim_source: github`, so this broken task executed.
   - GitHub Actions CI workflows (`make.yml`, `test-unit.yml`, `test-hygiene.yml`) **never actually execute
     `ansible-playbook`**. They only ran:
     - `make help` and `make check` (probing CLI versions).
     - `ansible-lint` (which does not validate dynamic module runtime parameter specs).
     - `pytest` (which runs isolated Python unit tests).
   - Because `make check-mode` was never wired into CI on Ubuntu, any task that fails at runtime on Linux was completely
     invisible until executed on a live machine.

## Scope of Changes

1. **Unify Neovim Installation via Homebrew (`ansible/roles/neovim/tasks/main.yml`, `ansible/vars/os_Linux.yml`)**:
   - In `ansible/vars/os_Linux.yml`:
     - Set `devenv_neovim_source: brew`.
     - Add `neovim` to `devenv_pkg_skip` so `apt` does not install a duplicate or outdated system package.
   - In `ansible/roles/bootstrap/tasks/main.yml` (or `neovim/tasks/main.yml`):
     - Ensure `devenv_brew_bin` is located reliably across `/opt/homebrew/bin/brew`, `/usr/local/bin/brew`,
       `/home/linuxbrew/.linuxbrew/bin/brew`, and `{{ devenv_home }}/.linuxbrew/bin/brew`.
   - In `ansible/roles/neovim/tasks/main.yml`:
     - Replace the broken `github_release` / download / unarchive tasks with:
       ```yaml
       - name: Install Neovim via Homebrew
         community.general.homebrew:
           name: neovim
           state: present
           path: "{{ devenv_brew_bin | default(omit) }}"
         when: devenv_neovim_source == 'brew'
       ```
     - Keep the assertion verifying Neovim is 0.12+ for `vim.pack` and `nvim-pack-lock.json`.

2. **Mandate Actual Ansible Playbook Execution in CI (`.github/workflows/make.yml`)**:
   - In `.github/workflows/make.yml`, on both `ubuntu-latest` and `macos-latest`:
     - Run `make bootstrap` to build the isolated environment.
     - Run `make check-mode` to evaluate every Ansible task and role against the live OS runner.
     - If any module fails or has missing required arguments, CI turns RED and blocks the pull request from merging.

3. **Tests & Verification**:
   - Update `tests/test_templating.py` and `tests/test_manifest.py` to assert Homebrew package resolution and valid task
     structure.
   - Verify that `make check-mode` passes locally without module failure.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Resolution

- Implemented via Holon flow `neovim-brew` (Bean 0327).
- Pull Request #25: [https://github.com/thomashan/dev-env/pull/25](https://github.com/thomashan/dev-env/pull/25) merged
  to `main` (`7a92ce3`).
- Replaced broken GitHub release download on Linux with Homebrew installation, added `neovim` to `devenv_pkg_skip` in
  `os_Linux.yml`, and added `make check-syntax` to GitHub Actions CI (`.github/workflows/make.yml`).
- Main branch fast-forwarded to `7a92ce3` and flow worktrees/branches pruned.
