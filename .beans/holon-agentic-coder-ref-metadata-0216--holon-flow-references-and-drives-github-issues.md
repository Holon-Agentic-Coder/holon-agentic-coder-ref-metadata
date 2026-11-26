---
# holon-agentic-coder-ref-metadata-0216
title: "Holon flow references and drives GitHub Issues (assign on intent, close on merge)"
status: in-progress
type: feature
priority: normal
tags:
  - issue-tracking
  - github-issues
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-11-26T04:10:00Z
---

## Problem

With GitHub Issues as the target tracker (Bean 0333; this bean was written for beads), flow provenance should reference
an issue number instead of a harness bean id: the intent JSON and `intents.jsonl` rows carry a target-native work-item
reference. This also honours the standing rule that harness bean ids never land in the target ledgers.

## Scope

- Intent schema: optional `work_item` field holding an issue number of the target repository; validated when present
  (the issue exists and is open).
- At intent time the host-side engine marks the issue in progress (assignee or label, and the Project status once Bean
  0317 exists) and reads its title and body into the intent context, so sandboxed role agents need no tracker access.
- When Stage 4 opens the pull request, its body carries `Closes #N`, so the maintainer's merge closes the issue. The
  flow never closes an issue itself. A decomposed flow links its child pull requests to the same issue without closing
  it until the final one.
- A flow that is abandoned or scrapped returns the issue to its ready state.
- Boundary with the 3-ledger invariant: ledger rows cite the issue number but never mirror issue state, and issues never
  duplicate ledger rows. No fourth ledger.
- Docs: flow usage docs explain the linkage. Failure to reach GitHub at intent time is a warning, not a stage failure.

## Notes

- Runs through the **Holon flow**. Touches the intent stage, the pull-request code in `flow/github/` and the CLI: never
  run it beside another flow on those files; sequence after Bean 0321 and Bean 0333.
- The token the flow already uses for pull requests (`repo` scope) covers issue writes; Project status needs the
  `project` scope (Bean 0317).
- Related: Bean 0333 (decision), Bean 0215 (import gives the issue numbers), Bean 0191 (one GitHub adapter).

> 2026-11-23: stale worktree deleted 2026-11-23; restart from current main. Backup:
> todo/stale-worktree-backups/flow-flow-references-github-issues-2026-11-23.bundle

## Progress (2026-11-24)

- Flow started from this Claude Code session: intent `todo/intent-0216-flow-references-github-issues.json`, slug
  `flow-references-github-issues`, `claude-agent` / `claude-fable-5-2`, worktree `flow-flow-references-github-issues`.

Note (2026-11-25): stale plan `flow-references-github-issues` deleted after PR #309 merged; restart from current main
via the kept `todo/intent-0216-flow-references-github-issues.json`.

parked 2026-11-26: Stage 3 overlap with PR #318 (context.py, docs/environment_variables.md); resume from checkpoint when
#318 merges.

Note (2026-11-26): in-progress. Flow `flow-references-github-issues` launched from origin/main 4e358955 via
`run_holon_flow.py` (target `apps/holon-agentic-coder/main`, `claude-agent` / `claude-opus-5-5`, log
`todo/flow-flow-references-github-issues.log`). Scope files `issues.py`, `test_issues.py`, `test_intent_work_item.py`
are new files to be created.

Note (2026-11-26): resumed from checkpoint
`apps/holon-agentic-coder/flow-flow-references-github-issues/.holon/flow/checkpoint-flow-references-github-issues.json`
(blocker flow `no-unneeded-full-review` merged as PRs #316-#334 and its worktree is gone). No live runner for the slug
at resume. Log `todo/flow-flow-references-github-issues.log`. parked 2026-11-26: resume from checkpoint hit Stage 3
touch-set overlap with PR #342 (`I-1795694671-ledgers-sorted-chronologically`) on `docs/git_flow.md`; resume from
checkpoint once #342 merges or releases the file.

Note (2026-11-26): resumed from checkpoint after PR #342 merged (20:58Z). No live runner for the slug at resume. parked
2026-11-26: Stage 3 touch-set overlap with open PR #351 (I-1795685390-single-runner-per-checkpoint) on
apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py; re-plan after a Stage 3 scope drift (P-1795727982) hit
it. Resume from checkpoint when #351 merges or releases the file.
