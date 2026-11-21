---
# holon-agentic-coder-ref-metadata-0351
title: "Clean up dev-env Ansible tasks and replace deprecated apt_repository"
status: todo
type: task
priority: high
tags: [target:dev-env]
created_at: 2026-11-21T01:43:13Z
updated_at: 2026-11-21T01:43:13Z
---

## Problem

Running `make configure; make install` (as well as `make check-syntax` and `make check-mode`) in
`/Users/thomashan/git/dev-env/main` under `ansible-core 2.22.0` emits a deprecation warning on every invocation
(including macOS runs, because Ansible loads all role task definitions at playbook parse time):

```text
[WARNING]: Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg.
[DEPRECATION WARNING]: ansible.builtin.apt_repository has been deprecated. Use deb822_repository instead. This feature will be removed from ansible-core version 2.25.
Origin: /Users/thomashan/git/dev-env/main/ansible/roles/packages/tasks/main.yml:174:3

172
173 - name: Add Ghostty PPA on Ubuntu
174   ansible.builtin.apt_repository:
      ^ column 3
```

`make check-syntax` currently checks only `ansible/site.yml` (omitting `ansible/playbooks/unlink.yml`) and exits `0`
even when `[DEPRECATION WARNING]` is printed to `stderr`. Furthermore, a full audit of all Ansible role task files
(`ansible/roles/*/tasks/main.yml`) and `ansible/playbooks/unlink.yml` revealed inconsistent `ansible.builtin.command`
invocation styles (free-form strings vs. structured `cmd:` dicts), missing `changed_when` declarations, and missing
`check_mode: false` declarations on read-only probes (`changed_when: false`) and GNU Stow dry-run tasks (`-n` when
`ansible_check_mode`).

## Action

Through the 5-stage Holon flow on `dev-env`:

1. **`ansible/roles/packages/tasks/main.yml`**
   - Replace deprecated `ansible.builtin.apt_repository` in `Add Ghostty PPA on Ubuntu` (line 173) with
     `ansible.builtin.deb822_repository`:
     - `name: ghostty-ubuntu`
     - `types: [deb]`
     - `uris: [https://ppa.launchpadcontent.net/mkasberg/ghostty-ubuntu/ubuntu]`
     - `suites: ["{{ ansible_facts['distribution_release'] }}"]`
     - `components: [main]`
     - `signed_by: https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x7981725F2B0C9E295E2C368B322003C4710E280B`
     - `state: present`
   - Add `changed_when: true` to `Remove packages that duplicate a managed runtime` (line 23).
   - Convert free-form `ansible.builtin.command: <cmd>` invocations to structured
     `ansible.builtin.command:\n  cmd: <cmd>` in:
     - `Probe Warp terminal binary` (line 64)
     - `Probe Ghostty binary` (line 118)
     - `Probe native Ghostty apt package availability` (line 128)
     - `Probe snap command` (line 150)
     - `Install Ghostty via snap` (line 162)
2. **`ansible/roles/conda/tasks/main.yml`**
   - Add `check_mode: false` to read-only probe tasks (`changed_when: false`):
     - `Probe existing conda in PATH` (line 7)
     - `Probe conda base prefix` (line 70)
     - `Assert conda is runnable` (line 151)
3. **`ansible/roles/dotfiles/tasks/main.yml`**
   - Add `check_mode: false` to:
     - `Locate GNU Stow binary` (line 6)
     - `Unstow inactive variant packages` (line 22, which already passes `{{ '-n' if ansible_check_mode else '' }}`)
     - `Execute GNU Stow to link per-tool dotfiles packages` (line 167, which already passes
       `{{ '-n' if ansible_check_mode else '' }}`)
4. **`ansible/roles/fish/tasks/main.yml`**
   - Add `check_mode: false` to read-only probe tasks (`changed_when: false`):
     - `Syntax-check every fish file now on disk` (line 15)
     - `Report the fish version in use` (line 23)
5. **`ansible/roles/neovim/tasks/main.yml`**
   - Add `check_mode: false` to read-only probe task `Count loaded packages` (line 55).
6. **`ansible/playbooks/unlink.yml`**
   - Add `check_mode: false` to `Locate GNU Stow binary` (line 30).
   - Add `{{ '-n' if ansible_check_mode else '' }}` and `check_mode: false` to
     `Invoke stow to delete all declared variant packages` (line 77).
7. **`Makefile`**
   - Update `check-syntax` (line 243) so it runs `--syntax-check` against both `$(SITE)` and
     `$(SELF_DIR)/ansible/playbooks/unlink.yml`.
8. **`tests/test_toolchain.py` & `tests/test_templating.py`** (keep `tests/test_manifest.py` <= 1,000 lines; it is
   currently at 990 lines)
   - Update `test_linux_packages_gui_terminal_tasks` in `tests/test_toolchain.py` to expect structured
     `ansible.builtin.command.cmd` and `ansible.builtin.deb822_repository` for `Add Ghostty PPA on Ubuntu`.
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

## Acceptance Criteria

- `make check-syntax`, `make lint`, `make check-mode`, and `uv run --extra test pytest -m "not network"` pass with zero
  `[DEPRECATION WARNING]` output.
- Every task file under `ansible/roles/*/tasks/main.yml` and `ansible/playbooks/unlink.yml` satisfies the static task
  hygiene checks (no deprecated APT modules, structured `cmd:` + `changed_when`/`creates` on all
  `ansible.builtin.command` tasks, `check_mode: false` on read-only probes and `ansible_check_mode` stow tasks).
- `tests/test_manifest.py` remains <= 1,000 lines.
- The Stage 2 plan in `dev-env` includes a `## Touch Set` section listing all modified/created repo-relative paths.

## Notes

- Target repository: `thomashan/dev-env` (`/Users/thomashan/git/dev-env/main`, at `d6b07de`).
- Any `dev-env` Holon flow intent JSON MUST explicitly instruct the Stage 2 planner to include a `## Touch Set` section
  listing all modified/created repo-relative file paths.

## Resolution
