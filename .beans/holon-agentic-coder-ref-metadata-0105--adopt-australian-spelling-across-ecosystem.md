---
# holon-agentic-coder-ref-metadata-0105
title: "Adopt Australian English spelling across all documentation, guidelines, and user-facing copy"
status: todo
type: task
priority: normal
tags:
  - documentation
  - style
  - standards
  - australian-english
created_at: 2026-10-17T03:54:30Z
updated_at: 2026-10-17T03:54:30Z
---

Adopt Australian English (`en-AU`) spelling across all documentation, guidelines, agent instructions, skill
descriptions, commit conventions, and user-facing messages across the Holon ecosystem.

## Context

- Currently, repository documentation mixes US and British/Australian conventions (e.g. `standardize` vs `standardise`,
  `behavior` vs `behaviour`, `synchronize` vs `synchronise`, `licence` (noun) vs `license` (verb), `color` vs `colour`,
  `catalog` vs `catalogue`, `optimize` vs `optimise`).
- Adopting Australian English as the official house style across instructions (`.agents/instructions.md`,
  `.agents/rules.md`, `AGENTS.md`), skills, beans, and UI copy ensures dialectal consistency, readability, and clarity.
- Programmatic code identifiers, standard library symbols, and external API contracts (e.g. `initialize`,
  `Authorization`) must remain preserved to avoid breaking compatibility.

## Tasks

- [ ] Add an orthography guideline in `.agents/instructions.md` specifying Australian English (`en-AU`) as the canonical
      documentation and communication standard.
- [ ] Audit and adjust spellings in core instructions (`AGENTS.md`, `.agents/instructions.md`, `.agents/rules.md`,
      `.agents/workflows.md`, `.agents/coordination.md`).
- [ ] Audit skill descriptions, prompts, and docstrings in `.agents/skills/`.
- [ ] Audit user-facing strings in `holon-coherence` (web interface, CLI help text) and `holon-agentic-coder`.
- [ ] Ensure programmatic identifiers / external API contracts remain unchanged while comments, docstrings, and
      documentation adopt Australian spelling.
- [ ] Format all modified markdown files with Prettier and verify link validation.
