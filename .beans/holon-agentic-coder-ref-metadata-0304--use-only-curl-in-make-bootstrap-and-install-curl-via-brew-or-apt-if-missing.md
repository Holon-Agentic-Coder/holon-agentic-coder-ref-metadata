---
# holon-agentic-coder-ref-metadata-0304
title: "Use only curl in make bootstrap and install curl via brew or apt if missing"
status: completed
type: task
priority: high
tags:
  - dev-env
  - makefile
  - bootstrap
  - curl
created_at: 2026-11-16T03:51:00Z
updated_at: 2026-11-16T05:10:00Z
---

## Summary

Keep `make bootstrap` in `thomashan/dev-env` as minimal as possible by fetching the Miniforge3 installer using **only
`curl`**, removing the `wget` and `python3 urllib.request` fallbacks, installing `curl` via `brew` (macOS) or `apt`
(Linux) if missing, and using `apt` everywhere instead of `apt-get`. Also require Conda's `python3` in `make configure`
rather than falling back to system `python3`.

## Requirements & Acceptance Criteria

1. **`Makefile` (`check`, `bootstrap`, & `configure`)**:
   - Replace all `apt-get` references with `apt` (`apt install -y make` and probing `command -v apt` in `make check`).
   - Remove `wget` and `python3 urllib.request` download fallbacks from `make bootstrap`.
   - If `curl` is missing when downloading the Miniforge3 installer, install `curl` via `brew` (`brew install curl` on
     `Darwin`) or `apt` (`apt update && apt install -y curl` on `Linux`, using `sudo` when not root), then fetch
     Miniforge3 with `curl -fsSL`.
   - Require `$(CONDA_DIR)/bin/python3` in `make configure` instead of falling back to system `python3`.
2. **`ansible/roles/packages/tasks/main.yml`, `README.md`, & `holon-config/world/constraints.md`**:
   - Replace `'apt-get remove -y '` with `'apt remove -y '` in `ansible/roles/packages/tasks/main.yml`.
   - Update `README.md` and `holon-config/world/constraints.md` to replace `apt-get` with `apt` and reflect `curl`-only
     Miniforge download with automatic `brew` / `apt` `curl` install (removing `wget` and `python3 urllib` mentions).
3. **Tests**:
   - Add `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt()` and `test_no_apt_get_in_repo()` in
     `tests/test_manifest.py` verifying `wget` and `urllib.request` are absent from `Makefile`, `apt-get` is absent from
     `Makefile`, `ansible/roles/packages/tasks/main.yml`, `README.md`, and `holon-config/world/constraints.md`, and that
     `curl -fsSL`, `brew` `install curl`, and `apt install -y curl` are present in `Makefile`'s `bootstrap` target.
4. **Verification**:
   - `uv run --extra test pytest -m "not network"`
   - `uv run ruff check .`
   - `uv run --extra test ansible-lint ansible/site.yml`
   - `npx prettier --check "**/*.md"`
   - `make check`

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Flow Worktree: `/Users/thomashan/git/dev-env/flow-curl`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/curl.json`

## Resolution

Delivered via [PR #6](https://github.com/thomashan/dev-env/pull/6) and merged into `main` (`d148d20`):

- **Key Architectural Deliverables**:
  - Simplified `make bootstrap` in `Makefile` to use **only `curl`** when downloading the Miniforge3 installer, removing
    the `wget` and `python3 urllib.request` fallbacks and automatically installing `curl` via `brew` (macOS) or `apt`
    (Linux) when missing.
  - Replaced all `apt-get` usage across `Makefile`, `ansible/roles/packages/tasks/main.yml`, `README.md`, and
    `holon-config/world/constraints.md` with `apt`.
  - Required `$(CONDA_DIR)/bin/python3` in `make configure` instead of falling back to host `python3`.
- **Verification & Tests**:
  - Added `test_makefile_bootstrap_uses_only_curl_and_installs_curl_via_brew_or_apt()` and `test_no_apt_get_in_repo()`
    in `tests/test_manifest.py`.
  - Unanimous 3/3 ensemble review approval (`APPROVED`) and all 6 GitHub Actions CI checks green.
- **Holon Flow Traversal**:
  - **Intent**: `I-1794801434-curl/_`
  - **Plan**: `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Execution**:
    `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-1794801664-21f0fec4-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Calibration**: `plans/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium_calibration.md` included in
    PR diff (Predicted EV `84.88`, Actual EV `88.52`, Delta `+3.64`).
