---
# holon-agentic-coder-ref-metadata-0364
title: "Define devenv_user in dev-env, skip WSL GUI terminal wizard prompt, and audit Ansible Jinja variables in tests"
status: completed
type: bug
priority: high
tags:
  - target:dev-env
  - ansible
  - wsl
  - wizard
  - testing
created_at: 2026-11-23T03:35:00Z
updated_at: 2026-11-23T04:20:00Z
pr: https://github.com/thomashan/dev-env/pull/37
---

## Problem

1. **Converge crash (`'devenv_user' is undefined`)**: Running `make install` (or any real non-check-mode converge) in
   `dev-env` fails on `TASK [conda : Verify Conda activation in a clean Fish login shell]` with:

   ```text
   Error while resolving value for 'cmd': 'devenv_user' is undefined
   Origin: ansible/roles/conda/tasks/main.yml:258:3
   ```

   All three clean-shell Conda verification tasks in `ansible/roles/conda/tasks/main.yml` (Fish line 261, Zsh line 297,
   Bash line 333) interpolate `USER="{{ devenv_user }}"`, while `ansible/group_vars/all.yml` only defines `devenv_home`
   and never defines `devenv_user`.

2. **Confusing GUI terminal prompt on WSL**: `scripts/devenv_wizard.py` still asks
   `Install GUI terminal apps (ghostty, warp)? (true/false) [true]:` whenever `chosen_backend == "apt"` with no WSL
   check, even though Ghostty and Warp are unconditionally excluded on WSL in `ansible/roles/packages/tasks/main.yml`.
3. **Test / CI blind spot**: Neither unit tests nor CI caught `'devenv_user' is undefined` because:
   - `tests/test_shell_hooks.py` (`test_conda_role_clean_env_shell_verification_tasks`) only inspects raw YAML
     substrings (`"env -i" in cmd`) without rendering Jinja2 through Ansible's `Templar`.
   - `tests/test_templating.py` only evaluates hand-picked `set_fact` expressions and never renders `command.cmd` task
     templates or sweeps role/playbook task files for undefined variables.
   - `make check-syntax` (`--syntax-check`) only validates YAML/task structure without evaluating Jinja2 expressions.
   - CI `make check-mode` only runs `--tags dotfiles,nvim-sync`, and the clean-shell verify tasks guard on
     `when: [not ansible_check_mode, ...]`.

## Action

Through the 5-stage Holon flow on `dev-env`:

1. **`ansible/group_vars/all.yml`**:
   - Define `devenv_user: "{{ ansible_facts.user_id | default(ansible_facts.env.USER) }}"` directly below
     `devenv_home: "{{ ansible_facts.env.HOME }}"` with a concise comment explaining fact resolution and `env.USER`
     fallback.
2. **`scripts/devenv_wizard.py`**:
   - Add `is_wsl() -> bool`: return `False` unless `platform.system() == "Linux"`, and `True` on Linux when
     `WSL_DISTRO_NAME` or `WSL_INTEROP` is non-empty in `os.environ`, or `"microsoft"` / `"wsl"` appears in
     `platform.release().lower()` or `/proc/version` (ignoring `OSError`).
   - In `run_wizard()`, preserve the literal `existing_choices.get("devenv_install_gui_casks", True)` line (asserted by
     `tests/test_manifest.py:828`), set `install_gui_casks = False` when `is_wsl()` is `True`, and guard the `apt` GUI
     terminal prompt with `elif chosen_backend == "apt" and not wsl:` so WSL never prompts
     `Install GUI terminal apps (ghostty, warp)? (true/false)` and persists `devenv_install_gui_casks: false`.
3. **`tests/test_templating.py`**:
   - Add `test_devenv_user_resolution(templar)` verifying `devenv_user` resolves from `ansible_facts.user_id` and falls
     back to `ansible_facts.env.USER`.
   - Add `test_conda_clean_env_shell_verification_cmd_templates(templar)` rendering all three
     `Verify Conda activation in a clean ... shell` `cmd:` templates from `ansible/roles/conda/tasks/main.yml` through
     the real `templar` fixture (with `ansible_facts` + `devenv_conda_has_<shell>`, and NO manual `devenv_user`
     override) and asserting resolved `HOME="..."` and `USER="..."` values.
   - Add `test_all_role_and_playbook_jinja_variables_are_defined(group_vars, os_vars, alias_tables)` walking every task
     in `role_task_files()` and `ansible/playbooks/*.yml` (all string fields plus bare `when`, `changed_when`,
     `failed_when`, and `assert.that` expressions), parsing Jinja2 ASTs with `jinja2.Environment()` and inspecting AST
     `jinja2.nodes.Name` load nodes (NOT accessing deprecated `Templar.environment` under `ansible-core 2.22`), and
     verifying every top-level referenced variable is declared in `group_vars/all.yml`, `ansible/vars/*.yml`, task
     `register:` / `set_fact` keys, or the explicit Ansible/wizard runtime builtin set (`ansible_facts`,
     `ansible_check_mode`, `ansible_playbook_python`, `playbook_dir`, `item`, `omit`, `lookup`,
     `devenv_selected_variants`, `devenv_skip_links`).
4. **`tests/test_wizard.py`**:
   - Add unit tests for `is_wsl()` across WSL2 kernel release, `WSL_DISTRO_NAME`, `WSL_INTEROP`, `/proc/version`,
     bare-metal Linux, and Darwin with `WSL_DISTRO_NAME`.
   - Patch `scripts.devenv_wizard.is_wsl` to `False` for the Linux `apt` case in
     `test_wizard_gui_apps_prompts_brew_and_apt` so it remains deterministic if pytest runs inside WSL.
   - Add `test_wizard_skips_gui_apps_prompt_on_wsl` verifying interactive mode on WSL omits the Ghostty/Warp GUI
     terminal prompt and persists `devenv_install_gui_casks: False`.
5. Keep `tests/test_manifest.py` untouched (`<= 1,000` lines) and zero `.sh` files outside `dotfiles/examples/`.

## Acceptance Criteria

- Stage 2 plan declares an explicit `## Touch Set` section listing all created/modified repo-relative paths.
- `ansible/group_vars/all.yml` defines `devenv_user` resolving from `ansible_facts.user_id` with
  `ansible_facts.env.USER` fallback.
- `scripts/devenv_wizard.py` detects WSL via `is_wsl()`, skips `Install GUI terminal apps (ghostty, warp)?` on WSL,
  persists `devenv_install_gui_casks: false` on WSL, and keeps `tests/test_manifest.py` passing unchanged.
- `tests/test_templating.py` renders all three Conda clean-shell `cmd` templates via `templar` and audits every Jinja2
  variable across all role task files and `ansible/playbooks/*.yml` with zero deprecation warnings.
- `tests/test_wizard.py` covers `is_wsl()` and verifies WSL interactive runs skip the GUI terminal prompt and write
  `devenv_install_gui_casks: False`.
- `make check-syntax`, `uv run --extra test ruff format --check .`, `uv run --extra test ruff check .`,
  `uv run --extra test ansible-lint`, `npx --yes prettier@3 --check "**/*.md"`, and
  `uv run --extra test pytest -m "not network"` all pass cleanly with zero deprecation warnings.

## Notes

- Target repository: `thomashan/dev-env` (`/Users/thomashan/git/dev-env/main`, at `a9dacf46`).
- Any `dev-env` Holon flow intent JSON MUST instruct the Stage 2 planner to include a `## Touch Set` section listing all
  modified/created repo-relative paths.

## Progress

- 2026-11-23: Wrote `todo/intent-0364-dev-env-user-and-wsl-wizard.json` and launched Holon flow
  `dev-env-user-and-wsl-wizard` off `/Users/thomashan/git/dev-env/main` (`a9dacf46`) with `antigravity-agent` /
  `gemini-4-argon`.
- 2026-11-23: Flow `dev-env-user-and-wsl-wizard` (`antigravity-agent` / `gemini-4-argon`) completed all 5 stages and
  opened [PR #37](https://github.com/thomashan/dev-env/pull/37) (head `686de567`): Stage 4 consensus 3/3 APPROVED (0
  critical, 0 important, 0 nit), Stage 5 calibration included in PR diff (predicted EV 95.02, actual 95.95, delta +0.93;
  touch-set precision/recall 100.0%), all 6 CI checks green (`hygiene`, `make-matrix` `ubuntu-latest` / `macos-latest`,
  `test-network`, `test-unit` `ubuntu-latest` / `macos-latest`), `MERGEABLE`/`CLEAN`, awaiting human maintainer merge.

## Resolution

Completed via [dev-env PR #37](https://github.com/thomashan/dev-env/pull/37) (merged into `main` as `4b1391c3` on
2026-11-23; head `686de567`):

- Defined `devenv_user: "{{ ansible_facts.user_id | default(ansible_facts.env.USER) }}"` in `ansible/group_vars/all.yml`
  directly under `devenv_home`.
- Added `is_wsl()` detection in `scripts/devenv_wizard.py` and updated `run_wizard()` to persist
  `devenv_install_gui_casks: false` and skip the `Install GUI terminal apps (ghostty, warp)?` prompt on WSL while
  preserving `tests/test_manifest.py` unchanged.
- Added `test_devenv_user_resolution`, `test_conda_clean_env_shell_verification_cmd_templates`, and
  `test_all_role_and_playbook_jinja_variables_are_defined` in `tests/test_templating.py`, plus `test_is_wsl_detection`
  and `test_wizard_skips_gui_apps_prompt_on_wsl` in `tests/test_wizard.py`.
- Traversed all 5 Holon flow stages (`antigravity-agent` / `gemini-4-argon`): Stage 4 consensus 3/3 APPROVED (0
  critical, 0 important, 0 nit), Stage 5 calibration included in PR diff (predicted EV 95.02, actual 95.95, delta +0.93;
  touch-set precision/recall 100.0%), all 6 CI checks green.
