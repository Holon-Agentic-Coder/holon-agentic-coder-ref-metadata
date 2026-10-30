---
# holon-agentic-coder-ref-metadata-0182
title: "Persistent GitHub event watcher that emits PR and CI events and drives harness actions"
status: completed
type: feature
priority: high
tags:
  - harness
  - review-loop
  - automation
  - ci
  - token-cost
created_at: 2026-10-29T03:10:00Z
updated_at: 2026-10-29T12:30:00Z
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
- 2026-10-30: implemented on harness branch `feat/0182-0170-event-watcher-and-loop-convergence` (`f14c2f0`, no PR yet),
  which also adds this bean's summary of changes, answers the open questions below (token from `gh auth token` passed
  only as `GH_TOKEN`, `.subagent/events.jsonl` with size rotation, a seq-based consumer cursor) and closes it on that
  branch. Here it stays `todo` until that branch lands; the status change is the maintainer's step.
- Related: Bean 0170 (review-loop convergence), Bean 0179 (Stage 4 reviewers in the role container), the
  `clean_workspace` and `install_holon` skills.
- Open questions: where the watcher's token comes from and its scopes; event log location and rotation; whether the
  consumer runs as a session-level monitor or a hook.

## Summary of Changes (2026-10-29)

Harness-only change, edited directly under the AGENTS.md harness exception. No target repository was touched.

- **Shared wait primitive**: `.agents/scripts/wait_for.py`. `ci <owner/repo> <pr> [--sha <head>]` wraps
  `gh pr checks --watch --fail-fast` (0 green, 1 failed, 2 timeout, 3 head superseded; retries while a fresh push has no
  checks registered yet). `merged <owner/repo> <pr>` is a bounded poll (0 merged with the merge commit, 1 closed, 2
  timeout). Exit 4 is a `gh` error, never a verdict. All output is token-redacted.
- **Watcher**: `.agents/scripts/event_watcher.py watch` polls open PRs, check runs per head and reviews of both managed
  repositories with `If-None-Match` ETags (a 304 costs no rate limit), and appends `head_moved`, `ci_pending`,
  `ci_passed`, `ci_failed`, `review_posted`, `pr_merged` and `pr_closed` events (`seq`, `id`, `type`, `repo`, `pr`,
  `sha`, `time`, `detail`) to `.subagent/events.jsonl`. The first successful read of each repository is a silent
  baseline; a failed read never consumes it. State (ETags, heads, CI state, review ids, next seq) lives in
  `.subagent/events_watcher_state.json`.
- **Consumer**: `event_watcher.py consume --cursor <file> [--peek]` replays events after the consumer's cursor; a live
  session tails the log with its monitor/background tooling.
- **Container**: `.agents/watcher/Dockerfile` and `compose.yaml` (restart `unless-stopped`, read-only root, all
  capabilities dropped, `.subagent/` mounted at `/data`). Start with
  `GH_TOKEN="$(gh auth token)" docker compose -f .agents/watcher/compose.yaml up -d --build`.
- **Rules table and guardrails**: `.agents/watcher/README.md` (event, precondition, action; no new spending, human-only
  actions stay human-only, cleanup only under the existing protections, superseded heads ignored, idempotent handlers,
  redaction).
- **Skills switched to the primitives**: `pr_review_loop` (CI watcher, Phase B gate, Phase D retarget, post-merge steps
  recorded in `post_merge` and triggered by `pr_merged` / `wait_for.py merged`), `clean_workspace` and `install_holon`
  (post-merge trigger notes). `validate-links.js` now also checks the watcher README.
- **Tests**: `tests/test_wait_for.py` and `tests/test_event_watcher.py` (gh faked, no network). A bounded smoke test ran
  `wait_for.py merged` and `wait_for.py ci` against real holon-coherence PRs (exit 0 each), and the built image ran two
  cycles against both repositories: baseline recorded, second cycle all 304, no events, no token in the state file.

## Decisions on the Open Questions

- **Token**: the operator's `gh auth token`, read at start and passed only as `GH_TOKEN` in the environment (not in the
  image, compose file, log or state). The watcher only issues `GET` requests. Docker keeps the variable in the container
  configuration (`docker inspect`), the same trust boundary as the operator's `gh` login. Hardening path: a fine-grained
  token restricted to the two repositories with read-only Pull requests, Checks, Commit statuses and Metadata, passed
  the same way.
- **Log location and rotation**: `.subagent/events.jsonl` in the harness checkout, rotated at 5 MiB with 5 generations.
  Consumers track `seq`, not byte offsets, so rotation neither loses nor repeats events. Delivery is at least once;
  handlers are idempotent.
- **Consumer**: a session-level monitor (tail of the log) plus `consume` for the backlog on session start. A hook was
  not chosen, because hooks fire on tool use, not on external events.

## Not Done Here

- The watcher is not left running: starting it is the operator's call (command above).
- The rules table is applied by consuming sessions; no automated dispatcher acts on events (by design: the watcher never
  acts).
- Holon flow Stage 4 reuse of the watcher image (with Bean 0179) stays a later change through the flow.
