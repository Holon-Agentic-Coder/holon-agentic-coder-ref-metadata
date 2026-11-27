---
# holon-agentic-coder-ref-metadata-0424
title: "A transient DNS or Docker failure ends the review stage and throws away finished reviewer work"
status: todo
type: bug
priority: high
tags:
  - flow
  - review
  - reliability
  - holon-agentic-coder
created_at: 2026-11-24T12:58:00Z
updated_at: 2026-11-27T07:50:33Z
---

## Problem

At 2026-11-24T12:52:22Z the host lost DNS for a short time. Two flows failed in the same second:

- Bean 0405 (PR #275): Stage 4 failed with "Reviewer ensemble container dispatch exited with code 125 without writing
  results" after 12.5 minutes of iteration 1. The three reviewers' work was lost; the resume at 12:53:01Z started
  iteration 2 from nothing.
- Bean 0403 (PR #272): iteration 4 ended `verdict FAILED` after 4.5 minutes, and the ledger push failed with
  `ssh: Could not resolve hostname github.com`.

Both wrappers relaunched within 50 seconds, so the network was back at once. The same signatures appear at
2026-11-23T21:17:09Z (exit 125) and 2026-11-24T06:23:58Z (Stage 3 failed on the same DNS error), and on 2026-11-21
(ledger push).

## Goal

- The engine classifies these as transient infrastructure failures: `docker run` exit 125, DNS resolution failure,
  connection reset or refused to github.com or the model API.
- A transient failure is retried in place with backoff (for example 3 tries over 2 minutes) before the step fails. It
  does not count as a review iteration, and reviewer results already written are kept.
- A reviewer container writes each reviewer's result as soon as that reviewer finishes, so a later failure of the
  ensemble container loses at most the unfinished reviewers.
- The log names the failure as transient infrastructure, with the retry count.

## Expected gain

12.5 minutes of reviewer time and one iteration on PR #275 in this event alone; the previous audit counted 3 iterations
(22 minutes) of infrastructure churn.

## Notes

- Related: Bean 0384 (stall budget), Bean 0417 (wrapper completion gate), Bean 0421 (OOM kill, a different
  infrastructure failure).

## Audit evidence, 2026-11-27T07:49Z (fifth-merge audit)

- **`holon-coherence#66` (`coherence-metrics-unification`, `07:16:26Z`):** after `13.1 min` of Stage 4 review produced
  `3/3 APPROVED (0/0/0)` verdicts, `posting.py` (`gh pr comment` and `gh pr review` via GraphQL) failed with
  `Post "https://api.github.com/graphql": read tcp 127.0.0.1:63992->127.0.0.1:8080: read: connection reset by peer`.
  Stage 4 exited `failed` immediately without retrying the transient `gh` proxy reset, discarding `3/3` approval work
  and precipitating `CF-0044`. Ensure `flow/review/posting.py` uses the in-place retry wrapper.
