---
# holon-agentic-coder-ref-metadata-0177
title: "Research the architecture and software principles for the target repos, then spawn beans to action them"
status: todo
type: task
priority: high
tags:
  - architecture
  - research
  - code-quality
  - concurrency
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-28T09:48:30Z
updated_at: 2026-10-28T09:48:30Z
---

## Problem

The maintainer's direction (2026-10-28):

> the files should be organised in such was the behaviour is belongs to the class, the naming should be intention
> revealing, function complexity is low. mutliple agents doing parallel work should minimum affect on other agents (e.g.
> no fille conflicts). find the architecture, software principals and incorporate all the good practices and sumarise

Today the code concentrates behaviour in a few very large modules. On `holon-agentic-coder` main (`fbd3b35`,
`apps/sandbox-executor/src`, about 23,100 lines):

| Module                          | Lines |
| ------------------------------- | ----- |
| `sandbox_executor/flow.py`      | 5,018 |
| `sandbox_executor/cli.py`       | 2,935 |
| `entrypoint/executor.py`        | 1,982 |
| `calibration.py`                | 1,524 |
| `token_reduction/mitm_addon.py` | 1,358 |
| `local_llm.py`                  | 1,048 |

These hot spots are where concurrent flows collide: PRs #94, #95 and #96 all changed `flow.py` and `cli.py`, which
forced 141 review-loop passes of re-review after each merge (Bean 0151). The PR #97 review never converged partly
because a growing diff in the same large files kept surfacing new findings (Bean 0170).

## Goal (research only; this bean changes no code)

Produce one research report, committed to the harness and summarised in this bean, covering both `holon-agentic-coder`
and `holon-coherence`:

1. **Current architecture, measured from real code** (no synthetic data): module and package map, dependency graph
   between modules, the largest classes and functions, cyclomatic/cognitive complexity per function (for example
   `radon cc`/`radon mi` or `ruff` `C901`/`PLR` rules, run in a scratch environment without adding dependencies to the
   targets), naming smells, and git change-coupling hot spots (files most often changed together across flow PRs, from
   `git log`).
2. **Principles and practices**, each with sources and a concrete reading for this codebase:
   - Cohesion: behaviour lives with the data it uses (Tell, Don't Ask; Information Expert; avoiding feature envy and
     anaemic models); single responsibility; small, focused modules and classes.
   - Intention-revealing names (Clean Code, domain-driven ubiquitous language: intent, plan, execution, review,
     calibration, ledger).
   - Low function complexity: thresholds to adopt (for example cyclomatic ≤ 10, function length, argument count), and
     how to enforce them in `uv run task lint` via `ruff` rules already available (no new dependency unless justified).
   - Architecture styles worth comparing: layered / hexagonal (ports and adapters for git, gh, docker, LLM runners),
     package-by-feature versus package-by-layer, one stage per module for the five-stage flow, a plugin or registry for
     agent runners and CLI subcommands.
   - **Parallel-agent friendliness**: a layout that minimises file conflicts between concurrent agents. Examples: one
     file per stage, subcommand or runner; registries assembled from per-file entries instead of one central list; no
     append-hot-spot files besides the three ledgers; small files; stable public interfaces between packages. Relate
     this to the touch-set admission in Bean 0151.
   - Testability (pytest only, Bean 0176), dependency injection at the seams, and keeping production and test layout
     mirrored so a change touches one source file and one test file.
3. **Summary of good practices**: a ranked, concise list of rules the targets should adopt, each with its rationale, the
   measurable check that enforces it, and the expected effect on review convergence and concurrent flows.
4. **Proposed target architecture**: the module or package layout for each repository, with a migration order that keeps
   every step small, reviewable and independently mergeable through the Holon flow (strangler-style extraction, no
   big-bang rewrite).

## Follow-up (required on completion)

When this research bean completes, it MUST spawn new beans, each next sequential id, one per actionable change: for
example "split `flow.py` into one module per stage", "move CLI subcommands into per-command modules with a registry",
"adopt ruff complexity rules with a baseline", "rename X to intention-revealing names". Each spawned bean:

- is sized to run through the five-stage Holon flow as one PR;
- declares the files it expects to touch, so non-overlapping beans can run in parallel and overlapping ones are
  sequenced (sequential overlapping flows);
- lists its dependencies on the other spawned beans with `blocked_by`.

Update `.beans/bean-triage-prioritisation.md` with the new beans and their order.

## Constraints

- Research and report only; no target-repo change in this bean.
- Real measurements only (AGENTS.md item 10).
- Target repos must never reference harness paths, bean ids or review ids in the spawned changes (AGENTS.md rule 12).
- Australian English.
