---
# holon-agentic-coder-ref-metadata-0352
title: "Push GitHub PR events through gh webhook forward, with cheap polling as the fallback"
status: todo
type: feature
priority: normal
tags:
  - github
  - ci
  - flow
  - harness
  - efficiency
  - holon-agentic-coder
created_at: 2026-11-21T13:12:00+11:00
updated_at: 2026-11-21T13:12:00+11:00
---

## Problem

The flow and the harness skills keep polling GitHub for PR state:

- the CI wait (`flow/github/ci_wait.py`, every 15 s);
- the review loop's mergeability and conflict gate;
- Stage 3 admission and the runner's overlap wait (`run_holon_flow.py`, every 60 s);
- `gh pr checks --watch` in the holon_flow and resolve-conflict skills;
- detecting merges for post-merge.

Every poll costs API rate limit and adds latency, and with several concurrent flows the calls multiply.

`gh event listen` (GitHub Event Streams) would be the natural push channel. It is waitlist-only, though, and returns
HTTP 403 "Event subscriptions are not enabled for this account" until GitHub approves the account. The maintainer is
waitlisted.

## Action

1. **Push channel: `gh webhook forward`** (official extension `cli/gh-webhook`).
   - One forwarder per repository (`holon-agentic-coder`, `holon-coherence`) streams these events to a local listener:
     `pull_request`, `check_suite`, `check_run`, `status`, `pull_request_review` and `push`.
   - Flows and skills subscribe to that listener by PR number or head SHA. There is a single forwarder per repo, and the
     listener fans events out to every waiter. A small local broker owns the forwarder's lifecycle: it starts on demand
     and stops when idle, and only one runs per repo at a time.
   - Events are hints. After each relevant event the waiter reads the current state once (`gh pr view`, `gh pr checks`).
   - Prerequisites (maintainer):
     - install the extension with `gh extension install cli/gh-webhook`;
     - add the `admin:repo_hook` scope with `gh auth refresh -s admin:repo_hook`;
     - repo admin is already in place on both repos (checked 2026-11-21).
2. **Fallback: cheap polling.** It is used whenever the forwarder is unavailable (no extension, missing scope, the
   forwarder dies, or no events arrive):
   - conditional requests with ETag / `If-None-Match`, so an unchanged state costs a 304 that is not rate-limited;
   - one batched GraphQL query covering every PR being watched (state, mergeable, mergeStateStatus, check rollup),
     instead of one `gh` call per PR;
   - backoff while nothing changes.

   Even with the forwarder up, a slow safety poll (every 5-10 min) covers dropped deliveries.

3. **One interface.** A single "wait for PR condition" API (CI finished, mergeable/conflicting, merged/closed, head
   changed, review submitted) with pluggable sources, in this order:
   - Event Streams (`gh event listen`), once the account is enabled, detected with a probe;
   - the webhook forwarder;
   - polling.

   It logs which source is in use.

4. **Callers to move to it:**
   - **Harness (direct edit):** the `run_holon_flow.py` overlap wait, and the CI-wait, merge-wait and conflict-wait
     steps in the holon_flow, resolve-conflict and post-pr-merge skills.
   - **Target repo (through the Holon flow):** `flow/github/ci_wait.py`, the review-loop conflict gate and mergeability
     checks, and the admission wait. Inside role containers, keep polling unless the host broker is reachable. Decide
     this in the plan.
5. **Tests**, hermetic, with a fake event stream and a fake GitHub API:
   - an event wakes the waiter and triggers one state read;
   - a missed event is caught by the safety poll;
   - a forwarder failure falls back to polling;
   - a 304 counts as no change;
   - batched GraphQL covers several PRs;
   - no secrets are logged.

## Replacement by `gh event listen`

`gh webhook forward` is a stopgap until GitHub enables Event Streams for the maintainer's account.

- Keep the forwarder and broker behind the single wait interface. No caller may depend on the forwarder directly.
- Once the probe shows `gh event listen` works (no 403), the replacement is:
  - make Event Streams the push source;
  - delete the forwarder, the broker and their tests;
  - drop the `admin:repo_hook` scope requirement;
  - keep cheap polling as the fallback.
- This should be a small follow-up change. Log it as a new bean when access is granted.

## Notes

- Never print the webhook secret or tokens. Forwarded payloads may include repo data, so keep them local and do not log
  bodies.
- Measure the API calls and wall-clock latency of a flow before and after, using real data only.
- Related: Bean 0234 (event-driven CI progress logging), Bean 0348 (admission), Bean 0191 (one GitHub adapter owns every
  `gh` call). Build on 0191's adapter if it lands first.
