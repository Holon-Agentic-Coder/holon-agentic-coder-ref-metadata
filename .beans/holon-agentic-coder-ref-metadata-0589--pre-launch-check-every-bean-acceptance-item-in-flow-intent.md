---
# holon-agentic-coder-ref-metadata-0589
title: "Pre-launch check: every bean acceptance item appears in the flow intent"
status: in-progress
type: task
priority: high
tags:
  - harness
  - intent
  - invariants
  - holon-flow
created_at: 2026-11-27T00:34:53Z
updated_at: 2026-11-27T00:38:30Z
---

## Evidence

Three PRs merged on 2026-11-27 delivered only part of their bean because the flow intent left out bean items:

| PR   | Bean | Missing item                                                                      | Ledger           |
| :--- | :--- | :-------------------------------------------------------------------------------- | :--------------- |
| #361 | 0574 | second checkpoint goal copy (`context.stage_results.intent...goal`) not refreshed | CF-0025          |
| #366 | 0570 | `module_budget_change` intent field not read by the CI gate                       | CF-0029 (family) |
| #364 | 0558 | CI job summary, calibration counts, executor pre-push gate                        | CF-0029          |

Each intent copied the bean's headline goal but not its acceptance items. Review and calibration passed because they
judge the diff against the intent, not against the bean.

## Goal

No flow launches with a bean acceptance item that the intent does not carry. A bean item missing from the intent refuses
the launch, before any stage runs.

## Design

- `run_holon_flow.py` runs a pre-launch check before `holon flow`. The check takes the intent path and the bean id as
  wrapper command-line arguments. The bean id is never written into the intent JSON (intent text is copied into the
  append-only `intents` ledger, and the target must not reference bean ids).
- The check extracts every item from the bean's `## Acceptance`, `## Check` and `## Common acceptance` sections
  (checkbox items, bullet items and table rows that state a requirement).
- Each bean item must be matched by an intent acceptance item. Matching is fuzzy (normalised tokens, stemming, a
  similarity threshold) and also accepts an explicit mapping.
- The explicit mapping file is written by the launcher to `todo/` as `bean-<id>-intent-map.json`: one row per bean item
  with the matched intent item, or `null`. Rows the fuzzy match rejects are resolved by hand in that file and re-run.
- Any unmapped bean item refuses the launch with a non-zero exit and names the item. The wrapper never passes
  `--skip-review` or any other bypass; a refused launch is reported, not forced.
- The post-merge skill (`post-pr-merge`) re-checks each bean item against the merged diff and records a pass or a gap in
  the bean's Resolution. A gap reopens the bean.
- The check lives in `.agents/skills/holon_flow/scripts/` as a small module with a `pytest` suite under `tests/`. Run
  only with `uv run pytest`.

## Fixtures (today's three cases)

Each fixture stores the bean's item list and the intent's acceptance list as they were on 2026-11-27.

1. Bean 0574 with the intent that omitted the second goal copy: the check must refuse on that item and pass once the
   intent carries it.
2. Bean 0570 with the intent that lacked the CI-read `module_budget_change` item: refused on that item.
3. Bean 0558 with the intent that had fail-closed and per-file counts only: refused on the job-summary,
   calibration-count and pre-push items.

Each fixture also includes a passing case where every item is matched, so the check is shown to fail on a real violation
and pass on the complete intent.

## Relation to other beans

- Bean 0562 (umbrella: every invariant has an explicit, automatic check). This bean adds the intent-coverage invariant
  to that list.
- Bean 0573 (invariant registry). The new check gets a registry entry so the registry test fails if the check is
  removed.
- Bean 0580 (brief builder). The brief builder should call this check so a brief cannot skip it.

## Acceptance

- [ ] Pre-launch check added to `run_holon_flow.py`; the bean id is a wrapper argument and is never written into the
      intent.
- [ ] Every item in the bean's `## Acceptance`, `## Check` and `## Common acceptance` sections is extracted.
- [ ] Each bean item must match an intent acceptance item (fuzzy match plus explicit mapping file in `todo/`); any
      unmatched item refuses the launch and names it.
- [ ] The launcher writes the mapping file to `todo/` for every run.
- [ ] No bypass flag: `--skip-review` stays refused and no new skip option is added.
- [ ] `post-pr-merge` re-checks each bean item against the merged diff and records pass or gap in the bean's Resolution.
- [ ] Tests use today's three cases (0574/PR #361, 0570/PR #366, 0558/PR #364) as fixtures, each with a refusal case and
      a passing case; run with `uv run pytest`.
- [ ] Registry entry (bean 0573) and brief-builder call (bean 0580) are added or linked.
- [ ] Code has no docstrings and no comments except `# why:`; the intent for this work states that invariant in its
      goal.

## Notes

- Ledger rows: CF-0025 (intent-scope, PR #361) and CF-0029 (intent-scope, PR #364). Preventive rule in both: every
  acceptance item of a bean is mapped verbatim to the intent before launch, and any unmapped item blocks the launch.
- Bean 0570's CI gap is tracked there; this bean covers only the launch-side check.

## Progress (2026-11-27T00:36:58Z)

Delivered: `.agents/skills/holon_flow/scripts/intent_coverage.py`, wired into `run_holon_flow.py` (`--bean NNNN`, exit 2
listing unmatched items, skipped on resume, loud warning when absent), mapping file `todo/intent-coverage-<bean>.json`
read, `tests/test_intent_coverage.py` (fixtures for 0574, 0570, 0558 with refusal and passing cases), SKILL.md launch
command, registry entry `intent-covers-bean-acceptance` (partial).

Remaining: make `--bean` mandatory; launcher auto-writing the mapping file; `post-pr-merge` re-check against the merged
diff; brief-builder call (bean 0580).

## Superseded in part by holon-agentic-coder-ref-metadata-0590

The intent-generation bean 0590 makes this check's coverage component part of the generator. The launch-side check here
stays until 0590 lands.

## Progress 2026-11-27T00:40:24Z

Headings now match case-insensitively by prefix (incl. Acceptance Criteria, Done when); a bean with no section is
refused with "bean has no acceptance section". Mapping file gains `excluded` (reason required; "delivered by PR #N"
verified merged via gh, warning offline; logged); mappings must share a content token. Stays in-progress for any
remaining acceptance items.
