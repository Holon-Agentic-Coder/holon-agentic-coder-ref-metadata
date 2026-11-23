---
# holon-agentic-coder-ref-metadata-0351
title:
  "Clean up dev-env Ansible tasks, replace deprecated apt_repository, exclude Ghostty and Warp on WSL, and enable tmux
  mouse scrolling"
status: completed
type: task
priority: high
tags:
  - target:dev-env
  - ansible
  - wsl
  - tmux
  - packages
created_at: 2026-11-21T01:43:13Z
updated_at: 2026-11-23T03:20:00Z
pr: https://github.com/thomashan/dev-env/pull/36
---

## Problem

1. Running `make configure; make install` (as well as `make check-syntax` and `make check-mode`) in
   `/Users/thomashan/git/dev-env/main` under `ansible-core 2.22.0` emits a deprecation warning on every invocation
   (including macOS runs and WSL runs, because Ansible loads all role task definitions at playbook parse time):

```text
[WARNING]: Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg.
[DEPRECATION WARNING]: ansible.builtin.apt_repository has been deprecated. Use deb822_repository instead. This feature will be removed from ansible-core version 2.25.
Origin: /Users/thomashan/git/dev-env/main/ansible/roles/packages/tasks/main.yml:174:3

172
173 - name: Add Ghostty PPA on Ubuntu
174   ansible.builtin.apt_repository:
      ^ column 3
```

2. `make check-syntax` currently checks only `ansible/site.yml` (omitting `ansible/playbooks/unlink.yml`) and exits `0`
   even when `[DEPRECATION WARNING]` is printed to `stderr`. Furthermore, a full audit of all Ansible role task files
   (`ansible/roles/*/tasks/main.yml`) and `ansible/playbooks/unlink.yml` revealed inconsistent `ansible.builtin.command`
   invocation styles (free-form strings vs. structured `cmd:` dicts), missing `changed_when` declarations, and missing
   `check_mode: false` declarations on read-only probes (`changed_when: false`) and GNU Stow dry-run tasks (`-n` when
   `ansible_check_mode`).
3. **WSL Linux GUI terminal install failure**: `devenv_install_gui_casks` defaults to `true` across all platforms in
   `ansible/group_vars/all.yml` without checking for WSL. Because WSL runs on top of a Windows host rather than a
   bare-metal Linux desktop, Ghostty and Warp (`warp-terminal` Linux `apt` fails with `403 Forbidden` fetching Warp's
   `/linux/deb/../../stable/...` `.deb`) cannot/should not be installed inside WSL, and abort `make install` before
   `dotfiles`, `conda`, `node`, `neovim`, and `fish` run. Both Ghostty and Warp should simply be excluded on WSL (no
   `winget.exe` automation needed).
4. **`tmux` mouse scrolling**: `dotfiles/tmux/.tmux.conf` leaves tmux `mouse` at factory default (`off`), so terminals
   like Windows Terminal translate mouse wheel scrolling into arrow-key escape sequences (`^[[B`/`^[OB`/`^[[A`) in
   alternate screen mode instead of scrolling tmux copy-mode.

## Action

Through the 5-stage Holon flow on `dev-env`:

1. **`ansible/roles/bootstrap/tasks/main.yml` (WSL detection)**
   - Compute `devenv_is_wsl` in `Classify host platform` (`devenv_system == 'Linux'` and either `'microsoft'` or `'wsl'`
     in `ansible_facts.kernel | default('') | lower`, or
     `(ansible_facts.env | default({})).WSL_DISTRO_NAME | default('') | length > 0`, or
     `(ansible_facts.env | default({})).WSL_INTEROP | default('') | length > 0`) and include `wsl: {{ devenv_is_wsl }}`
     in `Show resolved plan` (keep `devenv_install_gui_casks: true` and `scripts/devenv_wizard.py` unchanged; no
     `devenv_install_gui_on_wsl` flag).
2. **`ansible/roles/packages/tasks/main.yml`**
   - Replace deprecated `ansible.builtin.apt_repository` in `Add Ghostty PPA on Ubuntu` (line 173) with
     `ansible.builtin.deb822_repository`:
     - `name: ghostty-ubuntu`
     - `types: [deb]`
     - `uris: [https://ppa.launchpadcontent.net/mkasberg/ghostty-ubuntu/ubuntu]`
     - `suites: ["{{ ansible_facts['distribution_release'] }}"]`
     - `components: [main]`
     - `signed_by: https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x7981725F2B0C9E295E2C368B322003C4710E280B`
     - `state: present`
   - Unconditionally exclude Ghostty and Warp when inside WSL by adding `not (devenv_is_wsl | default(false) | bool)` to
     the `when:` list of all 12 Linux `warp-terminal` and `ghostty` tasks (no `winget.exe` tasks and no
     `devenv_install_gui_on_wsl` flag).
   - Add `changed_when: true` to `Remove packages that duplicate a managed runtime` (line 23).
   - Convert free-form `ansible.builtin.command: <cmd>` invocations to structured
     `ansible.builtin.command:\n  cmd: <cmd>` in:
     - `Probe Warp terminal binary` (line 64)
     - `Probe Ghostty binary` (line 118)
     - `Probe native Ghostty apt package availability` (line 128)
     - `Probe snap command` (line 150)
     - `Install Ghostty via snap` (line 162)
3. **`ansible/roles/conda/tasks/main.yml`**
   - Add `check_mode: false` to read-only probe tasks (`changed_when: false`):
     - `Probe existing conda in PATH` (line 7)
     - `Probe conda base prefix` (line 70)
     - `Assert conda is runnable` (line 151)
4. **`ansible/roles/dotfiles/tasks/main.yml`**
   - Add `check_mode: false` to:
     - `Locate GNU Stow binary` (line 6)
     - `Unstow inactive variant packages` (line 22, which already passes `{{ '-n' if ansible_check_mode else '' }}`)
     - `Execute GNU Stow to link per-tool dotfiles packages` (line 167, which already passes
       `{{ '-n' if ansible_check_mode else '' }}`)
5. **`ansible/roles/fish/tasks/main.yml`**
   - Add `check_mode: false` to read-only probe tasks (`changed_when: false`):
     - `Syntax-check every fish file now on disk` (line 15)
     - `Report the fish version in use` (line 23)
6. **`ansible/roles/neovim/tasks/main.yml`**
   - Add `check_mode: false` to read-only probe task `Count loaded packages` (line 55).
7. **`ansible/playbooks/unlink.yml`**
   - Add `check_mode: false` to `Locate GNU Stow binary` (line 30).
   - Add `{{ '-n' if ansible_check_mode else '' }}` and `check_mode: false` to
     `Invoke stow to delete all declared variant packages` (line 77).
8. **`dotfiles/tmux/.tmux.conf`**
   - Add `set -g mouse on` with a concise comment noting mouse wheel scrolling enters copy-mode instead of sending
     arrow-key escape sequences in alternate screen mode (and holding `Shift` selects natively).
9. **`Makefile`**
   - Update `check-syntax` (line 243) so it runs `--syntax-check` against both `$(SITE)` and
     `$(SELF_DIR)/ansible/playbooks/unlink.yml`.
10. **`tests/test_toolchain.py` & `tests/test_templating.py`** (keep `tests/test_manifest.py` <= 1,000 lines; it is
    currently at 990 lines)
    - Update `test_linux_packages_gui_terminal_tasks` in `tests/test_toolchain.py` to expect structured
      `ansible.builtin.command.cmd`, `ansible.builtin.deb822_repository` for `Add Ghostty PPA on Ubuntu`, the
      unconditional `not (devenv_is_wsl | default(false) | bool)` guard on all 12 Linux Warp/Ghostty tasks, and no
      `devenv_install_gui_on_wsl` flag.
    - Add assertions in `tests/test_toolchain.py` verifying:
      - `set -g mouse on` is present in `dotfiles/tmux/.tmux.conf`.
      - `ansible/roles/bootstrap/tasks/main.yml` defines `devenv_is_wsl`.
      - Zero `winget.exe` tasks and zero `devenv_install_gui_on_wsl` references exist in
        `ansible/roles/packages/tasks/main.yml`.
    - Add a static task hygiene test in `tests/test_toolchain.py` asserting across all `role_task_files()` and
      `ansible/playbooks/unlink.yml`:
      - No task uses deprecated modules (`ansible.builtin.apt_repository`, `ansible.builtin.apt_key`, `apt_repository`,
        `apt_key`).
      - Every `ansible.builtin.command` task uses a mapping with `cmd:` (never a free-form string) and declares
        `changed_when` or `creates`.
      - Every read-only probe task (`changed_when: false`) and every `stow` task using `ansible_check_mode` declares
        `check_mode: false`.
    - Add a regression test in `tests/test_templating.py` that runs `ansible-playbook --syntax-check` against
      `ansible/site.yml` and `ansible/playbooks/unlink.yml` with `ANSIBLE_DEPRECATION_WARNINGS=True` and asserts return
      code `0` and zero `[DEPRECATION WARNING]` output in `stderr`.
    - Add Jinja2 templating tests in `tests/test_templating.py` verifying `devenv_is_wsl` evaluates `True` on WSL facts
      (`microsoft-standard-WSL2` kernel or `WSL_DISTRO_NAME=Ubuntu`) and `False` on standard Linux and macOS facts.

## Acceptance Criteria

- `make check-syntax`, `make lint`, `make check-mode`, and `uv run --extra test pytest -m "not network"` pass with zero
  `[DEPRECATION WARNING]` output.
- Ghostty and Warp Linux GUI terminal tasks are unconditionally excluded on WSL (`not devenv_is_wsl`; no `winget.exe`
  tasks and no `devenv_install_gui_on_wsl` flag).
- `dotfiles/tmux/.tmux.conf` sets `set -g mouse on`.
- Every task file under `ansible/roles/*/tasks/main.yml` and `ansible/playbooks/unlink.yml` satisfies the static task
  hygiene checks (no deprecated APT modules, structured `cmd:` + `changed_when`/`creates` on all
  `ansible.builtin.command` tasks, `check_mode: false` on read-only probes and `ansible_check_mode` stow tasks).
- `tests/test_manifest.py` remains <= 1,000 lines.
- The Stage 2 plan in `dev-env` includes a `## Touch Set` section listing all modified/created repo-relative paths.

## Notes

- Target repository: `thomashan/dev-env` (`/Users/thomashan/git/dev-env/main`, at `425ff6fe`).
- Bundles all remaining unstarted `dev-env` work (Ansible cleanup/`deb822_repository`, unconditional WSL exclusion of
  Ghostty and Warp, and `tmux` mouse scrolling) into this single bean.
- Note: PR #33's clean-shell Conda probes in `ansible/roles/conda/tasks/main.yml` already declare `changed_when: false`
  and `check_mode: false`.
- Any `dev-env` Holon flow intent JSON MUST explicitly instruct the Stage 2 planner to include a `## Touch Set` section
  listing all modified/created repo-relative file paths.

## Progress

- 2026-11-23: First run (`dev-env-ansible-wsl-tmux`) opened PR #34 (head `1afad1a`), and second run
  (`dev-env-ansible-wsl-winget`) opened PR #35; both were closed unmerged per maintainer simplification: drop
  `devenv_install_gui_on_wsl` and `winget.exe` automation and simply exclude Ghostty and Warp when running on WSL.
- 2026-11-23: Wrote `todo/intent-0351-dev-env-ansible-wsl-skip.json` and launched fresh Holon flow
  `dev-env-ansible-wsl-skip` off `/Users/thomashan/git/dev-env/main` (`425ff6fe`) using `antigravity-agent` /
  `gemini-4-argon`.
- 2026-11-23: Flow `dev-env-ansible-wsl-skip` (`antigravity-agent` / `gemini-4-argon`) completed all 5 stages and opened
  [PR #36](https://github.com/thomashan/dev-env/pull/36) (head `cae95be`): Stage 4 consensus APPROVED 3/3 at iteration 2
  (0 critical, 0 important, 0 nit), Stage 5 calibration report included in PR diff (predicted EV 92.83, actual 94.64,
  delta +1.81; touch-set precision/recall 100%), all 6 post-calibration CI checks green (`hygiene` 44s, `make-matrix`
  `macos-latest` 2m29s / `ubuntu-latest` 59s, `test-network` 20s, `test-unit` `macos-latest` 2m55s / `ubuntu-latest`
  46s), `MERGEABLE`/`CLEAN`, awaiting human maintainer merge.

## Resolution

Completed via [dev-env PR #36](https://github.com/thomashan/dev-env/pull/36) (merged into `main` as `a9dacf46` on
2026-11-23; head `cae95be`, superseding closed PRs #34 and #35):

- Replaced deprecated `ansible.builtin.apt_repository` in `ansible/roles/packages/tasks/main.yml` with
  `ansible.builtin.deb822_repository` (`ghostty-ubuntu`), eliminating all `ansible-core 2.22.0` deprecation warnings.
- Added `devenv_is_wsl` detection in `ansible/roles/bootstrap/tasks/main.yml` and unconditionally excluded all 12 Linux
  Ghostty and Warp tasks when `devenv_is_wsl` is true (`not (devenv_is_wsl | default(false) | bool)`).
- Cleaned up Ansible task hygiene across `packages`, `conda`, `dotfiles`, `fish`, `neovim`, and
  `ansible/playbooks/unlink.yml` (structured `cmd:`, `changed_when`, `check_mode: false` on read-only probes and dry-run
  stow tasks), expanded `Makefile` `check-syntax` to cover `unlink.yml`, and enabled `set -g mouse on` in
  `dotfiles/tmux/.tmux.conf`.
- Added static task hygiene, `devenv_is_wsl` templating, and zero-deprecation `--syntax-check` regression tests in
  `tests/test_toolchain.py` and `tests/test_templating.py` while keeping `tests/test_manifest.py` <= 1,000 lines.
- Traversed all 5 Holon flow stages (`antigravity-agent` / `gemini-4-argon`): Stage 4 consensus 3/3 APPROVED at
  iteration 2 (0 critical, 0 important, 0 nit), Stage 5 calibration included in PR diff (predicted EV 92.83, actual
  94.64, delta +1.81; touch-set precision/recall 100%), all 6 CI checks green.
