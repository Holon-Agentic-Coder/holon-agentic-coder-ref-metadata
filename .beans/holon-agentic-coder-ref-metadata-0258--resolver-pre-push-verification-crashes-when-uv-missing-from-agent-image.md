---
# holon-agentic-coder-ref-metadata-0258
title: "Resolver pre-push verification crashes because `uv` is missing from the agent image, losing the fixes"
status: todo
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
updated_at: 2026-11-09T03:45:00Z
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
