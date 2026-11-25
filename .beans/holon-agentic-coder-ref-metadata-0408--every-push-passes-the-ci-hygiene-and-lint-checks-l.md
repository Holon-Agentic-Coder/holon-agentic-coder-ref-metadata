---
# holon-agentic-coder-ref-metadata-0408
title: "Every push passes the CI hygiene and lint checks locally before it leaves the machine"
status: todo
type: feature
priority: high
tags:
  - flow
  - ci
  - hygiene
  - pipeline
  - holon-agentic-coder
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-25T00:28:00Z
---

## Why

At the end of the review process only the pipeline pass and the consensus pass matter. A push that fails a check CI runs
in seconds on any machine (Prettier, ruff, JSON and JSONL validity, file growth) costs a full pipeline (median 7.9
minutes) and usually a resolver pass and a full review iteration (median 6.7 minutes) to undo.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

- 33 pull request heads failed a pipeline in the period; 17 of them failed `hygiene`. Samples read from the failed job
  logs:
  - run 44847881284 (PR #222): Prettier on `executions/E-1795184522-ANA-G3.8F.md`, a file the engine wrote itself.
  - run 45328034281 (PR #268): Prettier on 37 files, among them historical `plans/*_calibration.md` reports and
    `holon-config/metrics/README.md` (Bean 0392 is the resolver's half of this).
  - run 45182713288 (PR #263): `jq: parse error: Invalid numeric literal at line 8175` in the JSON and JSONL validation,
    on a head produced by a merge of `main` (a ledger left invalid by a merge).
- 20 of the 33 failed heads differed from the previous tested head only in bookkeeping files or by a merge of `main`.
- Reviewers raised 10 pure lint findings (ruff E501, F401, I001, E402, RUF022, for example a 162-character help string
  left by a merge resolution) and 25 findings that a file already over 1,000 lines grew (the review prompt's rule in
  `holon-config/prompts/review_loop.template.md`, item 11). Each was settled by a resolver pass and a full re-review.
- Stage 3 has no deterministic lint gate: the executor is only asked in its prompt to follow formatting and linting. The
  resolver has a Markdown gate (`entrypoint/review_markdown_gate.py`) for the Markdown it changed, and nothing for
  engine-written files.

## Proposed change

1. One local gate, the same commands CI's `hygiene` and lint jobs run, scoped to the files the push changes: ruff check
   and format check on changed Python, Prettier check on changed Markdown, `jq` on changed JSON and JSONL, and the
   growth rule for files over 1,000 lines.
2. It runs at the end of every executor turn, after every resolver turn, and before the engine pushes its own commits
   (ledger rows, calibration report, reconciliation, promotion, merge of the target).
3. A failure in an agent turn goes back to the same agent in the same turn (fail early). A failure in an engine-written
   file is fixed by the engine (format the file it wrote) or stops the push with the file named; an invalid JSONL after
   a merge stops the merge.
4. The container's Prettier is the version CI uses, so the local answer and CI's answer are the same.

## Expected gain

- Removes the 17 hygiene failures and the 10 lint findings seen in the period: about 17 pipelines (about 2.2 hours of
  flow waiting at 7.9 minutes each) and 10 resolver passes and re-reviews.
- With the growth rule, removes most of the 25 file-growth findings (12 percent of all 249 findings) before a reviewer
  sees them.

## Cost

Small to medium engine change (`entrypoint/`, `flow/review/`, `flow/stages/calibrate.py`): reuse the existing Markdown
gate, add ruff, `jq` and the growth check. A few seconds per turn.

## Notes

- Related: Bean 0392 (resolver's repo-wide Prettier), Bean 0380 (module budget on every package), Bean 0403 (no full
  pipeline for bookkeeping-only pushes), Bean 0371 (ledgers stop conflicting).

## Audit evidence, 2026-11-25T00:28Z (self-improvement audit, fifth merge)

- **PR #296 (`split-cli-init-modules`):** failed `Test - Hygiene` (`Lint with Ruff` and `make lint` -> `lint-md`
  Prettier check) on `5cc97090` (`chore(review): record review ledger rows (before iteration 1)`), and failed
  `make lint` -> `lint-md` again on `bd5fccc2` (after Stage 4 resolver pass `01418f78`) because the engine-generated
  `executions/E-1795563737-ANA-G4N.md` failed Prettier.
- **PR #289 (`core-helpers-self-doc`):** failed `Test - Hygiene` on Stage 3 push `80126bd7`.
