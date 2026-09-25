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

### 2. Implementation Cycle (The Holon Flow)

Changes to target codebases are authored by the flow, not by hand. Run the five stages in order; each stage produces the
branch and ledger record the next one consumes (see invariant 8 in [rules.md](rules.md)).

- **Intent**: Write the intent JSON (`description`, `goal`, `slug`, optional `target_branch`) and run
  `./holon intent <file>` to open the `I-.../_` branch and append to `holon-knowledge/ledger/intents.jsonl`. Encode the
  sandbox constraints the executor must respect inside `goal`.
- **Plan**: Run `./holon plan <intent_branch> --agent <agent> --model <model>`; review the generated `plans/P-*.md` and
  the predicted metrics recorded in `plans.jsonl` before proceeding.
- **Execute**: Run `./holon execute <plan_branch> --agent <agent> --model <model>`. Verify the pushed `E-...` branch is
  a real descendant of the plan branch (`git log --format='%H %P'`) and that the codebase tree survived -- an
  `executions.jsonl` `status: success` does not prove it.
- **Review**: Run the `pr-review-loop` skill until the ensemble reaches consensus approval. Never merge (see the
  Human-Only rule below).
- **Calibrate**: Run `holon calibrate <execution_branch>` to commit predicted-versus-actual deltas.
- **Document**: Add notes inside the task file explaining how the task was resolved, including the intent, plan, and
  execution branch names.

Until Beans 0039 and 0040 land, invoke these stages individually. Once they land, `holon flow <intent.json>` is the
preferred entrypoint; both modes satisfy the same requirement.

### 3. Task Completion

- Change the status field to `completed`.
- Format all markdown files by running `npx prettier --write "**/*.md"`.
- Commit the changes on your own feature branch/worktree (creating one is allowed autonomously; never commit in a `main`
  worktree).
- Squash all branch commits relative to the `main` branch into a single commit.
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
     commit to, or reuse another agent's worktree or branch.
   - **Never develop or make code changes directly on the `main` worktree in `apps/holon-agentic-coder` or `main`
     worktree in `apps/holon-coherence`.** Those checkouts are the **user's playground**: no edits, staging, commits,
     stashes, resets, cleans, checkouts, builds, stray files, or local-state mutation of any kind (including `.venv/`,
     caches, and generated artifacts).
   - **Autonomous branch creation is allowed.** Do not wait to be asked: create the worktree and branch yourself, then
     work exclusively inside it. Inside your own worktree you have full latitude to edit, commit, squash, test, and
     rebuild images.
   - For all code changes in `apps/holon-agentic-coder/`, work must happen in a dedicated Git worktree (e.g.
     `apps/holon-agentic-coder/feat-<name>` branched off `origin/main`).
   - For all code changes in `apps/holon-coherence/`, work must happen in a dedicated Git worktree (e.g.
     `apps/holon-coherence/feat-<name>` branched off `origin/main`).
   - If work has already landed in a `main` worktree, move it into a dedicated worktree and restore `main` to a pristine
     checkout.
   - Each worktree owns its environment: run `uv sync --group dev` inside it. Virtualenvs are directory-bound and their
     console-script shebangs are absolute, so never reuse another worktree's `.venv/` or reuse one after moving the
     repository (recreate it instead).
   - In this metadata repository (`holon-agentic-coder-ref-metadata`), work on the active checked-out branch.
   - Branch naming convention:
     `git worktree add --no-track -b <type>/<bean-id>-<short-description> ../<branch-dir> origin/main` (e.g.,
     `feat/0001-add-agent-rules`). Run this from the bare repository directory (`<project>/.git`): `../` resolves
     relative to that directory, which is what places the checkout at `<project>/<branch-dir>`.
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
4. **Squashing (Mandatory)**:
   - Before pushing your feature branch to the remote repository, you **MUST squash all commits** on your branch
     relative to the target branch into a **single commit** (e.g., relative to `main` in this metadata repository,
     `holon-agentic-coder`, or `holon-coherence`).
   - Your feature branch should only ever contain exactly **one commit** differing from the target branch.
   - To perform the squash, execute:

     ```bash
     git reset $(git merge-base origin/main HEAD)
     git add -A
     git commit -m "your-semantic-commit-message"
     ```

5. **Pull Requests & Pushing (Push Your Own Worktree Branch Freely)**:
   - Pushing **your own** feature branch is autonomous -- no user instruction needed, once it is squashed to a single
     commit: `git push -u origin <branch-name>`.
   - When rewriting history on your own branch, use `git push --force-with-lease origin <branch-name>`.
   - **Do NOT push directly to `main` under any circumstances**, never push or force-push a branch you do not own, and
     never push from a `main` worktree.
   - The human repository maintainer will review the changes and raise the Pull Request. Raising a Pull Request still
     requires explicit instruction, even though pushing does not.

> [!CAUTION] **Agents MUST NEVER merge a Pull Request.** Merging is exclusively the human maintainer's responsibility.
> The following actions are **strictly forbidden** with no exceptions:
>
> - `gh pr merge` (with any flags: `--squash`, `--rebase`, `--merge`, `--auto`, `--delete-branch`, etc.)
> - `gh pr merge --auto` or enabling auto-merge by any means
> - `gh api …` calls or any other mechanism that triggers a merge or adds a PR to the merge queue
> - `gh repo edit --enable-auto-merge` or any repository setting that enables automatic merging
>
> After the pr-reviewer ensemble consensus review is approved and posted to GitHub, the agent MUST stop all PR-related
> activity and notify the user:
>
> > ✅ **PR #N is approved.** The 3-agent ensemble consensus review has been posted to GitHub. Please review and merge
> > it manually at `<pr_url>` when you are ready. No further agent action is required.
>
> Branch and worktree cleanup may only be performed **after** the human confirms the merge has completed, or when the
> user explicitly requests it.
