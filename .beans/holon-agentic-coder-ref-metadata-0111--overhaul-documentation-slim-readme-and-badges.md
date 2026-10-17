---
# holon-agentic-coder-ref-metadata-0111
title: "Overhaul repository documentation with slimmed-down README, build badges, and structured reference"
status: todo
type: task
priority: normal
tags:
  - documentation
  - readme
  - ux
  - devex
  - badges
created_at: 2026-10-17T04:31:00Z
updated_at: 2026-10-17T04:31:00Z
---

Overhaul the repository documentation by replacing the bloated root `README.md` with a clean, highly structured,
at-a-glance landing page, relocating comprehensive architectural deep dives into `docs/`, and adding build badges and
quick-start instructions.

## Context

- The current root `README.md` is lengthy and mixes quick-start instructions, low-level git worktree mechanics,
  historical bootstrap explanations, multi-agent protocol details, and architectural rationale into a single wall of
  text.
- A well-structured repository landing page should provide immediate clarity within 30–60 seconds:
  1. Status and quality badges (CI build status, Prettier hygiene, Apache 2.0 license, link validation).
  2. Concise 1-paragraph summary of what the repository is and its role in the Holon ecosystem.
  3. Key capabilities and recent architectural improvements at a quick glance.
  4. Quick getting started guide for developers and autonomous agents.
  5. Clean visual navigation matrix linking to specialized guides (`AGENTS.md`, `.agents/instructions.md`,
     `docs/architecture.md`).
- The detailed architectural specifications, directory layout reference, and deep operational background must be
  systematically moved to a dedicated reference document (e.g. `docs/architecture-overview.md`) so no depth is lost.

## Tasks

- [ ] Design and author a slimmed-down, highly readable root `README.md`:
  - Add build and hygiene status badges at the top (GitHub Actions CI, Apache-2.0 License, Prettier style, Python
    3.12+).
  - Add "At a Glance" elevator pitch explaining the reference metadata and harness control plane.
  - Add structured "Key Capabilities & Improvements" highlights table.
  - Add streamlined "Quick Getting Started" (prerequisites, setup commands, worktree initialization).
  - Add clean navigation links to deep documentation (`docs/`, `AGENTS.md`, `.beans/`).
- [ ] Relocate comprehensive technical reference from existing `README.md` into `docs/architecture-overview.md`.
- [ ] Ensure all relative links, markdown references, and agent skill links remain valid.
- [ ] Format with Prettier (`npx prettier --write "**/*.md"`) and verify link validation
      (`node .agents/scripts/validate-links.js`).
