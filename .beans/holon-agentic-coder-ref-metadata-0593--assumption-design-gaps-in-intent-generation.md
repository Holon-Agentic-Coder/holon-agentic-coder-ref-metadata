---
# holon-agentic-coder-ref-metadata-0593
title: "Close the gaps in the assumption and risk design of intent generation (bean 0590)"
status: todo
type: task
priority: high
tags:
  - harness
  - holon-flow
  - intent
  - assumptions
created_at: 2026-11-27T00:57:23Z
updated_at: 2026-11-27T01:07:06Z
---

## Evidence

Review of the Design and Acceptance sections of bean 0590 as of the audit. Each gap is a way the design can pass while
the failure it is meant to prevent still happens.

1. **Completeness is unchecked.** The generating model lists the assumptions it knows it makes. The replays of 0574,
   0570 and 0558 name the missing assumption in hindsight; nothing makes a model find the unknown one. Likelihood and
   impact are scored by the same model that wrote the assumption, so an assumption it did not think of has score zero.
2. **Outcome has no "unknown".** Stage 5 records held or failed. An assumption validated only by `pr_question` or never
   exercised is neither; it will be recorded as held and calibrate the likelihood estimates falsely.
3. **Pinned assumptions go stale.** A resume reuses the pinned set unless the bean text changes. An assumption sourced
   `from_code` was validated against a main that has since moved (the CF-0030 and overlap cases show main moves within
   an hour); a resume hours later trusts it.
4. **Scope exclusions are assumptions but are not recorded as such.** "This intent delivers only X" (bean 0532) is the
   largest unrecorded assumption of the day; it belongs in `assumptions` with the sibling intent as validation (see the
   coverage ledger bean).
5. **Rollout order breaks in-flight flows.** Stage 1 refusing intents without the new sections will refuse every parked
   or resumed flow whose intent predates it; no migration is stated.
6. **`pr_question` is read once.** High-impact untestable assumptions proceed (non-blocking) and the question sits in
   the PR body; nothing records the maintainer's answer, so the same question recurs on the next bean and a wrong answer
   is not fed back. The open point on blocking versus non-blocking is undecided and the acceptance tests assume
   non-blocking.
7. **Score arithmetic hides the extremes.** Likelihood x impact makes high-impact/low-likelihood (3) equal to
   low-impact/high-likelihood (3); the first should always require a validation. Untestable raising one level is not
   applied to `impact: high`, `likelihood: low` (stays medium).
8. **Size and cost.** Every assumption, validation and risk entry is copied into the append-only `intents.jsonl` and the
   PR body; there is no cap, so a verbose generator inflates the ledger and the planner's tokens.
9. **Leak scan false positives.** "Bean ids `NNNN` in harness form" matches any four-digit number (years, ports, line
   counts); the rule needs the exact form or it will refuse valid intents.

## Goal

Each gap is closed in the 0590 design, or recorded there as a decision the maintainer accepted.

## Proposal

- Completeness: a second, independent pass (different model or adversarial prompt) lists assumptions the first pass
  missed, comparing the bean text with the generated intent; Stage 4 reviewers get the list. Calibration counts
  assumptions discovered late (a review finding or a failure that was not in the set) as the miss rate of the generator.
- Outcome values: `held`, `failed`, `not_exercised`; only `held` and `failed` train estimates.
- Staleness: a pinned `from_code` assumption carries the main commit it was validated against; a resume revalidates it
  when main changed any file named in it.
- Exclusions: a scope exclusion is an assumption with `source: from_standing_rule` or `inferred_from_description` and a
  validation naming the sibling intent.
- Rollout: Stage 1 accepts an intent with a content hash from before the schema (legacy flag) for resumes only; new
  launches require the sections.
- `pr_question`: the answer is written back into the bean (harness side) and read by the next generator; decide blocking
  policy with the maintainer before the target change is planned.
- Scoring: any `impact: high` assumption needs a validation regardless of likelihood.
- Size: a cap on count and on text length per entry, enforced at Stage 1.
- Leak scan: match `\b(bean|holon-agentic-coder-ref-metadata)[- ]?\d{4}\b` and paths, not bare four-digit numbers.

## Acceptance

- [ ] Each of the nine gaps is addressed in bean 0590 or recorded there as accepted by the maintainer.
- [ ] Replay: a generated set for the 0574 bean contains the stale-checkpoint-copy assumption without being told it.
- [ ] Stage 5 test: `not_exercised` assumptions are excluded from the likelihood calibration.
- [ ] Leak scan test: "port 8080" and "2026" pass; "bean 0574" and a `.beans/` path are refused.

## Notes

- Edits to 0590's scope belong to the maintainer or the coordinator, not this audit; this bean carries the list.
  Related: 0589, 0591.
