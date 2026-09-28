---
# holon-agentic-coder-ref-metadata-0063
title:
  "Make review-loop artifacts durable: every dry run and every real run leaves a file the next agent can resume from"
status: completed
type: task
created_at: 2026-09-30T12:30:00Z
updated_at: 2026-09-30T12:45:00Z
---

# Make review-loop artifacts durable

## Context

Running `pr-review-loop` on PR #61 (`holon-agentic-coder`) on 2026-09-29/30 lost most of its own work between sessions,
and the successor session had to rebuild it by hand. Three distinct causes, all of them instruction-level:

1. **The real-mode review body was deleted by design.** `pr-reviewer` step 5 ended with
   `rm -f .subagent/<repo>_pr<N>_review_body.md`. After a review is posted, the only record of what was submitted lives
   on GitHub — and a GitHub review does not record the head SHA it was written against. PR #59's bean note already
   admitted this: the run claimed two report files and "Neither file exists ... The durable record is the posted GitHub
   review, not a local scratch file."
2. **Terminal-state cleanup deleted the intermediates.** Principle 7 told the loop to "delete this repo+PR's
   intermediates except the final consensus report and the ledger". The next PR #61 session therefore opened with two
   stub reports, no history and no consensus baseline, and re-ran verification that had already been done.
3. **`.subagent/` was never resolved to a repository.** The skills say "under `.subagent/`" with no owner. The loop's
   real ledger happened to live in the **worktree's** `.subagent/` while the literal reading of the skill pointed at the
   **harness's** — the successor found the ledger only by accident. A worktree is disposable: Bean 0061 renamed this
   very one mid-loop, and a merged PR's worktree is deleted outright.

None of these is a defect in the change under review. Each one costs the next agent a re-derivation.

## Goals & Action Plan

1. **A canonical, resumable handoff file.** Add `.subagent/<repo>_pr<N>_state.json` — a per-PR singleton,
   machine-readable, holding head, iteration, mode, worktree, `artifacts_dir`, a `passes[]` array with `status` /
   verdict / counts / `done` / `remaining`, CI state, posting-gate state, the `posted_review` receipt, residual risks
   and a one-line `next_action`.
2. **Both modes write it.** Dry-run is not a throwaway pass: the only thing dry-run suppresses is the GitHub write. A
   pass that ends without updating the state file has not finished.
3. **Death leaves a usable trace.** A pass creates its entry as `DEAD` at the start and flips it to `COMPLETE` at the
   end, so a wall-clock kill still records what it established and what it never reached — turning the next attempt into
   a salvage instead of a restart. This is what the PR #61 loop needed 19 times.
4. **Keep the posted review.** Withdraw the `rm -f`. Keep `_review_body.md`, add a permanent `_posted_review.md`
   carrying the submitted text plus the GitHub receipt (`url`, `submitted_at`, accepted kind, head SHA).
5. **Never delete; archive instead.** Replace delete-on-completion with "move into `<repo>_pr<N>_archive/`, never `rm`",
   and name the five files that are permanently exempt. Stale regenerable caches remain discardable — re-fetching them
   is free, and a stale diff is worse than no diff.
6. **Pin the directory to the harness.** `<artifacts_dir>` is `holon-agentic-coder-ref-metadata/.subagent` — the
   checkout holding `.agents/` and `.beans/` — never a target-repo worktree's. Artifacts found elsewhere are **copied**
   forward (never moved or deleted, since the source may be the only surviving ledger) and the source recorded as
   `migrated_from`.
7. **Cold-start contract.** A successor reads three files before any prose: `_state.json`, then `_coordination.json`,
   then the newest report whose entry is `COMPLETE`.

## Resolution

Completed 2026-09-30, harness files edited directly (Sole Change Path control-plane exception).

| File                                         | Change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.agents/skills/pr_review_loop/SKILL.md`     | Principle 7: harness `.subagent/` resolution rule; two new artifact rows (`_state.json`, `_posted_review.md`); delete-on-completion replaced by never-delete/archive with a cache carve-out. New **Principle 10 — "Every Pass Leaves a File the Next Agent Can Read Cold"** with the full `state.json` schema and the four rules that make it a handoff rather than a log. Phase A dry-run contract step 6 now requires the state update. Phase B posting now requires the receipt copy and forbids deleting the body. |
| `.agents/skills/pr_reviewer/SKILL.md`        | Step 2: artifacts-directory rule. Step 4: dry-run keeps its files and updates state; real mode keeps the receipt after posting. **Step 5 rewritten** from "Clean Up" to "Keep the Artifacts (Nothing Is Deleted)"; the `rm -f` is withdrawn.                                                                                                                                                                                                                                                                           |
| `.agents/skills/pr_review_resolver/SKILL.md` | Step 6: resolver report goes to the harness `.subagent/`, and the pass must update `_state.json` with which findings were applied and which were skipped, so the next iteration does not re-adjudicate from zero.                                                                                                                                                                                                                                                                                                      |

Backward compatibility: pre-existing loops keep working — the legacy-union reading rule in Principle 7 still applies,
and a missing `_state.json` simply means "starting fresh" rather than being a failure. The PR #61 loop's own artifacts
(its `coordination.json`, `loop_history.md`, reports and evidence packet) still sit in the worktree `.subagent/` and
must be **copied** to the harness directory under the new rule, not moved, while that worktree still exists.

Target: this repository (harness instructions only). No `holon-agentic-coder` change is implied.

## Notes

- Related: Bean 0057 (the `.subagent/` naming collision that motivated namespacing), Bean 0061 (worktree naming — the
  rename that demonstrated a worktree path is not a durable address), Bean 0019 (the loop whose closeout already
  recorded lost artifacts), Bean 0062 (unrelated redaction-coverage defect deferred out of PR #61).
- Follow-up worth its own bean: `_state.json` is prose-convention only. Nothing in `sandbox_executor` validates it, so
  `flow.py`'s stage-4 orchestration could enforce the schema, refuse to post when `_state.json.head` != live PR head,
  and treat a `DEAD` pass entry as a required salvage input.
