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
updated_at: 2026-11-27T00:41:38Z
---

## Maintainer decision (2026-11-27 local)

"yes if you going to infer the intent, we need to be very explicit about the assumption. we should have another section
in the intent for what those assumptions were. often the biggest failures come from untested assumptions. we also need
to have another section on how we are going to test or fill in the assumption"

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

Launching a flow with `--bean NNNN` infers its intent from the bean's description, and no agent writes an intent by
hand. No agent, picker or launcher writes an intent by hand. Every intent keeps the standing invariant sentences,
carries every bean acceptance item, and contains no harness path or bean id. The target refuses an intent that breaks
those rules even when the harness is bypassed.

## Design

0. Input: the flow starts from the maintainer's description, held in the bean. The generator infers the intent from it
   and does not stop to ask. Every inference is recorded as an assumption (step 1) and each one is validated or
   explicitly left to the maintainer (step 3).

1. Harness side: `run_holon_flow.py --bean NNNN` generates the intent.
   - Title and goal are inferred from the bean's description and Acceptance sections. The goal states the
     self-explaining-code invariant.
   - Every item under the bean's Acceptance, Check and Common acceptance sections is carried over, rewritten without
     harness paths or bean ids.
   - The standing invariant sentences are appended by the generator, not by the author: self-explaining code, and
     clock-read UTC timestamps where the bean touches timestamps.
   - Assumptions: each inference the generator makes (goal wording, which files are in scope, whether an item is in
     scope, which stage owns a check, what the maintainer authorised) is written to `assumptions`. Each one gets a
     matching entry in `assumption_validation`. The generator refuses to emit an intent with an assumption that has no
     validation entry.
   - A leak scan (harness paths `.beans/`, `todo/`, `.agents/`; bean ids `NNNN` in harness form) runs over the title,
     goal, every acceptance item, and every assumption and validation text before anything is written to the target. A
     hit refuses the launch.
   - Scope is proposed by a model. `holon intent-check` validates it: no directories, no globs, hub files flagged. A
     flagged hub refuses the launch with the file named.
   - The coverage check from bean 0589 runs on the result: every bean item maps to an intent item, or the launch is
     refused and the item named.
   - The generated intent is written to `todo/` for audit with a content hash. Any hand edit changes the hash and the
     launch refuses it.

2. Target side: the intent schema gains two required sections (below). Stage 1 in `holon` refuses an intent that lacks
   an invariant sentence, has directories or globs in scope, references harness paths, lacks either assumption section,
   or has an assumption without a validation entry. This depends on PR #363 (beans 0564 and 0565). It protects the
   target from a bad intent even when the harness is bypassed.

3. Assumptions and their validation (target schema, harness generator):
   - `assumptions`: list of `{id, statement, why, impact, source}`.
     - `why`: the evidence for the assumption, or a plain statement that there is none.
     - `impact`: `low`, `medium` or `high`.
     - `source`: `inferred_from_description`, `from_code` or `from_standing_rule`.
   - `assumption_validation`: one entry per assumption id, `{assumption_id, method, detail, stage}`.
     - `method`: `research` (code read, with the file path and result cited), `test` (a test that proves it),
       `measurement` (a count or run that proves it), `reviewer_check`, or `pr_question`.
     - `pr_question` is allowed only for `impact: high` assumptions that no other method can validate. The question is
       recorded for the maintainer in the PR body and does not block the flow.
     - `stage`: `before_planning`, `plan_step`, `execution_test` or `review`.

4. Stage changes (target, through `holon flow`):
   - Stage 1: refuses a missing section, an assumption without a validation entry, a `pr_question` on a low or medium
     impact assumption, and an unknown enum value.
   - Stage 2: every validation with a method other than `pr_question` becomes a plan step. `before_planning` items are
     resolved first and their result is recorded in the plan.
   - Stage 4: reviewers check that each assumption was validated at its stage, and flag any untested assumption as a
     finding.
   - Stage 5: calibration records which assumptions held and which failed. Failed ones are promoted to the knowledge
     base (`holon-knowledge/kb`) as failure modes.
   - PR body: a table of every assumption with its validation method, its result, and any `pr_question` for the
     maintainer.

5. Resume: a resume regenerates the intent from the bean and refreshes both checkpoint goal copies
   (`context.intent_data.goal` and `context.stage_results.intent.payload.intent.goal`, bean 0574). Stale goals are
   removed by construction, because the goal is never read from the checkpoint. A resume must reuse the assumption set
   of the launched intent, not re-infer it, so that validation results are not lost (see Open points).

6. Slot keeper and launchers call `--bean` only. No picker drafts an intent.

## Harness and target split

- Harness (direct edits, this repository): the generator in `run_holon_flow.py --bean`, the leak scan, the assumption
  and validation emitter, the content hash, the calls to `holon intent-check` and the 0589 coverage check, the replay
  fixtures and their tests, the `holon_flow` SKILL.md and slot keeper brief, and the registry entry in
  `.agents/invariants.yml`.
- Target (`holon-agentic-coder`, produced through `holon flow` only): the `assumptions` and `assumption_validation`
  schema, the Stage 1 refusals, the Stage 2 plan steps, the Stage 4 review check, the Stage 5 calibration record and kb
  promotion, and the PR body table.
- Order: the target Stage 1 change lands before the generator starts emitting the sections, so the target never sees an
  intent it cannot judge.
- Intent text is copied verbatim into the target's append-only `intents.jsonl`. Assumption statements, `why` and
  validation details therefore name no harness path and no bean id either.

## Relation to the existing intent-questions mechanism

- Target main already has `apps/sandbox-executor/src/sandbox_executor/flow/intent_questions.py` (a rule table of
  `QuestionKind` records for `open_questions`, `questions` and `clarifications`) and its tests in
  `apps/sandbox-executor/tests/flow/test_intent_questions.py`. Stage 1 refuses an intent while any of those questions
  has no answer in `answers` or `resolved_questions`. I did not confirm that PR #363 is the PR that added them.
- Assumptions are a different thing: they are the author's inferences, not questions to a maintainer, and every one must
  carry a validation. The existing mechanism can only block, which is what an unanswered question does.
- Conflict to resolve: a `pr_question` on a high-impact assumption must not be written to `open_questions`. That would
  make Stage 1 halt the flow before the merge, which the no-halt rule forbids (maintainer, 2026-10-26). It is recorded
  in the PR body instead. The existing mechanism is not reused for it.

## Acceptance additions (assumptions)

- [ ] Target test: an intent without `assumptions` or without `assumption_validation` is refused at Stage 1.
- [ ] Target test: an intent with an assumption that has no validation entry is refused at Stage 1.
- [ ] Target test: a `pr_question` on a low or medium impact assumption is refused at Stage 1.
- [ ] Harness test: the generator refuses to emit an intent with an assumption that has no validation entry.
- [ ] Harness test: the leak scan covers assumption statements, `why` and validation details.
- [ ] Replay of today's partial deliveries; each replay must show the gap surfacing as an untested assumption, not as a
      silent pass:
  - 0574 (PR #361, second goal copy): an assumption that refreshing `context.intent_data` is enough for resume. With the
    `stage_results` goal still stale, its validation test fails, and no validation entry exists without that test.
  - 0570 (PR #366, `module_budget_change`): an assumption that the maintainer authorised the budget change, inferred
    from the bean text. It is high impact, so it can only be a `pr_question`; the replay shows it reaches the PR body as
    an open question.
  - 0558 (PR #364, counts): an assumption that per-PR docstring and comment counts appear in the job summary and the
    calibration report (gap 2 of that bean). Nothing validates it, so Stage 1 refuses the intent.
- [ ] Target Stage 4 and Stage 5 tests: an untested assumption becomes a review finding; a failed assumption is promoted
      to `holon-knowledge/kb`.
- [ ] PR body test: the table of assumptions and their validation results is rendered.

## Open points for the maintainer

- Resume re-infers the intent unless it is pinned. Proposal: a resume reuses the assumption set and its content hash
  from the launched intent, and re-infers only when the bean's text changes.
- The `pr_question` channel is non-blocking by design. Confirm that a high-impact assumption which cannot be validated
  should proceed to review with the question in the PR body rather than wait for an answer.

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
