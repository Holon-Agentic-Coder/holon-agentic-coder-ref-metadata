---
id: "0311"
title: "Fix Ansible dotfiles and unlink symlink assertion syntax error (.startswith() method syntax)"
status: in-progress
created_at: 2026-11-17T15:11:00+11:00
updated_at: 2026-11-17T15:11:00+11:00
tags:
  - dev-env
  - ansible
  - dotfiles
  - bugfix
---

# 0311 - Fix Ansible dotfiles and unlink symlink assertion syntax error

## Problem Statement

When running `make install` or `make converge`, Ansible failed at:
`TASK [dotfiles : Assert the link manifest is fully satisfied]` with:

```
Syntax error in expression: chunk after expression
Origin: ansible/roles/dotfiles/tasks/main.yml:169:9
```

The expression used `startswith devenv_repo_root` as an infix operator rather than calling the string method
`.startswith(devenv_repo_root)`. The identical syntax error exists in `ansible/playbooks/unlink.yml:62`.

## Scope of Changes

1. **`ansible/roles/dotfiles/tasks/main.yml`**:
   - Fix line 172 to properly call `.startswith(devenv_repo_root)` on the resolved realpath.
2. **`ansible/playbooks/unlink.yml`**:
   - Fix line 62 to properly call `.startswith(devenv_repo_root)` on the resolved realpath.
3. **Tests & Validation**:
   - Run `ansible-playbook --syntax-check` or test suite to ensure assertion syntax parses and evaluates cleanly.
   - Run full verification (`uv run pytest`, `ruff`, `ansible-lint`, `prettier`, `make check`).
