---
# holon-agentic-coder-ref-metadata-0104
title: "Standardise license to Apache 2.0 across all applications"
status: todo
type: task
priority: normal
tags:
  - license
  - legal
  - governance
  - ecosystem
created_at: 2026-10-17T03:54:00Z
updated_at: 2026-10-17T03:54:00Z
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

- [ ] Add standard `LICENSE` (Apache 2.0) with `Copyright 2026 Holon Agentic Coder Contributors` to
      `holon-agentic-coder`.
- [ ] Add standard `LICENSE` (Apache 2.0) with `Copyright 2026 Holon Agentic Coder Contributors` to
      `holon-agentic-coder-ref-metadata`.
- [ ] Ensure `pyproject.toml` in `holon-agentic-coder` specifies `license = { text = "Apache-2.0" }`.
- [ ] Update documentation and README files across repositories with license notices and badges.
- [ ] Verify formatting with Prettier and run link validation.
