---
# holon-agentic-coder-ref-metadata-0262
title:
  "Mount host-provisioned worktree into sandbox containers to eliminate in-container git cloning and mid-crash state
  loss"
status: todo
type: task
priority: high
tags:
  - flow
  - sandbox
  - docker
  - git
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-09T07:47:00Z
updated_at: 2026-11-09T07:47:00Z
---

## Problem

Currently, `sandbox-executor` dispatches role containers (review ensemble, Stage 4 resolver, and executors) using named
Docker volumes (e.g. `holon-review-ws-...`) and executes `git clone` or `git fetch` against `origin` (GitHub) inside the
container:

1. **Destructive Container Preamble & Mid-Crash State Loss**: Every container launch executes:
   ```bash
   git reset --hard HEAD
   git clean -fdx
   git fetch origin +refs/heads/<branch>:refs/remotes/origin/<branch>
   git checkout -B <branch> origin/<branch>
   ```
   If a container crashes, is killed by OOM or timeout, or fails midway through editing or testing, any unpushed edits
   or local commits are permanently destroyed on the next restart by `git reset --hard` and
   `git checkout -B ... origin/...`. This is the exact vulnerability that caused Bean 0256 (unpushed local resolver
   commits wiped on next iteration).
2. **Network & Proxy Fragility**: Cloning inside the container requires egress access to GitHub, passing GitHub tokens
   (`GITHUB_TOKEN`) into sandboxed environments, and waiting for proxy sidecars (e.g. mitmproxy) to become ready.
   Network hiccups, rate limits, or port delays crash or stall container initialization.
3. **Volume Management Overhead**: Named Docker volumes are root-owned on creation and require a separate root init
   container (`docker run --rm --network none --entrypoint chown ... -R 1000:1000`) before unprivileged agents can write
   to them, leaving orphaned volumes that must be manually pruned.

## Decision: Clean Division of Responsibilities

Adopt **Option A: Direct Bind-Mount of Dedicated Worktree** with a strict, minimalist boundary between the host harness
and the sandbox container:

### 1. Harness (Host) Responsibility: Pre-Launch Provisioning & Mount

Before starting up the container, the harness is solely responsible for worktree readiness:

- **Inspect / Provision Target Worktree**: Check whether `--target-worktree` / `--target-dir` is an existing valid git
  worktree. If absent, provision the dedicated sibling worktree (`apps/<repo>/flow-<slug>`) from `origin/main` (per Bean
  0259).
- **Bind-Mount Worktree into Container**: Mount the host worktree directory directly at
  `/home/holon/.holon-sandbox/workspace` (`-v /path/to/worktree:/home/holon/.holon-sandbox/workspace`).
- **Worktree Gitdir Resolution**: Ensure the backing `.git` directory is resolvable inside the container (e.g. read-only
  mount of the repository's `.git` or relative gitdir path) so git commands inside the container execute hermetically.
- **Launch Container**: Dispatch the container without named Docker volume creation or root `chown` init-container
  boilerplate.

### 2. Container Responsibility: Autonomous Execution, Verification & Direct Push

Once started, the container operates directly on the mounted worktree:

- **Zero Cloning & Zero Destructive Preamble**: The container finds its workspace already provisioned. It does **not**
  run `git clone`, `git fetch`, or destructive wipes (`git reset --hard HEAD` / `git clean -fdx`).
- **Autonomous Task Execution**: The agent / role (Intent, Plan, Execute, Review Ensemble, Resolver) runs all its edits,
  linter checks, and test suites directly in the mounted workspace.
- **Direct Commit & Push**: When fixes or stage outputs are ready, the container runs verification, commits with
  canonical trailers, and **pushes directly to the remote** (`git push origin HEAD:refs/heads/<branch>`). The harness
  does not need to intermediate git commits or pushes.
- **Unified Intermediate Artifacts in `<worktree>/.subagent/` (Singular)**:
  - The canonical directory is strictly **`.subagent/`** (singular, matching `AGENTS.md` Invariant 11, `.gitignore`, and
    existing skills).
  - All intermediate subagent files—reviewer turn prompts, agent responses, dispositions JSON, stderr tails, scratch
    notes, and review state artifacts—must be written to `<worktree>/.subagent/` (e.g.
    `<worktree>/.subagent/review/iter-<N>/`).
  - **Shared Contract Across Manual Skills & Sandbox**: This creates a seamless, unified contract between manual host
    skills (`pr-review-loop`, `pr-reviewer`, `pr-review-resolver`) and the containerized sandbox (`review_loop.py`).
    Regardless of whether a review pass was initiated manually by an agent skill on the host or inside a sandbox
    container, both read, write, resume, and audit intermediate files in the exact same location.
  - Because `.subagent` is in `.gitignore`, it never pollutes git history or PR diffs, while remaining immediately
    accessible on the host for live monitoring, resume operations, and post-crash forensics.
- **Instant Crash-Resilience**: Because the worktree is directly mounted from the host, every intermediate file edit and
  test log is already on the host disk in real time. If a container crashes, times out, or OOMs, zero state is lost.

### Worktree Naming Conventions (`flow-<slug>` vs `pr<N>-<slug>`)

To eliminate worktree fragmentation, avoid unnecessary directory churn, and provide a clean lifecycle:

1. **`flow-<slug>`: The Single, Persistent Worktree for the Entire Flow Lifecycle**:
   - When a change is produced via `holon flow`, the harness provisions `apps/<repo>/flow-<slug>` at the start of
     Stage 1.
   - **`flow-<slug>` is reused across ALL 5 stages**: Intent -> Plan -> Execute -> Review Loop -> Calibration.
   - Opening a Pull Request at the end of Stage 3 **does not rename or recreate** the worktree. Stage 4 Review Loop,
     Resolver turns, and Stage 5 Calibration continue operating directly inside the existing `apps/<repo>/flow-<slug>`
     worktree.
2. **`pr<N>-<slug>`: Strictly for Standalone External PR Reviews**:
   - The `pr<N>-<slug>` naming convention is reserved strictly for standalone skills (`pr-reviewer`, `/pr-review-loop`)
     when invoked on an existing Pull Request from GitHub **when no local worktree is already checked out**.
   - If a review loop or resolver is invoked on a PR that already has a local `flow-<slug>` worktree checked out, it
     **reuses `flow-<slug>` directly** without creating a redundant checkout.
3. **Container Mount Target**:
   - The active host worktree (`apps/<repo>/flow-<slug>` for flows, or `apps/<repo>/pr<N>-<slug>` for standalone PR
     reviews) is bind-mounted directly at: `/home/holon/.holon-sandbox/workspace`
4. **Concurrent Sub-Worktree Isolation (Optional / Multi-Reviewer Ensemble)**:
   - If concurrent reviewer turns in an ensemble run test suites simultaneously that conflict on local file locks or
     `.pytest_cache`, provision isolated ephemeral sibling worktrees: `apps/<repo>/flow-<slug>-rev<index>` (e.g.
     `apps/holon-agentic-coder/flow-resolver-commits-locally-skip-push-fix-rev1`), pruned automatically upon iteration
     completion.

### Removal of Obsolete In-Container Git & Docker Volume Logic

Mounting the host worktree makes extensive existing in-container git plumbing completely obsolete. This bean deletes:

1. **Delete In-Container Clone, Fetch & Destructive Wipe Functions (`entrypoint/review_loop.py`)**:
   - Delete `_clone_or_fetch()` (`git clone --branch`, `git fetch origin`).
   - Delete `_reset_reused_checkout()` (`git reset --hard HEAD`, `git clean -fdx`, `git rebase --abort`,
     `git merge --abort`).
   - Delete `_ensure_head()`, `_origin_matches()`, and `_has_checkout()`.
   - Simplify workspace initialization to a clean validation that `/home/holon/.holon-sandbox/workspace` exists and
     reading `git rev-parse HEAD`. The container starts working immediately.
2. **Direct Commit & Push Kept in Container**:
   - The container continues to create canonical trailer commits and push directly
     (`git push origin HEAD:refs/heads/<branch>`).
   - The harness does not need to intermediate git commits or pushes.
3. **Delete Docker Named Volume Machinery (`flow/review/workspace.py`)**:
   - Delete `ReviewWorkspaceSession` volume creation (`docker volume create --label holon.review-session=1`).
   - Delete root `chown` init container (`docker run --rm --network none --user root ... chown -R 1000:1000`).
   - Delete volume teardown (`docker volume rm -f`) and pruning heuristics (`review_session_volume_name()`,
     `HOLON_REVIEW_PERSIST`).

## Scope

- `apps/sandbox-executor/src/sandbox_executor/flow/review/workspace.py`
- `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`
- `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/flow.py`
- `apps/sandbox-executor/tests/flow/test_workspace.py`
- `apps/sandbox-executor/tests/test_review_loop.py`
