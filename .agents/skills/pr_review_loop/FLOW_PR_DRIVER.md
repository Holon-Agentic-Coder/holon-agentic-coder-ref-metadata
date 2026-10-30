# Flow PR Driver Brief (post-Stage-3 pipeline)

A reusable contract for a subagent that drives ONE Holon flow PR from "Stage 3 pushed" to "approved, calibrated,
awaiting the maintainer's merge". The orchestrating session points a fresh driver here with the per-flow parameters
(bean id, repo, worktree, execution branch prefix `<E>`, intent file, touch set, commit attribution line). Everything
below was learned the hard way across PRs #99–#115 and holon-coherence #28–#36; do not relearn it.

## Hard rules (never break)

- NEVER merge a PR, enable auto-merge, or use a merge queue. Never push to `main`. Never force-push, amend, rebase or
  squash a flow branch (`I-`/`P-`/`E-`); only ADD commits. No `pkill`/`killall`. Never print secrets: redact `sk-ant-`
  and `gh[opsu]_`/`github_pat_` tokens; never read out `~/.holon/secrets/*`.
- Never edit any `apps/*/main` worktree. Work only in YOUR worktree. No `rm` outside your scratch directory.
- Tests only via `uv run task test` / `uv run pytest` from the worktree root; never `PYTHONPATH`; no added line may name
  another test runner. Target files never reference harness paths (`.beans/`, `todo/`, `.agents/`), bean ids or review
  ids — bean ids go only in harness artifact/log names, never in target files, commits pushed to the target, or PR text.
- Exactly three append-only ledgers under `holon-knowledge/ledger/`. Other flows run concurrently in other worktrees;
  never touch them or their branches.

## Steps

1. **Sync**: `git -C <wt> fetch origin`; `git -C <wt> checkout -B "<E>/_" "origin/<E>/_"` (clear the flow's leftover
   staged `intents.jsonl` on the scratch branch first with `git restore --staged --worktree` if present).
2. **Touch set**: verify `git diff origin/main...HEAD` stays inside the agreed touch set (plus `plans/`, `executions/`,
   the ledgers). Out-of-scope hunks become review findings (reverted in a NEW commit with the reason), never silent.
3. **Ledger integrity — verify, don't assume**: `intents.jsonl` must equal `origin/main`'s bytes plus exactly the new
   intent row. Since the pure-append fix (PR #111) this normally holds; restore (main's bytes + the new row, one
   `fix(ledger): …` commit) only if it differs. Check `plans.jsonl`/`executions.jsonl` only append.
4. **Gates**: `uv sync --group dev -q`; `uv run task lint`; `uv run task lint-docs` (holon-coherence has no lint-docs
   task and no `.prettierrc` — use `npx prettier --no-config --check` on changed markdown); `uv run task test`. Fix
   nothing by hand except the ledger: failures become review-loop findings.
5. **PR**: push (`git push origin HEAD`) and open it autonomously (`gh pr create --base main --head "<E>/_"`), body =
   summary bullets + "Flow provenance" (intent/plan/execution ids) + "Stage 4 review runs next; Stage 5 calibration is
   added to this PR before merge.", ending with the Claude Code attribution line. No bean ids or harness paths.
6. **Review loop**: run `pr-review-loop` per [SKILL.md](SKILL.md) — fresh-context subagents for the dry run, resolver
   and each of the 3 blind ensemble reviewers; artifacts in the HARNESS `.subagent/` under `<repo>_pr<N>_*`; every Nit
   applied or rejected-with-reason; post only on 3/3 clean votes at ONE head with all CI green, as `--comment` (own PR);
   record `posted_review`. Wait for CI only at the ensemble/posting gate, via the shared helper
   `.agents/scripts/wait_for.py ci <owner/repo> <pr> [--sha <head>]` (exit 0 green / 1 failed / 2 timeout / 3 head moved
   / 4 gh error — 4 is infrastructure, never a CI verdict) run as a background command.
7. **Stage 5**: `HOLON_SKIP_PREFLIGHT=1 HOLON_TOKEN_REDUCE=0 holon calibrate --repo-dir <wt> "<E>/_"`. (Never use
   `holon-stage.sh` or wrapper scripts; invoke `holon` directly). Push `<E>/calibrated` unchanged, `git merge --ff-only`
   it into `<E>/_`, run the repository Prettier `--check` on the report (since PR #112 it normally passes; add the
   formatting commit only if not), push, confirm the report is in `gh pr diff --name-only`.
8. **Record and report**: calibration commit, EV predicted vs actual, final head, `next_action: "await human merge"` in
   `_state.json`. Report with the AGENTS.md-prescribed "PR #N is approved" message. The merge, and the Post-Merge
   Protocol that follows it, belong to the orchestrator/maintainer.

## Operational lessons (apply, don't rediscover)

- **Never end your turn while waiting.** Wait for your background children's notifications inside the turn. A driver
  that stops "waiting" with no live children is stalled and needs an external nudge — don't be that driver.
- **Salvage, don't duplicate**: a dead child leaves a partial report/edit; re-run it ON ITS OWN in salvage mode. An
  uncommitted resolver edit in the worktree is in-flight work: verify it against the findings and complete or correct
  it; never discard it without recording why. Never launch a replacement beside a live sibling.
- **A verdict with no report file on disk is not a vote.** If the Write tool is blocked, write via shell heredoc; no
  stub at the primary path when falling back.
- **Votes count only at the current head.** Any push (yours, the maintainer's, a concurrent session's) invalidates
  earlier votes; run the sync phase before every pass and re-review the new head.
- **Concurrent-PR ledger conflicts are mechanical**: resolve as `origin/main`'s rows unchanged + this PR's own rows
  appended (per AGENTS.md: interleave chronologically by `created_at`; no test run needed for ledger-only conflicts),
  via a normal merge commit — never a rebase of the flow branch.
- **Quota/credit exhaustion is not a stop**: follow AGENTS.md's fallback ladder (model tier down, then the other runner)
  and resume from the checkpoint/saved state.
