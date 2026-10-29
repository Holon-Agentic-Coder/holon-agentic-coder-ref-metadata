---
# holon-agentic-coder-ref-metadata-0182
title: "Persistent GitHub event watcher that emits PR and CI events and drives harness actions"
status: todo
type: feature
priority: high
tags:
  - harness
  - review-loop
  - automation
  - ci
  - token-cost
created_at: 2026-10-29T03:10:00Z
updated_at: 2026-10-29T03:10:00Z
---

## Problem

Every wait in the harness is an ad-hoc, hand-written polling loop started per task: CI watchers per PR head in the
pr-review-loop, and a merge watcher before the post-merge install (Bean 0143, PR #104). They are re-typed each time (one
broke on zsh word splitting on 2026-10-29), report results as printed text instead of exit status, stop when the session
ends, and only react to the one thing they were started for. Follow-on work that should happen automatically — cleanup
after a merge, the next review-loop iteration after a CI failure, the ensemble after CI turns green — waits for an agent
or the maintainer to notice.

A subagent is the wrong tool for waiting: it spends model tokens on every check. Waiting must cost zero tokens.

## Proposal (maintainer, 2026-10-29)

A continuously running watcher sends events to the harness whenever something changes, and rules map events to actions.

1. **Watcher.** A small container image with a restart policy, so it outlives sessions. It watches open PRs (and their
   head SHAs and check runs) in the managed repositories. GitHub cannot push to this machine, so it polls, using
   conditional requests (`If-None-Match` / ETags) that do not count against the rate limit when nothing changed. It gets
   a token with the minimum scopes it needs and nothing else from the host.
2. **Event log.** Each change is appended as one JSON line to an append-only harness log (for example
   `.subagent/events.jsonl`): `ci_failed`, `ci_passed`, `ci_pending`, `pr_merged`, `pr_closed`, `head_moved`,
   `review_posted`, each with `repo`, `pr`, `sha`, `time` and detail (failing job, merge commit). The watcher only
   detects and records; it never acts.
3. **Consumer.** A live session tails the log and is woken per event (zero tokens while waiting). With no live session,
   events accumulate and the next session processes the backlog from its last processed offset, so nothing is lost.
4. **Rules.** A small, reviewable table maps events to actions, for example:
   - `pr_merged` → run the post-merge steps recorded for that PR (install `holon` / `holon-coherence` from `main` when
     the PR changed them, the cleanup skill, close or update the bean).
   - `ci_failed` on a review loop's current head → dispatch the next resolver iteration.
   - `ci_passed` on a head whose dry run is clean → dispatch the ensemble.
5. **Shared wait primitive.** One tested helper replaces every inline loop: CI via `gh pr checks <pr> --watch` (blocks,
   exits 0/1), merge via a bounded poll (exit 0 merged, 1 closed, 2 timeout). Usable directly until the watcher exists,
   and by the watcher itself.

## Guardrails

- **Spending:** an event may only trigger work that is already authorised (a review loop in progress and under its
  iteration cap, a post-merge step recorded for that PR). A new or foreign PR never starts a token-spending loop on its
  own.
- **Destructive actions:** cleanup after `pr_merged` follows the existing rules: audit branches the maintainer asked to
  keep stay, unmerged work stays (saved as patches first), and the `main` worktrees are never touched. A `pr_merged`
  event counts as the merge confirmation those rules wait for.
- **Human-only actions stay human-only:** no event ever merges, enables auto-merge, joins a merge queue or pushes to
  `main`.
- **Ordering and duplicates:** events carry the head SHA; results for a superseded head are ignored (the review loop's
  "votes count only at the current head" rule). Handlers are idempotent, so a replayed event is harmless.
- **Secrets:** the watcher redacts tokens in everything it writes.

## Scope

- Harness first (it coordinates across repositories): watcher image, event log, consumer wiring for sessions, rules
  table, shared wait helper, and the pr-review-loop and post-merge steps switched to events.
- Later, through the Holon flow: `holon flow` Stage 4 can reuse the watcher image to wait for CI instead of the one-shot
  `probe_ci_checks()` snapshot (related to Bean 0179).

## Notes

- Supersedes the two smaller ideas discussed on 2026-10-29: a harness `wait_for` script and a CI-watcher role image.
- Related: Bean 0170 (review-loop convergence), Bean 0179 (Stage 4 reviewers in the role container), the
  `clean_workspace` and `install_holon` skills.
- Open questions: where the watcher's token comes from and its scopes; event log location and rotation; whether the
  consumer runs as a session-level monitor or a hook.
