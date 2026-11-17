---
id: "0318"
title: "Remove step letter prefixes from interactive wizard prompts"
status: in-progress
created_at: 2026-11-17T22:55:00+11:00
updated_at: 2026-11-17T22:55:00+11:00
tags:
  - dev-env
  - wizard
  - cli
  - ux
  - enhancement
---

# 0318 - Remove step letter prefixes from interactive wizard prompts

## Problem Statement

When running `make configure`, the interactive host wizard (`scripts/devenv_wizard.py`) outputs prompts with step letter
prefixes:

```text
Step A: Detected macOS (arm64). Package backend [brew]:
Step B: Select Neovim variant (kickstart, lazyvim, minimal) [kickstart]:
Step D: Change login shell to Fish? (true/false) [false]:
```

Because Step C (interactive dotfile conflict resolution) is conditional and only runs when differing files exist, users
see the prompt jump directly from `Step B` to `Step D`, giving the false appearance of a skipped or broken step.

Furthermore, other prompts in the wizard (such as `Install GUI casks?`, `Python version`, and `Default Node.js version`)
do not use step letter prefixes, creating inconsistency in the CLI UX.

## Scope of Changes

1. **`scripts/devenv_wizard.py`**:
   - Remove `Step A: ` prefix from the backend detection prompt.
   - Remove `Step B: ` prefix from the Neovim variant prompt.
   - Remove `Step D: ` prefix from the login shell prompt.
   - Ensure all prompts in `run_wizard()` use clean, direct phrasing without step letter prefixes.
2. **`README.md`**:
   - Align wizard documentation to describe the configuration flow cleanly without relying on "Step A", "Step B", etc.
3. **Tests & Validation**:
   - Update `tests/test_wizard.py` to verify that prompts are invoked cleanly without `Step [A-Z]:` prefixes.
   - Run verification test suite (`make test`, `make lint`, `make check`).
