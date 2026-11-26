---
# holon-agentic-coder-ref-metadata-0427
title: "Strip gh CLI stderr hints from pr_url so consensus review links are not corrupted"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-4
  - github
  - holon-agentic-coder
created_at: 2026-11-24T13:00:00Z
updated_at: 2026-11-26T10:41:00Z
---

## Why

Consensus review comments posted on `holon-agentic-coder#273`, `holon-agentic-coder#274`, and `holon-coherence#55`
contain broken Markdown links polluted with multi-line `gh event listen` CLI hint text:

```text
Reviewed [preflight-retry](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/274

hint: if you need to wait for this pull request to be reviewed, merged, or closed before continuing, use this instead of polling:
    gh event listen --resource https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/274 ...
```

## Evidence (`2026-11-24T11:05Z–12:47Z` audit)

- `apps/sandbox-executor/src/sandbox_executor/flow/github/adapter_runner.py:46-48`: `GhResult.output` concatenates
  `f"{self.stdout or ''}\n{self.stderr or ''}".strip()`.
- `apps/sandbox-executor/src/sandbox_executor/flow/github/adapter.py:246`: `create_or_update_pr` returns
  `"output": result.output` without a separate clean `pr_url` parsed from `stdout`.
- `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py:722-724`:
  `"pr_url": pr_res.get("pr_url") or (pr_res.get("output") if str(pr_res.get("output", "")).startswith("http") else None)`
  matches whenever `stdout` begins with `https://...` and passes the entire `stdout + "\n" + stderr` string into
  `build_pr_review_consensus_report`, corrupting `[slug](<pr_url>)` whenever `gh` emits a `hint:` on `stderr`.
- `adapter_runner.py:51-53`: `gh_env` sets only `DOCKER_CLI_HINTS=false`, leaving `gh` hint environment flags unset.

## Proposed change

1. Parse a clean single-line `pr_url` (`re.search(r"https://\S+", result.stdout)`) in `GitHubAdapter.open_or_update` /
   `create_or_update_pr` and return it explicitly as `pr_res["pr_url"]`.
2. In `loop.py` and `review_report.py`, sanitize `pr_url` to a single HTTP(S) URL line (never accepting multi-line
   `stderr` text) and add `GH_NO_UPDATE_NOTIFIER=1` / `GH_PROMPT_DISABLED=1` to `gh_env`.
3. Add a unit test in `tests/flow/github/` and `tests/test_review_loop.py` simulating `gh pr create` returning a URL on
   `stdout` plus a `hint:` block on `stderr`.

## Expected gain

Clean, clickable PR links in every posted consensus review across `holon-agentic-coder` and `holon-coherence`, with no
`gh` wrapper noise leaked into GitHub PR threads.

## Cost

Small target-repo change through the Holon flow (`adapter_runner.py`, `adapter.py`, `pr.py`, `review/loop.py`).

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- Still active across every target repository in this window: `gh event listen` stderr hints remain embedded inside the
  Markdown link URL of consensus review comments on `holon-agentic-coder#310`–`#313` and `thomashan/dev-env#42`–`#43`.

## Progress

- 2026-11-26: in-progress, flow `pr-url-without-gh-hints` (worktree flow-pr-url-without-gh-hints, claude-agent
  claude-opus-5-5). Scope narrowed to `flow/github/pr.py`, `adapter_runner.py` and a new test, so it is disjoint from
  the live review-loop and issue-tracking flows; the `loop.py` consumer already prefers `pr_res["pr_url"]`.
- 2026-11-26: PR #330 approved (3/3 consensus, review iteration 2), calibrated, MERGEABLE/CLEAN, all checks green;
  awaiting maintainer merge.

## Resolution

Delivered via [PR #330](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/330) and merged into `main`
(`a71b8a6b`, 2026-11-26T10:39:00Z):

- **Key Architectural Deliverables**: `create_or_update_pr` (`flow/github/pr.py`) returns an explicit single-line
  `pr_url` parsed from `gh` stdout only (`https://\S+`), never the stdout+stderr concatenation; `gh_env`
  (`flow/github/adapter_runner.py`) also sets `GH_PROMPT_DISABLED=1` and `GH_NO_UPDATE_NOTIFIER=1`.
  `flow/review/loop.py` drops the fallback to the combined `output` (outside the intent scope, the same consumer-side
  edit as bean 0502; the change is a 2-line simplification).
- **Verification & Tests**: new `apps/sandbox-executor/tests/flow/github/test_pr_url.py` simulating a URL on stdout with
  a `hint:` block on stderr; module budgets untouched.
- **Holon Flow Traversal**: Intent -> Plan -> Execute completed; Stage 4 review reached 3/3 consensus at iteration 2
  (one nit, R1-F1, applied); calibration recorded; PR checks green before merge.
