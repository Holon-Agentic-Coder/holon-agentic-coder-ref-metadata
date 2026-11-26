---
# holon-agentic-coder-ref-metadata-0461
title: "Main-push CI concurrency group silently cancels intermediate main commits during burst merges"
status: completed
type: bug
priority: high
tags:
  - ci
  - pipeline
  - github-actions
  - reliability
  - holon-agentic-coder
created_at: 2026-11-25T06:05:00Z
updated_at: 2026-11-26T10:52:52Z
---

# Main-push CI concurrency group silently cancels intermediate main commits during burst merges

## Problem

Five `holon-agentic-coder` GitHub Actions workflows share the same `concurrency` stanza:

- `.github/workflows/test-unit.yml:14-16`
- `.github/workflows/test-stress.yml:14-16`
- `.github/workflows/test-hygiene.yml:14-16`
- `.github/workflows/test-integration.yml:14-16`
- `.github/workflows/make.yml:14-16`

Each declares:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

Because GitHub Actions allows at most **one active run and one pending run per concurrency group**, setting
`group: ${{ github.workflow }}-${{ github.ref }}` on `push` to `main` (instead of scoping to `github.sha` or omitting
`concurrency` for `push`, as `.github/workflows/docker-build.yml` does) silently cancels intermediate queued `main` runs
whenever 3 or more PRs merge while `Test - Unit` or `Test - Stress` (`8–11 min`) are running. Even with
`cancel-in-progress: false`, the newer `push` displaces the older pending `main` run in the 1-deep queue.

## Evidence (2026-11-25T06:05Z audit, #301–#304 burst merges)

During the `#301–#304` merge burst (`05:38:33Z..05:46:57Z`, 4 merges in `8.4 min` on `main`):

- `ebcffd12` (`#301` merged `05:38:33Z`) held the active `Test - Unit` (`05:38:35Z..05:49:52Z`, `11.28 min`) and
  `Test - Stress` (`05:38:35Z..05:47:27Z`, `8.87 min`) slots.
- `67bfb621` (`#302` merged `05:41:14Z`) queued behind it, then was displaced when `d281e437` (`#303` merged
  `05:43:52Z`) arrived: **`Test - Unit` (`45555296940`) and `Test - Stress` (`45555296864`) finished
  `completed/cancelled` at `05:43:54Z` (`2.63 min` queued)** without testing `#302` on `main`.
- `d281e437` (`#303` merged `05:43:52Z`) was in turn displaced when `bdb2d5f1` (`#304` merged `05:46:57Z`) arrived:
  **`Test - Unit` (`45555590090`) and `Test - Stress` (`45555590188`) finished `completed/cancelled` at
  `05:46:59Z..05:47:00Z` (`3.10–3.12 min` queued)** without testing `#303` on `main`.

Combined with `#300–#304` all being merged `55 s` to `8.18 min` before their PR-side `Merge origin/main` CI checks
completed (`0458`), intermediate `main` commits `#302` and `#303` lost unit/stress verification on `main` as well.

## Proposed Change

1. In `.github/workflows/{test-unit,test-stress,test-hygiene,test-integration,make}.yml`, scope `concurrency.group` on
   `push` to `main` so every `main` commit's CI is not evicted from a 1-pending queue — e.g.:
   ```yaml
   concurrency:
     group:
       ${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.head_ref || format('{0}-{1}',
       github.ref, github.sha) }}
     cancel-in-progress: ${{ github.event_name == 'pull_request' }}
   ```
   (or verify `group: ...-${{ github.sha }}` when `push` vs `pull_request` `github.ref`). Confirm
   `.github/workflows/docker-build.yml` parity and update `.github/workflows/README.md` /
   `tests/test_workflow_triggers.py` if concurrency policy is tested.
2. Pair with maintainer merge wait (`0458`) so PR heads are verified before merge while `main` push history retains
   intact check-runs when not explicitly superseded.

## Expected Gain

Eliminates silent `completed/cancelled` gaps on `main` commits during burst merge sweeps (`2/6` `main` commits in the
`#300–#304` window lost `Test - Unit` + `Test - Stress` provenance).

## Cost

Small: 5 YAML workflow concurrency expressions (`+` any workflow YAML unit test) via `holon flow`
(`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0454` (`ci_bookkeeping_gate` on `Merge origin/main`), Bean `0458` (waiting for PR CI before merge).

In progress 2026-11-26: flow main-push-ci-concurrency-per-sha (log todo/flow-main-push-ci-concurrency-per-sha.log).

## Resolution

Delivered via [PR #333](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/333) and merged into `main`
(`06137f5`):

- **Key Architectural Deliverables**: the `concurrency` block of `test-unit.yml`, `test-stress.yml`, `test-hygiene.yml`,
  `test-integration.yml` and `make.yml` now groups `pull_request` runs by workflow and head branch, and every other
  event by workflow, ref and commit SHA, matching `docker-build.yml`. A `main` push is no longer evicted from the
  one-deep pending queue by a later push. `cancel-in-progress` is unchanged (`pull_request` only). No job, step,
  trigger, permission or environment variable changed.
- **Verification & Tests**: workflow-only change (5 files, +20/-5); no application code touched, so `install-holon` was
  not needed. Final-head CI was green before merge.
- **Holon Flow Traversal**: all 5 stages completed (intent ok, plan ok, execute ok, review approved, calibrate ok with
  the calibration report covering execution head `8bb210bd199f`).
