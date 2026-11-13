---
# holon-agentic-coder-ref-metadata-0258
title: "Resolver pre-push verification crashes because `uv` is missing from the agent image, losing the fixes"
status: completed
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - stage-4
  - resolver
  - docker
  - holon-agentic-coder
created_at: 2026-11-09T03:45:00Z
updated_at: 2026-11-09T05:30:00Z
---

## Problem

During the PR #147 flow (Bean 0254), the Stage 4 resolver crashed in review iterations 2 and 3 before it could push:

```text
File "/home/holon/src/sandbox_executor/entrypoint/review_loop.py", line 494, in _commit_and_push_resolution
  lint_ok, tests_ok, verify_err = _verify_before_push(repo_dir)
File "/home/holon/src/sandbox_executor/entrypoint/review_loop.py", line 341, in _verify_before_push
  lint_res = run_cmd(["uv", "run", "task", "lint"], cwd=repo_dir, check=False)
FileNotFoundError: [Errno 2] No such file or directory: 'uv'
```

Neither `holon/agent-claude` nor `holon/orchestrator` ships `uv` (checked on the images built after PR #146 merged):
`command -v uv` finds nothing, and neither `/usr/local/bin/uv` nor `/home/holon/.local/bin/uv` exists. The iteration 1
resolver did run `uv run task lint` and `uv run task test` successfully and pushed `1838ff7`, most likely because the
agent installed `uv` itself during that session. That is not guaranteed, so whether the resolver can push is a coin
toss.

Consequences:

1. **Fixes are lost silently.** The crash discarded the iteration 2 fixes (two important findings) and the iteration 3
   fixes (two nits). The loop then started the next iteration as if they had been resolved.
2. **The consensus post misreports the result.** The GitHub review posted at iteration 4 said "APPROVED (3/3)" with 0
   nits, but reviewer 3 was still `CHANGES_REQUESTED` with one open nit. That nit (the `flow/stage_conflicts.py` module
   docstring and the architecture map call the check "pre-push" when it runs before each stage) is still unfixed on the
   PR head. A resumed loop (iteration 5) approved 3/3 without anyone fixing it.

## Goal

1. **Ship `uv` in every image that runs the resolver** (pinned version, on `PATH` for the `holon` user), and add a
   build-time smoke check (`uv --version`) to the Bake target.
2. **Fail loudly, never silently**: If `_verify_before_push` cannot run its tools, return a structured resolver failure
   that halts the loop with an actionable error. Do not start the next iteration as if the findings were resolved.
3. **Honest consensus post**: The posted summary must reflect the final iteration's actual per-reviewer verdicts and
   open-finding counts. Never post 3/3 when a reviewer requested changes.
4. **Tests**: Hermetic tests in which `uv` is absent assert that the loop halts with the error. Another test asserts
   that the consensus post reports a 2/3 verdict as 2/3.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- Related to Bean 0256, which loses fixes when the resolver commits locally. The cause here is different: a missing
  binary crashes the verification step.
- Follow-up: once this lands, fix the stale "pre-push" wording in `flow/stage_conflicts.py` and `docs/architecture.md`
  through a flow.

## Resolution

Delivered via [PR #148](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/148) and merged into `main`
(`b6cd9a6`, 2026-11-09T05:16:55Z):

- **`uv` in the base image**: `holon-base` copies a pinned `uv` 0.13.7 (the latest release) from the official
  `ghcr.io/astral-sh/uv` image to `/usr/local/bin`, with a single `UV_VERSION` build argument and a build-time
  `uv --version` smoke check as the `holon` user. Documented in `docs/docker_bake.md`.
- **Fail loudly**: `entrypoint/review_verification.py` returns a structured failure naming the missing tool instead of
  raising. `resolver_result.py` turns a non-zero container exit or a missing result marker into a failed pass, and
  `flow/review/loop.py` halts the loop on any resolver error before adjudication.
- **Honest consensus post**: the heading fraction counts only completed approving reviewers, and open findings from the
  final iteration are listed (`review_report.py`, `tests/test_review_report.py`).
- **Verification**: hermetic tests for a missing `uv`, a non-zero container exit, a missing result, a 2/3 heading and
  the Dockerfile pin. CI 11/11 green. Flow module budgets were lowered, not raised.
- **Holon flow traversal**: all 5 stages on `claude-agent` / `claude-opus-5-5`. The first review loop hit the bug it
  fixes (the resolver crashed on the missing `uv` in iteration 1 and iteration 2 declared consensus on open nits). I
  rebuilt the images from the PR branch and resumed Stage 4. The resolver then ran its checks and pushed fixes in
  iterations 3 and 4, and 3/3 consensus with zero nits came at iteration 5. Calibration: predicted EV 28.58, actual
  −36.65 (ΔEV −65.23), distorted by Bean 0257 (`halted_for_human` counted as `p_success=0`). `/calibrated` was cut from
  a stale head (Bean 0253), so it was merged into the PR.
- **Follow-ups**: the stale "pre-push" wording from PR #147 (`flow/stage_conflicts.py` docstring and the architecture
  map) is still open for a follow-up flow. No Dependabot or Renovate config watches the `uv` pin.
