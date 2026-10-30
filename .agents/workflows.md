# Agent Workflows & Task Lifecycle

This document describes the workflow protocols you must follow when executing a task or coordinating code updates.

---

## 🔄 Task Lifecycle (The Bean System)

All work should be tracked under the `.beans/` directory. Bean files are **Markdown with YAML front matter** (`.md`
only). The `beans` CLI ignores any other extension, because `ParseFilename` strips only `.md`, so a `.yml` bean is
invisible to it.

Filename pattern: `.beans/<prefix><id>--<slug>.md` e.g.
`.beans/holon-agentic-coder-ref-metadata-0033--remove-the-native-host-mitmproxy-flag.md`

- `<id>` is a strictly sequential 4-digit zero-padded integer (`0001` through `9999`), prefixed by `prefix`. Never use
  random base36 IDs (e.g. `k4t7`, `1lh8`). To determine the next ID, inspect existing files in `.beans/`, find the
  highest integer ID, increment by 1, and zero-pad to 4 digits (e.g. `0034`).
- `<slug>` is the lowercased, hyphenated title, truncated to 50 characters with no trailing hyphen.
- The ID comes from the **filename**; it is not a front matter field. The `# <full id>` line at the top of the front
  matter is a cosmetic comment.
- Only the fields documented in [`.beans/template.md`](../.beans/template.md) may appear in front matter. The CLI
  persists exactly those and silently discards any other key on its next write, so task description, notes, assignee and
  resolution summary belong in the Markdown body, never in YAML block scalars.
- Timestamps are unquoted RFC3339 UTC (`2026-09-22T13:10:00Z`). Quoting them turns the value into a string that the CLI
  cannot decode into a timestamp.
- Statuses are fixed by the CLI and are `draft`, `todo`, `in-progress`, `completed` and `scrapped`. Do not use `done` or
  `in_progress`: the CLI rejects them, and `beans archive` only moves `completed` and `scrapped` beans out of the active
  directory.

### 1. Task Acquisition

- Look at the `.beans/` folder. Select a task with status `todo`.
- If no task matches the user's request, create a new bean: copy [`.beans/template.md`](../.beans/template.md) and
  assign the next sequential 4-digit ID (`0001`..`9999`) by incrementing the highest existing integer ID in `.beans/`.
  Do not use `beans create` if it generates random base36 IDs.
- Update the status field of the task file to `in-progress`.

## ❓ Questions Upfront, Then Unattended

Once the operator has specified a task, agent work is **autonomous by default**. Stopping to ask "shall I continue?"
mid-task is a defect, not courtesy: the operator has already authorised the work and is paying for the round trip.

1. **Surface every unknown before starting, in one batch.** Before touching anything, write out all the decisions the
   task leaves open that you would otherwise have to guess or ask about later -- scope, which repo/branch, acceptance
   criteria, destructive actions, fallback behaviour, what to do if a gate fails. Ask them together, once, at the start.
   If a question can be answered by reading the repository, reading a ledger, or running a probe, **do not ask it**:
   measure it.
2. **Then run to a terminal state without checkpoints.** Do not pause for approval between steps of an authorised task,
   do not summarise and wait at an intermediate stage, and do not end a turn on a confirmation question when the next
   action is already authorised. Report at the end, or when genuinely blocked.
3. **Decide the unanticipated conservatively, log it, keep moving.** When something unforeseen appears mid-task, choose
   the conservative option, record the decision and its rationale, and state it in the final report. A question that
   arises after work has started is answered this way, not by interrupting the operator.
4. **The standing exceptions stay absolute.** Merging a PR (human-only, `AGENTS.md`), destructive or irreversible
   actions (force-pushing a shared branch, deleting worktrees or branches before a merge is confirmed, writing to a
   `main` worktree, spending real money or quota beyond the task's scope), and any newly discovered scope beyond what
   was asked. Those stop and ask; nothing else does.
5. **Local-runtime serial dispatch is not a blocker to ask about.** On a local model runtime, run delegable children one
   at a time and keep going; do not stop and ask whether to relaunch a child.

Bean `0085` ports the same contract into the flow itself, so the sandboxed role agents inherit it: the Intent stage asks
everything once, and an intent with unresolved questions is not executable.

---

### 2. Implementation Cycle (The Holon Flow)

Changes to target codebases are authored by the flow, not by hand. Run the five stages in order; each stage produces the
branch and ledger record the next one consumes (see invariant 8 in [rules.md](rules.md)).

- **Intent**: Write the intent JSON (`description`, `goal`, `slug`, optional `target_branch`) and run
  `./holon intent <file>` to open the `I-.../_` branch and append to `holon-knowledge/ledger/intents.jsonl`. Encode the
  sandbox constraints the executor must respect inside `goal`. Request repeated test runs only when the change must
  measure performance, with an explicit N, each run under pytest-xdist (invariant 19 in [rules.md](rules.md)).
- **Plan**: Run `./holon plan <intent_branch> --agent <agent> --model <model>`; review the generated `plans/P-*.md` and
  the predicted metrics recorded in `plans.jsonl` before proceeding.
- **Execute**: Run `./holon execute <plan_branch> --agent <agent> --model <model>`. Verify the pushed `E-...` branch is
  a real descendant of the plan branch (`git log --format='%H %P'`) and that the codebase tree survived -- an
  `executions.jsonl` `status: success` does not prove it.
- **Review**: Run the `pr-review-loop` skill until the ensemble reaches consensus approval. Never merge (see the
  Human-Only rule below).
- **Calibrate**: Run `holon calibrate <execution_branch>` to commit predicted-versus-actual deltas. This is a
  **pre-merge** stage: merging consumes the `E-...` branch it reads (Bean 0054). Push the dedicated `/calibrated`
  branch, and for Pull Requests, also merge/fast-forward the calibration commit into the PR head branch and push so that
  the calibration report is included in the PR diff and lands on `main` when merged.
- **Document**: Add notes inside the task file explaining how the task was resolved, including the intent, plan, and
  execution branch names.
- **Post-merge** (on detecting the human's merge): close the delivered bean(s) with a summary, refresh the triage
  generator and regenerate the matrix, and recommend the next set of concurrently runnable beans (disjoint touch sets,
  dependencies honoured) to the maintainer. See the Post-Merge Protocol in [AGENTS.md](../AGENTS.md).

Invoke these stages individually or drive them with `holon flow <intent.json>`, which already exists on `main` with a
reduced flag set (Bean 0040 tracks the flags and usage docs still outstanding; the Bean 0039 pipeline engine is
completed). Both modes satisfy the same requirement.

- **Automatic Model & Runner Fallback on Credit / Quota Exhaustion**: If any stage (`plan`, `execute`, `review`, or
  `calibrate`) or AGY subagent fails because credit or session quota ran out on the higher-level model (for both
  **Claude** and **Antigravity**), automatically fall back to the next lower model tier that still has credit and
  **continue the flow from the current stage** (reusing the already-created `I-.../_`, `P-.../_`, or `E-.../_` branch
  rather than starting over):
  - **Claude (`claude-agent`)**: `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6` $\rightarrow$ `claude-haiku-4-5`.
  - **Antigravity (`antigravity-agent` CLI)**: `gemini-3.8-pro-high` $\rightarrow$ `gemini-3.8-flash-medium`
    $\rightarrow$ `gemini-3.8-flash`.
  - **Antigravity (`invoke_subagent`)**: `Model: "inherit"` / `"pro"` $\rightarrow$ `"flash"` $\rightarrow$
    `"flash_lite"`.
  - **Cross-Runner Continuation**: If all model tiers under the current runner share an exhausted account/session quota,
    switch `--agent` to the alternate runner (`antigravity-agent` or `claude-agent`) and resume from the failed stage
    (e.g. `holon plan <intent_branch> --agent antigravity-agent --model gemini-3.8-flash-medium`, followed by
    `holon execute <plan_branch>`, `holon review <execution_branch>`, and `holon calibrate <execution_branch>`).
- **Ledger-Only Conflicts Do Not Require Test Runs**: When merging or rebasing `origin/main` into a Holon flow branch
  and the conflict is confined entirely to `holon-knowledge/ledger/*.jsonl`, running test suites is not required.
  Resolve the conflict by interleaving records chronologically by timestamp (`created_at`), verify all lines parse as
  valid JSON, commit, and push directly.
- **Mandatory Target-Branch Conflict Resolution Before Review Approval & Calibration**: Before posting an `APPROVED`
  consensus review to GitHub or running `holon calibrate`, always check
  `gh pr view <pr> --json mergeable,mergeStateStatus`. If the PR is `CONFLICTING` or `DIRTY` against `origin/main`,
  immediately fetch `origin/main`, merge it into the execution branch, resolve the conflicts (interleaving ledger
  entries chronologically), commit, and push to `origin`. Never post approval or calibrate while a PR is conflicting.

### 3. Task Completion

- Change the status field to `completed`.
- **Format Before Commit (Harness vs Nested Target Worktrees)**:
  - **In the harness (`holon-agentic-coder-ref-metadata`)**: Format all markdown files by running
    `npx prettier --write "**/*.md"`.
  - **In nested target worktrees (`apps/<project>/<branch>/`)**: Prettier resolves configuration upward and will
    erroneously find the parent harness's `.prettierrc.json` (`printWidth: 100`, `proseWrap: always`), which target
    repositories do not carry. A repo-wide `prettier --write "**/*.md"` in a nested worktree reflows unrelated documents
    and breaks CI hygiene checks. Inside nested target worktrees:
    1. Format **only the changed files**: `npx prettier --write <changed_files>`.
    2. Scope Prettier to the target repository's own configuration if it defines one, or pass `--no-config` if it does
       not.
    3. Always verify with `git diff --stat` before committing that no unintended files were touched.
- Commit the changes on your own feature branch/worktree (creating one is allowed autonomously; never commit in a `main`
  worktree).
- Squash all branch commits relative to the `main` branch into a single commit, rule 4 exemptions excepted: a branch the
  Holon flow or a review loop drives keeps one commit per pass and is never squashed.
- **Pushing your own feature branch is allowed autonomously** (see step 5 below). Never push `main`, never push a branch
  another agent owns, and never push from a `main` worktree.

---

## 📥 Target Repositories Setup (Git Worktree)

To work with codebase repositories within this metadata repository, you must clone them as Git bare repositories and
check out branches as Git worktrees. This allows running multiple tasks on different branches simultaneously under a
clean directory structure.

### 1. `holon-agentic-coder` (Primary Fractal Intent Evolution Engine)

1. **Clone the repository as bare** into the hidden `.git` folder of the `apps/holon-agentic-coder` directory:
   ```bash
   git clone --bare git@github.com:Holon-Agentic-Coder/holon-agentic-coder.git apps/holon-agentic-coder/.git
   ```
2. **Navigate into the git database directory and configure fetch refspec**:
   ```bash
   cd apps/holon-agentic-coder/.git
   git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
   git fetch origin
   ```
3. **Set up worktrees for your branches**:
   - **For the `main` branch** (checked out to `apps/holon-agentic-coder/main`): This is the primary active branch
     tracking `origin/main`.
     ```bash
     git worktree add ../main main
     ```
   - **For a specific feature branch `{branch_name}`** (checked out to `apps/holon-agentic-coder/{branch_name}`): All
     development and feature changes must be created in their own dedicated worktree off `origin/main` with
     `--no-track`:
     ```bash
     git worktree add --no-track -b {branch_name} ../{branch_name} origin/main
     ```

### 2. `holon-coherence` (Optimization Gateway & Wire Telemetry)

1. **Clone the repository as bare** into the hidden `.git` folder of the `apps/holon-coherence` directory:
   ```bash
   git clone --bare git@github.com:Holon-Agentic-Coder/holon-coherence.git apps/holon-coherence/.git
   ```
2. **Navigate into the git database directory and configure fetch refspec**:
   ```bash
   cd apps/holon-coherence/.git
   git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
   git fetch origin
   ```
3. **Set up worktrees for your branches**:
   - **For the `main` branch** (checked out to `apps/holon-coherence/main`): This is the baseline active branch.
     ```bash
     git worktree add ../main main
     ```
   - **For a specific feature branch `{branch_name}`** (checked out to `apps/holon-coherence/{branch_name}`): All
     development and feature changes must be created in their own dedicated worktree off `origin/main` with
     `--no-track`:
     ```bash
     git worktree add --no-track -b {branch_name} ../{branch_name} origin/main
     ```

---

## 🌿 Git & Commit Guidelines

To maintain clean repository history, follow this Git workflow:

1. **Branching & Worktree Isolation (One Worktree Per Agent)**:
   - **Every agent works in its own worktree, and works exclusively there.** Give the worktree and branch your agent or
     bean identifier so concurrent agents never share a directory or a branch (e.g.
     `apps/holon-coherence/fix-0027-host-local-llm-routing` for branch `fix/0027-host-local-llm-routing`). Never edit,
     commit to, or reuse another agent's worktree or branch. Name it by whichever of these applies:
     - The checkout tracks a **Holon flow branch** (`I-.../P-.../E-.../...`), which always has a Pull Request: the
       worktree directory carries the **PR number and a slug**, `apps/<project>/pr<N>-<slug>` (e.g.
       `apps/holon-agentic-coder/pr61-agent-output-capture`). The flow ref keeps its exact audited name -- never rename
       or re-cut it -- so the marker lives on the directory.
     - **No Holon flow branch** is involved: the directory carries the **bean number**,
       `apps/<project>/<type>-<bean-id>-<slug>` for branch `<type>/<bean-id>-<slug>`. Log the bean first if the work is
       not tracked yet.
     - The worktree is **temporary**: make the name state its purpose in full,
       `apps/<project>/<purpose>-<subject>-<qualifier>` (e.g. `verify-pr61-agent-output-redaction`,
       `repro-0028-proxy-port-conflict`). Opaque names (`tmp`, `wip`, `scratch`, `test1`, or letter suffixes such as
       `resolve-a` / `calib-b`) are prohibited, because `git worktree list` exposes only path, commit and refname and a
       cleanup pass cannot attribute what it cannot read. Remove it when the purpose is done.
   - **Never develop or make code changes directly on the `main` worktree in `apps/holon-agentic-coder` or `main`
     worktree in `apps/holon-coherence`.** Those checkouts are the **user's playground**: no edits, staging, commits,
     stashes, resets, cleans, checkouts, builds, stray files, or local-state mutation of any kind (including `.venv/`,
     caches, and generated artifacts).
   - **Autonomous branch creation is allowed.** Do not wait to be asked: create the worktree and branch yourself, then
     work exclusively inside it. Inside your own worktree you have full latitude to edit, commit, squash, test, and
     rebuild images.
   - For `apps/holon-agentic-coder/`, a dedicated Git worktree (e.g. `apps/holon-agentic-coder/feat-<name>` branched off
     `origin/main`) is where you build images, inspect code, run verification, and operate the harness. It is **not** a
     surface for authoring changes: every `holon-agentic-coder` source change is produced by the Holon flow (invariant 8
     in [rules.md](rules.md) and the Sole Change Path in [AGENTS.md](../AGENTS.md)), so hand-authoring or
     hand-committing that repository's source from a worktree stays prohibited.
   - For all code changes in `apps/holon-coherence/`, work must happen in a dedicated Git worktree (e.g.
     `apps/holon-coherence/feat-<name>` branched off `origin/main`). The flow resolves exactly one remote per run and
     cannot reach this repository, so coherence changes are worktree-authored.
   - If work has already landed in a `main` worktree, move it into a dedicated worktree and restore `main` to a pristine
     checkout.
   - Each worktree owns its environment: run `uv sync --group dev` inside it. Virtualenvs are directory-bound and their
     console-script shebangs are absolute, so never reuse another worktree's `.venv/` or reuse one after moving the
     repository (recreate it instead).
   - In this metadata repository (`holon-agentic-coder-ref-metadata`), work on the active checked-out branch.
   - Branch naming convention:
     `git worktree add --no-track -b <type>/<bean-id>-<short-description> ../<branch-dir> origin/main` (e.g.,
     `feat/0001-add-agent-rules`). Run this from the bare repository directory (`<project>/.git`): `../` resolves
     relative to that directory, which is what places the checkout at `<project>/<branch-dir>`. When the checkout is
     raised for an existing Pull Request instead -- always the case for a `I-.../P-.../E-.../...` flow branch -- name
     the directory `pr<N>-<slug>` (e.g. `pr61-agent-output-capture`) while checking the flow ref out under its own exact
     name; a temporary checkout takes a fully descriptive `<purpose>-<subject>-<qualifier>` directory name.
2. **Formatting (Mandatory)**:
   - Always run `npx prettier --write "**/*.md"` to format markdown files before creating any commits.
3. **Commits**:
   - Write semantic commit messages. Example:

     ```text
     feat(agents): add core agent instructions and rules

     - Added .agents/instructions.md
     - Added .agents/rules.md
     - Configured landing page entrypoint in AGENTS.md
     ```

   - Avoid generic commit messages like "update files" or "fix".

4. **Squashing (Mandatory On Branches You Author)**:
   - Before pushing a branch you hand-authored, you **MUST squash all commits** on it relative to the target branch into
     a **single commit** (e.g., relative to `main` in this metadata repository, `holon-agentic-coder`, or
     `holon-coherence`). Such a branch should only ever contain exactly **one commit** differing from the target branch.
   - **Timing: squash once, at the very end, immediately before the push that finishes the task -- never mid-task.**
     While work is in progress, keep committing and push as you go; the maintainer checkpoints work in progress as
     `docs: wip` commits and that granularity is theirs to keep. Never `reset`, `amend`, `rebase` or squash over commits
     you did not author unless the maintainer explicitly asks: a mid-task squash destroys their checkpoints, rewrites
     shared history, and can capture another session's in-flight edits under your commit message.
   - **Branches the Holon flow or a review loop pushes are exempt.** `I-...`/`P-...`/`E-...` branches, and the branch a
     `pr-review-loop` run drives, carry one commit per intent, plan, execution, review, or resolution pass, and those
     commits are the audited provenance record: never squash, rewrite, or force-push them. Squashing mid-loop would
     require the `--force` that Principle 5 of the `pr-review-loop` skill forbids as an answer to drift, and the squash
     itself would swallow the other session's commits. The maintainer squashes when merging.
   - **Before resetting**, take the path list from `git diff --name-status $(git merge-base origin/main HEAD) HEAD` plus
     whatever you edited in the working tree: after the reset the merge base **is** `HEAD`, so running that command
     afterwards prints nothing and leaves the squash with no paths to stage. Then execute:

     ```bash
     git reset $(git merge-base origin/main HEAD)
     git add <path/this/branch/changed> <another/path/this/branch/changed>
     git commit -m "your-semantic-commit-message"
     ```

   - Stage the branch's own paths explicitly; **never `git add -A` or `git add .`**. A parallel agent session can hold
     unrelated in-flight edits in the same worktree, and a blanket add swallows them into your commit under your message
     (the hazard recorded in bean 0056).

5. **Pull Requests & Pushing (Push Your Own Worktree Branch Freely)**:
   - Pushing **your own** feature branch is autonomous -- no user instruction needed, once it is squashed to a single
     commit (rule 4; flow- and loop-driven branches push per iteration instead of squashing):
     `git push -u origin <branch-name>`.
   - When rewriting history on your own branch, use `git push --force-with-lease origin <branch-name>`.
   - **Do NOT push directly to `main` under any circumstances**, never push or force-push a branch you do not own, and
     never push from a `main` worktree.
   - **Autonomous PR Creation in the Holon Flow**: When executing the Holon flow lifecycle, Pull Request creation is
     **autonomous**: once Stage 3 (Execute) pushes the execution branch, the agent autonomously creates the Pull Request
     (`gh pr create`) against the base branch so that Stage 4 (PR review loop) can proceed seamlessly without manual
     handoff. For non-flow work (such as standalone harness branches or hand-authored worktrees), raising a Pull Request
     still requires explicit instruction from the human maintainer.
   - **Harness Branches Are Operational Workspaces (No Frequent Merging Needed)**: Branches in this metadata repository
     (`holon-agentic-coder-ref-metadata`) serve as day-to-day operational branches and persistent records of work
     completed (task tracking in `.beans/`, triage updates, rules refinement, and tooling). They do not need to be
     merged into `main` frequently. Raising a Pull Request or merging to `main` is an infrequent maintainer checkpoint,
     not a daily requirement.

> [!CAUTION] **Agents MUST NEVER merge a Pull Request.** Merging is exclusively the human maintainer's responsibility.
> The following actions are **strictly forbidden** with no exceptions:
>
> - `gh pr merge` (with any flags: `--squash`, `--rebase`, `--merge`, `--auto`, `--delete-branch`, etc.)
> - `gh pr merge --auto` or enabling auto-merge by any means
> - `gh api …` calls or any other mechanism that triggers a merge or adds a PR to the merge queue
> - `gh repo edit --enable-auto-merge` or any repository setting that enables automatic merging
>
> After the pr-reviewer ensemble consensus review is approved and posted to GitHub, the agent MUST stop all
> GitHub-facing PR activity (no further `gh pr` writes of any kind). On a PR the Holon flow drove it then runs stage 5
> (`holon calibrate <execution_branch>`) itself before requesting the merge, per "Ordering of the merge boundary" in
> [AGENTS.md](../AGENTS.md): it pushes the `/calibrated` branch, merges/fast-forwards the calibration commit into the PR
> execution branch so the calibration report is included in the PR diff, pushes to origin, and notifies the user:
>
> > ✅ **PR #N is approved.** The 3-agent ensemble consensus review has been posted to GitHub and Stage 5 calibration
> > has been completed and included in the PR. Please review and merge it manually at `<pr_url>` when you are ready;
> > merging before stage 5 (`holon calibrate`) has run destroys the `E-...` branch that calibration reads.
>
> Branch and worktree cleanup may only be performed **after** the human confirms the merge has completed, or when the
> user explicitly requests it.
