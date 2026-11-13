---
# holon-agentic-coder-ref-metadata-0294
title: "The committed uv.lock matches the project and container Python, so flows stop producing lockfile churn"
status: todo
type: bug
priority: high
tags:
  - uv
  - lockfile
  - flow
  - holon-agentic-coder
created_at: 2026-11-13T11:00:00Z
updated_at: 2026-11-13T11:00:00Z
---

## Problem

`apps/sandbox-executor/uv.lock` on `main` records `revision = 3` and `requires-python = ">=3.14"`, but the project and
the agent and review-loop containers run Python 3.13. Every `uv run` in a container (the executor's test run, the
resolver's verification) rewrites the lock to `revision = 5` and `>=3.13`, which then shows up in the pull request as
"unrelated lockfile churn". Seen on PR #184 and PR #187: the executor or resolver committed the rewrite, the reviewers
flagged it as an important finding, and the resolver's attempt to revert it to `main`'s version fought the rewrite. A
host `uv` (newer Python) rewrites it the other way. Flows also keep sweeping a stray lock edit into a commit.

## Goal

1. Regenerate and commit the lockfile so it matches the project's `requires-python` and the container's `uv`, so a
   container `uv run` leaves it unchanged.
2. Run the flow's own `uv` invocations with the lock frozen (`--frozen` or `UV_FROZEN`) so a stage can never rewrite it,
   and fail clearly if the lock and `pyproject.toml` disagree.
3. A test asserts the committed lock needs no rewrite (`uv lock --check`) in the container image and in CI.
4. Reviewers and the resolver treat a lockfile change that no `pyproject.toml` change explains as a defect to revert.

## Notes

- Target repository change in `holon-agentic-coder`: through the 5-stage Holon flow. The intent JSON must not mention
  bean ids or harness paths.
- Touches `uv.lock`, the container build and the stages' `uv` invocations; run it when no other flow edits those.
