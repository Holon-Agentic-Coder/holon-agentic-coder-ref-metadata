---
# holon-agentic-coder-ref-metadata-0365
title: "Disable expand_argument_vars on dev-env Conda clean-shell command tasks and test via ansible-playbook"
status: completed
type: bug
priority: high
tags:
  - target:dev-env
  - ansible
  - conda
  - wsl
  - testing
created_at: 2026-11-23T04:24:00Z
updated_at: 2026-11-23T04:57:00Z
pr: https://github.com/thomashan/dev-env/pull/38
---

## Problem

Real non-check-mode Ansible converges (such as `make install` on WSL) fail at
`TASK [conda : Verify Conda activation in a clean Fish login shell]` with `rc: 1` and empty `stderr`, while `stdout`
prints the parent `Makefile` / `ansible-playbook` `PATH` instead of the clean Fish shell's `$PATH`:

```text
fatal: [localhost]: FAILED! => {
  "cmd": ["env", "-i", ..., "/usr/bin/fish", "-lc", "type -t conda; echo \"ENV=$CONDA_DEFAULT_ENV\"; string join : $PATH"],
  "rc": 1,
  "stderr": "",
  "stdout": "function\nENV=base\n/opt/homebrew/bin:..."
}
```

**Root cause:** `ansible.builtin.command` defaults to `expand_argument_vars: true`, which calls Python's
`os.path.expandvars()` on each `argv` element using `ansible-playbook`'s own environment after `shlex.split` strips the
single quotes and _before_ `env -i` launches Fish/Zsh/Bash. In `ansible/roles/conda/tasks/main.yml` (Fish line 264, Zsh
line 300, Bash line 336):

1. In Fish, `$PATH` was expanded to one single colon-joined parent `PATH` string and passed to `string join : $PATH`. In
   Fish, `string join` exits `1` whenever fewer than 2 arguments are provided (zero joins performed), failing the task.
2. In Zsh and Bash, `$PATH` was likewise expanded to `ansible-playbook`'s parent `PATH`, silently asserting against
   parent `PATH` instead of the clean shell's `PATH`.

Tests missed this because `tests/test_shell_hooks.py` invokes `subprocess.run(["env", "-i", ...])` directly in Python
(bypassing `ansible.builtin.command`) and CI `make check-mode` only runs `--tags dotfiles,nvim-sync`.

## Action

Through the 5-stage Holon flow on `dev-env`:

1. **`ansible/roles/conda/tasks/main.yml`**:
   - Add `expand_argument_vars: false` under `ansible.builtin.command:` on all three clean-shell verification tasks:
     - `Verify Conda activation in a clean Fish login shell`
     - `Verify Conda activation in a clean Zsh login interactive shell`
     - `Verify Conda activation in a clean Bash login interactive shell`
   - Update the Fish command to use `string join : -- $PATH` defensively so no `PATH` entry starting with `-` can be
     treated as a flag.
2. **`tests/test_toolchain.py`**:
   - Extend `test_ansible_static_task_hygiene()` to strip `{{ ... }}` Jinja blocks from every `ansible.builtin.command`
     `cmd` string and assert `cmd_block.get("expand_argument_vars") is False` whenever the remaining string contains
     shell variable references matching `r"\$[A-Za-z_{]"`.
3. **`tests/test_shell_hooks.py`**:
   - Update `test_conda_role_clean_env_shell_verification_tasks()` to assert
     `verify_task["ansible.builtin.command"].get("expand_argument_vars") is False` for all three shells and
     `"string join : -- $PATH"` in the Fish command.
   - Add `test_ansible_conda_clean_env_shell_verification_playbook(tmp_path: Path)` that executes the actual extracted
     clean-shell verification + assert tasks from `ansible/roles/conda/tasks/main.yml` via real `ansible-playbook`
     (`gather_facts: true`, `vars_files: [ansible/group_vars/all.yml]`, `-e devenv_home=<fake_home>`,
     `-e devenv_conda_dir=<fake_home>/miniforge3`, omitting `-e devenv_user=...`) against
     `_build_hermetic_conda_and_nvm_home(tmp_path)` with a polluted parent environment (`PATH` prefixed with
     `/fake/polluted/makefile/path:` and `CONDA_DEFAULT_ENV=POLLUTED_PARENT_ENV`). Assert `proc.returncode == 0`, zero
     `[DEPRECATION WARNING]` in stderr, Bash assertion execution, and Fish / Zsh assertions when installed (failing
     closed in CI when `CI == "true"` and `HOLON_IN_SANDBOX != "1"`).
4. Keep `tests/test_manifest.py` and `tests/test_templating.py` untouched and zero `.sh` files outside
   `dotfiles/examples/`.

## Acceptance Criteria

- Stage 2 plan declares an explicit `## Touch Set` section listing all created/modified repo-relative paths.
- All three clean-shell Conda verification tasks in `ansible/roles/conda/tasks/main.yml` declare
  `expand_argument_vars: false` under `ansible.builtin.command`, and the Fish task uses `string join : -- $PATH`.
- `tests/test_toolchain.py` enforces `expand_argument_vars: false` on every `ansible.builtin.command` task whose `cmd`
  contains shell `$VAR` references outside `{{ ... }}`.
- `tests/test_shell_hooks.py` asserts `expand_argument_vars: false` on all three tasks and exercises the real extracted
  tasks via `ansible-playbook` against a hermetic fake HOME and polluted parent environment.
- `make check-syntax`, `uv run --extra test ruff format --check .`, `uv run --extra test ruff check .`,
  `uv run --extra test ansible-lint`, `npx --yes prettier@3 --check "**/*.md"`, and
  `uv run --extra test pytest -m "not network"` all pass cleanly with zero deprecation warnings.

## Notes

- Target repository: `thomashan/dev-env` (`/Users/thomashan/git/dev-env/main`, at `4b1391c3`).
- Any `dev-env` Holon flow intent JSON MUST instruct the Stage 2 planner to include a `## Touch Set` section listing all
  modified/created repo-relative paths.

## Progress

- 2026-11-23: Wrote `todo/intent-0365-dev-env-conda-cmd-no-expand.json` and launched Holon flow
  `dev-env-conda-cmd-no-expand` off `/Users/thomashan/git/dev-env/main` (`4b1391c3`) with `antigravity-agent` /
  `gemini-4-argon`.
- 2026-11-23: Flow `dev-env-conda-cmd-no-expand` (`antigravity-agent` / `gemini-4-argon`) completed all 5 stages and
  opened [PR #38](https://github.com/thomashan/dev-env/pull/38) (head `462fd8f3`): Stage 4 consensus 3/3 APPROVED (0
  critical, 0 important, 0 nit), Stage 5 calibration included in PR diff (predicted EV 96.27, actual 97.28, delta +1.01;
  touch-set precision/recall 100.0%), all 6 CI checks green (`hygiene`, `make-matrix` `ubuntu-latest` / `macos-latest`,
  `test-network`, `test-unit` `ubuntu-latest` / `macos-latest`), `MERGEABLE`/`CLEAN`, awaiting human maintainer merge.

## Resolution

Completed via [dev-env PR #38](https://github.com/thomashan/dev-env/pull/38) (merged into `main` as `68ddec98` on
2026-11-23; head `462fd8f3`):

- Set `expand_argument_vars: false` under `ansible.builtin.command:` on all three clean-shell Conda verification tasks
  (Fish, Zsh, Bash) in `ansible/roles/conda/tasks/main.yml`, and switched Fish to `string join : -- $PATH` so
  `ansible-playbook` no longer expands `$PATH` / `$CONDA_DEFAULT_ENV` from the parent environment before `env -i` runs.
- Extended `test_ansible_static_task_hygiene()` in `tests/test_toolchain.py` to require `expand_argument_vars: false` on
  every `ansible.builtin.command` task whose `cmd` contains shell `$VAR` references outside Jinja `{{ ... }}` blocks.
- Updated `test_conda_role_clean_env_shell_verification_tasks()` and added
  `test_ansible_conda_clean_env_shell_verification_playbook()` in `tests/test_shell_hooks.py` to execute the extracted
  Conda verification tasks via real `ansible-playbook` against a hermetic fake HOME with a polluted parent `PATH` and
  `CONDA_DEFAULT_ENV`.
- Traversed all 5 Holon flow stages (`antigravity-agent` / `gemini-4-argon`): Stage 4 consensus 3/3 APPROVED (0
  critical, 0 important, 0 nit), Stage 5 calibration included in PR diff (predicted EV 96.27, actual 97.28, delta +1.01;
  touch-set precision/recall 100.0%), all 6 CI checks green.
