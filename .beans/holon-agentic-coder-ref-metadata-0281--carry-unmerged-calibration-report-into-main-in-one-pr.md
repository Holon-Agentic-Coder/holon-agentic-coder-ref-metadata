---
# holon-agentic-coder-ref-metadata-0281
title: "Carry the calibration report that missed its PR into `main` in one pull request"
status: completed
type: task
priority: normal
tags:
  - calibration
  - flow
  - holon-agentic-coder
created_at: 2026-11-12T10:00:00Z
updated_at: 2026-11-13T12:54:27Z
---

## Problem

The first Bean 0262 flow (PR #159) produced a Stage 5 calibration report on its `calibrated` branch, but PR #159 was
reverted (#160) and the re-land (#162) was hand-assembled, so the report never reached `main`. A survey of every
`calibrated` branch left on `origin` after the 2026-11-12 branch clean-up found this is the only one whose report is
missing from `main`:

- `plans/P-1794268104-fd29467b-antigravity-agent-gemini-3.8-flash-medium_calibration.md`, branch
  `I-1794268087-mount-host-worktree-into-sandbox-containers/P-1794268104-fd29467b-antigravity-agent-gemini-3.8-flash-medium/E-1794270142-ea5a02bf-antigravity-agent-gemini-3.8-flash-high/calibrated`
  (commits `2e63f36` the report plus its ledger rows, and `26d7b9a` the stage-5 reconciliation row).

Older plans without a report in `main` have no `calibrated` branch left, so they cannot be recovered this way (see Bean
0268).

## Action

One branch off `origin/main` carrying the two calibration commits by `cherry-pick -x`, ledger-only conflicts resolved by
interleaving rows on `created_at` and removing duplicates, one pull request into `main` for the maintainer.

**Exception to the sole-change-path rule:** assembled by hand outside the Holon flow, at the maintainer's explicit
instruction (2026-11-12). It moves existing, flow-generated, already-audited artefacts and authors no new code. The
exception is named in the commit messages.

## Follow-up

Do not delete the `I-1794268087-...` branch tree until this pull request has merged.

## Resolution

Delivered via [PR #191](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/191) and merged into `main`
(`ff25d77`, 2026-11-13T12:51:41Z):

- **Calibration report in `main`**:
  `plans/P-1794268104-fd29467b-antigravity-agent-gemini-3.8-flash-medium_calibration.md` (62 lines), verified in
  `origin/main` at `ff25d77`.
- **Ledger rows in `main`**: 192 rows appended to `holon-knowledge/ledger/executions.jsonl` (two cherry-picked commits,
  `bf1e2a4` the report and 191 rows, `ff4f4b4` the reconciliation row, both with `-x`).
- **Branch tree**: the `I-1794268087-...` `calibrated` branch was deleted locally and on `origin` (last tip `26d7b9a`)
  after the report was confirmed in `main`. The cherry-picked commits carry new SHAs, so `calibrated` is not an ancestor
  of `main`; the content is preserved.
- **Exception to the sole-change-path rule**: the carry PR was hand-assembled outside the Holon flow at the maintainer's
  explicit instruction (2026-11-12). It has no ensemble review and no calibration report of its own (both set to "none:
  hand-assembled carry PR"). It moves existing, flow-generated, audited artefacts and authors no new code.

Bean 0281 is complete.

## Incident (2026-11-13)

The 2026-11-12 branch clean-up deleted the `I-1794268087-...` branch tree from `origin`, including the `calibrated`
branch this bean depends on, against the follow-up above. The commits `2e63f36` and `26d7b9a` were still in the object
store, and the branch was restored on 2026-11-13 under its original name at `26d7b9a` (pushed to `origin`). Do not
delete it until the carry pull request has merged. Clean-up runs must skip any `calibrated` branch whose report is not
in `main`.
