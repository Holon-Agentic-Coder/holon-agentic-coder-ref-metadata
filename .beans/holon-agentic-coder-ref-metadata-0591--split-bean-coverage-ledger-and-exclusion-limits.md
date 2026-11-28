---
# holon-agentic-coder-ref-metadata-0591
title: "Bean coverage across split flows: one ledger, bounded exclusions, no bypass"
status: todo
type: task
priority: high
tags:
  - harness
  - intent
  - holon-flow
  - invariants
created_at: 2026-11-27T00:57:23Z
updated_at: 2026-11-27T01:07:06Z
---

## Evidence

- Category `intent-scope` recurs: CF-0025 (#361), CF-0028 (#362), CF-0029 (#364), CF-0030 (budget step). High priority
  per the audit rule. Bean 0589 delivered the check, but its own Progress lists the gaps below as open or new.
- `todo/intent-coverage-0532.json` excludes all three remaining bean items with the same reason ("queued as separate
  intents"). Only `intent-0532-secret-bundle-private-files.json` exists; no intent exists for the limits test or the
  installer pin. The exclusion hides items that nothing will deliver, which is the partial-delivery failure the check
  was written to stop.
- `todo/intent-coverage-0570.json` excludes the CI-read item as "delivered in the harness repository"; only a "delivered
  by PR #N" reason is verified (via gh), every other reason is accepted as free text.
- Bean 0558 is split into four intents (fail-closed, counts, pre-push gate, markdown coverage). A per-intent check can
  only pass such a split through exclusions, so exclusions are the normal path, not the exception.
- `--bean` is still optional (loud warning only) and the check is skipped on resume. A mapping needs only one shared
  content token, so a weak match passes.

## Goal

A bean's acceptance items are tracked across every intent launched for it, and a bean cannot be launched, resumed or
closed with an item that no intent and no merged PR carries.

## Design

- Per-bean ledger in `todo/`: one row per acceptance item with `intent` (a sibling intent file that exists in `todo/` or
  the queue), `pr` once merged, or `excluded` with a reason.
- An exclusion must name an existing sibling intent file or a merged PR number (verified); free-text reasons are
  refused. An exclusion to a sibling that is not yet launched counts as open, and the bean cannot close until its PR
  merges.
- The keeper may not exclude every item of a bean in one run: an intent whose mapped items are fewer than half the
  bean's items is refused unless the siblings are all in the queue.
- Matching requires a normalised-token overlap above a threshold (not one shared token); the mapping file records the
  score.
- `--bean` mandatory for every launch and every resume; resume re-runs the check against the ledger.
- `post-pr-merge` updates the ledger row from the merged PR and keeps the bean open while any row lacks a merged PR
  (extends bean 0589 item on re-check).

## Acceptance

- [ ] Exclusion with a reason that names no existing sibling intent or merged PR is refused; fixtures: the 0532 and 0570
      files as they are today.
- [ ] An intent covering fewer than half of the bean's items is refused unless every sibling is queued.
- [ ] A one-token match is refused; the mapping file records the match score.
- [ ] `--bean` is required on launch and resume; a launch without it exits non-zero.
- [ ] The ledger blocks bean closure while any item has no merged PR; test uses the 0558 four-intent split.
- [ ] Code has no docstrings and no comments except `# why:`; run with `uv run pytest`.

## Notes

- Related: 0589 (check), 0590 (generator, supersedes the coverage component), 0545 and 0583 (keeper). Do not start
  before deciding whether 0590 absorbs this ledger; if so, link and scrap.
