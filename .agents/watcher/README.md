# GitHub Event Watcher and Rules (Bean 0182)

Waiting must cost zero model tokens. Two tools replace every hand-written polling loop in the harness:

- [`.agents/scripts/wait_for.py`](../scripts/wait_for.py) is the **shared wait primitive**: one blocking command whose
  exit status is the answer.
- [`.agents/scripts/event_watcher.py`](../scripts/event_watcher.py) is the **persistent watcher**: a container that
  outlives sessions, polls GitHub with conditional requests, and appends events to an append-only log. It only detects
  and records. It never acts.

## 1. Shared Wait Primitive

| Command                                                                         | Exit status                                             |
| ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `uv run python .agents/scripts/wait_for.py ci <owner/repo> <pr> [--sha <head>]` | 0 green, 1 failed, 2 timeout, 3 head superseded         |
| `uv run python .agents/scripts/wait_for.py merged <owner/repo> <pr>`            | 0 merged (prints the merge commit), 1 closed, 2 timeout |

Exit 4 means `gh` itself failed (authentication, unknown PR); it is never a CI verdict. `ci` wraps
`gh pr checks <pr> --watch --fail-fast`, retries while a fresh push has not registered its checks yet, and with `--sha`
refuses to report a result for any head other than the one named (the review loop's "votes count only at the current
head" rule). `merged` is a bounded poll (`--timeout`, default 24 hours; `--interval`, default 60 seconds). Both redact
`gh[opsur]_…`, `github_pat_…` and `sk-ant-…` tokens from everything they print.

Run it in the background with the session's background or monitor tooling and react when it exits. Never re-type a
`while`/`sleep` loop in a shell: one broke on zsh word splitting on 2026-10-29, and its result was printed text instead
of an exit status.

## 2. The Watcher

### Start, Stop, Inspect

```bash
# Start (restart policy: unless-stopped). The token comes from the operator's gh login and is passed through the
# environment only: it is not in the compose file, the image, the event log or the state file.
GH_TOKEN="$(gh auth token)" docker compose -f .agents/watcher/compose.yaml up -d --build

# Stop
docker compose -f .agents/watcher/compose.yaml down

# Container logs (rotated by the json-file driver; redacted at source)
docker compose -f .agents/watcher/compose.yaml logs --tail 50
```

Without Compose, the equivalent is:

```bash
docker build -f .agents/watcher/Dockerfile -t holon/event-watcher:local .agents
GH_TOKEN="$(gh auth token)" docker run -d --name holon-event-watcher --restart unless-stopped -e GH_TOKEN \
  --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges:true \
  -v "$PWD/.subagent:/data" holon/event-watcher:local
```

`-e GH_TOKEN` (no value) copies the variable from the invoking shell, so the token never appears on a command line.
Docker keeps it in the container's configuration, so `docker inspect` can show it to anyone with access to the Docker
daemon; that is the same trust boundary as the operator's own `gh` login. For a bounded foreground check, run the script
directly: `uv run python .agents/scripts/event_watcher.py --dir <scratch-dir> watch --max-cycles 2 --interval 5`.

### What It Polls

Every cycle (default 60 seconds), for each managed repository (`Holon-Agentic-Coder/holon-agentic-coder`,
`Holon-Agentic-Coder/holon-coherence`; override with `--repo`, repeatable):

1. `GET repos/<repo>/pulls?state=open` — head SHAs; a PR that leaves the list is fetched once to tell merged from
   closed.
2. `GET repos/<repo>/commits/<head>/check-runs` — aggregated to passed, failed or pending.
3. `GET repos/<repo>/pulls/<pr>/reviews` — new review ids.

Each request sends `If-None-Match` with the ETag of its last response. GitHub answers `304 Not Modified` when nothing
changed, and a 304 does not count against the rate limit, so an idle repository costs nothing. The first successful read
of each repository is a silent baseline, so starting the watcher does not flood the log with history. A failed read is
logged to stderr and retried on the next cycle; it never consumes the baseline and never stops the watcher.

### Files (All Under the Harness `.subagent/`, Git-Ignored)

| File                                   | Writer            | Purpose                                                          |
| -------------------------------------- | ----------------- | ---------------------------------------------------------------- |
| `events.jsonl`                         | watcher           | Append-only event log, one JSON object per line.                 |
| `events.jsonl.1` … `events.jsonl.5`    | watcher           | Size-based rotation (default 5 MiB per file, 5 generations).     |
| `events_watcher_state.json`            | watcher           | ETags, last-seen head, CI state and review ids per PR; next seq. |
| `events.cursor.json` (or `--cursor` …) | consumer sessions | The `seq` of the last event this consumer processed.             |

### Event Schema

```json
{
  "seq": 42,
  "id": "3f1c9a0b5d2e7a61",
  "type": "ci_failed",
  "repo": "Holon-Agentic-Coder/holon-coherence",
  "pr": 32,
  "sha": "<head sha the event is about>",
  "time": "2026-10-29T12:00:00Z",
  "detail": { "failing_jobs": ["unit (ubuntu-latest)"] }
}
```

| `type`          | `detail`                                    | Emitted when                                                   |
| --------------- | ------------------------------------------- | -------------------------------------------------------------- |
| `head_moved`    | `from` (`null` for a newly opened PR), `to` | A PR's head SHA changes, or a new PR appears after baseline.   |
| `ci_pending`    | `{}`                                        | The head's aggregated check state becomes pending.             |
| `ci_passed`     | `{}`                                        | Every check run on the head completed without a failure.       |
| `ci_failed`     | `failing_jobs`                              | Any check run concluded failure, cancelled, timed out, etc.    |
| `review_posted` | `review_id`, `state`, `user`, `url`         | A review id not seen before appears; `sha` is its `commit_id`. |
| `pr_merged`     | `merge_commit`, `merged_at`                 | A PR leaves the open list and GitHub reports it merged.        |
| `pr_closed`     | `closed_at`                                 | A PR leaves the open list without being merged.                |

`seq` is monotonic across rotation and restarts. `id` is a stable hash of type, repo, PR, SHA and key, so a replayed or
duplicated event (for example after the watcher was killed between appending and saving its state) can be recognised.
Delivery is **at least once**: handlers are idempotent.

## 3. Consumer Wiring

- **Live session**: tail the log with the session's monitor or background tooling, for example a Monitor on
  `tail -n0 -F .subagent/events.jsonl`, filtered with `jq` to the repo and PR the session is driving. The session is
  woken per line and spends nothing while waiting.
- **Backlog**: on session start, run `uv run python .agents/scripts/event_watcher.py consume --cursor <cursor-file>` to
  print every event after that consumer's cursor and advance it (`--peek` prints without advancing). Each consumer keeps
  its own cursor file (for example `.subagent/<repo>_pr<N>_events.cursor.json` for one review loop), so several sessions
  can read the same log independently. Nothing is lost while no session runs.

## 4. Rules: Event → Harness Action

The watcher never acts; a consuming session applies this table. A row fires only when its precondition holds; otherwise
the event is recorded as seen and ignored.

| Event                   | Precondition (all must hold)                                                                                                                          | Action                                                                                                                                                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ci_failed`             | A `pr-review-loop` is in progress for this PR (`<repo>_pr<N>_state.json` exists, not terminal), under its iteration cap, and `sha` equals its `head`. | Treat the failing jobs as a finding: fetch `gh run view <run> --log-failed` and dispatch the next resolver iteration (Phase C).                                                                                                           |
| `ci_passed`             | A loop is in progress for this PR, under its cap, `sha` equals its `head`, and the dry run at that head is clean (`posting_gate` reason `clean`).     | Dispatch the 3-agent ensemble (Phase B).                                                                                                                                                                                                  |
| `ci_pending`            | —                                                                                                                                                     | None. Record `ci.state = PENDING` for that head if a loop is tracking it.                                                                                                                                                                 |
| `head_moved`            | A loop is tracking this PR.                                                                                                                           | Run Phase A0.5 (re-sync). Every vote and CI result for the previous head is void.                                                                                                                                                         |
| `review_posted`         | A loop is tracking this PR and the review is not the loop's own posted review.                                                                        | Queue it for Phase A0 / the next resolver as a pre-existing comment to audit.                                                                                                                                                             |
| `pr_merged`             | Post-merge steps were recorded for this PR (in the bean or in `<repo>_pr<N>_state.json` as `post_merge`).                                             | Run exactly those steps: `install-holon` / `install-coherence` from `main` when the PR changed them, the `clean-workspace` skill for that PR's branches and worktrees, and close or update the bean. The event is the merge confirmation. |
| `pr_closed`             | A loop is tracking this PR.                                                                                                                           | Stop the loop for that PR, record `closed` in its state file, keep every artifact. No cleanup: unmerged work stays.                                                                                                                       |
| any, on an untracked PR | —                                                                                                                                                     | None beyond recording it. A new or foreign PR never starts a token-spending loop on its own.                                                                                                                                              |

### Guardrails (Override Every Row)

1. **No new spending.** An event may only continue work that is already authorised: a review loop in progress and under
   its iteration cap, or a post-merge step recorded for that PR. It never starts a loop, raises a cap or adds scope.
2. **Human-only actions stay human-only.** No event ever merges, enables auto-merge, joins a merge queue, approves on
   the maintainer's behalf, or pushes to `main`.
3. **Destructive actions follow the existing rules.** Cleanup after `pr_merged` runs only under the `clean-workspace`
   and `clean-branches` protections: audit branches the maintainer asked to keep stay, unmerged work stays (saved as
   patches first), and the `apps/*/main` worktrees are never touched. `pr_merged` counts as the merge confirmation those
   rules wait for; nothing else does.
4. **Superseded heads are ignored.** CI and review events whose `sha` is not the tracked head are recorded and dropped.
5. **Idempotent handlers.** A handler checks the state file before acting (iteration already dispatched, step already
   done) and records what it did, so a replayed event (`id` already handled) is harmless.
6. **Secrets.** The watcher's token is used read-only (it only issues `GET` requests). Everything it writes passes
   through `wait_for.redact`.

## 5. Decisions on the Bean's Open Questions

- **Token**: the operator's own `gh auth token`, read at start and passed as `GH_TOKEN` in the environment. The watcher
  only reads. Hardening path: a fine-grained token limited to the two repositories with read-only Pull requests, Checks,
  Commit statuses and Metadata, passed the same way.
- **Log location and rotation**: `.subagent/events.jsonl` in the harness checkout (git-ignored, shared by every
  session), rotated at 5 MiB with 5 generations kept (`--max-bytes`, `--keep`); consumers track `seq`, not byte offsets,
  so rotation never loses or repeats events.
- **Consumer**: a live session tails the log with its monitor/background tooling, and replays the backlog from its
  cursor with `consume` on start. A hook was not chosen: hooks fire on tool use, not on external events.
