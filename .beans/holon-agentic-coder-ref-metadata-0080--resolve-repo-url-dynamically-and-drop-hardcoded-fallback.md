---
# holon-agentic-coder-ref-metadata-0080
title: "Resolve the target repository URL dynamically and drop the hardcoded holon-agentic-coder fallback"
status: todo
type: bug
priority: high
tags:
  - sandbox-executor
  - cli
  - credentials
  - multi-repo
  - holon-flow
created_at: 2026-10-09T14:10:00Z
updated_at: 2026-10-09T14:10:00Z
---

## Summary

Operators currently have to prefix every `holon intent|plan|execute` call with
`HOLON_REPO_URL="https://x-access-token:$(gh auth token)@github.com/<org>/<repo>.git"`. `get_repo_url()` in
`apps/sandbox-executor/src/sandbox_executor/agent_runner.py` silently falls back to a **hardcoded**
`Holon-Agentic-Coder/holon-agentic-coder.git` (HTTPS when a `gh*`/`github_pat_*` token is present, SSH otherwise). That
is wrong for any other target repository (e.g. `holon-coherence`): the container would clone and push to the wrong
remote without any error.

The target repository must be discovered dynamically; there must be **no** hardcoded repository fallback.

## Why `.env` is not the answer

`HOLON_REPO_URL` embeds a live token (`$(gh auth token)`), which `.env` files cannot evaluate and which rotates. The CLI
also never loads `.env`. The URL and token must be derived at invocation time.

## Requirements & Acceptance Criteria

1. **Host-side resolution (`cli.py`)**: when `HOLON_REPO_URL` is unset, derive the remote from the git repository the
   command runs in (`git config --get remote.origin.url`, honouring `--repo-dir`/cwd and worktrees).
   - Normalise SSH (`git@host:org/repo.git`) and HTTPS forms into `host` + `org/repo`.
   - Pair with `find_github_token()` and forward `HOLON_REPO_URL=https://x-access-token:<token>@<host>/<org>/<repo>.git`
     into the container. If no token is available, forward the plain remote URL (SSH agent forwarding path).
   - An explicit `HOLON_REPO_URL` always wins.
2. **Container-side (`agent_runner.get_repo_url`)**: remove both hardcoded `holon-agentic-coder.git` returns. If
   `HOLON_REPO_URL` is unset, raise a clear error naming the variable and how it is normally populated. No silent
   default.
3. **Fail fast**: if the host cannot resolve a remote (not a git repo, no `origin`), exit non-zero before launching
   Docker.
4. **Never leak the token**: the tokenised URL must be redacted from logs, execution records and the ledger (reuse the
   `redact_text` path from Bean 0062); never persist it into `.git/config` of a committed artifact.
5. **Tests (hermetic)**: cover SSH and HTTPS origins, worktree origin, explicit override, missing origin, missing token,
   and assert no `holon-agentic-coder.git` literal remains in `apps/sandbox-executor/src` (update the existing
   `test_get_repo_url_*` / retired-reference guard accordingly).
6. **Docs**: update `docs/executor/execution_architecture_specification.md` and the credentials docs so `HOLON_REPO_URL`
   is described as an optional override, not a required prefix.

## Notes

- Flow-gated (`holon-agentic-coder`): must traverse all five stages; no hand-authored edit in a worktree.
- Natural batch partner for Beans 0078 + 0064 (same package, ledger/executor neighbourhood) or Bean 0079.
- Prerequisite for running the flow cleanly against `holon-coherence`.
