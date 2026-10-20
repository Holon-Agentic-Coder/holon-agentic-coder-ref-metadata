# Agent Landing Page & Entrypoint

> [!NOTE] **Bootstrapping Harness Intent** This repository is a temporary control plane and metadata store. It will only
> be used until the bootstrap process for
> [holon-agentic-coder](https://github.com/Holon-Agentic-Coder/holon-agentic-coder) is fully completed. Until that
> repository is fully bootstrapped, it does not possess enough autonomous power to develop or maintain itself. This
> repository serves as the external harness to bridge that gap.

Welcome, Agent. This document is your starting point for operating within this workspace. Read this document in its
entirety before performing any operations or modifying any code.

---

## 🎯 Quick Navigation

- [README.md](README.md) - Repository architecture and general overview.
- [.agents/instructions.md](.agents/instructions.md) - General operating principles and behavioural guidelines.
- [.agents/rules.md](.agents/rules.md) - Coding standards, file handling, and sandbox constraints.
- [.agents/workflows.md](.agents/workflows.md) - Task execution cycle, git guidelines, and PR procedures.
- [.agents/submodules.md](.agents/submodules.md) - Git submodules management and embedded repository workflows.
- [.agents/coordination.md](.agents/coordination.md) - Delegation, subagent communication, and peer coordination
  protocols.
- [.agents/skills/](.agents/skills/) - Project-specific agent skills and capability guidelines.
- [todo/](todo/) - Temporary scratchpad directory for local agent files, documents, and notes (git ignored).

---

## 🔒 Sole Change Path: The Holon Flow

> [!IMPORTANT] **Every change to a target codebase (`holon-agentic-coder` or `holon-coherence`) MUST be produced by the
> 5-stage Holon flow.** No agent or developer may hand-author, hand-patch, or directly commit changes to
> `holon-agentic-coder` or `holon-coherence` outside the flow lifecycle. Invoking `holon` inside either target
> repository's worktree dynamically resolves `remote.origin.url` via `resolve_target_repo_url()`, driving the target
> repository's `holon-knowledge/ledger/` provenance pipeline.

The lifecycle is a single pipeline, not a menu. A change is only "done through the flow" when it has traversed all of
its stages:

| #   | Stage          | Invocation (manual form)                                                                      | Artifact                                                                           |
| --- | -------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1   | Intent         | `holon intent <intent.json>`                                                                  | `I-{timestamp}-{slug}/_` + `holon-knowledge/ledger/intents.jsonl`                  |
| 2   | Plan           | `holon plan <intent_branch>`                                                                  | `I-.../P-{ts}-{agent}-{model}/_` + `plans/P-*.md` + `plans.jsonl`                  |
| 3   | Execute        | `holon execute <plan_branch>`                                                                 | `I-.../P-.../E-{ts}-{agent}-{model}/_` + `holon-knowledge/ledger/executions.jsonl` |
| 4   | PR review loop | `holon review <execution_branch>` (+ `pr-review-loop` ensemble/resolver when fixing findings) | Consensus approval posted to the PR + `executions.jsonl` (`ACT-REV`/`ACT-POST`)    |
| 5   | Calibration    | `holon calibrate <execution_branch>` (Bean 0038)                                              | `/calibrated` branch + `plans/P-*_calibration.md` (also included in PR diff)       |

**Ordering of the merge boundary**: stage 5 (Calibration) is a **pre-merge** stage, matching `STAGE_ORDER` in
`sandbox_executor/flow.py` (intent -> plan -> execute -> review -> calibrate). Run the review loop to consensus
approval, calibrate, and only then stop and request the merge -- never calibrate after it, because merging a flow PR
consumes the `E-...` execution branch that calibration reads.

**Calibration branch and PR inclusion**: Running calibration creates the audited `/calibrated` branch
(`I-.../P-.../E-.../calibrated`), which must be created and pushed. **For Pull Requests, the calibration report
(`plans/P-*_calibration.md`) MUST ALSO be included in the PR** (by fast-forwarding or merging the calibration commit
into the PR head execution branch `.../_` and pushing to `origin`) so that the calibration report appears in the PR diff
and is preserved in `main` history when merged. Merging itself stays human-only (see "🔒 PR Merging — Human-Only"
below).

**Whether the pipeline is driven by hand or by automation is irrelevant -- only that all five stages are executed.**
Running the stages one at a time with the individual commands is exactly as compliant as the unified runner. That runner
(`holon flow <intent.json>`) already exists on `main` with a reduced flag set; Bean 0040 tracks the five flags and the
usage docs still outstanding on it, while the pipeline engine itself (Bean 0039) is completed. Neither form changes what
"through the flow" means.

**Consequences for agents:**

- Changes are authored by the sandboxed role agents inside the containerised plan/execution branches and recorded in the
  append-only ledgers. The ledgers, not the agent's word, are the system of record.
- Host-side worktrees (`apps/<project>/{branch}`) exist to **build images, inspect code, run verification, and operate
  the harness** -- they are not a change-authoring surface. Editing `holon-agentic-coder` or `holon-coherence` source in
  a worktree outside the flow bypasses intent provenance, plan metrics, EV accounting, and the execution ledger, and is
  therefore prohibited.
- Skipping a stage is not permitted. If a stage cannot run (missing image, failed agent, unreachable remote), the change
  is **blocked**: report the blocker instead of hand-applying the diff as a workaround.
- The only permitted exception is an explicit, unambiguous user instruction to make a specific edit outside the flow,
  and that exception must be named in the commit message and in the bean summary.

**Harness exception (control plane only).** The `holon-agentic-coder-ref-metadata` control plane itself (`.beans/`,
`.agents/`, `AGENTS.md`) is the coordination harness rather than a flow-managed target repository. Those harness files
stay directly editable.

---

## 🚀 Incoming Agent Checklist

When you are spawned or begin a new session, follow these steps sequentially:

1. **Verify Your Environment**: Check the current working directory, workspace structure, and locate the `.beans`
   configuration. If the target repositories (`apps/holon-agentic-coder/` or `apps/holon-coherence/`) are not set up,
   follow the checkout instructions in [README.md](README.md) to clone the bare repositories and configure worktrees.
2. **Review the Tasks**: List the tasks in the [.beans/](.beans/) directory to determine your current assignment or log
   a new task if none exists.
3. **Internalise Constraints**: Load [.agents/rules.md](.agents/rules.md) to understand linting rules, language choices,
   and test requirements.
4. **Execute Tasks Systematically**: Follow the lifecycle specified in [.agents/workflows.md](.agents/workflows.md) to
   transition tasks from `todo` to `in-progress` and finally `completed`.
5. **Per-Agent Worktrees (Autonomous Branches Are Allowed)**: Every agent gets **its own worktree per project** and
   works **exclusively** inside it. Creating that branch and worktree is autonomous -- no user instruction required:
   - For `apps/holon-agentic-coder/`, all development and feature work must be based off the `origin/main` branch.
   - For `apps/holon-coherence/`, all development and feature work must be based off the `origin/main` branch.
   - Name the worktree and branch after you or your bean (for example `apps/holon-coherence/pr25-coherence-make-tasks`
     for a flow PR branch) so concurrent agents never share a directory or a branch. Which name applies is decided by
     this order:
     - **Checked out from a Holon flow branch** (`I-.../P-.../E-.../...`): such a branch always has a Pull Request, so
       the worktree **must carry the PR number and a slug** -- `apps/<project>/pr<N>-<slug>`, for example
       `apps/holon-agentic-coder/pr61-agent-output-capture`. Keep the flow ref itself exactly as the flow created it
       (never rename or re-cut an audited provenance branch); the `pr<N>-<slug>` marker lives on the **directory**.
     - **No Holon flow branch involved** (hand-authored harness work): the **bean number goes in the name** -- directory
       `apps/<project>/<type>-<bean-id>-<slug>` for branch `<type>/<bean-id>-<slug>`. Work that has neither a PR nor a
       bean yet needs the bean logged first.
   - **A worktree created for temporary use MUST be named descriptively enough to still read as its purpose months
     later**: `<purpose>-<subject>-<qualifier>`, for example
     `apps/holon-agentic-coder/verify-pr61-agent-output-redaction` or
     `apps/holon-coherence/repro-0028-proxy-port-conflict`. Opaque names are prohibited -- `tmp`, `wip`, `scratch`,
     `test1`, `worktree2`, or letter-suffixed names such as `resolve-a`, `calib-b`, `verify-0019-a` -- because
     `git worktree list` reports only path, commit and refname, so a cleanup pass cannot attribute a directory it cannot
     read. Delete the worktree as soon as its stated purpose is complete.
   - When a harness change must not disturb the user's active checkout of this metadata repository, cut the worktree
     under the git-ignored `apps/` tree instead: `apps/holon-agentic-coder-ref-metadata/{branch-dir}`.
   - Create it from the bare repository directory with
     `git worktree add --no-track -b {branch} ../{branch} origin/main`. Note that `../` resolves relative to
     `<project>/.git`, which is what places the checkout at `<project>/{branch}`.
   - Each worktree needs its own environment: virtualenvs are per-directory and cannot be shared, so run
     `uv sync --group dev` inside the new worktree and never point at another worktree's `.venv/`.
   - Inside your own worktree you have full latitude to edit, commit, squash, test, rebuild images and push -- **for
     harness work, image builds, verification runs, and handling branches the flow produced**. That squash latitude
     **never extends to a branch the Holon flow or a review loop drives** (item 7 below; rule 4 in
     [.agents/workflows.md](.agents/workflows.md)). Authoring `holon-agentic-coder` or `holon-coherence` source changes
     by hand in a worktree outside the flow is prohibited: that is the flow's job (see
     [🔒 Sole Change Path: The Holon Flow](#-sole-change-path-the-holon-flow)).
   - **The `main` worktree is the user's playground.** `apps/holon-agentic-coder/main` and `apps/holon-coherence/main`
     are off-limits to agents: never edit, stage, commit, stash, reset, clean or checkout in them, never build into or
     leave stray files there, and do not mutate their local state either (`.venv/`, caches, generated artifacts).
   - If changes have already landed in a `main` worktree, move them into a dedicated worktree and restore `main` to a
     pristine checkout of its committed state.
6. **Format Before Commit**: In the harness repository, always execute `npx prettier --write "**/*.md"` before
   committing. In nested target worktrees (`apps/<project>/<branch>`), format **only the changed files** using the
   target repository's configuration (or `--no-config` if none exists) to prevent resolving the harness's
   `.prettierrc.json` and reflowing unrelated files. Always verify `git diff --stat` before committing.
7. **Squash, Then Push Your Own Branch Freely**: Applies to branches you hand-author -- harness branches in this
   metadata repo and any supporting branch you cut for the flow. Ensure all commits on such a branch are squashed into a
   single commit relative to the `main` branch. **A branch a `pr-review-loop` run drives is exempt**: it pushes once per
   iteration and is never squashed, rewritten, or force-pushed (rule 4 in [.agents/workflows.md](.agents/workflows.md)).
   Pushing **your own** feature branch is allowed autonomously, without waiting for instruction:
   `git push -u origin {branch}`, and `--force-with-lease` when you rewrite history on it. The flow pushes its own
   `I-...`/`P-...`/`E-...` branches; never squash, rewrite, or force-push those, since they are the audited provenance
   record.
   - Never push to `main` (or any branch you do not own), never force-push a shared branch, and never push from a `main`
     worktree.
   - For hand-authored or non-flow work, Pull Request _creation_ stays with the human maintainer unless the user
     instructs otherwise. **When executing the Holon flow, Pull Request creation is fully autonomous**: once Stage 3
     (Execute) pushes the execution branch, the agent autonomously raises the Pull Request via `gh pr create` targeting
     the base branch so Stage 4 (PR review loop) can proceed seamlessly without manual interruption. **PR merging
     remains exclusively the human maintainer's responsibility — agents MUST NEVER merge a PR (see "🔒 PR Merging —
     Human-Only" below).**
8. **Report and Document**: Summarise changes cleanly and concisely. Point both the user and successor agents to updated
   files or artifacts.
9. **Route Every Change Through the Flow**: Produce all `holon-agentic-coder` and `holon-coherence` changes via the
   five-stage Holon flow (intent -> plan -> execute -> PR review loop -> calibration) rather than hand-authored
   host-side edits, and calibrate before requesting the merge. Manual stage-by-stage invocation is fully compliant;
   automating it with the `holon flow` runner that already exists on `main` is optional (Bean 0040 tracks its remaining
   flags and usage docs; the Bean 0039 engine is completed). See
   [🔒 Sole Change Path: The Holon Flow](#-sole-change-path-the-holon-flow).
10. **Zero Synthetic Data for Benchmarking**: Absolutely never use synthetic or mock data to measure efficacy or
    benchmark token reduction. Official evaluations and scorecards must derive exclusively from authentic real data
    streams (live sandbox task executions, genuine wire logs, or real production payloads).
11. **Token Conservation & Concise Communication**: Minimise prompt and generation token burn across harness and
    subagents. Deliver dense, factual, and strictly actionable updates without narrative bloat. Intermediate review
    iterations stay local in `.subagent/` — never post premature review comments to GitHub until all findings are fully
    resolved or consensus approved. Prune stale `.subagent/` artifacts upon completion.
12. **Target Repository Isolation & Zero Harness Path Leaks**: Target repositories (`holon-agentic-coder` and
    `holon-coherence`) are independent, standalone software systems. They **MUST NEVER** know about, import, reference,
    or configure harness-specific directories, conventions, or tooling (`.beans/`, `todo/`, `.agents/`). Any path lists,
    ignore patterns, filters, or calibration logic inside target repositories must strictly contain target-native paths
    only (`holon-knowledge/`, `plans/`, `.holon/`). Harness concerns must never leak into target codebases.
13. **Strict Test Execution & Tooling Prohibition (NEVER `unittest`, NEVER `python3 -m unittest`, NEVER `PYTHONPATH`)**:
    All test suites across all target repositories and the harness MUST be executed strictly using `uv run pytest`.
    - Running `unittest`, `python3 -m unittest`, `python -m unittest`, or bare `pytest` is strictly forbidden.
    - Executing commands with `PYTHONPATH` overrides (e.g., `PYTHONPATH=...`, `export PYTHONPATH=...`) is strictly
      forbidden. All virtual environment dependencies and editable workspace packages are managed and resolved cleanly
      by `uv`; manual `PYTHONPATH` overrides mask packaging and dependency errors, bypass workspace definitions, and
      break hermetic testing.
14. **Canonical 3-Ledger Architecture Invariant (`holon-knowledge/ledger/`)**: Target repositories maintain strictly
    three append-only ledgers under `holon-knowledge/ledger/`: `intents.jsonl` (Intent), `plans.jsonl` (Plan), and
    `executions.jsonl` (Execution, Review, and Calibration). **NEVER create auxiliary ledgers like `actions.jsonl` or
    `reviews.jsonl`**. All discrete micro-action records (`entry_type: "action"`, such as `ACT-REV`, `ACT-FIND`,
    `ACT-POST`, tool operations) and lifecycle summaries (`entry_type: "summary"`, such as `E-...`, `REV-...`) MUST be
    interleaved chronologically inside `executions.jsonl` under `LedgerLock`. Auxiliary ledgers fragment the provenance
    trail, break downstream query engines, and are strictly prohibited.

---

## 🌲 Managed Repositories & Git Worktree Structure

This metadata repository hosts bare clones of target codebases with checkout worktrees:

| Repository              | Worktree Directory              | Bare Git Location               | Base Branch   | Feature Branch Command                                            |
| ----------------------- | ------------------------------- | ------------------------------- | ------------- | ----------------------------------------------------------------- |
| **holon-agentic-coder** | `apps/holon-agentic-coder/main` | `apps/holon-agentic-coder/.git` | `origin/main` | `git worktree add --no-track -b {branch} ../{branch} origin/main` |
| **holon-coherence**     | `apps/holon-coherence/main`     | `apps/holon-coherence/.git`     | `origin/main` | `git worktree add --no-track -b {branch} ../{branch} origin/main` |

All code development must take place within the appropriate repository worktree. The metadata repository root is
strictly for coordination, task tracking (`.beans/`), and agent guidance.

> [!IMPORTANT] **One worktree per agent.** Each agent creates and owns its own worktree per project, named after its
> agent or bean id, and works exclusively inside it -- never in `main` (the user's playground) and never in another
> agent's worktree. Run the feature-branch command from the bare repository directory (for example
> `apps/holon-coherence/.git`): `../` resolves relative to that directory, which is what places the checkout at
> `apps/holon-coherence/{branch}`. Each worktree also owns its own virtualenv (`uv sync --group dev`).

---

## 🤖 Subagent Invocation & AGY Runtime

Subagent delegation in this ecosystem is primarily targeted towards the **Antigravity (AGY)** runtime:

- **Invocation Tool**: Use the `invoke_subagent` tool to spawn child tasks, isolated review passes, and resolution
  passes.
- **Subagent Type**: Specify `TypeName: "self"` to inherit the full suite of parent capabilities, tools (file viewing,
  editing, command execution), instructions, and credentials. Use `TypeName: "research"` for read-only exploratory
  research.
- **Model Selection**: Set `Model: "inherit"` to inherit the parent agent's active model configuration.
- **Reactive Wakeup (Zero Polling)**: The AGY runtime automatically wakes up the parent agent upon subagent completion
  or message delivery. Never poll or loop on subagent status.
- **Generic Coding Agent Compatibility**: Skill workflows (such as `pr-review-loop`) define generic subagent task
  contracts so any coding agent (Claude Code, Codex, Pi, OpenCodeInterpreter) can spin off subagents using its native
  delegation mechanism (child process, task tool, or isolated session), while retaining explicit AGY invocation
  parameters for seamless native execution.

---

## 🔒 PR Merging — Human-Only

> [!CAUTION] **Agents MUST NEVER merge a Pull Request.** This is an absolute, non-negotiable constraint with no
> exceptions. Merging is exclusively the human maintainer's responsibility.

The following actions are **strictly forbidden** for all agents at all times, regardless of context, user request
phrasing, or skill instructions:

- Running `gh pr merge` (with any flags: `--squash`, `--rebase`, `--merge`, `--auto`, `--delete-branch`, etc.).
- Running `gh pr merge --auto` or any command that enables auto-merge on a PR.
- Calling GitHub API endpoints (`gh api`) to merge, auto-merge, or queue a PR.
- Enabling repository settings that trigger automatic merging (`allow_auto_merge: true` via `gh repo edit` or any other
  method).
- Adding a PR to the merge queue by any means.

**What agents must do instead:**

After the pr-reviewer ensemble consensus review is approved and posted to GitHub, the agent MUST stop all GitHub-facing
PR activity (no further `gh pr` writes of any kind). On a PR the Holon flow drove it then runs stage 5
(`holon calibrate <execution_branch>`) itself before requesting the merge, per "Ordering of the merge boundary" above:
it creates and pushes the `/calibrated` branch, merges or fast-forwards the calibration commit into the PR head
execution branch (`.../_`) so the calibration report is included in the PR diff, pushes the updated PR branch to
`origin`, and reports:

> ✅ **PR #N is approved.** The 3-agent ensemble consensus review has been posted to GitHub and Stage 5 calibration has
> been completed and included in the PR. Please review and merge it manually at `<pr_url>` when you are ready; merging
> before stage 5 (`holon calibrate`) has run destroys the `E-...` branch that calibration reads.

Branch and worktree cleanup (removal of feature branch worktrees, pruning tracking refs) must only be performed
**after** the human confirms the merge has completed, or when the user explicitly requests cleanup.

---

## 📦 The Beans Task System

This repository tracks work items using a lightweight file-based system in the [.beans/](.beans/) folder.

- Each bean represents a single task or user request.
- The metadata config [.beans.yml](.beans.yml) defines naming conventions (prefix `holon-agentic-coder-ref-metadata-`).
- **Strict Sequential Numbering**: Bean IDs MUST follow a strictly sequential 4-digit zero-padded integer format
  (`0001`, `0002`, ..., `0033`, `0034`, `0035`, etc.). Never generate random base36 IDs (e.g. `k4t7`, `1lh8`). To
  determine the next ID, inspect existing files in `.beans/`, find the highest integer ID, increment by 1, and zero-pad
  to 4 digits.
- When picking up a task, update its status inside the task file to `in-progress`.
- Once finished, change the status to `completed` and add a summary of your resolution.
- Valid statuses are fixed by the [beans CLI](https://github.com/hmans/beans) and are `draft`, `todo`, `in-progress`,
  `completed` and `scrapped`. `done` and `in_progress` are **not** valid: the CLI rejects them on create and never
  archives them, because `beans archive` only moves `completed` and `scrapped` beans out of the active directory.

For details on how to create and manage task files, refer to [.agents/workflows.md](.agents/workflows.md).

---

## 📂 The Todo Directory (Temporary Scratchpad)

The `todo/` directory is a local, git-ignored workspace where agents and developers can store temporary scratch files,
draft documents, screenshots/images, and task notes.

- This folder serves as a transient workbench for staging thoughts and intermediate artifacts.
- **Strict Invariant**: None of the files in `todo/` should ever be committed to the repository (enforced via
  `.gitignore`).
