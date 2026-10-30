---
# holon-agentic-coder-ref-metadata-0177
title: "Research the architecture and software principles for the target repos, then spawn beans to action them"
status: completed
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
updated_at: 2026-10-29T12:20:00Z
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

## Research findings (2026-10-29)

Measured on `origin/main` snapshots exported with `git archive` (holon-agentic-coder `993b686`, holon-coherence
`68fdf67`) into a scratch directory, with `uvx radon cc -j` / `radon mi`, `uvx ruff check --isolated --no-cache`, `grep`
for imports and process calls, `git log` churn and `gh pr view --json files` for PRs #94-#109 and coherence #24-#31.
Real code only; no synthetic data.

### 1. Current architecture

| Repository          | Source                 | Tests        | Functions | CC > 10 (ruff C901) | Avg CC (radon) | Functions > 100 lines |
| ------------------- | ---------------------- | ------------ | --------- | ------------------- | -------------- | --------------------- |
| holon-agentic-coder | 37 files, 25,033 lines | 34,612 lines | 672       | 56                  | B (6.7)        | 35 (9 over 200)       |
| holon-coherence     | 25 files, 9,211 lines  | 10,185 lines | 209       | 38                  | B (8.7)        | 14 (3 over 200)       |

holon-agentic-coder (`apps/sandbox-executor/src/sandbox_executor/`) is a flat package with one god module per concern.
`flow.py` (5,157 lines, 94 free functions, 7 classes that are mostly data holders) holds the checkpoint, ledger
reconciliation, git helpers, GitHub PR/CI calls, intent validation, all five stages, the review loop and the pipeline
engine. Its function inventory falls into those nine clusters, which are the natural module seams.

| Module (lines)                   | Max CC | Internal imports | What is wrong                                                                                                |
| -------------------------------- | ------ | ---------------- | ------------------------------------------------------------------------------------------------------------ |
| `flow.py` (5,157)                | 131    | 17               | Nine concerns in one file; 14 raw `gh` calls; lazy-imports `cli` four times (cycle)                          |
| `cli.py` (2,962)                 | 114    | 19               | `main` is 1,097 lines: all 21 sub-parsers and handlers inline; also hosts docker launch and sidecar plumbing |
| `entrypoint/executor.py` (2,270) | 178    | 22               | `main` 798 lines; 81 raw `git` subprocess calls bypass `git.py`; imports the host engine (`flow`) five times |
| `calibration.py` (1,524)         | 61     | 5                | `parse_actual_metrics` 226 lines, CC 61                                                                      |
| `token_reduction/` (2,819)       | 85     | -                | Diverged copy of holon-coherence's proxy; production uses only `generate_root_ca`                            |
| `ledger.py` (806)                | 53     | -                | `query_ledger` CC 53                                                                                         |
| `agent_runner.py` (598)          | 31     | -                | `StandardAgentRunner.validate` is an if-chain per agent; agent facts also live in `agent_defaults` dicts     |

Coupling: `cli` imports `flow` at top level and `flow` imports `cli` lazily (`detect_holon_coherence`,
`dispatch_role_agent`, `get_host_proxy_envs`, `teardown_token_reduction_proxy`): a cycle. Container entrypoints
(`executor`, `planner`, `intent_creator`, `review_loop`) import the host orchestrator `flow` for `reconcile_ledgers`,
`check_and_resolve_stage_conflicts` and `failed_partial_head`, so an in-container change and a host change meet in the
same file. Highest fan-in: `redaction` (12), `knowledge` (10), `ledger` (9).

holon-coherence already has a `commands/` package (one handler module per command), but every parser still lives in
`cli.main` (349 lines), and handlers resolve the CLI module through `_dispatch.get_cli()` (a `sys.modules` lookup kept
for test patching). `mitm_addon.py` (2,348 lines) holds scrubbing, wire logging, timing, metrics, routing, Anthropic
normalisation, Gemini/OpenAI translation, the dashboard and the addon. Provider branching is repeated across
`payload_cleaner` (`_clean_openai` CC 32, `_clean_gemini` CC 32), `parsers/sse` (`extract_sse_token_counts` 192 lines,
CC 85), `parsers/tokens` (CC 28) and `hybrid_cache` (CC 31, 30).

### 2. Measured hotspots (churn x complexity, Tornhill)

| File                      | Commits touching (all / since 2026-10-01) | Flow PRs #94-#109 touching        | Worst function (lines, CC)         |
| ------------------------- | ----------------------------------------- | --------------------------------- | ---------------------------------- |
| three ledgers             | 59 / 45                                   | 15 (append-only, out of scope)    | -                                  |
| `flow.py`                 | 27 / 26                                   | 7: #94 #95 #96 #97 #100 #102 #108 | `run_review_loop` (528, 131)       |
| `tests/test_flow.py`      | 24 / 23                                   | 8                                 | 5,798-line test file               |
| `cli.py`                  | 31 / 18                                   | 6: #94 #95 #96 #97 #100 #102      | `main` (1,097, 114)                |
| `entrypoint/executor.py`  | 23 / 17                                   | 5: #94 #95 #96 #97 #108           | `main` (798, 178)                  |
| `docs/ledger_schema.md`   | 21 / 11                                   | 6                                 | -                                  |
| `calibration.py`          | - / 11                                    | -                                 | `parse_actual_metrics` (226, 61)   |
| coherence `cli.py`        | 18                                        | -                                 | `main` (349, 31)                   |
| coherence `mitm_addon.py` | 12                                        | -                                 | `MitmproxyAddon.request` (209, 65) |
| coherence workflows (5)   | -                                         | #24, #25, #30 each touched all 5  | CI timing step pasted per workflow |

Inside `flow.py` the seven PRs collided on the same few functions (hunk headers): `run_review_stage` and
`run_review_loop` (4 PRs each), `run_execute_stage` and `FlowContext.to_dict/from_dict` (3 each). Sync merges with
`main`: #94 5, #95 3, #96, #97, #106-#109 1 each; Bean 0151 counts 141 re-review passes from those syncs. `FlowContext`
is a shared record every stage extends, so it is a conflict magnet in its own right.

Naming: 26 functions named `run*`, 22 `get*`, five `main`s (each a whole program); `run_review_loop_cli` lives in the
engine; `_dispatch.get_cli` names a mechanism, not an intent. Tests mirror the god modules (`test_flow.py` 5,798,
`test_executor.py` 5,088, `test_token_reduction.py` 3,734, coherence `test_cli.py` 3,728).

### 3. Principles and how each applies here

| Principle (source)                                                                 | Reading for these repositories                                                                                                                                           |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Information hiding (Parnas 1972 [1])                                               | One module per design decision likely to change: a stage, a CLI command, a runner, a provider format, the `gh` and `git` adapters.                                       |
| Information Expert / Tell, Don't Ask; anaemic model smell (Larman [2], Fowler [3]) | `FlowCheckpoint` saves, loads and migrates itself; the review loop is an object whose steps read its own state instead of 500 lines of locals.                           |
| SRP and Common Closure Principle (Martin [4])                                      | Things that change together live together: a stage's code and test in one module pair; things that change for different reasons (gh vs stage logic) are split.           |
| Open/Closed via registries                                                         | Adding a CLI command, runner or provider adds one file and touches no central list (per-module `register()` or `pkgutil` discovery [5]).                                 |
| Ports and adapters (Cockburn [6])                                                  | `git`, `gh`, `docker` and the LLM runners are driven adapters behind small ports; the engine depends on ports, tests substitute fakes without `patch` on module globals. |
| Functional core, imperative shell (Bernhardt [7])                                  | Parsing, consensus, metrics and reconciliation are pure functions; subprocess and network calls sit at the edge. Pure code needs no hermetic git in tests.               |
| Acyclic dependencies (Martin [4])                                                  | `cli -> flow -> stages -> adapters`; nothing in an entrypoint imports the host engine; no lazy import cycles.                                                            |
| Low complexity (McCabe 1976 [8], ruff [9])                                         | CC <= 10, <= 50 statements, <= 12 branches, <= 6 returns, <= 5 arguments per function, enforced by ruff rules already shipped (C901, PLR0911-PLR0915).                   |
| Intention-revealing names, ubiquitous language (Beck, Evans [10])                  | Names say the domain step (`admit_execution`, `post_consensus_review`), using intent/plan/execution/review/calibration/ledger; no `main` beyond a 20-line entry point.   |
| Hotspots = churn x complexity (Tornhill [11]); Conway's law [12]                   | Refactor `flow.py`, `cli.py`, `executor.py` first; module boundaries should match how agents split work (one stage, one command, one runner).                            |
| Strangler fig, small safe steps (Fowler [13], Beck "Tidy First?")                  | Mechanical move first (AST-verifiable, re-exports kept), then decompose per module in parallel; each step is one flow PR.                                                |
| Append-only event store (Fowler [14])                                              | Keep the three ledgers as the only append hot spots (AGENTS.md item 14); conflicts there are exact unions. No other file should be an "everyone appends here" file.      |

### 4. Ranked good-practice rules for the targets

| #   | Rule                                                                         | Check that enforces it                                                                      | Expected effect                                                    |
| --- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 1   | One module per stage, command, runner and provider format                    | review checklist; touch-set admission (0151) shows overlap                                  | Concurrent flows touch disjoint files; fewer syncs and re-reviews  |
| 2   | Function CC <= 10, statements <= 50, branches <= 12, returns <= 6, args <= 5 | ruff C901, PLR0911, PLR0912, PLR0913, PLR0915 in `uv run task lint`; inline `noqa` baseline | Smaller diffs per change; reviewers see one intent per function    |
| 3   | No central registry edits to extend; registries discover per-file entries    | adding a command/runner/provider touches no shared list (test asserts discovery)            | Removes the `cli.main` and agent-dict collision points             |
| 4   | Behaviour lives on the class that owns the data                              | no module-level function whose first argument is always the same dataclass                  | Fewer cross-module edits per feature                               |
| 5   | Adapters own every subprocess (`git`, `gh`, `docker`)                        | `grep` gate: no `subprocess` outside `adapters/` (and entrypoint shells)                    | Hermetic tests with fakes; 0183 sandboxing becomes an adapter swap |
| 6   | Acyclic imports; entrypoints never import the host engine                    | import-linter-style pytest that walks `ast` imports                                         | Container and host changes stop meeting in `flow.py`               |
| 7   | Tests mirror source one-to-one                                               | `tests/<package>/test_<module>.py` exists for each module                                   | A change touches one source and one test file                      |
| 8   | Intention-revealing names in the ubiquitous language                         | review checklist; ruff `N` naming rules                                                     | Less prose and fewer stale comments (0153)                         |
| 9   | Files under ~400 lines                                                       | a pytest size check with an explicit allow-list that only shrinks                           | Files stay small enough to be independent units of work            |

An inline `# noqa: C901` baseline (generated once with `ruff check --add-noqa`) is preferred over `per-file-ignores` in
`pyproject.toml`: each refactor removes the `noqa` in its own file, so the baseline never becomes a shared file that
every flow edits.

### 5. Target layout (parallel-agent friendly)

holon-agentic-coder `sandbox_executor/`:

| Package / module                                                      | Holds (from today's)                                                               |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `flow/__init__.py`                                                    | re-exports during migration only                                                   |
| `flow/context.py`, `flow/checkpoint.py`                               | `FlowStage`, `StageResult`, `FlowContext`; `FlowCheckpoint` with save/load/migrate |
| `flow/pipeline.py`                                                    | `PipelineEngine`, `run_flow_pipeline`, the stage order                             |
| `flow/stages/{intent,plan,decomposition,execute,review,calibrate}.py` | one stage each, behind a common `Stage` protocol                                   |
| `flow/review_loop.py`                                                 | `ReviewLoop` (from `run_review_loop`)                                              |
| `flow/stage_conflicts.py`                                             | `check_and_resolve_stage_conflicts`                                                |
| `ledger/{rows,lock,query,reconcile}.py`                               | `ledger.py` plus the reconciliation now in `flow.py`                               |
| `adapters/{git,github,docker}.py`                                     | `git.py` grown into `GitRepository`; all `gh` calls; container launch              |
| `launcher/{role_dispatch,sidecar}.py`                                 | `dispatch_role_agent`, `run_docker_container`, proxy sidecar (from `cli.py`)       |
| `cli/{__init__,parser}.py`, `cli/commands/<command>.py`               | 20-line `main`; one module per subcommand with `register()` and `run()`            |
| `runners/<agent>.py`                                                  | one `RunnerSpec` per agent: image, default model, credential check                 |
| `entrypoint/executor/{run,sub_intents,pre_push,repair}.py`            | `ExecutionRun` steps from `executor.main`                                          |
| `calibration/{predicted,actual,deltas,report}.py`                     | `calibration.py`                                                                   |
| (deleted) `token_reduction/`                                          | owned by holon-coherence; only CA generation kept                                  |

holon-coherence `holon_coherence/`: `commands/<command>.py` each registering its own parser;
`proxy/{addon,routing, scrubbing,wire_log,timing,metrics,dashboard}.py`; `providers/{anthropic,openai,gemini}.py` each
owning cleaning, SSE and token parsing, cache-key extraction and translation for one wire format;
`ab_testing/evaluation.py`; `proxy_lifecycle.py`; one composite action for the CI timing steps.

### 6. Migration order (each step one Holon flow PR)

1. Lint gates with inline baselines (0185 hac, 0186 coherence). No behaviour change.
2. Mechanical moves that unlock parallel lanes, AST-verified as move-only: `flow.py` package (0187), `cli` package
   (0188) in parallel; coherence `cli` (0203) and `proxy` package (0204) in parallel.
3. Break the cycles: launcher module (0189), checkpoint and ledger reconciliation (0190).
4. Ports: GitHub adapter (0191), executor git adapter (0195).
5. Decompose in parallel lanes, one file set each: review loop (0192), intent/plan stages (0193), execute stage (0194),
   executor run (0196), calibration (0197), runners (0198), ledger query and knowledge (0199); coherence 0205-0208.
6. Remove the duplicated token-reduction package (0200, decision first), prompts carry the rules (0201), CI timing
   composite actions (0202, 0209).

This deliberately reverses Bean 0152's "decompose before splitting": a move-only split is cheap to review mechanically
and is what removes the shared files, after which decomposition runs in parallel per module.

Relation to existing beans: **0152** becomes the umbrella that tracks 0185-0200 and 0203-0208 (its audit stays the
baseline; its step 4 is 0200). **0153** should run per package after each split, not as one repository-wide flow that
touches every file. **0151** gains finer touch sets from this layout; every spawned bean declares its touch set.
**0183** should follow 0189 and 0190 (the launcher and the checkpoint class are where its sandbox-owned storage and thin
host plug in). **0158** (reconciliation reorders rows) should land before 0190 moves that code. **0160** and **0179**
overlap 0192's touch set and must be sequenced with it.

### Sources

1. D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules", CACM 15(12), 1972,
   https://doi.org/10.1145/361598.361623
2. C. Larman, _Applying UML and Patterns_ (GRASP: Information Expert), 3rd ed., 2004.
3. M. Fowler, "TellDontAsk", https://martinfowler.com/bliki/TellDontAsk.html; "AnemicDomainModel",
   https://martinfowler.com/bliki/AnemicDomainModel.html
4. R. C. Martin, _Clean Architecture_ (SRP, OCP, Common Closure, Acyclic Dependencies), 2017.
5. Python Packaging User Guide, "Creating and discovering plugins",
   https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
6. A. Cockburn, "Hexagonal Architecture", 2005, https://alistair.cockburn.us/hexagonal-architecture/
7. G. Bernhardt, "Functional Core, Imperative Shell",
   https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell
8. T. J. McCabe, "A Complexity Measure", IEEE TSE SE-2(4), 1976, https://doi.org/10.1109/TSE.1976.233837
9. Ruff rules C901 and PLR0911-PLR0915, https://docs.astral.sh/ruff/rules/complex-structure/,
   https://docs.astral.sh/ruff/rules/too-many-statements/
10. K. Beck, _Implementation Patterns_, 2007; E. Evans, _Domain-Driven Design_ (ubiquitous language), 2003.
11. A. Tornhill, _Your Code as a Crime Scene_, 2nd ed., Pragmatic Bookshelf, 2024,
    https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/
12. M. Conway, "How Do Committees Invent?", 1968, https://www.melconway.com/Home/Committees_Paper.html
13. M. Fowler, "StranglerFigApplication", https://martinfowler.com/bliki/StranglerFigApplication.html
14. M. Fowler, "Event Sourcing", https://martinfowler.com/eaaDev/EventSourcing.html

## Summary of resolution (2026-10-29)

Research complete (findings above; no target-repo change). Spawned 25 action beans, each one Holon flow PR with a
declared touch set and `blocked_by` dependencies:

| Bean | Repository          | Change                                                                 | Blocked by |
| ---- | ------------------- | ---------------------------------------------------------------------- | ---------- |
| 0185 | holon-agentic-coder | ruff complexity rules with inline `noqa` baseline and ratchet          | -          |
| 0186 | holon-coherence     | ruff complexity rules with inline `noqa` baseline and ratchet          | -          |
| 0187 | holon-agentic-coder | `flow.py` -> `flow/` package, one module per stage/concern (move only) | 0185       |
| 0188 | holon-agentic-coder | `cli.py` -> `cli/` package, self-registering command modules           | 0185       |
| 0189 | holon-agentic-coder | launcher module; break the `flow` -> `cli` import cycle                | 0187, 0188 |
| 0190 | holon-agentic-coder | `FlowCheckpoint` and ledger reconciliation own their behaviour         | 0187       |
| 0191 | holon-agentic-coder | GitHub adapter owns every `gh` call                                    | 0187       |
| 0192 | holon-agentic-coder | `ReviewLoop` object from `run_review_loop` (528 lines, CC 131)         | 0191       |
| 0193 | holon-agentic-coder | decompose intent and plan stage modules                                | 0187       |
| 0194 | holon-agentic-coder | `ExecuteStage` from `run_execute_stage`                                | 0187       |
| 0195 | holon-agentic-coder | executor's 81 raw `git` calls through a `GitRepository` adapter        | 0185       |
| 0196 | holon-agentic-coder | `ExecutionRun` from executor `main` (798 lines, CC 178)                | 0195, 0190 |
| 0197 | holon-agentic-coder | `calibration/` package; decompose metrics parsing                      | 0187       |
| 0198 | holon-agentic-coder | agent runner registry, one `RunnerSpec` per agent                      | 0185       |
| 0199 | holon-agentic-coder | decompose ledger query and knowledge index                             | 0190       |
| 0200 | holon-agentic-coder | remove the duplicated `token_reduction/` copy (decision first)         | 0189       |
| 0201 | holon-agentic-coder | role prompts carry the placement, complexity and naming rules          | 0185       |
| 0202 | holon-agentic-coder | CI timing-gate steps in one composite action                           | (0184)     |
| 0203 | holon-coherence     | commands register their own parsers; drop `_dispatch.get_cli`          | 0186       |
| 0204 | holon-coherence     | `mitm_addon.py` -> `proxy/` package (move only)                        | 0186       |
| 0205 | holon-coherence     | addon `request`/`response` as pipeline steps                           | 0204       |
| 0206 | holon-coherence     | one provider module per wire format                                    | 0204       |
| 0207 | holon-coherence     | A/B evaluation and metrics out of the command handlers                 | 0203       |
| 0208 | holon-coherence     | `ProxyLifecycle` for start-up and readiness                            | 0203       |
| 0209 | holon-coherence     | CI timing-gate steps in one composite action                           | 0184       |

Proposed re-scoping (not applied to those beans' scope): 0152 becomes the umbrella tracking these children; 0153 runs
per package after each split; 0183 follows 0189 and 0190; 0158 lands before 0190; 0160 and 0179 are sequenced with 0192.
Triage matrix updated.
