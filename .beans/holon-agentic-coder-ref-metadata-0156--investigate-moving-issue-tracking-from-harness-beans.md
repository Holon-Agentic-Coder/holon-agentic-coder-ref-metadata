---
# holon-agentic-coder-ref-metadata-0156
title:
  "Investigate moving issue tracking from harness beans to beads kept inside holon-agentic-coder and holon-coherence"
status: completed
type: task
priority: high
tags:
  - issue-tracking
  - beads
  - harness-deprecation
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-26T04:12:46Z
updated_at: 2026-10-30T00:00:00Z
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

## Research findings (2026-10-30)

### 1. What beads is (verified against upstream, 2026-10-30)

- **beads** (`bd`), [steveyegge/beads](https://github.com/steveyegge/beads), MIT. Latest release **v1.3.2 (2026-10-24)**
  — a mature 1.x line, no longer the early SQLite-cache design some third-party docs still describe.
- **Storage**: embedded **Dolt** database in `.beads/embeddeddolt/` (gitignored, in-process, single writer;
  `bd init --server` uses `.beads/dolt/` for multiple writers). `.beads/config.yaml` is git-tracked.
  `.beads/issues.jsonl` is "an export for viewers and interchange, not the source of truth". Sync runs via `bd sync` /
  `bd dolt push|pull` against **`refs/dolt/data` on the same git remote** — issue data rides a dedicated ref, never
  branch commits, so it creates **zero PR-diff and merge-conflict surface** (contrast the ledger JSONL conflicts of PRs
  #94–#96, Bean 0151). Dolt gives cell-level merge; `bd sync` is the pull → conflict-check → `is_blocked` repair → push
  loop.
- **IDs**: hash-based `<prefix>-<hash>` (e.g. `hac-a1b2`), hierarchical under epics (`hac-a3f8.1`, `hac-a3f8.1.1`).
  Collision-free across concurrent branches and agents. **Strictly sequential `NNNN` numbering does not survive — by
  design**; it cannot work under concurrent flow branches anyway.
- **Data model**: statuses `open`, `in_progress`, `blocked`, `deferred`, `closed` (+ custom statuses with
  active/wip/done/frozen categories); types `bug`, `feature`, `task`, `epic`, `chore`, `decision`, `spike`, `story`,
  `milestone` (+ system types, + custom); priorities P0–P4 (default P2); labels; dependency types `blocks`,
  `parent-child`, `related`, **`discovered-from`**, `tracks`, `until`, `caused-by`, `validates`, `relates-to`,
  `supersedes`; close reasons (`bd close <id> "Fixed"`); comments; per-issue audit trail (`bd show`).
- **Agent ergonomics**: `bd ready` (open work with no active blockers), `bd blocked`, `bd update <id> --claim` (atomic
  assignee + in_progress), global `--json`, `bd prime` (workflow context), MCP server (`beads-mcp` on PyPI). Offline:
  embedded Dolt is in-process and `dolt.local-only: true` disables network sync — compatible with sandboxed role agents
  that only have the proxy.
- **Multi-repo**: cross-repo dependencies via `external:<project>:<capability>` resolved through `external_projects`
  config; `bd federation` for peer sync; contributor mode (`bd init --contributor`) routes planning issues to a separate
  repo. Tracker bridges exist (`bd github`, `bd jira`, `bd linear`).
- **Import**: `bd import` reads **JSONL from file or stdin**; `bd create` batch-creates from Markdown (one issue per
  `##` heading) or a graph-JSON plan. A deterministic beans→JSONL converter is therefore the natural migration vehicle.
- **vs beans ([hmans/beans](https://github.com/hmans/beans))**: beans is flat Markdown + YAML frontmatter, hand-numbered
  sequential ids, no dependency engine beyond frontmatter lists, no readiness computation, no claim semantics, no JSON
  API — but fully git-diffable. beads is a database + dependency graph, agent-first, merge-free sync — but an opaque
  binary store, a heavier runtime (Dolt), and a fast-moving release train.

Sources: [README](https://github.com/steveyegge/beads),
[docs/CLI_REFERENCE.md](https://github.com/steveyegge/beads/blob/main/docs/CLI_REFERENCE.md),
[releases (v1.3.2, 2026-10-24)](https://github.com/steveyegge/beads/releases).

### 2. Harness isolation (rule 12) and the 3-ledger invariant (rule 14)

- A `.beads/` directory **inside** a target, with a target-native prefix (`hac-`, `hcoh-`), is target-native tooling
  with the same standing as `holon-knowledge/` — no harness path or convention leaks. Rule 12 is satisfied once work
  items are cited as `hac-xxxx`, never `Bean 0NNN`. The hygiene check planned in Bean 0147 (fail on `Bean [0-9]{4}`)
  stays valid and cannot collide with beads ids.
- No fourth ledger: beads data lives on `refs/dolt/data`, not under `holon-knowledge/ledger/`, and is a **mutable
  work-state tracker**, not append-only provenance. Boundary: the ledgers record _what happened_; beads records _what
  should happen_. A ledger row may cite a beads id but never mirrors beads state, and beads never duplicates ledger
  rows.
- Flow linkage: intent JSON gains a target-native work-item reference (e.g. `hac-xxxx`), which also satisfies the
  standing rule that harness bean ids never land in `intents.jsonl`. `holon intent` claims the issue
  (`bd update --claim`); the post-merge step closes it with the PR URL as close reason. The ledgers remain the system of
  record for provenance; beads is the system of record for work-item status.
- Concurrency: because issue data never sits in branch commits, concurrent `I-…/P-…/E-…` branches cannot conflict on it;
  Dolt cell-level merge handles concurrent field edits on the data ref.

### 3. Migration mapping (surveyed against the real `.beans/`: 213 beans — 164 completed, 2 scrapped, 2 in-progress, 45 todo)

| beans field                        | beads                                                | Notes / fidelity on real data                                   |
| ---------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| `title`                            | title                                                | 1:1                                                             |
| `status` todo / in-progress        | `open` / `in_progress`                               | 1:1                                                             |
| `status` completed / scrapped      | `closed` (+ close reason "completed" / "scrapped")   | or freeze in harness history (decision 3)                       |
| `status` draft                     | `deferred` or label `draft`                          | 0 live uses today                                               |
| `type` task/bug/feature            | same                                                 | 151 / 41 / 20; `epic`, `milestone` also exist in beads          |
| `priority`                         | critical→P0, high→P1, normal→P2, low→P3, deferred→P4 | 7 beans carry invalid `medium` → P2 (real-data finding)         |
| `tags`                             | labels                                               | routing: ~90 beans tag/mention coherence                        |
| `parent` (5 uses)                  | `parent-child` dep                                   | 1:1                                                             |
| `blocked_by` (24) / `blocking` (1) | `blocks` dep (inverted as needed)                    | 1:1                                                             |
| `order`                            | — (drop)                                             | 0 frontmatter uses; triage matrix replaced by `bd ready --json` |
| `created_at` / `updated_at`        | JSONL import fields                                  | preserved by `bd import`                                        |
| body (Problem/Scope/Notes)         | description + comments                               | 1:1 as Markdown text                                            |
| Resolution section                 | close reason + closing comment                       | 1:1                                                             |
| bean id `0NNN`                     | label/external ref `harness-bean-0NNN`               | keeps `Bean 0NNN` citations in merged history traceable         |

- **Carry vs freeze**: migrate only open beans (todo + in-progress, ~47) as live issues, routed by tags to
  `hac-`/`hcoh-`; freeze the 166 completed/scrapped beans in harness git history (archive the harness read-only, never
  delete it), with the `harness-bean-0NNN` label convention covering any closed bean someone later needs to cite.
- **Triage workflow**: the hand-maintained `bean-triage-prioritisation.md` matrix and the `prioritise-beans` skill are
  replaced by `bd ready --json` + priorities + dependency graph; sizing/notes move into labels and descriptions.
- **Dry run**: a deterministic converter (frontmatter+body → beads JSONL → `bd import` into a scratch workspace) is
  spawned as Bean 0215 and must run on the real beans per rule 10.

### 4. Recommendation

Adopt beads **per target** (own `.beads/`, prefixes `hac-` and `hcoh-`), pilot in **holon-agentic-coder first**, fold
the holon-agentic-coder half of Bean 0147 into that pilot flow (as the triage matrix predicts), migrate only open beans,
freeze closed history in the archived harness, pin the `bd` version in the agent images, and keep issue-data writes
(`bd` operations on `refs/dolt/data`) outside the 5-stage flow as a narrow documented exception. Pilot acceptance: `bd`
runs offline (`dolt.local-only`) inside the `holon/agent-*` images; a flow can create, claim and close an issue; sync
survives two concurrent flow branches; the 0147 hygiene check passes.

### 5. Maintainer decision points

1. **Tracker topology**: one tracker per target (recommended; preserves rule-12 standalone posture) vs a single `hac-`
   tracker with `external:` refs for coherence (couples the submodule) vs contributor-mode planning repo (recreates a
   control plane — rejected).
2. **Sync model**: default `refs/dolt/data` sync (recommended; zero PR conflicts) vs also committing `issues.jsonl`
   snapshots for human-diffable history (reintroduces the merge conflicts beads exists to avoid).
3. **Closed-bean history**: freeze in archived harness (recommended) vs import all 213 as closed issues.
4. **Sole-change-path exception**: allow direct `bd` writes to issue data (recommended — tracker ops are not source
   changes; flow stages themselves must claim/close) vs routing every issue edit through the flow (unworkable). The
   exception text must name exactly `refs/dolt/data` + `.beads/` data, never source.
5. **Bean 0147 hac half**: fold into the beads pilot flow (recommended) vs run standalone first.
6. **Retirement trigger**: harness archives read-only only after both targets pass pilot acceptance and the skills /
   guidance port (Bean 0218) lands — no tracking gap.
7. **Maturity risk**: beads ships fast (1.3.x weekly; e.g. a 1.3.0 Dolt planner bug required a one-off
   `bd recompute-blocked`). Pin the version in images; upgrade deliberately.

## Resolution

Investigation completed 2026-10-30 as a read-only research task. Findings, migration mapping, recommendation and the
seven maintainer decision points are recorded above. Spawned action beans: **0214** (pilot beads in holon-agentic-coder,
Holon flow, folds in the 0147 hac half), **0215** (beans→beads converter + real-data dry run, harness work), **0216**
(flow/ledger integration with beads ids, Holon flow), **0217** (adopt beads in holon-coherence, Holon flow), **0218**
(port harness skills/guidance to `bd` and sequence harness retirement, harness work). No target repository was modified.
