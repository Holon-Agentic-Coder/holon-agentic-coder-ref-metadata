---
# holon-agentic-coder-ref-metadata-0306
title:
  "Detect existing conda, bootstrap conda via brew, and add Getting Started & per-tool categories to dev-env README"
status: completed
type: task
priority: high
tags:
  - dev-env
  - readme
  - docs
  - conda
  - makefile
  - ansible
created_at: 2026-11-16T07:58:00Z
updated_at: 2026-11-16T22:21:27Z
---

## Summary

Absorb the follow-up Conda/bootstrap fixes and `README.md` improvements into a single `getting-started` flow on
`thomashan/dev-env`: detect existing Conda installations via `command -v conda` (and `conda info --base`) so Conda is
never reinstalled when already present; use `brew` on both macOS and Linux strictly inside `make bootstrap` (and Conda
role fallback) to install Conda when absent while keeping one system package manager per OS (`brew` on macOS, `apt` on
Linux) for Ansible packages; add a `## Getting Started` section highlighting **`make install`**; fix `` `nvm`/node ``;
and attribute every tool's programming language or functional category across `README.md`.

## Requirements & Acceptance Criteria

1. **Detect Existing `conda` via `command -v conda` & Bootstrap via `brew` When Missing**:
   - In `Makefile`: resolve `CONDA_DIR` dynamically (compatible with GNU Make 3.81) using `command -v conda` ->
     `conda info --base` first, then `/opt/homebrew/Caskroom/miniforge/base`, `/usr/local/Caskroom/miniforge/base`, and
     `$(HOME)/miniforge3`.
   - In `Makefile` `check:`: recognize existing `conda` via `command -v conda` or `[ -x "$(CONDA)" ]`; require `brew` on
     both macOS and Linux and `apt` on Linux.
   - In `Makefile` `bootstrap:`: reuse existing `conda` when `command -v conda` or `[ -x "$(CONDA)" ]` succeeds; if
     missing, install via `"$$brew_bin" install --cask miniforge` (macOS) or `"$$brew_bin" install micromamba` +
     `micromamba create` (Linux), removing `curl` `.sh` downloads and `install curl` fallbacks.
   - In `ansible/roles/conda/tasks/main.yml`: probe `command -v conda` / candidate roots and reuse existing Conda
     without reinstalling; fall back to `brew` (`miniforge` cask on macOS, `micromamba` on Linux) when absent while
     keeping Ansible's `packages` role single-backend per OS (`brew` on macOS, `apt` on Linux).
2. **Intro Fix & `## Getting Started` (`README.md`, `holon-config/world/`)**:
   - Fix `` `nvm`/node `` formatting in line 5 of `README.md` and attribute `fish`, `neovim`, `conda`, and `nvm`.
   - Add `## Getting Started` right after the intro paragraph with Prerequisites (`brew` on macOS/Linux, `apt` on Linux,
     installing `make`/`git` if needed), bare-worktree clone steps, and **`make install`** as the single command that
     kicks off `dev-env`.
   - Update Mermaid diagram, `Stage-by-Stage Execution` table, and `holon-config/world/{ruleset,constraints}.md`.
3. **Explicit Category / Language for Every Tool (`README.md`)**:
   - Add a `Category` column across all 22 core CLI packages in `devenv_packages_core`.
   - Use a structured table in `### 2. Language Runtimes & Conda Tools` and annotate categories/languages across Stow
     packages, Fish plugins (`fisher`, `sdkman-for-fish`, `nvm.fish`), all 26 Neovim (Editor/IDE / Lua) plugins, and
     casks/purged packages.
4. **Tests & Verification**:
   - Update `tests/test_manifest.py` and `tests/test_templating.py` and verify with `pytest -m "not network"`,
     `ruff check .`, `ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Notes

- Target Repository: `thomashan/dev-env`
- Bare Repository: `/Users/thomashan/git/dev-env/.git`
- Main Worktree: `/Users/thomashan/git/dev-env/main`
- Flow Worktree: `/Users/thomashan/git/dev-env/flow-getting-started`
- Intent File: `/Users/thomashan/git/dev-env/main/intents/getting-started.json`

## Resolution

Delivered via [PR #9](https://github.com/thomashan/dev-env/pull/9) and merged into `main` (`fae409b` /
`fae409b56c880d78d617ef8b2c5cdbf064e80f89`):

- **Key Architectural Deliverables**:
  - Updated `Makefile` (`CONDA_DIR`, `check:`, `bootstrap:`), `ansible/roles/conda/tasks/main.yml`, and
    `ansible/roles/homebrew/tasks/main.yml` to detect existing Conda installations via `command -v conda` /
    `conda info --base` (plus standard candidate paths) so existing Conda installs are reused without reinstalling.
  - Streamlined Conda bootstrap via `brew` when missing (`brew install --cask miniforge` on macOS,
    `brew install micromamba` + `micromamba create` on Linux) in `make bootstrap`, removing `curl` `.sh` downloads from
    `Makefile`, while keeping Ansible's `packages` role single-backend per OS (`brew` on macOS, `apt` on Linux).
  - Added a top-level `## Getting Started` section to `README.md` highlighting **`make install`** as the single
    entry-point command, fixed the `` `nvm`/node `` inline formatting, updated the Mermaid diagram / tables / world
    docs, and added explicit Category / Programming Language attribution for every tool across the inventory.
- **Verification & Tests**: Updated `tests/test_manifest.py` and `tests/test_templating.py`; verified with
  `pytest -m "not network"` (`80 passed, 4 deselected`), `ruff check .`, `npx prettier --check "**/*.md"`, `make check`,
  and all 6 GitHub Actions CI checks (`hygiene`, `make-matrix` on macOS/Ubuntu, `test-unit` on macOS/Ubuntu,
  `test-network`).
- **Holon Flow Traversal**: Completed all 5 stages (`I-1794817597-getting-started/_` ->
  `P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium` ->
  `E-1794817852-83fda13c-antigravity-agent-gemini-3.8-flash-medium` -> 3/3 ensemble review approval -> calibration
  `c12c3e4` with Predicted EV `88.74`, Actual EV `91.27`, $\Delta\text{EV} = +2.53$).
