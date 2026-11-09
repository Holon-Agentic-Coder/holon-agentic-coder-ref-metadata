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

To eliminate worktree fragmentation, avoid unnecessary directory churn, and establish an unambiguous contract, the exact
rules governing worktree naming are defined below:

| Scenario                        | Target Path                          | When It Applies                                                                                               | Reuse Rule                                                                                                                        |
| :------------------------------ | :----------------------------------- | :------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------- |
| **Full Flow (`holon flow`)**    | `apps/<repo>/flow-<slug>`            | Stages 1–5: Intent $\rightarrow$ Plan $\rightarrow$ Execute $\rightarrow$ Review Loop $\rightarrow$ Calibrate | **Single persistent worktree**: provisioned at start and reused through calibration. Opening a PR does NOT rename or recreate it. |
| **Review on Existing Worktree** | `apps/<repo>/flow-<slug>`            | Running review loop / resolver on a branch/PR that already has a local worktree                               | **Reuses `flow-<slug>` directly**: never provisions a redundant `pr<N>-<slug>` checkout.                                          |
| **Standalone PR Review**        | `apps/<repo>/pr<N>-<slug>`           | Ad-hoc external review (`/pr-reviewer`, `/pr-review-loop`) where no local worktree exists                     | **Provisions `pr<N>-<slug>`**: strictly because no worktree is currently checked out on the host.                                 |
| **Concurrent Ensemble Turns**   | `apps/<repo>/flow-<slug>-rev<index>` | Parallel reviewer turns executing simultaneous test suites                                                    | **Ephemeral sibling**: isolated for the pass, pruned automatically upon iteration completion.                                     |

### Mandatory Purge of Obsolete In-Container Git Functionality & Tests

> [!CAUTION] **Zero Dead Git Code Policy**: As demonstrated in Bean 0256, in-container git plumbing (`git reset --hard`,
> `git clean -fdx`, `git checkout -B`, unpushed resolver commits) is inherently fragile and error-prone. With host
> worktree mounting, **all in-container cloning, checkout, and volume reset logic becomes completely obsolete**. Leaving
> dead in-container git functions, fallback branches, or legacy tests lying around will cause confusion, false
> regressions, and serious maintenance hindrance. **All legacy in-container git functions and their associated unit
> tests MUST be completely deleted.**

Specifically, this bean deletes:

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
4. **Purge Associated Legacy Tests (`tests/test_review_loop.py` & `tests/flow/test_workspace.py`)**:
   - Remove obsolete unit tests that assert named volume creation, root `chown` invocation, container-side git cloning,
     or `_reset_reused_checkout` behavior.
   - Replace with clean tests asserting:
     - The host worktree is validated / provisioned and bind-mounted into the container.
     - The container starts without remote cloning or destructive resets.
     - Files written by the container are immediately present on the host worktree.
     - Container crashes preserve all uncommitted edits and test logs on the host.

## Scope

- `apps/sandbox-executor/src/sandbox_executor/flow/review/workspace.py`
- `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`
- `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/flow.py`
- `apps/sandbox-executor/tests/flow/test_workspace.py`
- `apps/sandbox-executor/tests/test_review_loop.py`
