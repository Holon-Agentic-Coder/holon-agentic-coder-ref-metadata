# Worktrees and Git Rules

Per-agent worktrees, naming, formatting before commit, the squash-once rule, and the managed repositories table. Moved
verbatim from `AGENTS.md`.

---

5. **Per-Agent Worktrees (Autonomous Branches Are Allowed)**: Every agent gets **its own worktree per project** and
   works **exclusively** inside it. Creating that branch and worktree is autonomous -- no user instruction required:
   - **Sole Change Path — Holon Flow is the Only Option**: `holon flow <intent.json>` is not merely a preferred option;
     it is the **sole and exclusive option** for all development across `holon-agentic-coder` and `holon-coherence`.
     Every change MUST be produced by traversing the containerised 5-stage lifecycle. Because all stages (Intent, Plan,
     Execute, and Stage 4 Review Loop & Resolver) run inside Docker containers using the globally installed `holon` CLI
     (`~/.local/bin/holon`), the worktree serves purely as a Git anchor to resolve repository URLs and Git state—running
     `uv sync --group dev` on the host is not required for flow execution.
   - **Legacy Worktree & Hand-Authoring Fallback**: Hand-authoring changes directly in a worktree is strictly a fallback
     for when `holon flow` itself is broken or blocked and we must hand-author PRs to fix the bootstrap harness, or when
     performing local container image builds, harness coordination, or manual host-side verification suites. In those
     exceptional cases only, follow the legacy worktree instructions below:
   - For `apps/holon-agentic-coder/`, all development and feature work must be based off the `origin/main` branch.
   - For `apps/holon-coherence/`, all development and feature work must be based off the `origin/main` branch.
   - Name the worktree and branch after you or your bean so concurrent agents never share a directory or a branch. Which
     name applies is decided by this order:
     - **Holon flow (`holon flow`)**: The worktree is named `apps/<project>/flow-<slug>`. It is provisioned at the start
       of the flow (Bean 0259) and **persists across all 5 stages** (Intent $\rightarrow$ Plan $\rightarrow$ Execute
       $\rightarrow$ PR Review Loop $\rightarrow$ Calibrate). Opening a PR does NOT rename or recreate the worktree; the
       review loop and calibration reuse `flow-<slug>` directly.
     - **Standalone PR review (no local worktree checked out)**: If an ad-hoc review (`/pr-reviewer`, `/pr-review-loop`)
       is triggered for an existing remote PR and **no local worktree exists** for that branch, provision
       `apps/<project>/pr<N>-<slug>`. If a local worktree (`flow-<slug>`) is already checked out, reuse it directly
       instead of creating a redundant checkout.
     - **No Holon flow branch involved** (hand-authored harness work or fallback): the **bean number goes in the name**
       -- directory `apps/<project>/<type>-<bean-id>-<slug>` for branch `<type>/<bean-id>-<slug>`. Work that has neither
       a PR nor a bean yet needs the bean logged first.
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
   - Each worktree needs its own environment when authoring by hand or running host verification: virtualenvs are
     per-directory and cannot be shared, so run `uv sync --group dev` inside the new worktree (legacy/manual authoring
     and verification path only) and never point at another worktree's `.venv/`.
   - Inside your own worktree you have full latitude to edit, commit, squash, test, rebuild images and push -- **for
     harness work, image builds, verification runs, and handling branches the flow produced**. That squash latitude
     **never extends to a branch the Holon flow or a review loop drives** (item 7 below; rule 4 in
     [.agents/workflows.md](workflows.md)). Authoring `holon-agentic-coder` or `holon-coherence` source changes by hand
     in a worktree outside the flow is prohibited: that is the flow's job (see
     [🔒 Sole Change Path: The Holon Flow](holon-flow.md#-sole-change-path-the-holon-flow)).
   - **The `main` worktree is the user's playground.** `apps/holon-agentic-coder/main` and `apps/holon-coherence/main`
     are off-limits to agents: never edit, stage, commit, stash, reset, clean or checkout in them, never build into or
     leave stray files there, and do not mutate their local state either (`.venv/`, caches, generated artifacts).
   - **A flow never runs in the `main` worktree, even when its target is `main`.** Naming `main` as the target selects
     the repository and base branch only. `holon flow` checks out the execution branch in its `--target-worktree` and
     commits calibration and ledger rows there, so run it in a dedicated `flow-<slug>` worktree cut from `origin/main`
     (`git worktree add --no-track -b flow-<slug> ../flow-<slug> origin/main`; the `holon-flow` skill's script does this
     for you). The `main` worktree must stay on `main`, identical to `origin/main` including local files. The same goes
     for image builds: use a separate temporary worktree.
   - If changes have already landed in a `main` worktree, move them into a dedicated worktree and restore `main` to a
     pristine checkout of its committed state.
6. **Format Before Commit**: In the harness repository, always execute `npx prettier --write "**/*.md"` before
   committing. In nested target worktrees (`apps/<project>/<branch>`), format **only the changed files** using the
   target repository's configuration (or `--no-config` if none exists) to prevent resolving the harness's
   `.prettierrc.json` and reflowing unrelated files. Always verify `git diff --stat` before committing.
7. **Squash Once, at the Very End, Then Push Your Own Branch Freely**: Applies to branches you hand-author -- harness
   branches in this metadata repo and any supporting branch you cut for the flow. Ensure all commits on such a branch
   are squashed into a single commit relative to the `main` branch, but **squash exactly once, immediately before the
   push that finishes the task -- never mid-task**. While work is in progress, add new commits and push them as they
   are. Mid-task history is the maintainer's checkpoint surface: they commit as `docs: wip` as they go, and those
   commits are theirs to keep, split or discard. Never `reset`, `amend`, `rebase` or squash over commits you did not
   author (including `docs: wip` checkpoints) unless the maintainer explicitly asks -- a squash swallows their
   granularity and can capture another session's in-flight work under your message. Take the path list before any reset,
   since after the reset the merge base _is_ `HEAD` and the diff that produced the list prints nothing (rule 4 in
   [.agents/workflows.md](workflows.md)). **A branch a `pr-review-loop` run drives is exempt**: it pushes once per
   iteration and is never squashed, rewritten, or force-pushed (rule 4 in [.agents/workflows.md](workflows.md)). Pushing
   **your own** feature branch is allowed autonomously, without waiting for instruction: `git push -u origin {branch}`,
   and `--force-with-lease` when you rewrite history on it. The flow pushes its own `I-...`/`P-...`/`E-...` branches;
   never squash, rewrite, or force-push those, since they are the audited provenance record.
   - Never push to `main` (or any branch you do not own), never force-push a shared branch, and never push from a `main`
     worktree.
   - For hand-authored or non-flow work, Pull Request _creation_ stays with the human maintainer unless the user
     instructs otherwise. Harness branches in this repository exist for day-to-day operations and logging work done, so
     they do not need to be merged to `main` often. **When executing the Holon flow, Pull Request creation is fully
     autonomous**: once Stage 3 (Execute) pushes the execution branch, the agent autonomously raises the Pull Request
     via `gh pr create` targeting the base branch so Stage 4 (PR review loop) can proceed seamlessly without manual
     interruption. **PR merging remains exclusively the human maintainer's responsibility — agents MUST NEVER merge a PR
     that targets `main` (see "🔒 PR Merging — Human-Only" below).**

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
> `apps/holon-coherence/{branch}`. Each worktree also owns its own virtualenv (`uv sync --group dev` when hand-authoring
> or running host verification).

---
