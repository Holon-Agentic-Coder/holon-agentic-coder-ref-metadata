---
# holon-agentic-coder-ref-metadata-0116
title: "Align Makefile targets and build-image aliases across holon-coherence and holon-agentic-coder"
status: completed
type: task
priority: normal
tags:
  - makefile
  - build
  - devex
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-17T06:58:00Z
updated_at: 2026-10-17T14:00:00Z
---

## Summary

Align Makefile targets, aliases, toolbelt inspection, and linting tasks between `holon-agentic-coder` and
`holon-coherence`. Specifically, provide bidirectional `build-image` and `build-images` aliases so commands work
identically across both repositories, port OS toolbelt inspection (`tools`) and file hygiene linters (`lint`,
`lint-json`, `lint-yaml`, `lint-shell`, `lint-md`) to `holon-coherence`, and harmonise help output.

## Context & Problem Statement

Currently, developers switching between `holon-agentic-coder` and `holon-coherence` encounter conflicting target names
and missing aliases:

1. **`build-image` vs `build-images` Mismatch**:
   - In `holon-agentic-coder`, the target is named `build-images` (plural). Running `make build-image` fails with:
     ```text
     make: *** No rule to make target `build-image'.  Stop.
     ```
   - In `holon-coherence`, the target is named `build-image` (singular). Running `make build-images` similarly fails.
   - Both repositories should accept both `make build-image` and `make build-images` as interchangeable aliases.

2. **Missing Toolbelt and Linting Targets in `holon-coherence`**:
   - `holon-agentic-coder/Makefile` provides comprehensive tool inspection and repo hygiene targets:
     - `make tools`: Inspects and prints paths and versions of `git`, `jq`, `shellcheck`, `uv`, `gh`, `npx`, `openssl`.
     - `make lint`: Composite linter running JSON, YAML, Shell, Markdown, and Python linters.
     - `make lint-json`, `make lint-yaml`, `make lint-shell`, `make lint-md`: Specific file validators.
   - `holon-coherence/Makefile` currently lacks `tools` and all `lint-*` targets, forcing developers to run manual
     commands or rely solely on CI workflows.

3. **Inconsistent Help Output**:
   - Help text formatting, target ordering, and descriptions differ between the two Makefiles.

## Comparison Matrix

| Target / Alias        | `holon-agentic-coder` | `holon-coherence`  | Target State (Both Repos)            |
| --------------------- | --------------------- | ------------------ | ------------------------------------ |
| `build-image`         | ❌ Missing            | ✅ Present         | ✅ Supported (alias or primary)      |
| `build-images`        | ✅ Present            | ❌ Missing         | ✅ Supported (alias or primary)      |
| `check-prerequisites` | ✅ Present            | ✅ Present         | ✅ Supported                         |
| `prerequisites`       | ✅ Present (alias)    | ✅ Present (alias) | ✅ Supported (alias)                 |
| `check-docker`        | ✅ Present            | ✅ Present         | ✅ Supported                         |
| `install-docker`      | ✅ Present            | ✅ Present         | ✅ Supported                         |
| `install-homebrew`    | ✅ Present            | ✅ Present         | ✅ Supported                         |
| `install-miniforge`   | — (uv native)         | ✅ Present         | Preserved in `holon-coherence`       |
| `create-conda-env`    | — (uv native)         | ✅ Present         | Preserved in `holon-coherence`       |
| `activate-conda-env`  | — (uv native)         | ✅ Present         | Preserved in `holon-coherence`       |
| `tools`               | ✅ Present            | ❌ Missing         | ✅ Supported in both repos           |
| `lint`                | ✅ Present            | ❌ Missing         | ✅ Supported in both repos           |
| `lint-json`           | ✅ Present            | ❌ Missing         | ✅ Supported in both repos           |
| `lint-yaml`           | ✅ Present            | ❌ Missing         | ✅ Supported in both repos           |
| `lint-shell`          | ✅ Present            | ❌ Missing         | ✅ Supported in both repos           |
| `lint-md`             | ✅ Present            | ❌ Missing         | ✅ Supported in both repos           |
| `help`                | ✅ Present            | ✅ Present         | ✅ Supported and formatted uniformly |

## Tasks & Scope

### 1. `holon-agentic-coder` (via Holon Flow)

- [x] Add `build-image: build-images` alias and declare it in `.PHONY`.
- [x] Update `help` target in `Makefile` and relevant documentation (e.g., `README.md`) to document `build-image`.
- [x] Route the change through the 5-stage Holon flow (Intent -> Plan -> Execute -> Review Loop -> Calibration).

### 2. `holon-coherence` (via dedicated worktree)

- [x] Add `build-images: build-image` alias and declare it in `.PHONY`.
- [x] Port the `tools` target from `holon-agentic-coder` to verify and display toolbelt dependencies (`git`, `jq`,
      `shellcheck`, `uv`, `gh`, `npx`, `openssl`).
- [x] Port `lint`, `lint-json`, `lint-yaml`, `lint-shell`, and `lint-md` targets into `Makefile`, configuring
      `TARGET_DIR` / `DIR` / `LINT_TARGET` filtering appropriate for `holon-coherence`.
- [x] Update `help` target to list new targets cleanly.
- [x] Verify execution of `make build-image`, `make build-images`, `make tools`, and `make lint` in a clean worktree.

### 3. Harness & Metadata

- [x] Format markdown with Prettier (`npx prettier --write "**/*.md"`).
- [x] Validate relative links using `node .agents/scripts/validate-links.js`.

## Resolution

- In `holon-coherence`: PR [#24](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/24) ported `build-images`
  alias, `tools`, and `lint` targets (`lint-json`, `lint-yaml`, `lint-shell`, `lint-md` with `--no-config` Prettier),
  with full unit test coverage in `tests/test_makefile.py`. Unanimously approved by 3-agent ensemble.
- In `holon-agentic-coder`: Routed through the 5-stage Holon flow, adding `build-image: build-images` alias, `.PHONY`
  entry, `make help` entry, and tests in `test_makefile.py` in PR
  [#82](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/82). Calibration executed and included in PR.
  Unanimously approved by 3-agent ensemble.
