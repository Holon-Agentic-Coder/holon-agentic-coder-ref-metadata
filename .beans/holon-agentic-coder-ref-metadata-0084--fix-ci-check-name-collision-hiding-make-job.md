---
# holon-agentic-coder-ref-metadata-0084
title: "Fix GitHub Actions check-name collision that hides the make job in holon-coherence CI"
status: completed
type: task
priority: low
tags:
  - ci
  - github-actions
  - holon-coherence
created_at: 2026-10-10T16:05:00Z
updated_at: 2026-10-12T18:40:00Z
---

## Summary

Spotted while reviewing holon-coherence PR #13 and deliberately kept out of it: several checks reported by
`gh pr checks 13` collide on the same name, so the `Run Make` job's result is not distinguishable in the status rollup
(observed as a bare `build` row alongside `build (macos-latest)` and `build (ubuntu-latest)`, and the make job's own row
being hard to attribute).

When a check name is ambiguous, branch protection and reviewers both read the wrong row, and a red make job can hide
behind a green one of the same name.

## Scope

- `.github/workflows/make.yml` (and `docker-build.yml` if it emits the same job name) — give each job a unique `name:`
  so `gh pr checks` / `statusCheckRollup` rows are unambiguous.
- Confirm `gh pr checks <pr>` lists every job distinctly after the change.

## Origin

Recorded `rejected: pre-existing, deferred` in `.subagent/holon-coherence_pr13_coordination.json` (reviewer 1 finding
N6) during iteration 1 of the PR #13 review loop.

## Resolution

- Worktree: `apps/holon-coherence/fix-0084-ci-check-name-collision`
- Branch: `fix/0084-ci-check-name-collision`
- In `.github/workflows/make.yml`, renamed job from `build` to `make` (`name: make (${{ matrix.os }})`).
- In `.github/workflows/docker-build.yml`, renamed job from `build` to `docker-build` (`name: docker-build`).
- Verified local test suites (530 tests pass, `task lint` pass).
- Raised [PR #15](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/15).
- All 7 GitHub Actions checks passed with distinct names: `docker-build`, `make (macos-latest)`, `make (ubuntu-latest)`,
  `hygiene`, `integration`, `unit (macos-latest)`, `unit (ubuntu-latest)`.
- 3-agent ensemble review passed with unanimous `APPROVED` verdict.
- **Merged**: PR #15 merged into `origin/main` on 2026-10-12 (merge commit `e72fc2b3bbb6650ef6475ec3d45f5e6555a380dd`).
