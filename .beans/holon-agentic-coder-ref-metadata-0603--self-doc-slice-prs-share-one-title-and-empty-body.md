---
# holon-agentic-coder-ref-metadata-0603
title: "Self-doc slice PRs all share one truncated title and a boilerplate body with no counts"
status: todo
type: task
priority: medium
tags:
  - holon-flow
  - pr-metadata
  - self-explaining-code
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T04:33:33Z
---

## Evidence

- All ten merged PRs of the window except the first three carry the same title: "feat(self): Modules in one package
  still carry docstrings and explanatory comments, against the r..." (#395 to #402), and the open PRs #393, #394, #396,
  #403 to #409 repeat it with "Test modules ...". The title is the intent problem sentence cut at 100 characters; the
  slice (which package) is not in it, so the merge list, git log and post-merge steps cannot tell the PRs apart.
- The body is boilerplate: "Key Changes: Implement <the same sentence>", "References: None". The 0153 criterion "each PR
  reports before and after counts" is not met; the bean notes it for #397 ("PR #397 body reports no before/after
  counts").
- #401 diff: 17 files, +790/-168; 675 of the added lines are plan, calibration, execution and ledger files; the code
  change is -168/+43 over ten modules. Reviewers and the maintainer scan a diff that is 85 percent bookkeeping.

## Goal

1. Title: conventional prefix plus the intent slug and scope (for example "refactor(flow-review): remove docstrings and
   comments from 10 modules"), at most 72 characters, unique per slice.
2. Body: key changes from the diff (files, before and after docstring and comment counts from the gate), no "None"
   references when the bean is known.
3. Mark bookkeeping files in the PR body or collapse them so the code diff is reviewable first.

## Expected gain and cost

Gain: maintainer merge decisions and post-merge steps identify the right PR; 0153 criterion 3 is satisfied by the
engine, not by hand. Cost: PR metadata builder in the engine; touches the same builder as 0597 (agent and model N/A), so
schedule them together, not in parallel.

## Notes

- Source: self-improvement audit 2026-11-27. Related: 0153, 0597, 0109.
