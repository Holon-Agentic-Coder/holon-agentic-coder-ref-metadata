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
blocked_by:
  - "0333"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-11-23T00:00:00Z
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
