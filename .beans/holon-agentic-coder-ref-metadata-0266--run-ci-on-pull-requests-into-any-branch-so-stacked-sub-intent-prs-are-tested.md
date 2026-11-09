---
# holon-agentic-coder-ref-metadata-0266
title: "Run CI on pull requests into any branch so stacked sub-intent PRs are tested"
status: in-progress
type: bug
priority: critical
tags:
  - ci
  - github-actions
  - flow
  - decomposition
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-09T11:00:00Z
updated_at: 2026-11-09T11:00:00Z
---

## Problem

When a plan is over its entropy budget, Stage 3 decomposes it into sub-intents and runs each as a child flow. Each child
opens its own pull request **against the parent intent branch** (`I-.../_`), not against `main`. During the Bean 0262
flow, PR #152 (sub-intent 1 of 4) had base `I-1794214501-mount-host-worktree-into-sandbox-containers/_`.

Every CI workflow in `.github/workflows/` restricts its `pull_request` trigger to `branches: [main]`:
`docker-build.yml`, `make.yml`, `test-hygiene.yml`, `test-integration.yml`, `test-stress.yml` and `test-unit.yml`. A
pull request into any other branch therefore gets **no checks at all**. The Stage 4 review loop then found no Stage 3
test result and no CI checks, waited 180 seconds for checks to register, and halted:

```text
[Review Loop] No CI checks registered within 180s.
[Review Loop] Halting review loop without consensus: test results not measured.
Stage 4 failed: Autonomous review consensus failed: test results not measured: no recorded Stage 3 test result and no CI checks.
```

This happened with all three reviewers approving at iteration 5 (0 critical, 0 important, 0 nit), so the failure is
purely that nothing measured the tests. It will hit every sub-intent of every decomposed flow, so decomposed flows
cannot currently complete.

## Goal

1. **Run the CI workflows for pull requests into any base branch.** Remove the `branches: [main]` filter from the
   `pull_request` trigger of the six workflows above, so stacked sub-intent PRs get the same checks as PRs into `main`.
   Keep the `push` trigger limited to `main` (flow branches are not built on push), and keep the existing `types`,
   `concurrency` and `workflow_dispatch` settings. Do not add triggers that run twice for the same commit.
2. **Document it.** Update `.github/workflows/README.md` (and any CI notes in `docs/`) to say that pull requests into
   any branch run the checks, and why.
3. **Guard it with a test.** Add a hermetic pytest that reads each workflow in `.github/workflows/` and fails when a
   workflow that runs on `pull_request` restricts it to named base branches, so the filter cannot come back. Use only
   the standard library or a parser already in the project's dependencies; add no new dependency.
4. **Check the review loop's expectation.** Confirm `Stage 4` waits for and reads checks on a stacked PR the same way as
   for a PR into `main`; if any code assumes the base is `main` when resolving checks or mergeability, fix it. Add a
   test for a stacked PR whose base is a parent intent branch.
5. **Constraints**: `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no behaviour change outside CI
   triggers and the check resolution above.

## Notes

- Checks named `Analyze (python)`, `Analyze (actions)` and `CodeQL` come from GitHub's default CodeQL setup, not from a
  file in this repository, so they may still not run on stacked PRs. The review loop only needs at least one check to
  register, which the six workflows provide.
- Cost: stacked PRs now run the full matrix. That is the intended trade-off, and `concurrency` already cancels
  superseded runs on pull requests.
- Blocks the Bean 0262 flow, which is halted at sub-intent 1 of 4 with a checkpoint at
  `apps/holon-agentic-coder/flow-mount-host-worktree-into-sandbox-containers/.holon/flow/`. Resume it from that
  checkpoint once this lands and the images are rebuilt.
- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow. The intent JSON
  must not mention bean IDs or harness paths.
