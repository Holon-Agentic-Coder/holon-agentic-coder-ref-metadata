---
# holon-agentic-coder-ref-metadata-0175
title: "Check GitHub token scopes before Stage 3 when the plan touches workflow files"
status: in-progress
type: bug
priority: high
tags:
  - holon-flow
  - github
  - preflight
  - holon-agentic-coder
created_at: 2026-10-27T14:59:39Z
updated_at: 2026-11-21T01:20:00+11:00
---

## Problem

On 2026-10-27, attempt 3 of Stage 3 for Bean 0168 ran for 54.8 minutes under a 10080-minute budget, finished its work,
and then failed at the final push (`todo/logs/0168-flow-execute3.log`):

```text
! [remote rejected] I-…/P-…/E-1793109846-…/_ (refusing to allow an OAuth App to create or update workflow
`.github/workflows/test-unit.yml` without `workflow` scope)
```

`holon` hands the sandbox the `gh` CLI's token (`cli.py` around line 207, `gh auth token`). Its scopes were
`admin:public_key, gist, read:org, repo`, with no `workflow`. The intent explicitly asks for a change to
`.github/workflows/test-unit.yml`, so the push was bound to fail, and nothing checked this before the agent spent an
hour. The work was then lost: the agent had committed it inside the container, the push failed, the `--rm` container
exited, and the failure path saves nothing (Bean 0171).

## Scope

- **Pre-flight before Stage 3,** or as early as the plan's file list is known (Bean 0151's touch set). If the plan or
  intent touches `.github/workflows/**`, check that the token has the `workflow` scope (`gh api -i user` and the
  `X-OAuth-Scopes` header, or the fine-grained token's permissions). If it does not, fail fast with an actionable
  message, for example "run `gh auth refresh -h github.com -s workflow`", before any agent tokens are spent.
- **`holon doctor`** reports the GitHub token's type and scopes, never its value, and warns when `workflow` is missing.
- **Push failures.** On a rejected push, Stage 3 must keep the execution's commits. Push them to a recovery ref, or
  leave them in a preserved container or volume, and say where. Share the implementation with Bean 0171.
- **Tests,** with mocked `gh` responses only: scope present or missing, against a touch set with and without workflow
  files; a rejected push keeps the commits.

## Notes

- Run through the Holon flow on holon-agentic-coder. It overlaps Bean 0171 (the executor failure path) and
  `preflight.py` and `cli.py`.
- The immediate fix for Bean 0168 is a maintainer action: `gh auth refresh -h github.com -s workflow`.

## Audit (2026-11-21)

Still valid; no scope check exists. The `gh auth token` handoff now lives under `cli/__init__.py` (the `cli.py`
references above are stale), and the flow-level touch set (`touch_set.py`,
[PR #194](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/194)) now gives the pre-flight a plan file
list to inspect for `.github/workflows/**`.

## Flow run (2026-11-23)

- Intent: `todo/intent-0175-preflight-github-token-scopes-v2.json` (fresh from current main; the earlier attempt
  `I-1795388456-preflight-github-token-scopes` never opened a PR and is stale, its `flow-preflight-github-token-scopes`
  worktree and branches are for cleanup).
- PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/244
- Stage 3 first attempt exited with SIGKILL (exit -9) after 2.5 min, probably the Docker VM's 8 GB limit under
  concurrent flows (not confirmed); resumed from the execute checkpoint. Stage 4 halted on a DIRTY PR (ledger-only
  conflict), merged origin/main and resumed from review.
