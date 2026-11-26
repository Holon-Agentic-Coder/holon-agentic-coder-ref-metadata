---
# holon-agentic-coder-ref-metadata-0512
title: "Push PR-merged events to wake the agent and automatically run post-pr-merge"
status: todo
type: feature
priority: high
tags:
  - harness
  - github
  - webhook
  - post-pr-merge
  - automation
  - ntfy
created_at: 2026-11-26T10:55:00Z
updated_at: 2026-11-26T10:55:00Z
---

# Push PR-merged events to wake the agent and automatically run `post-pr-merge`

## Problem

Every time the maintainer merges a ready Pull Request on GitHub (`holon-agentic-coder`, `holon-coherence`, or
`dev-env`), the agent remains unaware until the maintainer manually pastes `<pr_url> has been merged` into the chat
session. Only then does the agent trigger `post-pr-merge` (trunk sync, CLI/image rebuild, bean closure, worktree/branch
cleanup, triage refresh, audit count, and next-bean backfill).

Existing pieces do not close this loop:

- Bean `0182` built `.agents/scripts/event_watcher.py` and `.agents/scripts/wait_for.py`, but the watcher is not kept
  running, relies on polling, and explicitly stops short of dispatching `post-pr-merge`.
- Bean `0352` designs `gh webhook forward` as a general wait-source abstraction for CI/review waits, but does not wire
  an automatic post-merge push trigger into active agent sessions or a persistent host dispatcher across all managed
  repositories (including `dev-env`).

## Proposed Change

Build an end-to-end **PR-merged push $\rightarrow$ automatic `post-pr-merge`** pipeline across all managed repositories
(`Holon-Agentic-Coder/holon-agentic-coder`, `Holon-Agentic-Coder/holon-coherence`, and `thomashan/dev-env`):

1. **Push Ingress (GitHub $\rightarrow$ Host, Zero-Poll Primary)**:
   - Support a pluggable push listener with two push transports (plus ETag polling fallback when offline/unconfigured):
     - **Option A — `gh webhook forward` / `gh event listen`** (reusing Bean `0352`'s source interface): stream
       `pull_request` (`closed` + `merged`) events directly to a local listener with zero repo workflow changes
       (switches to `gh event listen` automatically once GitHub enables Event Streams on the account).
     - **Option B — GitHub Actions `pull_request` (`closed` + `merged == true`) $\rightarrow$ private `ntfy.sh` SSE
       stream**: a tiny workflow in each managed repository publishes a minimal hint (`repo` + `pr` number only, zero
       secrets or code) to a dedicated private `ntfy` topic, and the host subscribes over Server-Sent Events
       (`GET /<topic>/json`, zero polling, zero GitHub API rate limit, works behind NAT without `admin:repo_hook`).
   - Treat every push message strictly as an **untrusted hint**: before acting, always verify live state via
     `gh pr view <N> --repo <owner>/<repo> --json state,mergedAt,mergeCommit,baseRefName` and confirm
     `state == "MERGED"` and `baseRefName == "main"`.
2. **Agent Wakeup & Automatic `post-pr-merge` Dispatch**:
   - **In-session reactive wakeup (zero tokens while waiting)**: when a `holon-flow` reaches Stage 5
     approval/calibration and reports "awaiting human merge", automatically start a lightweight background merge-wait
     task subscribed to the push stream for `<repo>#<N>` (costing zero model tokens while idle). The moment the PR
     merges on GitHub, the background task exits `0` with verified `{repo, pr, merge_commit, merged_at}`, reactively
     waking the session to spawn `#<N> - post-merge` via the `post-pr-merge` skill.
   - **Persistent host dispatcher (when no session is waiting)**: run a lightweight macOS `launchd` LaunchAgent
     (mirroring `.agents/skills/run_247/scripts/com.holon.limit-watch.plist`) listening to the push stream so merges
     performed while no interactive chat is open still trigger `post-pr-merge` (for example by creating a lowest-tier
     Antigravity conversation via `ConversationService/CreateConversation` or invoking a deterministic post-merge
     runner), then sending a single completion `ntfy` once post-merge finishes.
3. **Idempotency, Concurrency & Guardrails**:
   - Maintain an atomic lock and handled-merge ledger (e.g. `.subagent/handled_merges.json` keyed by
     `<owner>/<repo>#<N>@<merge_commit>`) so in-session reactive waiters, parallel sessions, and the persistent daemon
     never double-run `post-pr-merge` for the same PR (addressing burst-merge races noted in Bean `0455`).
   - Strict repository allowlist (`holon-agentic-coder`, `holon-coherence`, `dev-env`) and `baseRefName == "main"`
     filter (sub-intent PRs into plan branches never trigger `main` post-merge).
   - Only act on PRs tracked by a flow worktree, state file, or bean; ignore foreign/untracked PRs.
   - Human-only merge boundary stays absolute: the push pipeline reacts strictly _after_ human merge and never merges,
     approves, or pushes to `main`.
   - Redact all tokens and never log or commit `ntfy` topics or webhook secrets.
4. **Tests & Documentation**:
   - Add hermetic pytest coverage in `tests/` (faked push stream + faked `gh` CLI) verifying:
     - a `pr_merged` push hint triggers live `gh pr view` verification and fires `post-pr-merge` dispatch once,
     - spoofed or unmerged hints (`state != "MERGED"` or `baseRefName != "main"`) are rejected,
     - duplicate deliveries or simultaneous in-session + daemon triggers are deduplicated by the atomic handled-merge
       lock,
     - disconnected push streams reconnect with backoff and fall back cleanly to ETag polling.
   - Document setup, start/stop, and guardrails in `.agents/pr-merging.md` and `.agents/skills/post_pr_merge/SKILL.md`.

## Acceptance Criteria

- Merging an approved PR into `main` on `holon-agentic-coder`, `holon-coherence`, or `dev-env` automatically notifies
  the agent via push (within seconds, zero polling tokens) and runs the `post-pr-merge` lifecycle without the maintainer
  typing a manual merge message.
- Verified live against GitHub before acting; duplicate or non-`main` merge events are ignored idempotently.
- Works both when an interactive session is open (reactive background wakeup) and when no session is open (persistent
  host dispatcher).
- Hermetic pytest suite passes via `uv run pytest`, and all touched harness markdown passes Prettier.

## Notes

- Primary work lives in the harness (`.agents/` and `tests/`); if Option B (`ntfy` workflow) is selected, each target
  repository's GitHub Actions workflow change goes through `holon flow`.
- Related beans: Bean `0182` (persistent polling event watcher & `wait_for.py`), Bean `0352` (`gh webhook forward` push
  primitive), Bean `0455` (`post-pr-merge` burst-merge safety), Bean `0396` (session-surviving flow runs).

## Resolution

Pending.
