---
# holon-agentic-coder-ref-metadata-0321
title: "Short flow branch names: agent tickers, model codes, no hex, plans keyed by intent"
status: in-progress
type: feature
priority: high
tags:
  - flow
  - branches
  - ledger
  - provenance
  - holon-agentic-coder
created_at: 2026-11-17T14:15:00Z
updated_at: 2026-11-18T04:34:00Z
---

## Problem

A flow branch is `I-{epoch}-{slug}/P-{epoch}-{hex}-{agent}-{model}/E-{epoch}-{hex}-{agent}-{model}/calibrated`. A
typical one is 138 characters, of which about 62 are the agent and model spelled out twice and 18 are the two hex
fields. Decomposed flows nest further and run into GitHub's 255-character ref limit (Bean 0275), which is why intent
slugs are held to 8 characters.

The hex was added by Bean 0149 because a plan ID is used on its own as a flat key (plan file name, calibration report
name, `plans.jsonl` lookup), so two intents planned in the same second by the same runner and model collided. The
branches themselves never collided: each plan sits under its own intent.

## Decisions (maintainer, 2026-11-18)

1. **Agent ticker**: three uppercase letters, defined beside the runner in `agent_defaults.py`. Only the runners that
   are needed get one:

   | Runner              | Ticker |
   | ------------------- | ------ |
   | `claude-agent`      | `CLA`  |
   | `antigravity-agent` | `ANA`  |
   | `pi-agent`          | `PIA`  |

   Tickers are unique (test-enforced) and never reassigned or reused. A runner with no ticker fails at `holon doctor`
   and at intent time, before any branch exists; there is no fallback. `local-model` is not a runner and gets none.
   `codex-agent` and `opencode-agent` get one when they are first needed.

2. **Model code**: derived by rule, no table. First letter of each word in upper case, version numbers kept and joined
   with a dot, anything before a `/` dropped, characters invalid in a git ref removed. `claude-sonnet-5-5` -> `CS5.5`,
   `claude-fable-5` -> `CF5`, `claude-opus-5-5` -> `CO5.5`, `gemini-3.8-flash-medium` -> `G3.8FM`, `gemini-4-argon` ->
   `G4A`, `gpt-5-codex` -> `G5C`, `anthropic/claude-opus-5-5` -> `CO5.5`. A local model name such as `qwen2.5-coder:32b`
   must give a valid ref.

3. **Drop the hex**. New IDs are `P-{epoch}-{ticker}-{model code}` and `E-{epoch}-{ticker}-{model code}`:

   ```
   I-1794567515-sleepfix/P-1794567531-CLA-CS5.5/E-1794567598-CLA-CS5.5/calibrated   (78 characters)
   ```

4. **Plan files follow the branch name**: `plans/{intent}/{plan-id}.md` with the calibration report beside it, mirroring
   the full nesting (child intents, and a child intent hanging off its parent's plan segment,
   `I-…/P-…--{n}-{slug}/P-…/E-…`, as in PRs #194 and #200).

5. **Every plan query names both the intent and the plan ID**, and the duplicate check runs on the intent-and-plan pair.
   The ledger keeps the full `agent` and `model`; the ticker and code are for names only.

6. **Migration of existing plans and ledgers**, with a one-off exemption from the append-only rule granted for this
   migration only:
   - Everything must match the remote branch names. Merged branches are pruned, so the durable record is the head branch
     name of each pull request (204 PRs surveyed 2026-11-18): 131 of 141 `plans.jsonl` rows match a PR head exactly on
     intent plus plan ID; the other 10 are early plans that never raised a PR, for which the ledger's `intent_branch` is
     the record. No plan ID appears under two intents.
   - So no existing ID is renamed. Old-generation names (`P-{epoch}-{agent}-{model}` from PR #47 to #146, with `{hex}`
     from PR #147) stay as they are and stay parseable; only new plans get the short form.
   - Move each of the 262 files in `plans/` to the path its branch had, and rewrite only the stored paths in the ledgers
     (`plan_file`, `calibration_report_path`).
   - The migration verifies each moved file against the PR head branch names and reports mismatches.
   - 25 plan files have no ledger row: match each to a PR head branch by plan ID, otherwise park it in `plans/legacy/`.

7. **Slugs are at most 32 characters**, root and child alike. A hand-written root slug over 32 is rejected at intent
   time; an engine-derived slug is cut to 32 at a word boundary. Budget: a branch name without `refs/heads/` and
   `/calibrated` may be 233 characters. A new `P-` or `E-` segment is at most 26 (model code up to 8). A simple flow is
   65 + slug; each level of nesting adds 31 + slug. With 32-character slugs: 97 simple, 160 with one level of child
   intents, 223 with two. So 32 is the largest round figure that guarantees two levels unshortened (the exact ceiling is
   35); a third level falls back to the existing slug shortening. This replaces the 8-character workaround from
   Bean 0275.

## Action

Run through the Holon flow on `holon-agentic-coder` (`todo/intent-0321-shortref.json`). One intent, so that no
intermediate ID format (`P-{epoch}-{hex}-CLA-…`) ever reaches the ledger; the planner may decompose it.

## Notes

- Touches `ledger.py`, `ref_names.py`, `agent_defaults.py`, `calibration.py`, the planner and executor entrypoints and
  the flow package; do not run concurrently with another flow on those files.
- Most of the agent and model shortening in `ref_names.py` (digests, `original_agent`/`original_model` ledger fields)
  becomes unnecessary; slug shortening stays.
- Not traced yet: every place an execution ID is used without its plan and intent. The flow must check this before the
  hex comes off the `E-` segment.
- `gemini-agent` is redundant with antigravity but still wired into the code (image target, runner, registry). Its
  removal is a separate bean, not part of this one.
