---
# holon-agentic-coder-ref-metadata-0156
title:
  "Investigate moving issue tracking from harness beans to beads kept inside holon-agentic-coder and holon-coherence"
status: todo
type: task
priority: high
tags:
  - issue-tracking
  - beads
  - harness-deprecation
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-26T04:12:46Z
updated_at: 2026-10-26T04:12:46Z
---

## Problem

The `holon-agentic-coder-ref-metadata` harness is going to be deprecated. Its `.beans/` directory (155 beans,
`0001`–`0155` at the time of writing; new beans keep landing) is the only issue tracker for both target repositories.
Once the harness is gone, the targets need to track their own work.

The maintainer has decided to move from [beans](https://github.com/hmans/beans) to
[beads](https://github.com/steveyegge/beads) (`bd`). Issues will live **inside** `holon-agentic-coder` and
`holon-coherence`, not in a separate control-plane repository.

This bean is an **extensive investigation** only. It produces a design and a migration plan. It does not migrate
anything or change either target.

## Investigation Scope

### 1. Beads itself (verify against the current upstream release, not memory)

- Current version, licence, install method (Homebrew, `go install`, npm), and whether it runs in the `holon/agent-*`
  images and the `holon-coherence` image.
- Storage model: which files sit in the repo (`.beads/`, JSONL export, SQLite or Dolt database), which are committed and
  which are ignored, and how git sync, merge drivers and hooks work.
- ID scheme: hash-based or prefixed IDs versus this harness's strictly sequential `NNNN` rule. Decide whether sequential
  numbering survives; it likely cannot under concurrent branches.
- Data model: statuses, types, priorities, labels, dependencies (`blocks`, `parent-child`, `related`,
  `discovered-from`), comments and close reasons. Map each to the current beans frontmatter (`status`, `type`,
  `priority`, `tags`, `parent`, `blocking`, `blocked_by`, `created_at`, `updated_at`, `order`).
- Agent ergonomics: `bd ready`, JSON output, any MCP server, and how a sandboxed role agent would query or update issues
  without network access beyond the existing proxy.
- Multi-repo support: whether beads can relate issues across two repositories, and how that works with `holon-coherence`
  as a submodule of `holon-agentic-coder`.

### 2. Placement and ownership

- One `.beads/` per target repository, each with its own prefix (for example `hac-` and `hcoh-`).
- Where cross-cutting issues go, i.e. those spanning both targets or covering the harness's own tooling (images, skills,
  `install-holon`, the mitmproxy sidecar).
- What happens to harness-only beans (`.agents/` guidance, skills, harness workflows) once the harness is gone: migrate,
  re-home into a target, or close as obsolete.

### 3. Interaction with the Holon flow and target invariants

- **Sole Change Path**: the harness exception for directly editable `.beans/` disappears. Decide whether creating or
  closing a beads issue inside a target counts as a target change that must go through the 5-stage flow. If not, define
  a narrow, documented exception, for example `.beads/` only and never source.
- **Intent ↔ issue linkage**: intent JSON and `intents.jsonl` should reference a beads ID. Decide whether `holon intent`
  creates or claims the issue, whether calibration closes it, and whether the ledgers or beads are the system of record
  for status.
- **3-ledger invariant** (AGENTS.md rule 14): beads must not become a fourth ledger or duplicate ledger data. Define the
  boundary between `holon-knowledge/ledger/` and `.beads/`.
- **Concurrent branches**: work out how beads data merges when several flow branches (`I-…/P-…/E-…`) each touch issues.
  Compare with the ledger append conflicts seen on PRs #94–#96 (see Bean 0151).
- **Target isolation** (rule 12): once beads are target-native, the targets still must not reference `.beans/`, `todo/`
  or `.agents/` from the harness. Check overlap with Bean 0147.

### 4. Migration of existing beans

- A field-by-field mapping and a deterministic converter design: frontmatter to beads fields, and the Markdown body
  (Problem, Scope, Notes, Resolution) to description, notes and close reason.
- Routing rules that send each of the 155 beans (plus any logged since) to `holon-agentic-coder`, `holon-coherence`, or
  "not migrated".
- Whether `completed` and `scrapped` beans are imported as closed issues or left only in harness history.
- How each issue keeps its original bean ID as an external reference, so commit messages, PR bodies and ledger rows that
  cite `Bean 0NNN` stay traceable.
- A dry run on **real** beans, not synthetic ones (rule 10). Report the conversion fidelity for each field.

### 5. Agent guidance and harness deprecation

- What moves from `AGENTS.md` and `.agents/` into each target. `holon-coherence` already has its own `.agents/` and
  `AGENTS.md`.
- Skills that read or write beans (for example `install-holon`, `pr-review-loop`, and the triage and prioritisation
  docs) and need rewriting for `bd`.
- An order of operations for retiring the harness without a gap in tracking.

## Deliverables

- An investigation report: tool facts with sources, placement design, flow-integration design, migration mapping and
  dry-run results, risks, and a recommendation.
- A sequenced set of follow-up beans (or, once beads exists in a target, beads issues) for the implementation. Order
  them so that overlapping file sets never run as concurrent flows, because changes to `flow.py`/`cli.py` must not run
  concurrently.
- A pilot recommendation stating which target adopts beads first and the acceptance criteria for that pilot.

## Non-goals

- Installing beads into either target, converting beans, or editing target source in this bean. Target changes go
  through the Holon flow once the design is approved.

## Notes

- Related: Bean 0147 (harness paths tracked in targets), Bean 0151 (touch-set estimation and overlapping flows), Bean
  0152 (decomposition), Bean 0143 (claude runner, needed before flows can run on claude-agent).

## Resolution

Pending.
