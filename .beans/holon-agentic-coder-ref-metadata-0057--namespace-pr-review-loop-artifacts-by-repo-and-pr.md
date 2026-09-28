---
# holon-agentic-coder-ref-metadata-0057
title: "Namespace every pr-review-loop temporary artifact by repository and pull request number"
status: completed
type: task
priority: normal
tags:
  - agents
  - pr-review-loop
  - concurrency
  - tooling
created_at: 2026-09-27T22:25:00Z
updated_at: 2026-09-27T22:25:00Z
---

`.subagent/` is one flat, git-ignored directory shared by every session, every agent and every pull request worked in a
checkout, yet the review skills named their artifacts as if the loop were the only writer:
`dry_run_review_iter_<iteration>_<sha>.md`, `consensus_review_iter_<iteration>_<sha>.md`, `review_body.md`,
`coordination.json`. Two PRs (or two sessions on one PR) overwrite each other's reports, ledger and review body.

## Measured evidence (PR #47, 2026-09-27)

- **The collision already fired.** A parallel session's `consensus_review_iter_1_a14e631.md` and this loop's report of
  the same name occupy the same path; the earlier `dry_run_review_iter_1_a14e631.md` had to be renamed to
  `prior_antigravity_dry_run_iter_1_a14e631.md` by hand before the loop could write its own.
- **Naming drifted toward whatever each model invented.** One live run left 60+ files under `.subagent/` in three
  conventions at once: unscoped (`sync_iter_5_6c03d4a.md`, `resolver_iter_4_6c03d4a.md`, `loop_history.md`,
  `commit_msg_iter4.txt`, `pr47_err.txt`) and ad-hoc PR-prefixed (`pr47_body_fetched_iter5_6c03d4a.md`,
  `pr47_readback_body_iter5.md`, `pr47_title_body_iter5_6c03d4a.json`). Nothing was recoverable as "the artifacts of PR
  N in repo R" by pattern.
- **The ledger is the dangerous one.** `coordination.json` holds `rejected_suggestions`; a second PR writing it erases
  the first PR's adjudications, so disproved findings get re-raised and re-"fixed".

## Change

Canonical pattern, now stated in principle 7 of `.agents/skills/pr_review_loop/SKILL.md`:

```text
.subagent/<repo>_pr<N>_<purpose>_iter_<iteration>_{short_git_commit}.<ext>
```

`<repo>` is the repository name (`holon-agentic-coder-ref-metadata`, `holon-agentic-coder`, `holon-coherence`), `<N>`
the bare PR number, and the `_iter_..._{sha}` tail is dropped only for per-PR singletons. Principle 7 carries the full
artifact table (`_diff.txt`, `_meta.json`, `_dry_run_review_`, `_ensemble_review_iter_N_reviewer_K_`,
`_consensus_review_`, `_resolver_`, `_sync_`, `_concurrent_..._.patch`, `_review_body.md`, `_pr_body.md`,
`_loop_history.md`, `_coordination.json`) plus two behavioural rules: a **legacy read fallback** so a loop already in
flight keeps its rulings while writing onward under the new names, and **scoped cleanup** at a terminal state that
removes only this repo+PR's intermediates and never another PR's files.

Propagated to every skill that touches the directory, so the rule cannot be escaped by entering through another door:

- `.agents/skills/pr_review_loop/SKILL.md` -- principle 7 rewritten; the diff cache, concurrent-edit patch, dry-run
  report, consensus report, review body, adjudication ledger, inspection globs and the resolver's report all reference
  namespaced paths.
- `.agents/skills/pr_reviewer/SKILL.md` -- naming callout in Step 2; ledger read in Step 3; trailer rule now also binds
  the prefix; `gh pr review -F` uses `<repo>_pr<N>_review_body.md`; Step 5 cleanup is scoped instead of "remove any
  temporary files".
- `.agents/skills/pr_review_resolver/SKILL.md` -- step 3e reads/writes `<repo>_pr<N>_coordination.json`; new step 6
  defines the namespaced resolution report and incremental writing.
- `.agents/coordination.md` -- the artifact-inspection example now uses the namespaced glob.

## Notes

- `.subagent/` stays git-ignored; this changes naming, not visibility.
- Deliberately **not** destructive: existing unscoped files are left in place as legacy inputs, and the ledger was
  copied (not moved) to `holon-agentic-coder-ref-metadata_pr47_coordination.json` so the loop running at the time of
  this change never loses its adjudications mid-pass.
- Related: 0056 (never pause; the same run that exposed the collision), 0052 (record wisdom per agent action -- the
  ledger is where those rulings live and is now protected from cross-PR clobbering).

## Resolution

Implemented across the four instruction files above on `actions/features` (PR #47). Verification:
`npx prettier --check "**/*.md"` passes, `node .agents/scripts/validate-links.js` passes, and
`grep -rn "subagent/review_body.md\|subagent/coordination.json\|subagent/dry_run_review_iter_\|subagent/concurrent_iter_" .agents`
returns only the two legacy-fallback mentions that intentionally name the old paths.
