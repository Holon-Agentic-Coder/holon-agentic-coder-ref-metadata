---
# holon-agentic-coder-ref-metadata-0175
title: "Check GitHub token scopes before Stage 3 when the plan touches workflow files"
status: completed
type: bug
priority: high
tags:
  - holon-flow
  - github
  - preflight
  - holon-agentic-coder
created_at: 2026-10-27T14:59:39Z
updated_at: 2026-11-23T05:53:23Z
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

## Manual review and calibration (2026-11-23)

- The flow driver had stopped. On head 575655bb the Workspace survival job failed in 2/2480 cases of
  `test_invalid_envelope_value_never_echoed_by_doctor_or_run_path` (a re-run passed). This was a false positive in the
  test, not a leak: `run_docker_container` argv holds the random `$HOME/.holon/tmp/holon-pi-agent-<8>` mkdtemp folder,
  and the test masked only the `--env-file` path. A random suffix could share a 4-letter run with the random credential
  (it fails about 1-2% of runs; reproduced deterministically). Fixed in f6feb1fc by masking exactly the fixture-owned
  paths (the check is no looser), with deterministic collision tests; review Nits (surviving mutants) applied in
  7420e5af, and the calibration-base Nit was rejected.
- Coordinator merged origin/main (#246) as f65e82bf. Iteration 13: dry run clean, CI 11/11 green, ensemble 3/3 APPROVED
  0/0/0 at 7420e5af; consensus posted as a comment (approve returns 422 on own PR).
- Stage 5 `holon calibrate`: report evaluated 7420e5af, committed 705ca34f on the PR branch (calibrated branch
  fast-forwarded to it). Calibrator still measures the touch set from the pre-merge base 64e0f0f1 (recall 0.15).

## Resolution

Delivered via [PR #244](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/244) and merged into `main`
(`252004a`):

- **Key Architectural Deliverables**: Stage 3 pre-flight checks the GitHub token's OAuth scopes against the plan's touch
  set and fails fast when `.github/workflows/**` is touched without the `workflow` scope, with the `gh auth refresh`
  remedy. `holon doctor` reports token type and scopes (never the value) and warns when `workflow` is missing. A
  rejected Stage 3 push keeps the execution's commits on a recovery ref and reports where they are.
- **Verification & Tests**: Hermetic tests with mocked `gh` responses cover scope present and missing, touch sets with
  and without workflow files, and a rejected push keeping its commits.
- **Holon Flow Traversal**: Intent, plan, execute, review loop (consensus approval, ensemble 3/3) and calibration
  completed on the v2 flow (`I-1795398772-preflight-github-token-scopes-v2`). The calibration report evaluates
  `5696afa2`: predicted EV 62.25, actual EV 73.79 (+11.54). Touch-set recall was 14.4%.
- **Cleanup**: The first-attempt worktree `flow-preflight-github-token-scopes` and the v2 flow worktree were removed
  with their leaf branches.
