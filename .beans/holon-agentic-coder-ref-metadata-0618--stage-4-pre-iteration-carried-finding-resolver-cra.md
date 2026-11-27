---
# holon-agentic-coder-ref-metadata-0618
title: "Stage 4 pre-iteration carried-finding resolver crashes on clean tree and commits empty ledger rows"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-27T07:49:17Z
updated_at: 2026-11-27T07:50:33Z
---

## Notes

### Evidence (2026-11-27T07:49Z fifth-merge audit)

- On `holon-agentic-coder#408` (`self-doc-tests-49`, `CF-0043`), `abcd50c7` passed `APPROVED (3/3)` at `04:49:18Z`.
  Stage 5 synced `origin/main` (`9773e1d15`), hit `hygiene` (`45944550433` `Check module budgets` on `wisdom.py`), and
  withdrew consensus (`05:47:05Z`).
- On `90e4222d1` (`05:54:58Z`), all 3 reviewers voted `APPROVED (0/0/0)` while `gates.pipeline.state` was `"red"`
  (`45948608972`, `FIND-CI-001`), and the resolver exited 1 at `06:05:22Z` leaving only an unstaged ledger file.
- Across **6 consecutive `--from-stage review` resumes** (`06:05:46Z`–`06:32:14Z`), the pre-iteration carried-finding
  resolver (`Resolving 1 carried finding(s) from an earlier iteration before reviewing`) ran `3.7–4.6 min` each
  (`~24 min` total), produced zero code edits, crashed with
  `Resolver commit failed: ... nothing to commit, working tree clean (resolver exit code 1)`, and still committed and
  pushed **6 empty `chore(review): record review ledger rows (iteration 1)` commits** (`c778c1633`..`be2a5e799`),
  triggering `54` wasted CI workflow runs (`6 x 9`) without clearing `FIND-CI-001` or starting a review.
- Distinct from `0409`/`0449` (inside-loop full-review skips and `unchanged_streak` on `open` reviewer findings): this
  failure sits in the pre-iteration `carried_findings` pass and its unconditional empty ledger commit/push on crash.

### Proposed Change

- In `flow/review/carried_findings.py` and `flow/review/loop.py`:
  1. When a pre-iteration carried-finding resolver pass makes no code diff (`nothing to commit`), do not fail with
     `Resolver commit failed`; if the sole carried finding is `FIND-CI-*` and current head CI is green (or clears after
     target sync), clear the stale `FIND-CI-*` and proceed to review/gate; otherwise halt once with `blocked_on` so
     subsequent resumes do not loop blindly.
  2. Do not commit or push `chore(review): record review ledger rows` on a pre-iteration crash where zero reviews ran
     and zero code changed (avoiding `9` CI workflow triggers per failed resume).

### Expected Gain & Cost

- Saves `~24 min` of dead resolver turns and `54` CI runs on `#408` alone, and stops multi-resume crash loops on carried
  `FIND-CI` findings.
- Cost: small change in `carried_findings.py` / `loop.py` + unit tests.

## Resolution
