---
# holon-agentic-coder-ref-metadata-0590
title: "Generate flow intents from beans inside the flow; agents never hand-write intents"
status: todo
type: feature
priority: critical
tags:
  - harness
  - holon-flow
  - intent
  - invariants
created_at: 2026-11-27T00:38:30Z
updated_at: 2026-11-27T00:38:30Z
---

## Evidence (2026-11-26 and 2026-11-27)

Hand-written intents in `todo/` caused every intent-side failure of the last two days:

- Partial deliveries: PR #361 (bean 0574), PR #366 (bean 0570), PR #364 (bean 0558) merged without acceptance items the
  intent left out (CF-0025, CF-0029). Review and calibration judged the diff against the intent, so they passed.
- Forbidden code merged: PRs #351, #353, #356, #358 merged docstrings or a stale checkpoint goal without the
  self-explaining-code sentence (bean 0574).
- Overlap parks: directories and hub files in intent scope blocked every flow (CF-0009).
- Ledger risk: harness paths and bean ids typed into intent JSON are copied into the target's append-only `intents`
  ledger.
- Idle slots: pickers drafted intents from scratch while flow slots sat empty.

Bean 0589 (coverage check) and the intent half of bean 0580 (brief builder) each cover one slice. This bean makes the
intent a generated artefact, so the slices stop depending on what an agent types.

## Goal

Launching a flow with `--bean NNNN` produces its intent from the bean. No agent, picker or launcher writes an intent by
hand. Every intent keeps the standing invariant sentences, carries every bean acceptance item, and contains no harness
path or bean id. The target refuses an intent that breaks those rules even when the harness is bypassed.

## Design

1. Harness side: `run_holon_flow.py --bean NNNN` generates the intent.
   - Title and goal come from the bean.
   - Every item under the bean's Acceptance, Check and Common acceptance sections is carried over, rewritten without
     harness paths or bean ids.
   - The standing invariant sentences are appended by the generator, not by the author: self-explaining code, and
     clock-read UTC timestamps where the bean touches timestamps.
   - A leak scan (harness paths `.beans/`, `todo/`, `.agents/`; bean ids `NNNN` in harness form) runs before anything is
     written to the target. A hit refuses the launch.
   - Scope is the only judgement step. A model proposes files. `holon intent-check` validates them: no directories, no
     globs, hub files flagged. A flagged hub refuses the launch with the file named.
   - The coverage check from bean 0589 runs on the result: every bean item maps to an intent item, or the launch is
     refused and the item named.
   - The generated intent is written to `todo/` for audit with a content hash. Any hand edit changes the hash and the
     launch refuses it.
2. Target side: Stage 1 in `holon` refuses an intent that lacks an invariant sentence, has directories or globs in
   scope, or references harness paths. This depends on PR #363 (beans 0564 and 0565). It protects the target from a bad
   intent even when the harness is bypassed.
3. Resume: a resume regenerates the intent from the bean and refreshes both checkpoint goal copies
   (`context.intent_data.goal` and `context.stage_results.intent.payload.intent.goal`, bean 0574). Stale goals are
   removed by construction, because the goal is never read from the checkpoint.
4. Slot keeper and launchers call `--bean` only. No picker drafts an intent.

## Fixtures (today's three cases)

Regenerate the intents for beans 0574 (PR #361), 0570 (PR #366) and 0558 (PR #364) from their bean files. Tests assert
that each generated intent contains the acceptance items that the merged intent dropped, and that the coverage check
refuses the merged intent for each case.

## Acceptance

- [ ] `run_holon_flow.py --bean NNNN` produces an intent containing every bean Acceptance, Check and Common acceptance
      item.
- [ ] The generated intent contains the standing invariant sentences and no harness path or bean id (leak scan test).
- [ ] A hand-edited generated intent is refused (content hash test).
- [ ] Fixtures for beans 0574, 0570 and 0558, regenerated, produce intents that would have caught the gaps; tests run
      with `uv run pytest`.
- [ ] Scope is proposed by a model and validated by `holon intent-check`: directories and globs refused, hub files
      flagged (tests for each).
- [ ] Coverage check from bean 0589 runs on every generated intent; an unmapped item refuses the launch and is named.
- [ ] Resume regenerates the intent from the bean and refreshes both checkpoint goal copies; a test covers a checkpoint
      with stale goals in both places.
- [ ] `holon_flow` SKILL.md and the slot keeper brief use `--bean` only; no picker drafts an intent.
- [ ] Target-side Stage 1 refusal is linked to beans 0564 and 0565 (PR #363).
- [ ] Registry entry in `.agents/invariants.yml` for intent generation, so the registry test fails if the generator or
      its checks are removed.
- [ ] Code has no docstrings and no comments except `# why:`; the intent for this work states that invariant in its
      goal.

## Relation to other beans

- Supersedes bean 0589 (its coverage component becomes part of this bean) and the intent half of bean 0580.
- Related: beans 0562 (every invariant has an automatic check), 0564 and 0565 (target-side harness-reference refusal),
  0574 (resume goal copies), 0579.

## Notes

- Maintainer, 2026-11-27: "do we need to incorporate intent creation as part of holon flow?" ... "ok create a bean for
  this".
- Launch and resume both go through the generator, so the generator's output is the only intent the flow sees.
