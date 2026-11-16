---
# holon-agentic-coder-ref-metadata-0303
title: "Add host interactive wizard for dotfile merge and package variants"
status: completed
type: feature
priority: high
tags:
  - dev-env
  - dotfiles
  - stow
  - wizard
  - ansible
  - conda
created_at: 2026-11-16T02:05:00Z
updated_at: 2026-11-16T03:45:00Z
---

## Summary

Enforce the pure `GNU Make -> Conda -> Ansible` bootstrap tool chain (`make` is the sole cold-start prerequisite; `git`
and `curl` are deferred to Ansible; all Python/Ansible/app-dev installations including `uv` are done through Conda, with
`uv` strictly an application-dev tool), add multi-variant GNU Stow packages (`devenv_package_variants`:
`nvim-kickstart`, `nvim-minimal`, `nvim-lazyvim`) and a host interactive pre-Ansible wizard
(`scripts/devenv_wizard.py` + `make configure`), and rework `README.md` so the tool chain, prerequisites, and all
installed/configured packages are blindingly obvious.

## Requirements & Acceptance Criteria

1. **Pure `make -> conda -> ansible` Tool Chain (No `git`, `curl`, or `uv` Cold-Start Prerequisite)**:
   - `GNU Make >= 3.81` (`make`) is the **sole** cold-start host prerequisite required for any action in `dev-env`.
     `git`, `curl`, and `uv` are not required in `make check` (`git` and `curl` are deferred to Ansible's `packages`
     role; `uv` is only installed for application development).
   - `make bootstrap` installs Miniforge3 (`~/miniforge3/bin/conda`) first if missing (fetching with `curl`, `wget`, or
     `python3` `urllib.request`), and uses `conda install -y -c conda-forge --override-channels` to install
     `python=3.13`, `ansible-core`, `ansible-lint`, and `pyyaml`, then `ansible-galaxy` for `community.general`.
   - `https://astral.sh/uv/install.sh` and `uv tool install` must not appear in `Makefile` or
     `ansible/roles/uv/tasks/main.yml`.
   - `ansible/site.yml` runs `conda` before `uv`; `ansible/roles/uv/tasks/main.yml` installs `uv` and `devenv_uv_tools`
     (`ruff`, `pre-commit`) through `conda` purely as application-dev tools.
2. **Multi-Variant Stow Packages (`devenv_package_variants`)**:
   - Declare `devenv_package_variants` in `ansible/group_vars/all.yml` (`nvim-kickstart`, `nvim-minimal`,
     `nvim-lazyvim`).
   - Load `~/.config/dev-env/choices.yml` in `ansible/roles/bootstrap/tasks/main.yml` when present while falling back to
     defaults in CI/non-interactive runs.
   - Unstow inactive variants (`stow --delete`) before stowing active packages (`stow --no-folding --restow`) and honour
     `devenv_skip_links`.
3. **Host Interactive Pre-Ansible Wizard (`scripts/devenv_wizard.py` + `make configure`)**:
   - Implement `scripts/devenv_wizard.py` collecting OS/distro confirmation, Stow package enablement & variant
     selection, interactive dotfile conflict resolution (`[d]` diff, `[m]` merge via `nvim -d`, `[l]` extract to
     `.local`, `[a]` adopt, `[b]` backup & replace, `[s]` skip), host feature flags (`devenv_set_login_shell`,
     `devenv_install_gui_casks`, `devenv_remove_unmanaged`), and runtime pins into `~/.config/dev-env/choices.yml`.
   - Add `make configure` in `Makefile` and auto-run on interactive TTY `make install` when `choices.yml` is absent.
4. **Blindingly Obvious Tool Chain & Package Inventory (`README.md`)**:
   - Place a clear visual diagram and stage-by-stage table of
     `GNU Make (sole prerequisite) -> Conda -> Ansible -> Wizard -> Converge` at the top of `README.md`.
   - Explicitly document every prerequisite by stage and every installed/configured package, runtime, Conda app-dev tool
     (`uv`, `ruff`, `pre-commit`), Stow package/variant, Fish plugin, Neovim plugin, GUI cask, and purged duplicate.
5. **Tests & World Docs**:
   - Update `holon-config/world/ruleset.md` & `constraints.md`, add `tests/test_wizard.py`, and assert in
     `tests/test_manifest.py` that `astral.sh/uv/install.sh` and `uv tool install` are absent from `Makefile` and
     `ansible/roles/uv`, `conda` precedes `uv` in `ansible/site.yml`, `make check` does not fail without
     `git`/`curl`/`uv`, variants stay consistent, and `README.md` covers all items.
6. **Verification**:
   - `uv run --extra test pytest -m "not network"`
   - `uv run ruff check .`
   - `uv run --extra test ansible-lint ansible/site.yml`
   - `npx prettier --check "**/*.md"`
   - `make check`

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Flow Worktree: `/Users/thomashan/git/dev-env/flow-wizard`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/wizard.json`

## Resolution

Delivered via [PR #5](https://github.com/thomashan/dev-env/pull/5) and merged into `main` (`973f627`):

- **Key Architectural Deliverables**:
  - Enforced the pure `make -> conda -> ansible` bootstrap chain (`GNU Make >= 3.81` as sole cold-start prerequisite;
    `git` and `curl` deferred to Ansible; all Python/Ansible/app-dev installs including `uv` performed via Conda;
    `astral.sh/uv/install.sh` and `uv tool install` removed).
  - Implemented multi-variant GNU Stow packages (`devenv_package_variants`: `nvim-kickstart`, `nvim-minimal`,
    `nvim-lazyvim`) with inactive-variant unstowing (`stow --delete`) and `devenv_skip_links` support.
  - Added the host interactive pre-Ansible wizard (`scripts/devenv_wizard.py` + `make configure`) collecting OS/distro
    confirmation, Stow package/variant selection, interactive dotfile conflict resolution (`[d]` diff, `[m]` merge via
    `nvim -d`, `[l]` `.local` override extraction, `[a]` adopt, `[b]` backup & replace, `[s]` skip), host feature flags,
    and runtime pins into `~/.config/dev-env/choices.yml`.
  - Reworked `README.md` to prominently display the `make -> conda -> ansible -> wizard -> converge` chain diagram,
    prerequisites by stage, and complete package/variant/plugin tables.
- **Verification & Tests**:
  - Added `tests/test_wizard.py` and expanded `tests/test_manifest.py` and `tests/test_templating.py`.
  - 3/3 unanimous ensemble approval (`APPROVED`, 0 open findings on iteration 2) and all 6 GitHub Actions CI checks
    green.
- **Holon Flow Traversal**:
  - **Intent**: `I-1794797329-wizard/_`
  - **Plan**: `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Execution**:
    `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-1794797638-0efc6fff-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Calibration**: `plans/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium_calibration.md` included in
    PR diff (Predicted EV `78.55`, Actual EV `85.77`, Delta `+7.22`).
