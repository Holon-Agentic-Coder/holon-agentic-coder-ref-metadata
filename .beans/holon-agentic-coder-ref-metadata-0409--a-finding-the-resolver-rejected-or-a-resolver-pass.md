---
# holon-agentic-coder-ref-metadata-0409
title: "A finding the resolver rejected, or a resolver pass that changed nothing, does not start another full review"
status: todo
type: feature
priority: high
tags:
  - flow
  - stage-4
  - review
  - resolver
  - holon-agentic-coder
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-27T12:12:18Z
---

## Why

The consensus pass is one of the two gates that matter. In the period, review iterations were spent re-reviewing a head
that had not changed, because the resolver rejected the findings (or produced no new commit) and the loop started a full
review again. The reviewers then raised the same finding, or a new one on code they had already passed.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

- 18 full review iterations (median 6.7 minutes each, 160 minutes of re-review in total together with 8 other churn
  iterations) followed a resolver pass that pushed no new head: the log shows "Dispatching review-loop agent", then
  "Committed ledger rows", and no "Resolver pushed new head".
  - PR #248 (flow-no-auto-sidecar-spawn-v2): 14 full iterations, 10 of them churn. Reviewers raised the same finding 18
    times ("the intent requires the confirmed cause of the in-network 'Failed to connect to holon-proxy port 8080'
    failure, but the PR description omits it"); the resolver rejected it 13 times.
  - Flow checkpoint-and-ledger-ownership (2026-11-21): 19 full iterations, 10 of them on an unchanged head after a
    resolver pass.
- 26 of 249 findings were rejected by the resolver; reviewers are not told which findings were rejected and why.

### Evidence (2026-11-27, PR #408)

- Resumed HAC PR `#408` (`self-doc-tests-49`) got `3/3 APPROVED` in iteration 2, blocked only on `FIND-CI-002`, then ran
  the in-loop `--resolve` resolver pass (`lint_passed: true`, `tests_passed: true`, `disposition: applied`), leaving
  zero non-ledger working-tree changes. Unlike the carried-finding path fixed by Bean `0618` (PR `#412`), the in-loop
  resolver still ran `git commit` after `git add -A -- . :(exclude)holon-knowledge/ledger/...` and crashed with exit
  code `1` (`no changes added to commit`).

## Proposed change

1. **No new head, no full review.** When a resolver pass ends without changing the pull request's diff, the next step is
   not a full review of the same diff.
2. **Rejected findings are adjudicated once.** Each reviewer of the next pass receives the previous findings with their
   dispositions and rejection reasons. A rejected finding that a reviewer raises again with no new evidence goes to one
   adjudication turn (a single reviewer reading the finding, the rejection reason and the code), whose answer is final
   for that finding: either the resolver must apply it, or it is closed and not raised again.
3. **Intent evidence is checked in Stage 3.** When the intent's goal asks for a stated outcome (a confirmed cause, a
   reproducing seed), Stage 3 checks the execution record and the pull request description for it before the review
   starts, and sends it back to the executor if missing.

## Expected gain

Up to 18 full iterations in the period (about 2 hours of reviewer time and three reviewer turns each), and the ping-pong
that kept PR #248 in review for 10 extra iterations.

## Cost

Medium engine change in the review loop (`flow/review/loop.py`, the review prompt). Nits are still actioned: applied, or
rejected with a reason (maintainer's rule); this bean only stops the same rejection from being argued again in full.

## Notes

- Overlap: Bean 0407 (no full review when nothing reviewable changed) is the same family. Bean 0407 owns the skip rule;
  this bean covers the rejected-finding and no-change resolver cases and builds on it.
- Related: Bean 0407 (scoped re-review when nothing reviewable changed; this bean covers the resolver-without-change and
  rejection cases), Bean 0255 (streaming resolvers), Bean 0323 (crashed resolver records findings as rejected).
