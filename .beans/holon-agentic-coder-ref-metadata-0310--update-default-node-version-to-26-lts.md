---
id: "0310"
title: "Update default Node.js version from nvm to latest 26 LTS (v26.13.1 Lithium)"
status: in-progress
created_at: 2026-11-17T15:10:00+11:00
updated_at: 2026-11-17T15:10:00+11:00
tags:
  - dev-env
  - node
  - nvm
  - runtime
---

# 0310 - Update default Node.js version from nvm to latest 26 LTS (v26.13.1 Lithium)

## Problem Statement

The default Node.js version managed via `nvm.fish` in `dev-env` was previously pinned to `22.23.2`. The current active
LTS release for Node.js 26 is `v26.13.1` (codename "Lithium").

## Scope of Changes

1. **`dotfiles/fish/.config/fish/conf.d/00-devenv.fish`**:
   - Update `set -g devenv_node_default_version 26.13.1`.
2. **`scripts/devenv_wizard.py`**:
   - Update fallback `node_version` default from `22.23.2` to `26.13.1`.
3. **`README.md`**:
   - Update table reference from `Node.js 22.23.2` to `Node.js 26.13.1`.
4. **Tests & Validation**:
   - Verify tests in `tests/test_manifest.py` and `tests/test_templating.py` continue to pass.
