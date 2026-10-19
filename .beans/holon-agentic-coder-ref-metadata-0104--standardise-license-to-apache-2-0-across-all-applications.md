---
# holon-agentic-coder-ref-metadata-0104
title: "Standardise license to Apache 2.0 across all applications"
status: completed
type: task
priority: normal
tags:
  - license
  - legal
  - governance
  - ecosystem
created_at: 2026-10-17T03:54:00Z
updated_at: 2026-10-18T00:22:00Z
---

Standardise the open source license across the entire Holon ecosystem (`holon-agentic-coder`, `holon-coherence`, and
`holon-agentic-coder-ref-metadata`) to the **Apache License 2.0**.

## Context

- `holon-coherence` is already licensed under Apache 2.0 with full license text and `pyproject.toml` declaration
  (`license = { text = "Apache-2.0" }`) with `Copyright 2026 Holon Agentic Coder Contributors`.
- `holon-agentic-coder` and `holon-agentic-coder-ref-metadata` currently lack explicit `LICENSE` files and package
  metadata declarations.
- Standardising on Apache 2.0 across all repositories provides explicit patent grants and retaliation protection,
  trademark protection, and seamless consistency for enterprise adoption.

## Tasks

- [x] Add standard `LICENSE` (Apache 2.0) with `Copyright 2026 Holon Agentic Coder Contributors` to
      `holon-agentic-coder`.
- [x] Add standard `LICENSE` (Apache 2.0) with `Copyright 2026 Holon Agentic Coder Contributors` to
      `holon-agentic-coder-ref-metadata`.
- [x] Ensure `pyproject.toml` in `holon-agentic-coder` specifies `license = { text = "Apache-2.0" }`.
- [x] Update documentation and README files across repositories with license notices and badges.
- [x] Verify formatting with Prettier and run link validation.

## Resolution

- In `holon-agentic-coder`, Apache 2.0 LICENSE file and `pyproject.toml` metadata were standardized in PR #79.
- In `holon-agentic-coder-ref-metadata`, Apache 2.0 LICENSE file was added with
  `Copyright 2026 Holon Agentic Coder Contributors` and referenced in README.md.
