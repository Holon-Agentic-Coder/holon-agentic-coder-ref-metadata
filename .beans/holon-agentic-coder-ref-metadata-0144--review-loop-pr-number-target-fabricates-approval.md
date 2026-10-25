---
# holon-agentic-coder-ref-metadata-0144
title: "holon review-loop <PR number> clones a nonexistent branch and still reports consensus APPROVED"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - provenance
  - flow
created_at: 2026-10-23T15:05:00Z
updated_at: 2026-10-23T15:05:00Z
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

- Workaround in use: pass the execution branch (`I-.../P-.../E-.../_`) as the target.
- Run through the Holon flow on `holon-agentic-coder`.

- Found in the PR #95 review loop (2026-10-24, iterations 19 and 21): once PR #95 merges, the review loop's empty-diff
  guard (fail-closed refusal on `empty_diff` / `diff_unverified`) runs only when `--auto-pr` is set (`flow.py:~3297`),
  and it does not run at all for a PR-number target. Both gaps belong with this bean's PR-number-target fix: run the
  guard whatever the PR-creation mode, so a review can never approve a diff it couldn't verify.
