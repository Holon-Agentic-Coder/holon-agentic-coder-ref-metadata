---
id: "0309"
title: "Check and skip existing Ansible collections in bootstrap and provide side-by-side diff in wizard"
status: in-progress
created_at: 2026-11-17T15:08:00+11:00
updated_at: 2026-11-17T15:08:00+11:00
tags:
  - dev-env
  - makefile
  - galaxy
  - wizard
  - enhancement
---

# 0309 - Check and skip existing Ansible collections in bootstrap and provide side-by-side diff in wizard

## Problem Statement

1. In `Makefile`, `make bootstrap` unconditionally runs:
   ```makefile
   @ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install \
       -r "$(SELF_DIR)/ansible/requirements.yml" --force || exit 1
   ```
   Passing `--force` causes `ansible-galaxy` to re-download `community.general` from the web every time, even when it is
   already installed in `$(COLLECTIONS)`.
2. `make bootstrap` lacks a directory guard: if `$(COLLECTIONS)/ansible_collections/community/general` is already
   present, it should skip calling `ansible-galaxy` entirely.
3. In `scripts/devenv_wizard.py`, option `[d]` (diff) currently prints unified diff (`+`/`-`), while users need a
   readable side-by-side terminal comparison using `delta --side-by-side` or `diff -y -W $COLUMNS`.

## Scope of Changes

1. **`Makefile`**:
   - In `bootstrap:` target, guard collection installation:
     ```makefile
     @if [ ! -d "$(COLLECTIONS)/ansible_collections/community/general" ]; then \
         echo "Installing Ansible collections..."; \
         ANSIBLE_COLLECTIONS_PATH="$(COLLECTIONS)" "$(GALAXY)" collection install \
             -r "$(SELF_DIR)/ansible/requirements.yml" || exit 1; \
     else \
         echo "Ansible collections: ok (already installed in $(COLLECTIONS))"; \
     fi
     ```
   - Remove `--force` from `ansible-galaxy collection install`.
2. **`scripts/devenv_wizard.py`**:
   - In `format_diff()`: produce side-by-side diff using `delta -s` or `diff -y -W $COLUMNS` when running on an
     interactive terminal, falling back to unified diff.
3. **Tests & Verification**:
   - Add tests in `tests/test_manifest.py` verifying `--force` is not present in collection install command and
     directory check is present.
   - Run test suite (`uv run pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`).
