---
# holon-agentic-coder-ref-metadata-0144
title: "holon review-loop <PR number> clones a nonexistent branch and still reports consensus APPROVED"
status: completed
type: bug
priority: critical
tags:
  - review-loop
  - provenance
  - flow
created_at: 2026-10-23T15:05:00Z
updated_at: 2026-10-29T03:00:00Z
---

## Problem

`holon review-loop --help` documents `target` as "execution branch name, PR number, or PR URL", but a PR number is used
verbatim as a branch name inside the container:

```text
Cloning 90 into /home/holon/.holon-sandbox/workspace from https://x-access-token:gho_[REDACTED]@github.com/...
Running: git clone --branch 90 https://x-access-token:gho_[REDACTED]@github.com/Holon-Agentic-Coder/holon-agentic-coder.git .
gh pr comment failed with returncode 1: failed to run git: fatal: not a git repository (or any of the parent directories): .git
  Iterations     : 1 / 25
  CI Checks      : 1 total, 1 passed, 0 failed, 0 pending (local_tests)
  Consensus      : APPROVED
[BEAN 0034 SAFETY HALT] PR Review Loop reached consensus approval.
```

Observed 2026-10-24 on PRs #90 and #91 (`claude-agent`/`claude-opus-5-5`): each run took about a minute, started no
reviewer container, failed the clone, failed the consensus post, and still exited 0 with `Consensus: APPROVED`. Nothing
reached GitHub (0 comments, 0 reviews on both PRs), so no false approval became public -- but the CLI verdict, and any
ledger row it wrote, is fabricated. Same class of defect as Bean 0134 (success recorded for work that never happened)
and Bean 0135 (verdict inferred from a missing ref).

### The native review loop runs no reviewer at all

Reading `apps/sandbox-executor/src/sandbox_executor/flow.py` (`origin/main` `3bef6f7`, `run_review_loop()` at
`:2547-2740`): one "iteration" is `check_pr_mergeability()` + `probe_ci_checks()`, and findings are only `FIND-DIRTY`
(merge conflict) or `FIND-CI` (CI not green). Consensus is `not dirty and CI green`; `--agent`/`--model` are only
labels. `build_pr_review_consensus_report()` (`:1586-1600`) then renders a "3-Agent Independent Ensemble" in which each
"Reviewer i" has an id hashed from the commit and a vote copied from that single CI verdict. Posted to GitHub, it would
be a fabricated three-reviewer approval. A branch-name target additionally hung host-side at 99% CPU for 21 minutes with
no child process or socket (sample in `todo/logs/0132-review-branch-hang.sample`).

Until fixed, Stage 4 for flow PRs runs through the harness `pr-review-loop` skill (real 3-reviewer ensemble + resolver),
as decided by the maintainer on 2026-10-24.

## Scope

- Dispatch real reviewer agents for the ensemble (one container per reviewer, independent contexts, report files);
  consensus only from their verdicts plus CI. Never synthesise reviewer identities or votes.
- Fix the host-side busy loop on branch-name targets.

- Resolve a PR number or URL to its head branch (`gh pr view <n> --json headRefName`) before cloning; never pass a bare
  number to `git clone --branch`.
- Treat a failed clone/checkout as a hard failure of the iteration: no consensus, non-zero exit, a failure action
  record.
- Consensus `APPROVED` must require that every ensemble reviewer actually ran and returned a verdict; zero dispatched
  reviewers can never yield approval.
- A failed consensus post must fail the stage instead of being logged and ignored.
- Tests: PR-number and PR-URL targets resolve to the head branch; a clone failure yields no approval and non-zero exit;
  an ensemble with zero completed reviewers cannot approve.

## Notes

- **Reached GitHub (2026-10-26, PR #97):** `holon flow` Stage 4 reached "consensus" in 2 s with no reviewer container
  ("no remaining stage from 'review' dispatches an agent runner") and posted two COMMENTED reviews describing a "3-Agent
  Ensemble" with three hashed reviewer IDs, all "APPROVED". The summary described unrelated work ("Audit Remediation",
  "Pre-Commit Security & Hygiene Guard") from the hard-coded fallback title in `flow.py` (~1671). `role_dispatcher.sh`
  dispatches a `review-loop` role, but `entrypoint/review_loop.py` never calls an agent runner. Raised to critical:
  every unattended flow now publishes a fabricated approval. The harness `pr-review-loop` skill remains the Stage 4 path
  until this lands.

- Workaround in use: pass the execution branch (`I-.../P-.../E-.../_`) as the target.
- Run through the Holon flow on `holon-agentic-coder`.

- Found in the PR #95 review loop (2026-10-24, iterations 19 and 21): once PR #95 merges, the review loop's empty-diff
  guard (fail-closed refusal on `empty_diff` / `diff_unverified`) runs only when `--auto-pr` is set (`flow.py:~3297`),
  and it does not run at all for a PR-number target. Both gaps belong with this bean's PR-number-target fix: run the
  guard whatever the PR-creation mode, so a review can never approve a diff it couldn't verify.

## Decomposed first run — branches kept for audit (2026-10-28)

The first `holon flow` run (intent `I-1793188814-native-review-loop-real-ensemble-no-fabricated-approval`) planned a
SPLIT into three ordered sub-intents (plan `P-1793188831`, EV 25.45). It was stopped during child 1's Stage 3 because
child 3 depends on children 1 and 2, which the decomposed-child path cannot yet deliver (Bean 0161). The maintainer
chose three sequential root flows instead (first: `review-loop-fail-closed-target-and-guards`).

**Do not delete these remote branches**: the maintainer is auditing how the sub-intent was created. Every cleanup pass
(`clean-branches`, `clean-workspace`, manual pruning) must skip them until the maintainer says otherwise:

- `I-1793188814-native-review-loop-real-ensemble-no-fabricated-approval/_`
- `I-1793188814-native-review-loop-real-ensemble-no-fabricated-approval/P-1793188831-claude-agent-claude-opus-5-5/_`
- `I-1793188814-native-review-loop-real-ensemble-no-fabricated-approval/P-1793188831-claude-agent-claude-opus-5-5/E-1793189086-claude-agent-claude-opus-5-5/_`
- `I-1793188814-native-review-loop-real-ensemble-no-fabricated-approval--1-harden-the-native-stage-4-review-loop-to-fail-cl/_`
- `I-1793188814-native-review-loop-real-ensemble-no-fabricated-approval--1-harden-the-native-stage-4-review-loop-to-fail-cl/P-1793189108-claude-agent-claude-opus-5-5/_`

Flow log: `todo/logs/0144-flow.log`.

## Progress (2026-10-28)

- **Flow 1 of 3 — merged:** PR #100 (`acb5dc0`, 2026-10-28T15:15:52Z), `review-loop-fail-closed-target-and-guards`. PR
  number or URL resolved to the head branch and SHA before cloning; resolution, clone, fetch, checkout, diff
  verification, git timeouts and posting all fail closed (exit 1, never approved); empty-diff guard on every target
  against the PR's own base, with heads and bases fetched from `origin`; the 21-minute host spin was `_find_git_root()`
  never advancing. Review loop 5 iterations (all findings applied), 3/3 ensemble approval at `575030b`, calibrated (EV
  45.60 predicted, 69.16 actual).
- **Flow 2 of 3 — merged:** PR #101 (`b1b5a1b`, 2026-10-28T21:41:04Z), `review-ensemble-module`. New
  `review_ensemble.py`: N independent reviewer turns (three by default), strict JSON trailer (repeated keys, oversized
  or deep input rejected), any-turn budget breach or unparseable report fails that reviewer only, unanimity consensus,
  scratch root contained to `.holon/review/`. Review loop 10 iterations (all findings applied), 3/3 approval at
  `b6be885`, calibrated (EV 52.70 predicted, 73.08 actual); head `58ad02a`.
- **Flow 3 of 3 — merged:** PR #102 (`f09ca5e`, `review-loop-wire-real-ensemble`, head `45debd1`). Stage 4 is decided
  only by the real ensemble plus mergeable and green CI; the fabricated report is gone (`review_report.py`);
  ACT-REV/ACT-FIND rows; host reviewer turns refused (routing into the role container is Bean 0179). Review loop 5
  iterations (all findings applied), 3/3 approval at `d2acda6`, calibrated (EV 41.32 predicted, 73.82 actual). Original
  scope note: wire the ensemble into `run_review_loop()` and Stage 4, rebuild the consensus report from real results,
  docs.

## Summary of Changes (2026-10-29)

Completed through three sequential Holon flows, all merged by the maintainer: PR #100 (`acb5dc0`, fail-closed target
resolution and guards), PR #101 (`b1b5a1b`, `review_ensemble.py`) and PR #102 (`f09ca5e`, Stage 4 decided by the real
ensemble, fabricated report removed). Each was reviewed with the harness pr-review-loop to 3/3 approval and calibrated.
Host-side reviewer turns are refused (fail closed); routing them through the `review-loop` role container is Bean 0179.
The decomposed first run's five audit branches and every flow branch stay on `origin` at the maintainer's request.
